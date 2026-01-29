from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
import os
import uuid
from PIL import Image
import aiofiles
from pathlib import Path
from services.dataset_service import DatasetService

# Register HEIF plugin for iPhone photos
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIF support not available

router = APIRouter()
dataset_service = DatasetService()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".heic", ".heif", ".webp", ".gif"}

@router.post("/")
@router.post("")
async def upload_images(
    files: List[UploadFile] = File(...),
    dataset_id: Optional[str] = Query(None, description="Dataset ID to upload to (uses active dataset if not provided)")
):
    """
    Upload multiple images for annotation and training
    If dataset_id is provided, use that dataset; otherwise use active dataset
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Get dataset
    if dataset_id:
        dataset = dataset_service.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    else:
        dataset = dataset_service.get_active_dataset()
        if not dataset:
            raise HTTPException(status_code=400, detail="No active dataset. Please create or select a dataset first.")
    
    # Use dataset-specific upload directory
    upload_dir = dataset_service.get_dataset_upload_dir(dataset["id"])
    os.makedirs(upload_dir, exist_ok=True)
    
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
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Validate and get image info
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    format = img.format
                    
                # Use relative path for serving (will be handled by static file mount)
                # The path should match the mount: /static/datasets -> datasets directory
                uploaded_files.append({
                    "id": file_id,
                    "filename": filename,
                    "original_name": file.filename,
                    "size": len(content),
                    "width": width,
                    "height": height,
                    "format": format,
                    "path": f"/static/datasets/{dataset['id']}/images/{filename}"
                })
            except Exception as e:
                # Remove invalid image file
                if os.path.exists(file_path):
                    os.remove(file_path)
                errors.append(f"{file.filename}: Invalid image file - {str(e)}")
                
        except Exception as e:
            errors.append(f"{file.filename}: Upload failed - {str(e)}")
    
    # Update dataset stats after upload
    dataset_service.update_dataset_stats(dataset["id"])
    
    return {
        "success": True,
        "uploaded": uploaded_files,
        "errors": errors,
        "total_uploaded": len(uploaded_files),
        "total_errors": len(errors),
        "dataset_id": dataset["id"]
    }

@router.get("/list")
async def list_uploaded_images(
    dataset_id: Optional[str] = Query(None, description="Dataset ID to list images from (uses active dataset if not provided)")
):
    """
    Get list of all uploaded images in the specified dataset
    """
    try:
        # Get dataset
        if dataset_id:
            dataset = dataset_service.get_dataset(dataset_id)
            if not dataset:
                raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        else:
            dataset = dataset_service.get_active_dataset()
            if not dataset:
                return {"success": True, "images": [], "total": 0, "dataset_id": None}
        
        upload_dir = dataset_service.get_dataset_upload_dir(dataset["id"])
        images = []
        
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                # Skip temporary files (they should be in temp/ directory, but check just in case)
                if filename.startswith('temp_'):
                    continue
                # Skip annotated images (they should be in temp/ directory, but check just in case)
                if filename.endswith('_annotated.jpg') or filename.endswith('_annotated.webp') or filename.endswith('_annotated.png'):
                    continue
                if any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    file_path = os.path.join(upload_dir, filename)
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
                            "path": f"/static/datasets/{dataset['id']}/images/{filename}"
                        })
                    except Exception as e:
                        continue
        
        return {
            "success": True,
            "images": images,
            "total": len(images),
            "dataset_id": dataset["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {str(e)}")

@router.delete("/{file_id}")
async def delete_image(
    file_id: str,
    dataset_id: Optional[str] = Query(None, description="Dataset ID to delete image from (uses active dataset if not provided)")
):
    """
    Delete an uploaded image
    """
    try:
        # Get dataset
        if dataset_id:
            dataset = dataset_service.get_dataset(dataset_id)
            if not dataset:
                raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        else:
            dataset = dataset_service.get_active_dataset()
            if not dataset:
                raise HTTPException(status_code=400, detail="No active dataset")
        
        upload_dir = dataset_service.get_dataset_upload_dir(dataset["id"])
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        
        # Find the file with this ID
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.startswith(file_id):
                    file_path = os.path.join(upload_dir, filename)
                    os.remove(file_path)
                    
                    # Also delete associated annotation if exists
                    annotation_path = os.path.join(annotation_dir, f"{file_id}.json")
                    if os.path.exists(annotation_path):
                        os.remove(annotation_path)
                    
                    # Update dataset stats
                    dataset_service.update_dataset_stats(dataset["id"])
                    
                    return {"success": True, "message": f"Image {file_id} deleted successfully"}
        
        raise HTTPException(status_code=404, detail="Image not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
