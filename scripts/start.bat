@echo off
REM Shrimp Vision Startup Script for Windows
REM This script starts both the backend and frontend servers

echo 🦐 Starting Shrimp Vision Application...
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install npm and try again.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Start backend server
echo 🚀 Starting backend server...
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if requirements.txt is newer than last install
if not exist "venv\pyvenv.cfg" (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
)

REM Start backend in background
start "Shrimp Vision Backend" cmd /k "venv\Scripts\activate.bat && python run.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🚀 Starting frontend server...
cd ..\frontend

REM Install dependencies if package.json is newer than node_modules
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

REM Create .env.local if it doesn't exist
if not exist ".env.local" (
    echo 📝 Creating environment file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
)

REM Start frontend in background
start "Shrimp Vision Frontend" cmd /k "npm run dev"

echo.
echo 🎉 Shrimp Vision is starting up!
echo ========================================
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Both servers are starting in separate windows.
echo Close those windows to stop the servers.
echo.
pause
