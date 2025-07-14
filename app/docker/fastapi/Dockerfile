FROM python:3.11-slim

WORKDIR /app

# Install system dependencies only
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from mounted requirements
RUN pip install --upgrade pip

# Create directories that might be needed
RUN mkdir -p /app/storage /app/models /app/logs

# Everything else handled by docker-compose volumes and commands