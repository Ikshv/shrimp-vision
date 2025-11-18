@echo off
REM Shrimp Vision Network Startup Script for Windows
REM This script starts both servers accessible from the network

echo 🦐 Starting Shrimp Vision for Network Access...
echo ==============================================

REM Get the local IP address (simplified for Windows)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set LOCAL_IP=%%a
    goto :found_ip
)
:found_ip
set LOCAL_IP=%LOCAL_IP: =%

echo 📍 Your local IP address: %LOCAL_IP%
echo 🌐 Frontend will be available at: http://%LOCAL_IP%:3000
echo 🔧 Backend API will be available at: http://%LOCAL_IP%:8000
echo.

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

REM Install dependencies if needed
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

REM Install dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
)

REM Create environment file with network IP
if not exist ".env.local" (
    echo 📝 Creating environment file...
    echo NEXT_PUBLIC_API_URL=http://%LOCAL_IP%:8000 > .env.local
) else (
    REM Update existing env file
    echo NEXT_PUBLIC_API_URL=http://%LOCAL_IP%:8000 > .env.local
)

REM Start frontend in background
start "Shrimp Vision Frontend" cmd /k "set HOSTNAME=0.0.0.0 && npm run dev"

echo.
echo 🎉 Shrimp Vision is starting up for network access!
echo ==============================================
echo 🌐 Frontend: http://%LOCAL_IP%:3000
echo 🔧 Backend API: http://%LOCAL_IP%:8000
echo 📚 API Docs: http://%LOCAL_IP%:8000/docs
echo.
echo Share these URLs with your roommate:
echo   Main App: http://%LOCAL_IP%:3000
echo.
echo Both servers are starting in separate windows.
echo Close those windows to stop the servers.
echo.
pause
