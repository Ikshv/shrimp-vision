from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from pathlib import Path

from routes import upload, annotate, train, inference, export, websocket

# Create FastAPI app
app = FastAPI(
    title="Shrimp Vision API",
    description="AI-powered shrimp detection and counting system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3099", "http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/annotations", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("dataset/images/train", exist_ok=True)
os.makedirs("dataset/images/val", exist_ok=True)
os.makedirs("dataset/labels/train", exist_ok=True)
os.makedirs("dataset/labels/val", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(annotate.router, prefix="/api/annotate", tags=["annotate"])
app.include_router(train.router, prefix="/api/train", tags=["train"])
app.include_router(inference.router, prefix="/api/inference", tags=["inference"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "Shrimp Vision API is running!"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Shrimp Vision API is operational"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
