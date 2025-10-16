#!/bin/bash

echo "🚀 Starting AI Compliance Copilot Frontend..."

cd web

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check for .env.local file
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local file not found. Copying from .env.local.example..."
    cp .env.local.example .env.local
fi

# Start dev server
echo "✨ Starting Next.js dev server on http://localhost:3000"
echo ""
npm run dev
