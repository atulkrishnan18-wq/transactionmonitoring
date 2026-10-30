# ScoreSentinel Flask API — Production Dockerfile (AWS EC2 ap-south-1 Mumbai)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose port 5000
EXPOSE 5000

# Run with Gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
