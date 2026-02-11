#!/bin/bash

# screenwrite Unified Setup Script (Unix)

echo -e "\033[0;36mStarting screenwrite setup...\033[0m"

# 1. Check for Python and Node.js
if ! command -v python3 &> /dev/null; then
    echo -e "\033[0;31mError: Python3 is not installed or not in PATH.\033[0m"
    exit 1
fi
if ! command -v npm &> /dev/null; then
    echo -e "\033[0;31mError: Node.js/npm is not installed or not in PATH.\033[0m"
    exit 1
fi

# 2. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate venv and install dependencies
source venv/bin/activate

echo "Installing Python dependencies (Core + Backend)..."
pip install -e .
pip install -r webapp/backend/requirements.txt

# 4. Frontend dependencies
if [ -d "webapp/frontend" ]; then
    echo "Installing frontend dependencies..."
    cd webapp/frontend
    npm install
    cd ../..
fi

# 5. Run onboarding wizard
echo "Running onboarding wizard..."
python3 onboarding.py

echo -e "\n\033[0;32mSetup complete!\033[0m"
echo -e "\033[0;36mTo run the application in development mode, use:\033[0m"
echo -e "  \033[1;33m./run_dev.sh\033[0m"