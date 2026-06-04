FROM python:3.11-slim

WORKDIR /workers/slicer

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

# Add /app/shared to Python's search path so `from state import ...` works
# without any sys.path hacks inside the source files.
ENV PYTHONPATH="/workers/shared:${PYTHONPATH}"

CMD python -c "import compas_slicer; print(compas_slicer.__version__)"
