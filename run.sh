#!/bin/bash

# AI Compliance Copilot - Quick Start Script
# This script sets up and runs the complete application

set -e

echo "🚀 AI Compliance Copilot - Quick Start"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before running again!"
    echo "   - GROQ_API_KEY: Get from https://console.groq.com"
    echo "   - SUPABASE_URL & SUPABASE_KEY: Get from https://supabase.com"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install additional demo dependencies
echo "📦 Installing demo dependencies..."
pip install reportlab requests

# Check if web/node_modules exists
if [ ! -d "web/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd web
    npm install
    cd ..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting the application..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "🔧 Starting FastAPI backend..."
uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🌐 Starting Next.js frontend..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID