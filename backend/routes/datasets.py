from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.dataset_service import DatasetService

router = APIRouter()
dataset_service = DatasetService()

class CreateDatasetRequest(BaseModel):
    name: str
    description: Optional[str] = ""

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

