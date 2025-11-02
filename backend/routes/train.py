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
        # Step 0: Initial verification
        training_status.status = "preparing"
        training_status.message = "Verifying training configuration..."
        training_status.progress = 5.0
        await send_training_update("preparing", 5.0, "Verifying training configuration...")
        await asyncio.sleep(0.5)  # Brief pause for UI update
        
        # Step 1: Prepare dataset
        training_status.message = "Preparing dataset and splitting images..."
        training_status.progress = 10.0
        await send_training_update("preparing", 10.0, "Preparing dataset and splitting images...")
        
        dataset_manager = DatasetManager()
        dataset_path = await dataset_manager.prepare_dataset(
            train_split=config.train_split,
            val_split=config.val_split
        )
        
        if not dataset_path:
            raise Exception("Failed to prepare dataset")
        
        # Get dataset stats for verification message
        dataset_stats = dataset_manager.get_dataset_stats()
        
        training_status.progress = 20.0
        training_status.message = f"Dataset prepared: {dataset_stats['train_images']} train, {dataset_stats['val_images']} val images"
        
        # Send WebSocket update
        await send_training_update("preparing", 20.0, f"✓ Dataset ready: {dataset_stats['train_images']} train, {dataset_stats['val_images']} val images")
        await asyncio.sleep(0.5)  # Brief pause for UI update
        
        # Step 2: Initialize trainer
        training_status.message = f"Initializing {config.model_type} model (downloading if needed)..."
        training_status.progress = 25.0
        await send_training_update("preparing", 25.0, f"Initializing {config.model_type} model (downloading if needed)...")
        
        trainer = SimpleTrainer()
        
        # Step 3: Start training - verification complete
        training_status.status = "training"
        training_status.message = f"Starting training: {config.model_type}, {config.epochs} epochs, batch size {config.batch_size}"
        training_status.progress = 25.0
        training_status.current_epoch = 0
        training_status.total_epochs = config.epochs
        
        # Send WebSocket update
        await send_training_update("training", 25.0, f"✓ Training started: {config.model_type} for {config.epochs} epochs", 0, config.epochs)
        
        # Train the model with progress callback
        model_path = await trainer.train(
            dataset_path=dataset_path,
            model_type=config.model_type,
            epochs=config.epochs,
            batch_size=config.batch_size,
            image_size=config.image_size,
            learning_rate=config.learning_rate,
            progress_callback=async_progress_callback  # Enable progress callback
        )
        
        # Step 4: Training completed - verify model exists
        if not model_path or not os.path.exists(model_path):
            raise Exception(f"Training completed but model file not found at: {model_path}")
        
        # Verify model file size is reasonable (at least 1MB)
        model_size = os.path.getsize(model_path) / (1024 * 1024)  # Size in MB
        if model_size < 1:
            raise Exception(f"Model file seems too small ({model_size:.2f} MB). Training may have failed.")
        
        training_status.status = "completed"
        training_status.progress = 100.0
        training_status.message = f"Training completed successfully! Model saved ({model_size:.2f} MB)"
        training_status.model_path = model_path
        
        # Send final WebSocket update
        await send_training_update("completed", 100.0, f"Training completed successfully! Model: {os.path.basename(model_path)}")
        
    except Exception as e:
        training_status.status = "failed"
        training_status.message = f"Training failed: {str(e)}"
        print(f"Training error: {str(e)}")
        
        # Send error WebSocket update
        await send_training_update("failed", 0.0, f"Training failed: {str(e)}")

async def async_progress_callback(epoch: int, total_epochs: int, loss: float, metrics: dict):
    """
    Progress callback for training updates - called for each epoch or initialization step
    """
    # Update global status (this is what polling will read)
    global training_status
    
    if epoch == 0:
        # This is an initialization update (model download, etc.)
        init_message = metrics.get('init_message', None) if metrics else None
        if init_message:
            training_status.message = init_message
            # Extract progress from message if it's a download percentage
            if 'downloading' in init_message.lower():
                # Try to extract percentage
                import re
                pct_match = re.search(r'(\d+)%', init_message)
                if pct_match:
                    download_pct = int(pct_match.group(1))
                    training_status.progress = 25.0 + (download_pct * 0.05)  # 25-30%
                else:
                    training_status.progress = min(training_status.progress + 1.0, 30.0)
            else:
                training_status.progress = min(training_status.progress + 1.0, 30.0)
        else:
            training_status.message = training_status.message or "Loading model..."
            training_status.progress = min(training_status.progress + 1.0, 30.0)  # Cap at 30% during init
    else:
        # Actual training epoch
        # Calculate progress (25% for prep, 75% for training)
        progress = 25.0 + (epoch / total_epochs) * 70.0
        accuracy = metrics.get('mAP50', 0.0) if metrics else None
        
        training_status.current_epoch = epoch
        training_status.total_epochs = total_epochs
        training_status.loss = loss if loss > 0 else training_status.loss  # Keep previous loss if invalid
        training_status.accuracy = accuracy
        training_status.progress = min(progress, 95.0)  # Cap at 95% until complete
        training_status.message = f"Epoch {epoch}/{total_epochs} - Loss: {loss:.4f}" if loss > 0 else f"Epoch {epoch}/{total_epochs}"
        
        # Print to console for debugging
        print(f"Training progress: Epoch {epoch}/{total_epochs}, Loss: {loss:.4f}, Progress: {training_status.progress:.1f}%")
    
    # Send WebSocket update immediately
    await send_training_update(
        training_status.status if epoch > 0 else "preparing", 
        training_status.progress, 
        training_status.message,
        epoch, 
        total_epochs, 
        training_status.loss if epoch > 0 else None, 
        metrics.get('mAP50', None) if metrics and epoch > 0 else None
    )

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
