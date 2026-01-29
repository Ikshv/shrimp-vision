#!/bin/bash

# Shrimp Vision Startup Script
# This script starts both the backend and frontend servers

echo "🦐 Starting Shrimp Vision Application..."
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "🚀 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt venv/pyvenv.cfg ] || [ ! -f venv/pyvenv.cfg ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start backend in background
source venv/bin/activate && python run.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🚀 Starting frontend server..."
cd ../frontend

# Install dependencies if package.json is newer than node_modules
if [ package.json -nt node_modules/.package-lock.json ] || [ ! -d node_modules ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Create .env.local if it doesn't exist or update if port is wrong
if [ ! -f .env.local ]; then
    echo "📝 Creating environment file..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:3100" > .env.local
elif ! grep -q "NEXT_PUBLIC_API_URL=http://localhost:3100" .env.local; then
    echo "📝 Updating environment file with correct port..."
    sed -i.bak "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://localhost:3100|" .env.local
    rm -f .env.local.bak
fi

# Start frontend in background
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Shrimp Vision is starting up!"
echo "========================================"
echo "🌐 Frontend: http://localhost:3099"
echo "🔧 Backend API: http://localhost:3100"
echo "📚 API Docs: http://localhost:3100/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
