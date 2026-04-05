from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.dataset_service import DatasetService
from services.dataset_manifest import (
    load_manifest,
    detection_classes_as_types,
    color_attributes_as_map,
    additional_attributes_as_map,
    normalize_detection_class_rows,
    normalize_color_attribute_rows,
    normalize_additional_attribute_rows,
    apply_manifest_labels_update,
)

router = APIRouter()
dataset_service = DatasetService()

class CreateDatasetRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class DetectionClassInput(BaseModel):
    name: str
    display_name: str = ""
    color: str = "#6B7280"
    description: str = ""


class ColorAttributeInput(BaseModel):
    name: str
    display_name: str = ""
    color: str = "#6B7280"
    description: str = ""


class AdditionalAttributeInput(BaseModel):
    name: str
    display_name: str = ""
    description: str = ""


class UpdateDatasetLabelsRequest(BaseModel):
    detection_classes: List[DetectionClassInput]
    color_attributes: Optional[List[ColorAttributeInput]] = None
    additional_attributes: Optional[List[AdditionalAttributeInput]] = None

@router.get("/list")
async def list_datasets():
    """Get list of all datasets"""
    try:
        datasets = dataset_service.list_datasets()
        active_dataset = dataset_service.get_active_dataset()
        return {
            "success": True,
            "datasets": datasets,
            "active_dataset_id": active_dataset["id"] if active_dataset else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")

@router.get("/active")
async def get_active_dataset():
    """Get the currently active dataset"""
    try:
        dataset = dataset_service.get_active_dataset()
        if not dataset:
            raise HTTPException(status_code=404, detail="No active dataset")
        # Update stats and reload dataset to get fresh stats
        dataset_service.update_dataset_stats(dataset["id"])
        dataset = dataset_service.get_dataset(dataset["id"])  # Reload to get updated stats
        return {"success": True, "dataset": dataset}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active dataset: {str(e)}")

@router.post("/create")
async def create_dataset(request: CreateDatasetRequest):
    """Create a new dataset"""
    try:
        if not request.name or not request.name.strip():
            raise HTTPException(status_code=400, detail="Dataset name is required")
        
        dataset = dataset_service.create_dataset(request.name.strip(), request.description or "")
        return {"success": True, "dataset": dataset}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dataset: {str(e)}")

@router.post("/{dataset_id}/activate")
async def activate_dataset(dataset_id: str):
    """Set a dataset as active"""
    try:
        if dataset_service.set_active_dataset(dataset_id):
            # Update stats for the newly activated dataset
            dataset_service.update_dataset_stats(dataset_id)
            return {"success": True, "message": f"Dataset {dataset_id} activated"}
        raise HTTPException(status_code=404, detail="Dataset not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate dataset: {str(e)}")

@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    try:
        if dataset_service.delete_dataset(dataset_id):
            return {"success": True, "message": f"Dataset {dataset_id} deleted"}
        raise HTTPException(status_code=400, detail="Cannot delete active dataset or dataset not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete dataset: {str(e)}")

@router.get("/{dataset_id}/classes")
async def get_dataset_classes(dataset_id: str):
    """Detection classes for a dataset (YOLO order = list order)."""
    try:
        dataset = dataset_service.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        manifest = load_manifest(dataset["path"])
        classes = manifest.get("detection_classes", [])
        color_rows = manifest.get("color_attributes", [])
        add_rows = manifest.get("additional_attributes", [])
        types = detection_classes_as_types(classes)
        return {
            "success": True,
            "schema_version": manifest.get("schema_version", 1),
            "detection_classes": classes,
            "types": types,
            "color_attributes": color_rows,
            "additional_attributes": add_rows,
            "colors": color_attributes_as_map(color_rows),
            "attributes": additional_attributes_as_map(add_rows),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{dataset_id}/classes")
async def put_dataset_classes(dataset_id: str, body: UpdateDatasetLabelsRequest):
    """Replace detection classes and optional/tag attributes; remap YOLO ids and scrub stale tags."""
    try:
        dataset = dataset_service.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        manifest = load_manifest(dataset["path"])
        raw = [c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in body.detection_classes]
        normalized = normalize_detection_class_rows(raw)
        if body.color_attributes is not None:
            cr = [
                c.model_dump() if hasattr(c, "model_dump") else c.dict() for c in body.color_attributes
            ]
            norm_colors = normalize_color_attribute_rows(cr)
        else:
            norm_colors = manifest.get("color_attributes", [])
        if body.additional_attributes is not None:
            ar = [
                c.model_dump() if hasattr(c, "model_dump") else c.dict()
                for c in body.additional_attributes
            ]
            norm_add = normalize_additional_attribute_rows(ar)
        else:
            norm_add = manifest.get("additional_attributes", [])
        ann_dir = dataset_service.get_dataset_annotation_dir(dataset_id)
        try:
            apply_manifest_labels_update(
                dataset["path"], normalized, norm_colors, norm_add, ann_dir
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        manifest = load_manifest(dataset["path"])
        return {
            "success": True,
            "detection_classes": manifest["detection_classes"],
            "types": detection_classes_as_types(manifest["detection_classes"]),
            "color_attributes": manifest["color_attributes"],
            "additional_attributes": manifest["additional_attributes"],
            "colors": color_attributes_as_map(manifest["color_attributes"]),
            "attributes": additional_attributes_as_map(manifest["additional_attributes"]),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get a specific dataset by ID"""
    try:
        dataset = dataset_service.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        # Update stats and reload dataset to get fresh stats
        dataset_service.update_dataset_stats(dataset_id)
        dataset = dataset_service.get_dataset(dataset_id)  # Reload to get updated stats
        return {"success": True, "dataset": dataset}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dataset: {str(e)}")

