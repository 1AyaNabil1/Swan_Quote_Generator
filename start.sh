#!/bin/bash

# Start script for AI Quote Generator

echo "🚀 Starting AI Quote Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env file and add your OpenAI API key before running the server."
    exit 1
fi

# Start the server
echo "Starting FastAPI server..."
echo "API Documentation will be available at: http://localhost:8000/docs"
echo "Alternative docs at: http://localhost:8000/redoc"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
