#!/bin/bash
# Startup script that initializes database and starts the server

set -e  # Exit on error

echo "🚀 Starting HCI Experiment Backend..."

# Wait for database to be ready (if using external DB)
if [ -n "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database connection..."
    sleep 2
fi

# Initialize database (idempotent - safe to run multiple times)
echo "📊 Initializing database..."
python init_db.py || {
    echo "⚠️  Database initialization had issues, but continuing..."
}

# Generate ground truth if tasks exist but don't have ground truth
echo "🎯 Generating ground truth answers..."
python generate_ground_truth.py || {
    echo "⚠️  Ground truth generation skipped (may already exist or no tasks yet)"
}

# Start the server
echo "✅ Starting Gunicorn server..."
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --timeout 120 --workers 2

