#!/bin/bash

# screenwrite Development Runner (Unix)

echo -e "\033[0;36mStarting ScreenWrite in development mode...\033[0m"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "\033[0;31mError: Virtual environment not found. Please run ./setup.sh first.\033[0m"
    exit 1
fi

# Activate venv
source venv/bin/activate

echo -e "\033[0;32m1. Starting Backend (Flask) on http://localhost:5000\033[0m"
# Start backend in background
cd webapp/backend
python3 app.py &
BACKEND_PID=$!
cd ../..

echo -e "\033[0;32m2. Starting Frontend (Vite) on http://localhost:3000\033[0m"
# Start frontend in foreground
cd webapp/frontend
npm run dev

# Cleanup backend when frontend stops
kill $BACKEND_PID
