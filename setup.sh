#!/bin/bash

# screenwrite Unified Setup Script (Unix)

echo "Starting screenwrite setup..."

# 1. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate venv and install dependencies
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

# 3. Frontend dependencies
if [ -d "webapp/frontend" ]; then
    echo "Installing frontend dependencies..."
    cd webapp/frontend
    npm install
    cd ../..
fi

# 4. Run onboarding wizard
# python onboarding.py