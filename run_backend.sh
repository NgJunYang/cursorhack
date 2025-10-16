#!/bin/bash

echo "🚀 Starting AI Compliance Copilot Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "❗ Please edit backend/.env with your API keys before continuing"
    exit 1
fi

# Start server
echo "✨ Starting FastAPI server on http://localhost:8000"
echo ""
uvicorn app:app --reload --port 8000
