#!/bin/bash
# Start the Flask backend server

cd "$(dirname "$0")"
source venv/bin/activate
python app.py

