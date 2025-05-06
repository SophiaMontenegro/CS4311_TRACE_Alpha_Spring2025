#!/bin/bash

# Go to backend, activate virtual environment, and start backend
echo "Starting backend..."
cd Backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Go to frontend and start dev server
echo "Starting frontend..."
cd ../Frontend
npm run dev &
FRONTEND_PID=$!

# Handle Ctrl+C to cleanly exit both
trap "echo 'Stopping the system...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" SIGINT

# Wait for both processes
wait
