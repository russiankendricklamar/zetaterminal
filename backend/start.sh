#!/bin/bash
# Start script for Railpack deployment

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the application using uvicorn
exec python -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
