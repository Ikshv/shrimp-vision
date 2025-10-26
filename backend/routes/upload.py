from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
from PIL import Image
import aiofiles
from pathlib import Path

# Register HEIF plugin for iPhone photos
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIF support not available

router = APIRouter()

UPLOAD_DIR = "static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".heic", ".heif", ".webp", ".gif"}

@router.post("/")
async def upload_images(files: List[UploadFile] = File(...)):
    """
    Upload multiple images for annotation and training
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate file extension
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                errors.append(f"{file.filename}: Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
                continue
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            filename = f"{file_id}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Validate and get image info
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    format = img.format
                    
                uploaded_files.append({
                    "id": file_id,
                    "filename": filename,
                    "original_name": file.filename,
                    "size": len(content),
                    "width": width,
                    "height": height,
                    "format": format,
                    "path": f"/static/uploads/{filename}"
                })
            except Exception as e:
                # Remove invalid image file
                if os.path.exists(file_path):
                    os.remove(file_path)
                errors.append(f"{file.filename}: Invalid image file - {str(e)}")
                
        except Exception as e:
            errors.append(f"{file.filename}: Upload failed - {str(e)}")
    
    return {
        "success": True,
        "uploaded": uploaded_files,
        "errors": errors,
        "total_uploaded": len(uploaded_files),
        "total_errors": len(errors)
    }

@router.get("/list")
async def list_uploaded_images():
    """
    Get list of all uploaded images
    """
    try:
        images = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    file_path = os.path.join(UPLOAD_DIR, filename)
                    file_id = filename.split('.')[0]
                    
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                            format = img.format
                            
                        images.append({
                            "id": file_id,
                            "filename": filename,
                            "width": width,
                            "height": height,
                            "format": format,
                            "path": f"/static/uploads/{filename}"
                        })
                    except Exception as e:
                        continue
        
        return {
            "success": True,
            "images": images,
            "total": len(images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")

@router.delete("/{file_id}")
async def delete_image(file_id: str):
    """
    Delete an uploaded image
    """
    try:
        # Find the file with this ID
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename.startswith(file_id):
                    file_path = os.path.join(UPLOAD_DIR, filename)
                    os.remove(file_path)
                    
                    # Also delete associated annotation if exists
                    annotation_path = f"static/annotations/{file_id}.json"
                    if os.path.exists(annotation_path):
                        os.remove(annotation_path)
                    
                    return {"success": True, "message": f"Image {file_id} deleted successfully"}
        
        raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
