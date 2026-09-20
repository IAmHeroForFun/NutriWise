# NutriWise Production Dockerfile
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (build tools, OCR libraries for scanned PDFs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    libmupdf-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/media /app/staticfiles /app/data && \
    chown -R appuser:appuser /app

USER appuser

# Expose internal port
EXPOSE 8000

# Default command: Run database migrations, collect static files, and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn dietary_app.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"]
