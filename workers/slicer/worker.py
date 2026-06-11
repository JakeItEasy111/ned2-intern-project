
import sys
sys.path.insert(0, "/app/shared")  # make shared/ importable

from compas_slicer.post_processing import generate_brim, simplify_paths_rdp, seams_smooth
from compas_slicer.print_organization import PlanarPrintOrganizer, set_extruder_toggle
from compas_slicer.post_processing import generate_medial_axis_infill
from compas_slicer.pre_processing import move_mesh_to_point
from compas_slicer.utilities import save_to_text_file
from compas_slicer.slicers import PlanarSlicer
from compas_slicer.config import GcodeConfig
from compas.datastructures import Mesh
from compas.geometry import Point

from arq.connections import RedisSettings
from state import set_status, set_value
from settings import REDIS_URL
from pathlib import Path
from arq import ArqRedis
import asyncio

#---------
# STAGE 2 
#---------

MK4_CONFIG = {
    'LAYER_HEIGHT': 0.2,          # Default structural layer height (mm)
    'EXTRUSION_WIDTH': 0.45,      # Default for standard 0.4mm Nextruder nozzle
    
    # Prusa MK4 Build Volume Boundaries
    'BUILD_VOLUME': {
        'X_MAX': 250.0,
        'Y_MAX': 210.0,
        'Z_MAX': 220.0
    },
    
    # Nextruder Temperature defaults (e.g., PLA)
    'NOZZLE_TEMPERATURE': 220,    
    'BED_TEMPERATURE': 60,
    
    # Kinematics & Nextruder Retraction Safe Limits
    'PRINT_SPEED': 120.0,         # External perimeter baseline speed (mm/s)
    'TRAVEL_SPEED': 200.0,        # Safe X/Y travel speed (mm/s)
    'RETRACTION_LENGTH': 0.8,     # Nextruder short-path retraction (mm)
    'RETRACTION_SPEED': 35.0      # Nextruder retraction speed (mm/s)
}

MIN_INFILL_LENGTH = 7.5 
BRIM_OFFSETS = 4 
THRESHOLD = 0.6
SMOOTH_DISTANCE = 10 
OUTPUT_PATH = "/gcode/"


async def slicer_job(ctx, job_id):

    filepath = Path("/models") / f"{job_id}.stl"
    mesh = Mesh.from_stl(str(filepath))
    gcode_config = configure_gcode_config()

    move_mesh_to_point(mesh, 
                    Point(gcode_config.print_volume_x / 2,
                            gcode_config.print_volume_y / 2,
                            0))
    
    slice_stl_to_gcode(mesh, gcode_config, filepath, f"{job_id}.gcode")

    print(f"Slice [{job_id}] complete. Gcode saved to {OUTPUT_PATH}/{job_id}.gcode")

    redis = ctx["redis"]
    await redis.enqueue_job("prusalink_job", job_id, _queue_name="prusalink")

    return {
        "status": "success",
        "job_id": job_id
    }


async def configure_gcode_config():

    gcode_config = GcodeConfig(
        layer_height=MK4_CONFIG['LAYER_HEIGHT'],
        print_volume=(MK4_CONFIG['BUILD_VOLUME']['X_MAX'],
                      MK4_CONFIG['BUILD_VOLUME']['Y_MAX'],
                      MK4_CONFIG['BUILD_VOLUME']['Z_MAX']),
        feedrate=MK4_CONFIG['PRINT_SPEED'],
        feedrate_travel=MK4_CONFIG['TRAVEL_SPEED'],
        retraction_length=MK4_CONFIG['RETRACTION_LENGTH'],
        feedrate_retraction=MK4_CONFIG['RETRACTION_SPEED'],
        extruder_temperature=MK4_CONFIG['NOZZLE_TEMPERATURE'],
        bed_temperature=MK4_CONFIG['BED_TEMPERATURE']
    )

    # Prusa Buddy Firmware Start G-Code
    gcode_config.start_gcode = """
    M17 ; Enable steppers
    G90 ; Use absolute coordinates
    M83 ; Extruder relative mode
    M104 S170 ; Preheat nozzle to safe probe temp
    M140 S60 ; Heat bed to target
    M190 S60 ; Wait for bed
    G28 ; Home all axes
    G29 P1 ; Prusa MK4 Load Cell automatic mesh bed leveling
    M109 S220 ; Wait for nozzle final temp
    G1 Z0.2 F720
    G1 X50 E10 F1000 ; Intro line
    G92 E0 ; Reset extrusion distance
    """

    # Prusa End G-Code
    gcode_config.end_gcode = """
    G1 E-0.8 F2100 ; Retract filament slightly
    G1 Z220 F720 ; Move print head to max height safely
    G28 X0 ; Home X axis
    M104 S0 ; Turn off hotend
    M140 S0 ; Turn off bed
    M84 ; Disable motors
    """
    return gcode_config


async def slice_stl_to_gcode(mesh, gcode_config, stl_path, filename):
    # Slicing
    slicer = PlanarSlicer(mesh, slicer_type='cgal', layer_height=MK4_CONFIG['LAYER_HEIGHT'])
    slicer.slice_model()

    # Post processing 
    generate_brim(slicer, layer_width=MK4_CONFIG['EXTRUSION_WIDTH'], number_of_brim_offsets=BRIM_OFFSETS)
    simplify_paths_rdp(slicer, threshold=THRESHOLD)
    seams_smooth(slicer, distance=SMOOTH_DISTANCE)

    # Generate infill
    generate_medial_axis_infill(
        slicer,
        min_length=MIN_INFILL_LENGTH,
        include_bisectors=True
        )

    # PrintPoints generation
    print_organizer = PlanarPrintOrganizer(slicer)
    print_organizer.create_printpoints()
    set_extruder_toggle(print_organizer, slicer)

    # Save gcode to file 
    gcode = print_organizer.output_gcode(gcode_config)
    save_to_text_file(gcode, OUTPUT_PATH, filename)


class WorkerSettings:
    functions = [slicer_job, configure_gcode_config, slice_stl_to_gcode]  # list every job this worker handles
    queue_name = "slicer"

    # parsed from REDIS_URL: host, port, password, db
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

    # how many jobs to run concurrently in this process
    max_jobs = 1