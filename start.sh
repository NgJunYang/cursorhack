#!/bin/bash

# AI Compliance Copilot Startup Script
# Cursor Hackathon Singapore 2025

echo "🧠 Starting AI Compliance Copilot..."
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd web
npm install
cd ..

# Start backend
echo "🚀 Starting FastAPI backend..."
uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start MCP server
echo "🤖 Starting MCP server..."
cd smithery
python smithery_mcp.py &
MCP_PID=$!
cd ..

# Wait for MCP server to start
sleep 2

# Start frontend
echo "🌐 Starting Next.js frontend..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ AI Compliance Copilot is running!"
echo "=================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🤖 MCP Server: ws://127.0.0.1:8765"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID $MCP_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for any process to exit
wait