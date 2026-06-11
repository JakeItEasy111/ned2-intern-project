FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Maintain your exact workspace path
WORKDIR /workers/slicer

# Install system dependencies. 
# libgmp10 and libmpfr6 are required specifically for compas_cgal's nanobind engine.
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    git \
    libgl1 \
    libglib2.0-0 \
    libxrender1 \
    libxext6 \
    libgmp10 \
    libmpfr6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Upgrading wheel tools ensures the manylinux wheel extracts its native bindings correctly
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Replace the deprecated `mesh_bounding_box` import statement with the modern `bounding_box` utility
# inside compas_slicer's base_slicer.py file so it passes the initialization check on COMPAS 2.0+
# RUN sed -i 's/from compas.datastructures import mesh_bounding_box/from compas.geometry import bounding_box as mesh_bounding_box/' /usr/local/lib/python3.11/site-packages/compas_slicer/slicers/base_slicer.py

COPY . . 

# Retain your exact microservice shared path strategy
ENV PYTHONPATH="/workers/shared:${PYTHONPATH}"

# Runtime safety verification step
RUN python -c "import compas; import compas_cgal; import compas_slicer; print('COMPAS Slicer and CGAL backend successfully loaded!')"

CMD ["python"]