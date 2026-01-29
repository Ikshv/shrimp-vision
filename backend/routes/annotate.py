from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
from config.classes import AVAILABLE_CLASSES, is_valid_class, get_class_by_name
from services.dataset_service import DatasetService

router = APIRouter()
dataset_service = DatasetService()

class BoundingBox(BaseModel):
    x: float  # x coordinate (0-1 normalized)
    y: float  # y coordinate (0-1 normalized)
    width: float  # width (0-1 normalized)
    height: float  # height (0-1 normalized)
    label: str = "shrimp"  # Class name (type)
    confidence: float = 1.0
    class_id: Optional[int] = None  # Class ID for YOLO format
    color: Optional[str] = None  # Color attribute (e.g., "red", "blue")
    attributes: Optional[List[str]] = []  # Additional attributes (e.g., ["berried", "healthy"])

class Annotation(BaseModel):
    image_id: str
    image_filename: str
    image_width: int
    image_height: int
    bounding_boxes: List[BoundingBox]
    total_shrimp: int
    class_counts: Optional[Dict[str, int]] = None  # Count of each class

class AnnotationList(BaseModel):
    annotations: List[Annotation]

@router.get("/classes")
async def get_available_classes():
    """
    Get list of available classes and attributes for multi-tagging
    """
    from config.classes import COLOR_ATTRIBUTES, ADDITIONAL_ATTRIBUTES, SHRIMP_TYPES
    
    return {
        "success": True,
        "types": SHRIMP_TYPES,
        "colors": COLOR_ATTRIBUTES,
        "attributes": ADDITIONAL_ATTRIBUTES,
        "classes": AVAILABLE_CLASSES,  # For backward compatibility
        "class_names": list(AVAILABLE_CLASSES.keys())
    }

@router.post("/save")
async def save_annotation(
    annotation: Annotation,
    dataset_id: Optional[str] = Query(None, description="Dataset ID (uses active dataset if not provided)")
):
    """
    Save annotation data for a single image
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
        
        # Validate image exists
        image_path = os.path.join(upload_dir, annotation.image_filename)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Validate all bounding box classes
        class_counts = {}
        for bbox in annotation.bounding_boxes:
            if not is_valid_class(bbox.label):
                raise HTTPException(status_code=400, detail=f"Invalid class: {bbox.label}")
            
            # Set class_id if not provided
            if bbox.class_id is None:
                class_info = get_class_by_name(bbox.label)
                bbox.class_id = class_info["id"] if class_info else 0
            
            # Count classes
            class_counts[bbox.label] = class_counts.get(bbox.label, 0) + 1
        
        # Update annotation with class counts
        annotation.class_counts = class_counts
        
        # Create annotations directory if it doesn't exist
        os.makedirs(annotation_dir, exist_ok=True)
        
        # Save annotation as JSON
        annotation_path = os.path.join(annotation_dir, f"{annotation.image_id}.json")
        with open(annotation_path, 'w') as f:
            json.dump(annotation.dict(), f, indent=2)
        
        # Update dataset stats
        dataset_service.update_dataset_stats(dataset["id"])
        
        return {
            "success": True,
            "message": f"Annotation saved for {annotation.image_filename}",
            "total_shrimp": annotation.total_shrimp,
            "bounding_boxes": len(annotation.bounding_boxes),
            "class_counts": class_counts,
            "dataset_id": dataset["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save annotation: {str(e)}")

@router.post("/save-all")
async def save_all_annotations(
    annotation_list: AnnotationList,
    dataset_id: Optional[str] = Query(None, description="Dataset ID (uses active dataset if not provided)")
):
    """
    Save multiple annotations at once
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
        os.makedirs(annotation_dir, exist_ok=True)
        
        saved_count = 0
        errors = []
        
        for annotation in annotation_list.annotations:
            try:
                # Validate image exists
                image_path = os.path.join(upload_dir, annotation.image_filename)
                if not os.path.exists(image_path):
                    errors.append(f"Image not found: {annotation.image_filename}")
                    continue
                
                # Save annotation as JSON
                annotation_path = os.path.join(annotation_dir, f"{annotation.image_id}.json")
                with open(annotation_path, 'w') as f:
                    json.dump(annotation.dict(), f, indent=2)
                
                saved_count += 1
            except Exception as e:
                errors.append(f"Failed to save {annotation.image_filename}: {str(e)}")
        
        # Update dataset stats
        dataset_service.update_dataset_stats(dataset["id"])
        
        return {
            "success": True,
            "saved_count": saved_count,
            "total_count": len(annotation_list.annotations),
            "errors": errors,
            "dataset_id": dataset["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save annotations: {str(e)}")

@router.get("/{image_id}")
async def get_annotation(
    image_id: str,
    dataset_id: Optional[str] = Query(None, description="Dataset ID (uses active dataset if not provided)")
):
    """
    Get annotation data for a specific image
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
                return {"success": True, "annotation": None, "message": "No active dataset"}
        
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        annotation_path = os.path.join(annotation_dir, f"{image_id}.json")
        
        if not os.path.exists(annotation_path):
            return {"success": True, "annotation": None, "message": "No annotation found"}
        
        with open(annotation_path, 'r') as f:
            annotation_data = json.load(f)
        
        return {
            "success": True,
            "annotation": annotation_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get annotation: {str(e)}")

@router.get("/list/all")
async def list_all_annotations(
    dataset_id: Optional[str] = Query(None, description="Dataset ID (uses active dataset if not provided)")
):
    """
    Get list of all annotations
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
                return {"success": True, "annotations": [], "total": 0}
        
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        annotations = []
        
        if os.path.exists(annotation_dir):
            for filename in os.listdir(annotation_dir):
                if filename.endswith('.json'):
                    image_id = filename.replace('.json', '')
                    annotation_path = os.path.join(annotation_dir, filename)
                    
                    try:
                        with open(annotation_path, 'r') as f:
                            annotation_data = json.load(f)
                        annotations.append(annotation_data)
                    except Exception as e:
                        continue
        
        return {
            "success": True,
            "annotations": annotations,
            "total": len(annotations),
            "dataset_id": dataset["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list annotations: {str(e)}")

@router.delete("/{image_id}")
async def delete_annotation(
    image_id: str,
    dataset_id: Optional[str] = Query(None, description="Dataset ID (uses active dataset if not provided)")
):
    """
    Delete annotation for a specific image
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
        
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        annotation_path = os.path.join(annotation_dir, f"{image_id}.json")
        
        if not os.path.exists(annotation_path):
            raise HTTPException(status_code=404, detail="Annotation not found")
        
        os.remove(annotation_path)
        
        # Update dataset stats
        dataset_service.update_dataset_stats(dataset["id"])
        
        return {"success": True, "message": f"Annotation for {image_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete annotation: {str(e)}")

@router.get("/stats/summary")
async def get_annotation_stats(
    dataset_id: Optional[str] = Query(None, description="Dataset ID (uses active dataset if not provided)")
):
    """
    Get summary statistics of annotations
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
                return {
                    "success": True,
                    "stats": {
                        "total_images": 0,
                        "annotated_images": 0,
                        "annotation_progress": 0,
                        "total_shrimp": 0,
                        "total_bounding_boxes": 0,
                        "avg_shrimp_per_image": 0
                    },
                    "dataset_id": None
                }
        
        upload_dir = dataset_service.get_dataset_upload_dir(dataset["id"])
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        
        total_images = 0
        annotated_images = 0
        total_shrimp = 0
        total_boxes = 0
        
        # Count uploaded images
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                    total_images += 1
        
        # Count annotations
        if os.path.exists(annotation_dir):
            for filename in os.listdir(annotation_dir):
                if filename.endswith('.json'):
                    annotated_images += 1
                    annotation_path = os.path.join(annotation_dir, filename)
                    
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
            },
            "dataset_id": dataset["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get annotation stats: {str(e)}")
