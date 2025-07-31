#!/bin/bash

echo "=========================================="
echo "   ClientHunter CLEAN - Email Tool"
echo "=========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS detected - Setting up for Mac..."
    echo ""
    
    # Check if running from right-click -> Open With -> Terminal
    if [ -t 1 ]; then
        echo "✅ Running in Terminal - Good!"
    else
        echo "⚠️  If this window closes immediately, please:"
        echo "   1. Right-click the file 'start_clienthunter.sh'"
        echo "   2. Choose 'Open With' → 'Terminal'"
        echo "   3. Or drag this file to Terminal app"
        echo ""
        sleep 3
    fi
fi

echo "[1/4] Checking Python installation..."

# Check for Python (try multiple versions)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ Found python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        PYTHON_CMD="python"
        echo "✅ Found python (Python 3)"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ ERROR: Python 3 is not installed"
    echo ""
    echo "📝 Easy fix for Mac users:"
    echo "   1. Open Safari and go to: https://www.python.org/downloads/"
    echo "   2. Download 'Python 3.x for macOS'"
    echo "   3. Double-click the downloaded file to install"
    echo "   4. Restart this application"
    echo ""
    echo "💡 Alternative - If you have Homebrew:"
    echo "   Open Terminal and type: brew install python3"
    echo ""
    read -p "Press enter to exit..."
    exit 1
fi

echo "[2/4] Installing required packages..."
echo "Installing packages from requirements.txt..."
echo "(This may take a minute on first run...)"

# Install required packages with better error handling
if ! $PYTHON_CMD -m pip install -r requirements.txt; then
    echo ""
    echo "⚠️  Package installation had issues. Trying alternative method..."
    
    # Try with user install if system install fails
    if ! $PYTHON_CMD -m pip install --user -r requirements.txt; then
        echo "❌ Package installation failed."
        echo ""
        echo "🔧 Quick fix:"
        echo "   1. Open Terminal"
        echo "   2. Type: $PYTHON_CMD -m pip install --upgrade pip"
        echo "   3. Then type: $PYTHON_CMD -m pip install streamlit pandas requests beautifulsoup4 googlesearch-python"
        echo ""
        read -p "Press enter to exit..."
        exit 1
    fi
fi

echo "[3/4] Starting ClientHunter application..."
echo ""
echo "🌐 The application will open in your web browser automatically."
echo "📍 If it doesn't open, manually go to: http://localhost:8502"
echo ""
echo "🛑 To stop the application, press Ctrl+C in this window"
echo ""

# Start Streamlit with the correct Python command
if ! $PYTHON_CMD -m streamlit run app.py --server.port 8502 --server.headless true; then
    echo ""
    echo "❌ Failed to start the application."
    echo ""
    echo "🔧 Manual start:"
    echo "   1. Open Terminal"
    echo "   2. Navigate to this folder"
    echo "   3. Type: $PYTHON_CMD -m streamlit run app.py"
    echo ""
fi

echo ""
echo "Application stopped."
read -p "Press enter to exit..."
