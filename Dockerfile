# 1. Builder stage: build venv, preload data, train models
FROM python:3.9-slim AS builder

WORKDIR /app

# Install build tools, then clean up apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies into a virtualenv
COPY requirements.txt ./
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY classify.py data_preload.py models.py server.py train.py utils.py test.py ./

# Create directories for data and models
RUN mkdir data models

# Preload raw datasets
RUN /opt/venv/bin/python data_preload.py --dataset mnist && \
    /opt/venv/bin/python data_preload.py --dataset kmnist

# Train both free (ff) and premium (cnn) models
RUN DATASET=mnist TYPE=ff /opt/venv/bin/python train.py && \
    DATASET=kmnist TYPE=cnn /opt/venv/bin/python train.py

# 2. Runtime stage: slim image with venv, code, trained artifacts, AWS CLI
FROM python:3.9-slim

WORKDIR /app

# Install unzip (needed for AWS CLI installer) and AWS CLI v2
RUN apt-get update && \
    apt-get install -y --no-install-recommends unzip curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Copy the virtualenv and application from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# ensure we have all Python deps in this venv
COPY requirements.txt .
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask/FastAPI server uses
EXPOSE 5000

# Default environment (can override at docker run)
ENV DATASET=mnist
ENV TYPE=ff

# Launch your server
ENTRYPOINT ["/opt/venv/bin/python", "server.py"]