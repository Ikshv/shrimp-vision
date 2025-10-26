from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import zipfile
import shutil
import json
from pathlib import Path
from datetime import datetime

router = APIRouter()

class ExportConfig(BaseModel):
    include_images: bool = True
    include_annotations: bool = True
    include_models: bool = True
    include_dataset: bool = True
    format: str = "yolo"  # "yolo", "coco", "both"

@router.post("/dataset")
async def export_dataset(config: ExportConfig):
    """
    Export the complete dataset as a ZIP file
    """
    try:
        # Create export directory
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"shrimp_dataset_{timestamp}.zip"
        zip_path = os.path.join(export_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add images if requested
            if config.include_images and os.path.exists("static/uploads"):
                for filename in os.listdir("static/uploads"):
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                        file_path = os.path.join("static/uploads", filename)
                        zipf.write(file_path, f"images/{filename}")
            
            # Add annotations if requested
            if config.include_annotations and os.path.exists("static/annotations"):
                for filename in os.listdir("static/annotations"):
                    if filename.endswith('.json'):
                        file_path = os.path.join("static/annotations", filename)
                        zipf.write(file_path, f"annotations/{filename}")
            
            # Add dataset structure if requested
            if config.include_dataset and os.path.exists("dataset"):
                for root, dirs, files in os.walk("dataset"):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, "dataset")
                        zipf.write(file_path, f"dataset/{arc_path}")
            
            # Add models if requested
            if config.include_models and os.path.exists("models"):
                for filename in os.listdir("models"):
                    if filename.endswith('.pt'):
                        file_path = os.path.join("models", filename)
                        zipf.write(file_path, f"models/{filename}")
            
            # Add metadata
            metadata = {
                "export_timestamp": timestamp,
                "export_config": config.dict(),
                "total_images": len([f for f in os.listdir("static/uploads") if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif'])]) if os.path.exists("static/uploads") else 0,
                "total_annotations": len([f for f in os.listdir("static/annotations") if f.endswith('.json')]) if os.path.exists("static/annotations") else 0,
                "total_models": len([f for f in os.listdir("models") if f.endswith('.pt')]) if os.path.exists("models") else 0
            }
            
            zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type='application/zip'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export dataset: {str(e)}")

@router.get("/model/{model_name}")
async def export_model(model_name: str):
    """
    Export a specific trained model
    """
    try:
        model_path = f"models/{model_name}"
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model not found")
        
        return FileResponse(
            path=model_path,
            filename=model_name,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export model: {str(e)}")

@router.get("/annotations")
async def export_annotations(format: str = "json"):
    """
    Export all annotations in the specified format
    """
    try:
        if not os.path.exists("static/annotations"):
            raise HTTPException(status_code=404, detail="No annotations found")
        
        # Create export directory
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            zip_filename = f"annotations_{timestamp}.zip"
            zip_path = os.path.join(export_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in os.listdir("static/annotations"):
                    if filename.endswith('.json'):
                        file_path = os.path.join("static/annotations", filename)
                        zipf.write(file_path, f"annotations/{filename}")
                
                # Add combined annotations file
                all_annotations = []
                for filename in os.listdir("static/annotations"):
                    if filename.endswith('.json'):
                        file_path = os.path.join("static/annotations", filename)
                        with open(file_path, 'r') as f:
                            annotation_data = json.load(f)
                            all_annotations.append(annotation_data)
                
                zipf.writestr("all_annotations.json", json.dumps(all_annotations, indent=2))
            
            return FileResponse(
                path=zip_path,
                filename=zip_filename,
                media_type='application/zip'
            )
        
        elif format.lower() == "yolo":
            # Export in YOLO format
            zip_filename = f"annotations_yolo_{timestamp}.zip"
            zip_path = os.path.join(export_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in os.listdir("static/annotations"):
                    if filename.endswith('.json'):
                        annotation_path = os.path.join("static/annotations", filename)
                        
                        with open(annotation_path, 'r') as f:
                            annotation_data = json.load(f)
                        
                        # Convert to YOLO format
                        yolo_filename = filename.replace('.json', '.txt')
                        yolo_content = []
                        
                        for bbox in annotation_data.get('bounding_boxes', []):
                            # YOLO format: class_id x_center y_center width height (all normalized)
                            x_center = bbox['x'] + bbox['width'] / 2
                            y_center = bbox['y'] + bbox['height'] / 2
                            yolo_content.append(f"0 {x_center:.6f} {y_center:.6f} {bbox['width']:.6f} {bbox['height']:.6f}")
                        
                        zipf.writestr(f"labels/{yolo_filename}", '\n'.join(yolo_content))
            
            return FileResponse(
                path=zip_path,
                filename=zip_filename,
                media_type='application/zip'
            )
        
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'json' or 'yolo'")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export annotations: {str(e)}")

@router.get("/images")
async def export_images():
    """
    Export all uploaded images
    """
    try:
        if not os.path.exists("static/uploads"):
            raise HTTPException(status_code=404, detail="No images found")
        
        # Create export directory
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"images_{timestamp}.zip"
        zip_path = os.path.join(export_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir("static/uploads"):
                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                    file_path = os.path.join("static/uploads", filename)
                    zipf.write(file_path, f"images/{filename}")
        
        return FileResponse(
            path=zip_path,
            filename=zip_filename,
            media_type='application/zip'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export images: {str(e)}")

@router.get("/summary")
async def get_export_summary():
    """
    Get summary of what can be exported
    """
    try:
        summary = {
            "images": {
                "count": 0,
                "total_size_mb": 0,
                "available": False
            },
            "annotations": {
                "count": 0,
                "available": False
            },
            "models": {
                "count": 0,
                "total_size_mb": 0,
                "available": False
            },
            "dataset": {
                "available": False,
                "train_images": 0,
                "val_images": 0,
                "train_labels": 0,
                "val_labels": 0
            }
        }
        
        # Count images
        if os.path.exists("static/uploads"):
            summary["images"]["available"] = True
            total_size = 0
            for filename in os.listdir("static/uploads"):
                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                    summary["images"]["count"] += 1
                    file_path = os.path.join("static/uploads", filename)
                    total_size += os.path.getsize(file_path)
            summary["images"]["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Count annotations
        if os.path.exists("static/annotations"):
            summary["annotations"]["available"] = True
            for filename in os.listdir("static/annotations"):
                if filename.endswith('.json'):
                    summary["annotations"]["count"] += 1
        
        # Count models
        if os.path.exists("models"):
            summary["models"]["available"] = True
            total_size = 0
            for filename in os.listdir("models"):
                if filename.endswith('.pt'):
                    summary["models"]["count"] += 1
                    file_path = os.path.join("models", filename)
                    total_size += os.path.getsize(file_path)
            summary["models"]["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Check dataset
        if os.path.exists("dataset"):
            summary["dataset"]["available"] = True
            
            # Count train images
            train_images_dir = "dataset/images/train"
            if os.path.exists(train_images_dir):
                for filename in os.listdir(train_images_dir):
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                        summary["dataset"]["train_images"] += 1
            
            # Count val images
            val_images_dir = "dataset/images/val"
            if os.path.exists(val_images_dir):
                for filename in os.listdir(val_images_dir):
                    if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                        summary["dataset"]["val_images"] += 1
            
            # Count train labels
            train_labels_dir = "dataset/labels/train"
            if os.path.exists(train_labels_dir):
                for filename in os.listdir(train_labels_dir):
                    if filename.endswith('.txt'):
                        summary["dataset"]["train_labels"] += 1
            
            # Count val labels
            val_labels_dir = "dataset/labels/val"
            if os.path.exists(val_labels_dir):
                for filename in os.listdir(val_labels_dir):
                    if filename.endswith('.txt'):
                        summary["dataset"]["val_labels"] += 1
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export summary: {str(e)}")
