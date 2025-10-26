#!/bin/bash

# Shrimp Vision Cross-Subnet Startup Script
# For accessing from 192.168.1.x network

echo "🦐 Starting Shrimp Vision for Cross-Subnet Access..."
echo "=================================================="

# Network information
YOUR_IP="10.229.64.145"
ROUTER_IP="10.229.64.220"
ROOMMATE_NETWORK="192.168.1.x"

echo "📍 Your IP: $YOUR_IP"
echo "🔗 Router IP: $ROUTER_IP"
echo "👥 Roommate's Network: $ROOMMATE_NETWORK"
echo ""

echo "🔧 Configuration needed on router ($ROUTER_IP):"
echo "   Port Forward: 3099 → $YOUR_IP:3099"
echo "   Port Forward: 3100 → $YOUR_IP:3100"
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

# Create environment file with your IP
if [ ! -f .env.local ]; then
    echo "📝 Creating environment file..."
    echo "NEXT_PUBLIC_API_URL=http://$YOUR_IP:3100" > .env.local
else
    # Update existing env file
    sed -i.bak "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=http://$YOUR_IP:3100|" .env.local
fi

# Start frontend in background
HOSTNAME=0.0.0.0 PORT=3099 npm run dev &
FRONTEND_PID=$!

echo ""
echo "🎉 Shrimp Vision is starting up!"
echo "=============================================="
echo "🌐 Frontend: http://$YOUR_IP:3099"
echo "🔧 Backend API: http://$YOUR_IP:3100"
echo "📚 API Docs: http://$YOUR_IP:3100/docs"
echo ""
echo "📋 Next Steps:"
echo "1. Configure port forwarding on your router ($ROUTER_IP):"
echo "   - Port 3099 → $YOUR_IP:3099"
echo "   - Port 3100 → $YOUR_IP:3100"
echo ""
echo "2. Your roommate can then access:"
echo "   - http://[ROUTER_EXTERNAL_IP]:3099"
echo "   - http://[ROUTER_EXTERNAL_IP]:3100"
echo ""
echo "3. Or try direct access first:"
echo "   - http://$YOUR_IP:3099"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
