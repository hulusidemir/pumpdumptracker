#!/bin/bash

# Professional Crypto Pump Detector Bot - Linux/Mac Startup Script

echo "=========================================="
echo "🚀 Crypto Pump Detector Bot"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env file and add your Telegram credentials:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import requests, telegram, numpy" &> /dev/null; then
    echo "⚠️  Some dependencies are missing"
    echo "Installing requirements..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
fi
echo ""

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate configuration
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ Configuration Error!"
    echo "Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file"
    exit 1
fi

# Create log file if doesn't exist
touch pump_detector.log

echo "✅ Configuration validated"
echo ""
echo "🚀 Starting Pump Detector Bot..."
echo "Press Ctrl+C to stop"
echo ""
echo "=========================================="
echo ""

# Run the bot
python3 main.py

# Handle exit
echo ""
echo "=========================================="
echo "Bot stopped"
echo "=========================================="
