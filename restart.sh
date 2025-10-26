#!/bin/bash

# Shrimp Vision Restart Script
# This script stops any running instances and starts fresh

echo "🦐 Restarting Shrimp Vision..."
echo "============================="

# Kill any existing processes
echo "🛑 Stopping existing servers..."
pkill -f "python run.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null

# Wait a moment
sleep 2

# Start backend
echo "🚀 Starting backend..."
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Shrimp Vision restarted successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
