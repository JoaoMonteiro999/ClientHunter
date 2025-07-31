@echo off
title ClientHunter CLEAN - Starting...
echo.
echo ==========================================
echo    ClientHunter CLEAN - Email Tool
echo ==========================================
echo.
echo [1/4] Checking Python installation...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [2/4] Installing required packages...
echo Installing packages from requirements.txt...

REM Install required packages
pip install -r requirements.txt >nul 2>&1

echo [3/4] Starting ClientHunter application...
echo.
echo The application will open in your web browser automatically.
echo If it doesn't open, go to: http://localhost:8502
echo.
echo To stop the application, close this window or press Ctrl+C
echo.

REM Start Streamlit
streamlit run app.py --server.port 8502 --server.headless true

echo.
echo Application stopped.
pause
