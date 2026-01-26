#!/bin/bash

# ScreenWrite One-Command Setup & Launch (macOS/Linux)
# This script installs dependencies and starts both Backend and Frontend.

# Colors for output
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎬 Initializing ScreenWrite...${NC}"

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# 2. Check for Node.js
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm not found. Please install Node.js${NC}"
    exit 1
fi

# 3. Setup Backend
echo -e "${YELLOW}📦 Setting up Backend...${NC}"
cd webapp/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
./venv/bin/pip install -r requirements.txt
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
cd ../..

# 4. Setup Frontend
echo -e "${YELLOW}📦 Setting up Frontend...${NC}"
cd webapp/frontend
npm install
cd ../..

# 5. Launch both
echo -e "${GREEN}🚀 Launching ScreenWrite Engines...${NC}"
echo -e "💡 Backend will run on http://localhost:5000"
echo -e "💡 Frontend will run on http://localhost:3000"

# Start Backend in background
cd webapp/backend
./venv/bin/python3 app.py &
BACKEND_PID=$!

# Function to kill backend on exit
trap "kill $BACKEND_PID" EXIT

# Start Frontend in foreground
cd ../frontend
npm run dev
