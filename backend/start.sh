#!/bin/bash

# =========================================
# Backend Setup and Start Script
# =========================================

echo "=========================================="
echo "🚀 Multi-Agent Medical Assistant Backend"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

cd backend

# Check if virtual environment exists in parent directory
if [ -d "../venv" ]; then
    echo "✅ Found existing virtual environment"
    source ../venv/bin/activate
else
    echo "⚠️  No virtual environment found in parent directory"
    echo "Creating new virtual environment..."
    cd ..
    python3 -m venv venv
    source venv/bin/activate
    cd backend
fi

# Install/Update dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo ""
    echo "⚠️  Warning: .env file not found in project root"
    echo "Please create .env file with required API keys"
    echo "See .env.example for reference"
fi

# Start the backend server
echo ""
echo "=========================================="
echo "🎯 Starting Backend Server..."
echo "=========================================="
echo "📡 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/api/docs"
echo "🔍 Health: http://localhost:8000/api/health"
echo "=========================================="
echo ""

python main.py
