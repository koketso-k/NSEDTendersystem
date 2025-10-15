# =============================================================================
# TENDER INSIGHT HUB - PRODUCTION DOCKERFILE
# =============================================================================
# Project: TIH-2025-001
# Base Image: Python 3.11 Alpine for optimal size and security
# Purpose: Production-ready container for FastAPI application

# Use official Python 3.11 Alpine image for smaller size and better security
FROM python:3.11-alpine3.18

# =============================================================================
# BUILD ARGUMENTS & METADATA
# =============================================================================
ARG APP_VERSION=1.0.0
ARG BUILD_DATE
ARG VCS_REF

# Metadata labels for container identification
LABEL maintainer="TIH Development Team <dev@tenderinsighthub.co.za>" \
      org.label-schema.name="Tender Insight Hub" \
      org.label-schema.description="Cloud-Native SaaS Platform for SME Tender Management" \
      org.label-schema.version="${APP_VERSION}" \
      org.label-schema.build-date="${BUILD_DATE}" \
      org.label-schema.vcs-ref="${VCS_REF}" \
      org.label-schema.schema-version="1.0"

# =============================================================================
# SYSTEM DEPENDENCIES & SECURITY
# =============================================================================
# Install system dependencies required for Python packages and security
RUN apk add --no-cache \
    # Build dependencies
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    # PostgreSQL client dependencies
    postgresql-dev \
    # PDF processing dependencies
    poppler-utils \
    # Image processing dependencies
    jpeg-dev \
    zlib-dev \
    # Text processing
    tesseract-ocr \
    tesseract-ocr-data-eng \
    # Security and utilities
    curl \
    && rm -rf /var/cache/apk/*

# =============================================================================
# APPLICATION USER & SECURITY
# =============================================================================
# Create non-root user for security best practices
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Set working directory
WORKDIR /app

# =============================================================================
# PYTHON DEPENDENCIES
# =============================================================================
# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip==23.3.1 && \
    pip install --no-cache-dir -r requirements.txt && \
    # Clean up build dependencies to reduce image size
    apk del gcc musl-dev libffi-dev

# =============================================================================
# APPLICATION CODE
# =============================================================================
# Copy application code
COPY . .

# Set ownership of application files to appuser
RUN chown -R appuser:appgroup /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/uploads /app/reports && \
    chown -R appuser:appgroup /app/logs /app/uploads /app/reports && \
    chmod 755 /app/logs /app/uploads /app/reports

# =============================================================================
# ENVIRONMENT CONFIGURATION
# =============================================================================
# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Application-specific environment variables
ENV APP_NAME="Tender Insight Hub" \
    APP_VERSION="${APP_VERSION}" \
    ENVIRONMENT=production \
    WORKERS=4 \
    HOST=0.0.0.0 \
    PORT=8000

# =============================================================================
# HEALTH CHECK CONFIGURATION
# =============================================================================
# Add health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# =============================================================================
# SECURITY & RUNTIME CONFIGURATION
# =============================================================================
# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# =============================================================================
# STARTUP COMMAND
# =============================================================================
# Use exec form for proper signal handling
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "30", \
     "--keep-alive", "5", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance", \
     "app.main:app"]

# =============================================================================
# DEVELOPMENT DOCKERFILE (Multi-stage option)
# =============================================================================
# Uncomment the section below for development builds

# FROM python:3.11-alpine3.18 as development
# 
# # Install development dependencies
# RUN apk add --no-cache git
# 
# WORKDIR /app
# 
# # Copy requirements including dev dependencies
# COPY requirements.txt requirements-dev.txt ./
# 
# # Install all dependencies including development tools
# RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
# 
# # Copy source code
# COPY . .
# 
# # Development command with auto-reload
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# =============================================================================
# BUILD INSTRUCTIONS
# =============================================================================
#
# Build Commands:
# ---------------
# # Build production image
# docker build -t tender-insight-hub:latest .
# 
# # Build with version tag
# docker build -t tender-insight-hub:v1.0.0 \
#              --build-arg APP_VERSION=1.0.0 \
#              --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#              --build-arg VCS_REF=$(git rev-parse --short HEAD) .
# 
# # Build development image
# docker build -t tender-insight-hub:dev --target development .
#
# Run Commands:
# -------------
# # Run with environment file
# docker run -d \
#   --name tender-insight-hub \
#   --env-file .env \
#   -p 8000:8000 \
#   tender-insight-hub:latest
#
# # Run in development mode with volume mount
# docker run -d \
#   --name tender-insight-hub-dev \
#   --env-file .env.development \
#   -p 8000:8000 \
#   -v $(pwd):/app \
#   tender-insight-hub:dev
#
# Security Scanning:
# ------------------
# # Scan for vulnerabilities
# docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
#   aquasec/trivy image tender-insight-hub:latest
#
# Registry Commands:
# ------------------
# # Tag for registry
# docker tag tender-insight-hub:latest ghcr.io/your-org/tender-insight-hub:latest
# 
# # Push to registry
# docker push ghcr.io/your-org/tender-insight-hub:latest
#
# =============================================================================
