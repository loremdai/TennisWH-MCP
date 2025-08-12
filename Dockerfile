# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements-api.txt .
RUN pip install --no-cache-dir --user -r requirements-api.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY tennis_warehouse_api.py .
COPY api_server.py .

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Set environment variables
ENV TW_API_TIMEOUT=10
ENV TW_MAX_RESULTS=20

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/categories')"

# Run the application
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]