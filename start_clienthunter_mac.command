#!/bin/bash

# This .command file is specifically for macOS
# It can be double-clicked directly from Finder

echo "=========================================="
echo "   ClientHunter CLEAN - Email Tool"
echo "        🍎 Mac Version 🍎"
echo "=========================================="
echo ""

# Change to the directory where this script is located
cd "$(dirname "$0")"

echo "📂 Working directory: $(pwd)"
echo ""

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS detected"
    
    # Get macOS version for better troubleshooting
    MAC_VERSION=$(sw_vers -productVersion)
    echo "🖥️  macOS version: $MAC_VERSION"
else
    echo "⚠️  This script is optimized for macOS"
fi

echo ""
echo "[1/4] Checking Python installation..."

# Check for Python (try multiple common locations on Mac)
PYTHON_CMD=""

# Check common Python locations on macOS
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Found: $PYTHON_VERSION"
elif command -v /usr/bin/python3 &> /dev/null; then
    PYTHON_CMD="/usr/bin/python3"
    PYTHON_VERSION=$(/usr/bin/python3 --version 2>&1)
    echo "✅ Found: $PYTHON_VERSION (system)"
elif command -v /usr/local/bin/python3 &> /dev/null; then
    PYTHON_CMD="/usr/local/bin/python3"
    PYTHON_VERSION=$(/usr/local/bin/python3 --version 2>&1)
    echo "✅ Found: $PYTHON_VERSION (Homebrew)"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        echo "✅ Found: $PYTHON_VERSION"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ ERROR: Python 3 is not installed on this Mac"
    echo ""
    echo "🚀 Easy installation for Mac:"
    echo "   Option 1 (Recommended):"
    echo "   1. Open Safari"
    echo "   2. Go to: https://www.python.org/downloads/"
    echo "   3. Click 'Download Python 3.x.x'"
    echo "   4. Double-click the downloaded .pkg file"
    echo "   5. Follow the installer (click Continue → Continue → Install)"
    echo "   6. Double-click this file again"
    echo ""
    echo "   Option 2 (If you have Homebrew):"
    echo "   1. Open Terminal (Cmd+Space, type 'Terminal')"
    echo "   2. Type: brew install python3"
    echo ""
    echo "Press any key to open Python download page..."
    read -n 1
    open "https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "[2/4] Installing required packages..."
echo "📦 Installing packages from requirements.txt..."
echo "⏳ This may take 1-2 minutes on first run..."
echo ""

# Install required packages with comprehensive error handling
if ! $PYTHON_CMD -m pip install -r requirements.txt --quiet; then
    echo ""
    echo "⚠️  Standard installation had issues. Trying user-level install..."
    
    if ! $PYTHON_CMD -m pip install --user -r requirements.txt --quiet; then
        echo ""
        echo "⚠️  User installation also had issues. Trying with upgrade..."
        
        # Try upgrading pip first
        $PYTHON_CMD -m pip install --upgrade pip --quiet
        
        if ! $PYTHON_CMD -m pip install --user -r requirements.txt; then
            echo "❌ Package installation failed."
            echo ""
            echo "🔧 Manual fix (copy and paste these commands in Terminal):"
            echo "   $PYTHON_CMD -m pip install --upgrade pip"
            echo "   $PYTHON_CMD -m pip install streamlit pandas requests beautifulsoup4 googlesearch-python"
            echo ""
            echo "After running those commands, double-click this file again."
            read -p "Press enter to exit..."
            exit 1
        fi
    fi
fi

echo "✅ Packages installed successfully!"
echo ""

echo "[3/4] Starting ClientHunter application..."
echo ""
echo "🌐 Opening your web browser..."
echo "📍 Application URL: http://localhost:8502"
echo ""
echo "💡 Instructions:"
echo "   • The app will open in your default web browser"
echo "   • Keep this terminal window open while using the app"
echo "   • To stop: Press Ctrl+C or close this window"
echo ""

# Give user a moment to read
sleep 2

# Start Streamlit with the correct Python command
echo "🚀 Launching application..."
if ! $PYTHON_CMD -m streamlit run app.py --server.port 8502 --server.headless false --browser.gatherUsageStats false; then
    echo ""
    echo "❌ Failed to start the application."
    echo ""
    echo "🔧 Manual start option:"
    echo "   1. Open Terminal (Cmd+Space, type 'Terminal')"
    echo "   2. Type: cd '$(pwd)'"
    echo "   3. Type: $PYTHON_CMD -m streamlit run app.py"
    echo ""
    read -p "Press enter to exit..."
    exit 1
fi

echo ""
echo "👋 Application stopped. Thanks for using ClientHunter!"
echo ""
read -p "Press enter to close this window..."
