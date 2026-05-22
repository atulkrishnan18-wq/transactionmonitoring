# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure stdout/stderr are sent straight to terminal
ENV PYTHONUNBUFFERED 1

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set PYTHONPATH to include current directory for engine imports
ENV PYTHONPATH=/app

# Expose port 5000 for the Flask API
EXPOSE 5000

# Use Gunicorn for production instead of the built-in Flask server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.app:app"]
