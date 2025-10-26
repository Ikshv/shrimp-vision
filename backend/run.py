#!/usr/bin/env python3
"""
Shrimp Vision Backend Server
Run this script to start the FastAPI backend server
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Start the FastAPI server"""
    print("🦐 Starting Shrimp Vision Backend Server...")
    print("📍 Server will be available at: http://localhost:3100")
    print("📚 API Documentation: http://localhost:3100/docs")
    print("🔧 Health Check: http://localhost:3100/api/health")
    print("-" * 50)
    
    # Create necessary directories
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/annotations", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("dataset/images/train", exist_ok=True)
    os.makedirs("dataset/images/val", exist_ok=True)
    os.makedirs("dataset/labels/train", exist_ok=True)
    os.makedirs("dataset/labels/val", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=3100,
        reload=True,
        reload_dirs=[str(backend_dir)],
        log_level="info"
    )

if __name__ == "__main__":
    main()
