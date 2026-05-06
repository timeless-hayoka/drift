# DRIFT API — Production container
# --------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies (some Python packages need compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY drift/ ./drift/

# Expose the FastAPI port
EXPOSE 8080

# Run the ASGI server
CMD ["uvicorn", "drift.api.server:app", "--host", "0.0.0.0", "--port", "8080"]
