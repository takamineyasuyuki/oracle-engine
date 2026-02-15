#!/bin/bash
# Oracle Engine - Quick Start Script
# MacBook Air (M1) 対応

echo "🚀 Oracle Engine - Phase 1 Quick Start"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed"
    echo "Install Python 3.11+ from https://www.python.org/"
    exit 1
fi

echo ""
echo "Setting up virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ All dependencies installed"
echo ""
echo "======================================"
echo "🎯 Setup Complete!"
echo "======================================"
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Or simply run:"
echo "  source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo ""
