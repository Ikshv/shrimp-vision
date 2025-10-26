from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
import shutil
from pathlib import Path
import asyncio
from services.simple_trainer import SimpleTrainer
from services.dataset_manager import DatasetManager
from routes.websocket import send_training_update

router = APIRouter()

class TrainingConfig(BaseModel):
    model_type: str = "yolov8n"  # yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    epochs: int = 100
    batch_size: int = 16
    image_size: int = 640
    learning_rate: float = 0.01
    train_split: float = 0.8
    val_split: float = 0.2

class TrainingStatus(BaseModel):
    status: str  # "idle", "preparing", "training", "completed", "failed"
    progress: float  # 0-100
    current_epoch: int
    total_epochs: int
    loss: Optional[float]
    accuracy: Optional[float]
    message: str
    model_path: Optional[str]

# Global training status
training_status = TrainingStatus(
    status="idle",
    progress=0.0,
    current_epoch=0,
    total_epochs=0,
    loss=None,
    accuracy=None,
    message="Ready to train",
    model_path=None
)

@router.post("/start")
async def start_training(config: TrainingConfig, background_tasks: BackgroundTasks):
    """
    Start model training with the given configuration
    """
    global training_status
    
    try:
        # Check if training is already in progress
        if training_status.status in ["preparing", "training"]:
            raise HTTPException(status_code=400, detail="Training already in progress")
        
        # Check if we have enough annotated data
        annotation_stats = await get_annotation_stats()
        if annotation_stats["stats"]["annotated_images"] < 5:
            raise HTTPException(
                status_code=400, 
                detail="Need at least 5 annotated images to start training"
            )
        
        # Reset training status
        training_status = TrainingStatus(
            status="preparing",
            progress=0.0,
            current_epoch=0,
            total_epochs=config.epochs,
            loss=None,
            accuracy=None,
            message="Preparing dataset...",
            model_path=None
        )
        
        # Start training in background
        background_tasks.add_task(run_training, config)
        
        return {
            "success": True,
            "message": "Training started successfully",
            "config": config.dict(),
            "status": training_status.dict()
        }
    except Exception as e:
        training_status.status = "failed"
        training_status.message = f"Failed to start training: {str(e)}"
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_training_status():
    """
    Get current training status
    """
    return {
        "success": True,
        "status": training_status.dict()
    }

@router.post("/stop")
async def stop_training():
    """
    Stop current training (if in progress)
    """
    global training_status
    
    if training_status.status in ["preparing", "training"]:
        training_status.status = "idle"
        training_status.message = "Training stopped by user"
        return {"success": True, "message": "Training stopped"}
    else:
        raise HTTPException(status_code=400, detail="No training in progress")

async def run_training(config: TrainingConfig):
    """
    Background task to run model training
    """
    global training_status
    
    try:
        # Step 1: Prepare dataset
        training_status.status = "preparing"
        training_status.message = "Preparing dataset..."
        training_status.progress = 10.0
        
        # Send WebSocket update
        await send_training_update("preparing", 10.0, "Preparing dataset...")
        
        dataset_manager = DatasetManager()
        dataset_path = await dataset_manager.prepare_dataset(
            train_split=config.train_split,
            val_split=config.val_split
        )
        
        if not dataset_path:
            raise Exception("Failed to prepare dataset")
        
        training_status.progress = 20.0
        training_status.message = "Dataset prepared, starting training..."
        
        # Send WebSocket update
        await send_training_update("preparing", 20.0, "Dataset prepared, starting training...")
        
        # Step 2: Initialize trainer
        trainer = SimpleTrainer()
        
        # Step 3: Start training
        training_status.status = "training"
        training_status.message = "Training model..."
        
        # Send WebSocket update
        await send_training_update("training", 20.0, "Training model...", 0, config.epochs)
        
        # Update status to show training is in progress
        training_status.status = "training"
        training_status.message = f"Training {config.model_type} model for {config.epochs} epochs..."
        training_status.progress = 25.0
        
        # Start a background task to update progress periodically
        async def update_progress():
            import asyncio
            progress = 25.0
            while training_status.status == "training" and progress < 95.0:
                await asyncio.sleep(5)  # Update every 5 seconds
                if training_status.status == "training":
                    progress += 5.0
                    training_status.progress = min(progress, 95.0)
                    training_status.message = f"Training {config.model_type} model... ({progress:.0f}% complete)"
        
        # Start progress updater
        progress_task = asyncio.create_task(update_progress())
        
        # Train the model with progress callback
        model_path = await trainer.train(
            dataset_path=dataset_path,
            model_type=config.model_type,
            epochs=config.epochs,
            batch_size=config.batch_size,
            image_size=config.image_size,
            learning_rate=config.learning_rate,
            progress_callback=None  # Disable for now to prevent issues
        )
        
        # Cancel progress updater
        progress_task.cancel()
        
        # Step 4: Training completed
        training_status.status = "completed"
        training_status.progress = 100.0
        training_status.message = "Training completed successfully!"
        training_status.model_path = model_path
        
        # Send final WebSocket update
        await send_training_update("completed", 100.0, "Training completed successfully!")
        
    except Exception as e:
        training_status.status = "failed"
        training_status.message = f"Training failed: {str(e)}"
        print(f"Training error: {str(e)}")
        
        # Send error WebSocket update
        await send_training_update("failed", 0.0, f"Training failed: {str(e)}")

async def async_progress_callback(epoch: int, total_epochs: int, loss: float, metrics: dict):
    """
    Progress callback for training updates
    """
    progress = 20.0 + (epoch / total_epochs) * 70.0
    accuracy = metrics.get('mAP50', 0.0) if metrics else None
    
    # Update global status
    global training_status
    training_status.current_epoch = epoch
    training_status.total_epochs = total_epochs
    training_status.loss = loss
    training_status.accuracy = accuracy
    training_status.progress = progress
    training_status.message = f"Training epoch {epoch}/{total_epochs}"
    
    # Send WebSocket update
    await send_training_update("training", progress, f"Training epoch {epoch}/{total_epochs}", epoch, total_epochs, loss, accuracy)

@router.get("/models/list")
async def list_trained_models():
    """
    List all trained models
    """
    try:
        models = []
        models_dir = "models"
        
        if os.path.exists(models_dir):
            for filename in os.listdir(models_dir):
                if filename.endswith('.pt'):
                    model_path = os.path.join(models_dir, filename)
                    file_size = os.path.getsize(model_path)
                    
                    models.append({
                        "filename": filename,
                        "path": model_path,
                        "size": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2)
                    })
        
        return {
            "success": True,
            "models": models,
            "total": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """
    Get information about a specific trained model
    """
    try:
        model_path = f"models/{model_name}"
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model not found")
        
        file_size = os.path.getsize(model_path)
        
        return {
            "success": True,
            "model": {
                "filename": model_name,
                "path": model_path,
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

async def get_annotation_stats():
    """
    Helper function to get annotation statistics
    """
    try:
        total_images = 0
        annotated_images = 0
        
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
        
        return {
            "stats": {
                "total_images": total_images,
                "annotated_images": annotated_images
            }
        }
    except Exception as e:
        return {"stats": {"total_images": 0, "annotated_images": 0}}
