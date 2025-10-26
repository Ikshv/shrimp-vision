#!/bin/bash

# Shrimp Vision Network Startup Script
# This script starts both servers accessible from the network

echo "🦐 Starting Shrimp Vision for Network Access..."
echo "=============================================="

# Get the local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

echo "📍 Your local IP address: $LOCAL_IP"
echo "🌐 Frontend will be available at: http://$LOCAL_IP:3000"
echo "🔧 Backend API will be available at: http://$LOCAL_IP:8000"
echo ""

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

# Install dependencies if needed
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

# Install dependencies if needed
if [ package.json -nt node_modules/.package-lock.json ] || [ ! -d node_modules ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Create environment file with network IP
if [ ! -f .env.local ]; then
    echo "📝 Creating environment file..."
    echo "NEXT_PUBLIC_API_URL=http://$LOCAL_IP:8000" > .env.local
else
    # Update existing env file
    sed -i.bak "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://$LOCAL_IP:8000|" .env.local
fi

# Start frontend in background
HOSTNAME=0.0.0.0 npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Shrimp Vision is starting up for network access!"
echo "=============================================="
echo "🌐 Frontend: http://$LOCAL_IP:3000"
echo "🔧 Backend API: http://$LOCAL_IP:8000"
echo "📚 API Docs: http://$LOCAL_IP:8000/docs"
echo ""
echo "Share these URLs with your roommate:"
echo "  Main App: http://$LOCAL_IP:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
