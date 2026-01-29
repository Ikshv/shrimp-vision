from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import time
from pathlib import Path

from routes import upload, annotate, train, inference, export, websocket, datasets

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
temp_dir = Path("temp")
temp_dir.mkdir(exist_ok=True)  # For temporary inference files

# Clean up ALL temp files on startup (they're temporary inference results)
if temp_dir.exists():
    cleaned_count = 0
    for file in temp_dir.iterdir():
        if file.is_file():
            try:
                file.unlink()
                cleaned_count += 1
            except Exception as e:
                print(f"Error cleaning up temp file {file.name}: {e}")
    if cleaned_count > 0:
        print(f"🧹 Cleaned up {cleaned_count} old temp files on startup")

os.makedirs("models", exist_ok=True)
os.makedirs("dataset/images/train", exist_ok=True)
os.makedirs("dataset/images/val", exist_ok=True)
os.makedirs("dataset/labels/train", exist_ok=True)
os.makedirs("dataset/labels/val", exist_ok=True)
os.makedirs("datasets", exist_ok=True)  # For multi-dataset support

# Initialize dataset service to ensure datasets directory exists
from services.dataset_service import DatasetService
dataset_service_init = DatasetService()  # This creates the datasets directory and default dataset if needed

# Add route handlers for dataset file serving
# These MUST be registered BEFORE static mounts to ensure they match first
# FastAPI matches routes in order, so these will take precedence over the /static mount
backend_dir = Path(__file__).parent

@app.get("/static/datasets/{dataset_id}/{path:path}")
async def serve_static_dataset_file(dataset_id: str, path: str):
    """
    Serve files from dataset directories via /static/datasets/ path
    Handles requests like /static/datasets/{dataset_id}/images/{filename}
    Also handles legacy /uploads/ paths for backward compatibility
    """
    file_path = backend_dir / "datasets" / dataset_id / path
    
    # Handle legacy uploads path -> images path
    if "uploads" in path:
        legacy_path = file_path
        new_path = backend_dir / "datasets" / dataset_id / path.replace("uploads/", "images/")
        if new_path.exists() and new_path.is_file():
            return FileResponse(str(new_path))
        # Also check if legacy path exists (for backward compatibility)
        if legacy_path.exists() and legacy_path.is_file():
            return FileResponse(str(legacy_path))
    else:
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
    
    # Debug: log when file not found
    print(f"DEBUG: File not found - dataset_id={dataset_id}, path={path}, file_path={file_path}, exists={file_path.exists()}")
    raise HTTPException(status_code=404, detail=f"File not found: {path}")

@app.get("/datasets/{dataset_id}/{path:path}")
async def serve_dataset_file(dataset_id: str, path: str):
    """
    Serve files from dataset directories via /datasets/ path (for Next.js rewrite compatibility)
    Handles requests like /datasets/{dataset_id}/images/{filename}
    Also handles legacy /uploads/ paths for backward compatibility
    """
    file_path = backend_dir / "datasets" / dataset_id / path
    
    # Handle legacy uploads path -> images path
    if "uploads" in path:
        legacy_path = file_path
        new_path = backend_dir / "datasets" / dataset_id / path.replace("uploads/", "images/")
        if new_path.exists() and new_path.is_file():
            return FileResponse(str(new_path))
        # Also check if legacy path exists (for backward compatibility)
        if legacy_path.exists() and legacy_path.is_file():
            return FileResponse(str(legacy_path))
    else:
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
    
    # Debug: log when file not found
    print(f"DEBUG: File not found - dataset_id={dataset_id}, path={path}, file_path={file_path}, exists={file_path.exists()}")
    raise HTTPException(status_code=404, detail=f"File not found: {path}")

@app.get("/temp/{path:path}")
async def serve_temp_file(path: str):
    """
    Serve files from temp directory via /temp/ path (for Next.js compatibility)
    Handles requests like /temp/{filename}
    """
    # Use absolute path to backend/temp directory
    temp_dir = backend_dir / "temp"
    file_path = temp_dir / path
    
    # Debug logging to see what's happening
    print(f"DEBUG: Serving temp file - path={path}, file_path={file_path}, exists={file_path.exists()}, temp_dir={temp_dir}")
    
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    
    # Debug logging
    print(f"DEBUG: Temp file not found - path={path}, file_path={file_path}, exists={file_path.exists()}")
    raise HTTPException(status_code=404, detail=f"File not found: {path}")

# Mount static files (AFTER route handlers so routes take precedence)
# The /static mount will handle other static files, but /static/datasets/... will be caught by the route handler above
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount temp directory for serving temporary inference files
app.mount("/static/temp", StaticFiles(directory="temp"), name="temp")

# Include routers
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
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
