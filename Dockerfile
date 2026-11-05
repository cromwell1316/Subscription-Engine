FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing .pyc and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and documentation
COPY src/ /app/src/
COPY docs/ /app/docs/
COPY tests/ /app/tests/

EXPOSE 8000

# Default command launches FastAPI app via uvicorn
CMD ["uvicorn", "billing.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
