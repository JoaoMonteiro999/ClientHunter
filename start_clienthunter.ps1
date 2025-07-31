# ClientHunter CLEAN Launcher
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   ClientHunter CLEAN - Email Tool" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Checking Python installation..." -ForegroundColor Yellow

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[2/4] Installing required packages..." -ForegroundColor Yellow
Write-Host "Installing streamlit, pandas, requests, beautifulsoup4, googlesearch-python..." -ForegroundColor Gray

# Install required packages
try {
    pip install -r requirements.txt --quiet
    Write-Host "✅ Packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some packages may have failed to install, but continuing..." -ForegroundColor Yellow
}

Write-Host "[3/4] Starting ClientHunter application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 The application will open in your web browser automatically." -ForegroundColor Green
Write-Host "📍 If it doesn't open, go to: http://localhost:8502" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 To stop the application, close this window or press Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
try {
    streamlit run app.py --server.port 8502 --server.headless true
} catch {
    Write-Host "❌ Failed to start application" -ForegroundColor Red
    Write-Host "Please check if all files are present and try again" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Application stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
