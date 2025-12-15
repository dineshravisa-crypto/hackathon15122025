# PowerShell start script for Windows
# Commander Data Agent API

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Commander Data Agent API - Quick Start" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please create a .env file with your API keys:" -ForegroundColor Yellow
    Write-Host "1. Copy env.example to .env"
    Write-Host "2. Add your OPENAI_API_KEY"
    Write-Host "3. Optionally add TAVILY_API_KEY for web search"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path env312)) {
    Write-Host "Creating virtual environment with Python 3.12..." -ForegroundColor Yellow
    py -3.12 -m venv env312
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Trying with 'python' command..." -ForegroundColor Yellow
        python -m venv env312
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\env312\Scripts\Activate.ps1"

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Check if requirements are installed
$fastapi = pip show fastapi 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies (this may take 2-3 minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Write-Host ""
        Write-Host "Try running PowerShell as Administrator:" -ForegroundColor Yellow
        Write-Host "Right-click PowerShell -> Run as Administrator" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
    Write-Host ""
}

# Start the server
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Starting Commander Data Agent API..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python main.py

Read-Host "Press Enter to exit"

