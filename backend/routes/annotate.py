from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
from pathlib import Path

router = APIRouter()

class BoundingBox(BaseModel):
    x: float  # x coordinate (0-1 normalized)
    y: float  # y coordinate (0-1 normalized)
    width: float  # width (0-1 normalized)
    height: float  # height (0-1 normalized)
    label: str = "shrimp"
    confidence: float = 1.0

class Annotation(BaseModel):
    image_id: str
    image_filename: str
    image_width: int
    image_height: int
    bounding_boxes: List[BoundingBox]
    total_shrimp: int

class AnnotationList(BaseModel):
    annotations: List[Annotation]

@router.post("/save")
async def save_annotation(annotation: Annotation):
    """
    Save annotation data for a single image
    """
    try:
        # Validate image exists
        image_path = f"static/uploads/{annotation.image_filename}"
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Create annotations directory if it doesn't exist
        os.makedirs("static/annotations", exist_ok=True)
        
        # Save annotation as JSON
        annotation_path = f"static/annotations/{annotation.image_id}.json"
        with open(annotation_path, 'w') as f:
            json.dump(annotation.dict(), f, indent=2)
        
        return {
            "success": True,
            "message": f"Annotation saved for {annotation.image_filename}",
            "total_shrimp": annotation.total_shrimp,
            "bounding_boxes": len(annotation.bounding_boxes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save annotation: {str(e)}")

@router.post("/save-all")
async def save_all_annotations(annotation_list: AnnotationList):
    """
    Save multiple annotations at once
    """
    try:
        saved_count = 0
        errors = []
        
        for annotation in annotation_list.annotations:
            try:
                # Validate image exists
                image_path = f"static/uploads/{annotation.image_filename}"
                if not os.path.exists(image_path):
                    errors.append(f"Image not found: {annotation.image_filename}")
                    continue
                
                # Create annotations directory if it doesn't exist
                os.makedirs("static/annotations", exist_ok=True)
                
                # Save annotation as JSON
                annotation_path = f"static/annotations/{annotation.image_id}.json"
                with open(annotation_path, 'w') as f:
                    json.dump(annotation.dict(), f, indent=2)
                
                saved_count += 1
            except Exception as e:
                errors.append(f"Failed to save {annotation.image_filename}: {str(e)}")
        
        return {
            "success": True,
            "saved_count": saved_count,
            "total_count": len(annotation_list.annotations),
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save annotations: {str(e)}")

@router.get("/{image_id}")
async def get_annotation(image_id: str):
    """
    Get annotation data for a specific image
    """
    try:
        annotation_path = f"static/annotations/{image_id}.json"
        if not os.path.exists(annotation_path):
            return {"success": True, "annotation": None, "message": "No annotation found"}
        
        with open(annotation_path, 'r') as f:
            annotation_data = json.load(f)
        
        return {
            "success": True,
            "annotation": annotation_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get annotation: {str(e)}")

@router.get("/list/all")
async def list_all_annotations():
    """
    Get list of all annotations
    """
    try:
        annotations = []
        if os.path.exists("static/annotations"):
            for filename in os.listdir("static/annotations"):
                if filename.endswith('.json'):
                    image_id = filename.replace('.json', '')
                    annotation_path = os.path.join("static/annotations", filename)
                    
                    try:
                        with open(annotation_path, 'r') as f:
                            annotation_data = json.load(f)
                        annotations.append(annotation_data)
                    except Exception as e:
                        continue
        
        return {
            "success": True,
            "annotations": annotations,
            "total": len(annotations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list annotations: {str(e)}")

@router.delete("/{image_id}")
async def delete_annotation(image_id: str):
    """
    Delete annotation for a specific image
    """
    try:
        annotation_path = f"static/annotations/{image_id}.json"
        if not os.path.exists(annotation_path):
            raise HTTPException(status_code=404, detail="Annotation not found")
        
        os.remove(annotation_path)
        return {"success": True, "message": f"Annotation for {image_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete annotation: {str(e)}")

@router.get("/stats/summary")
async def get_annotation_stats():
    """
    Get summary statistics of annotations
    """
    try:
        total_images = 0
        annotated_images = 0
        total_shrimp = 0
        total_boxes = 0
        
        # Count uploaded images
        if os.path.exists("static/uploads"):
            for filename in os.listdir("static/uploads"):
                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']):
                    total_images += 1
        
        # Count annotations
        if os.path.exists("static/annotations"):
            for filename in os.listdir("static/annotations"):
                if filename.endswith('.json'):
                    annotated_images += 1
                    annotation_path = os.path.join("static/annotations", filename)
                    
                    try:
                        with open(annotation_path, 'r') as f:
                            annotation_data = json.load(f)
                            total_shrimp += annotation_data.get('total_shrimp', 0)
                            total_boxes += len(annotation_data.get('bounding_boxes', []))
                    except Exception as e:
                        continue
        
        return {
            "success": True,
            "stats": {
                "total_images": total_images,
                "annotated_images": annotated_images,
                "annotation_progress": (annotated_images / total_images * 100) if total_images > 0 else 0,
                "total_shrimp": total_shrimp,
                "total_bounding_boxes": total_boxes,
                "avg_shrimp_per_image": total_shrimp / annotated_images if annotated_images > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get annotation stats: {str(e)}")
