@echo off
REM Quick start script for Windows
REM Commander Data Agent API

echo ================================================
echo Agent Easy Insurance Sales Agent API - Quick Start
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo.
    echo Please create a .env file with your API keys:
    echo 1. Copy env.example to .env
    echo 2. Add your OPENAI_API_KEY
    echo 3. Optionally add TAVILY_API_KEY for web search
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist env312 (
    echo Creating virtual environment with Python 3.12...
    py -3.12 -m venv env312
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        echo Trying with 'python' command...
        python -m venv env312
        if %errorlevel% neq 0 (
            pause
            exit /b 1
        )
    )
    echo Virtual environment created successfully!
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call env312\Scripts\activate.bat

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Check if requirements are installed
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
    echo.
)

REM Start the server
echo ================================================
echo Starting Commander Data Agent API...
echo ================================================
echo.
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

python main.py

pause

