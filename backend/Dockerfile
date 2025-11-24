# Use Python 3.12 explicitly (pandas 2.1.3 requires Python < 3.13)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render will set PORT env var)
EXPOSE 5000

# Run gunicorn
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120 --workers 2
