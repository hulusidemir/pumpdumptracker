@echo off
REM Professional Crypto Pump Detector Bot - Windows Startup Script

echo ==========================================
echo 🚀 Crypto Pump Detector Bot
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env >nul
    echo.
    echo 📝 Please edit .env file and add your Telegram credentials:
    echo    - TELEGRAM_BOT_TOKEN
    echo    - TELEGRAM_CHAT_ID
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import requests, telegram, numpy" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some dependencies are missing
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
)
echo.

echo ✅ Configuration validated
echo.
echo 🚀 Starting Pump Detector Bot...
echo Press Ctrl+C to stop
echo.
echo ==========================================
echo.

REM Run the bot
python main.py

echo.
echo ==========================================
echo Bot stopped
echo ==========================================
pause
