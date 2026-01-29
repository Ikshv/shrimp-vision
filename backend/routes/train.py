from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
import shutil
import re
from pathlib import Path
import asyncio
import aiofiles
import aiofiles.os
from services.simple_trainer import SimpleTrainer
from services.dataset_manager import DatasetManager
from services.dataset_service import DatasetService
from routes.websocket import send_training_update

# Path to persist training status across server restarts
TRAINING_STATUS_FILE = Path("training_status.json")

def sanitize_model_name(name: str) -> str:
    """
    Sanitize model name for filesystem use:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters (keep only alphanumeric, hyphens, underscores)
    - Limit length
    """
    if not name:
        return "shrimp"
    # Convert to lowercase
    name = name.lower().strip()
    # Replace spaces with hyphens
    name = name.replace(' ', '-')
    # Remove special characters, keep only alphanumeric, hyphens, underscores
    name = re.sub(r'[^a-z0-9_-]', '', name)
    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    # Limit length
    if len(name) > 50:
        name = name[:50]
    # Ensure it's not empty
    if not name:
        name = "shrimp"
    return name

router = APIRouter()
dataset_service = DatasetService()

class TrainingConfig(BaseModel):
    model_type: str = "yolov8n"  # yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    model_name: Optional[str] = "shrimp"  # Custom name for the model (e.g., "shrimp-red", "shrimp-blue")
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

def save_training_status():
    """Save training status to file for persistence across server restarts"""
    try:
        # Use atomic write: write to temp file first, then rename (prevents corruption)
        temp_file = TRAINING_STATUS_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(training_status.dict(), f, indent=2)
        # Atomic rename (works on Unix/Mac, Windows may need different approach)
        temp_file.replace(TRAINING_STATUS_FILE)
    except Exception as e:
        print(f"Error saving training status: {e}")
        import traceback
        traceback.print_exc()

def load_training_status():
    """Load training status from file on startup"""
    global training_status
    try:
        if TRAINING_STATUS_FILE.exists():
            with open(TRAINING_STATUS_FILE, 'r') as f:
                data = json.load(f)
                # Only restore if training was in progress (not completed/failed/idle)
                if data.get('status') in ['preparing', 'training']:
                    # If training was in progress, mark as failed (since server restarted)
                    training_status = TrainingStatus(
                        status="failed",
                        progress=data.get('progress', 0.0),
                        current_epoch=data.get('current_epoch', 0),
                        total_epochs=data.get('total_epochs', 0),
                        loss=data.get('loss'),
                        accuracy=data.get('accuracy'),
                        message="Training was interrupted by server restart",
                        model_path=data.get('model_path')
                    )
                    save_training_status()  # Save the updated status
                elif data.get('status') == 'failed':
                    # Restore failed status (user might want to see what went wrong)
                    training_status = TrainingStatus(**data)
                # For 'completed' status, reset to idle so user can start a new training
                # The completed model is still available in the models directory
                else:
                    # Reset to idle for completed or any other status
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
                    save_training_status()  # Save the reset status
    except Exception as e:
        print(f"Error loading training status: {e}")
        # On error, reset to idle
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

# Load training status on module initialization
load_training_status()

@router.post("/start")
async def start_training(
    config: TrainingConfig, 
    background_tasks: BackgroundTasks,
    dataset_id: Optional[str] = Query(None, description="Dataset ID to train on (uses active dataset if not provided)")
):
    """
    Start model training with the given configuration
    """
    global training_status
    
    try:
        # Check if training is already in progress
        if training_status.status in ["preparing", "training"]:
            raise HTTPException(status_code=400, detail="Training already in progress")
        
        # Get dataset
        if dataset_id:
            dataset = dataset_service.get_dataset(dataset_id)
            if not dataset:
                raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
        else:
            dataset = dataset_service.get_active_dataset()
            if not dataset:
                raise HTTPException(status_code=400, detail="No active dataset. Please create or select a dataset first.")
        
        # Check if we have enough annotated data
        annotation_stats = await get_annotation_stats(dataset["id"])
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
        save_training_status()  # Persist initial status
        
        # Start training in background
        background_tasks.add_task(run_training, config, dataset["id"])
        
        return {
            "success": True,
            "message": "Training started successfully",
            "config": config.dict(),
            "status": training_status.dict(),
            "dataset_id": dataset["id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        training_status.status = "failed"
        training_status.message = f"Failed to start training: {str(e)}"
        save_training_status()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_training_status():
    """
    Get current training status - reads directly from JSON file for reliability.
    This is a simple, fast, non-blocking endpoint that uses async file I/O.
    """
    try:
        # Use async file I/O to prevent blocking the event loop
        file_exists = await aiofiles.os.path.exists(str(TRAINING_STATUS_FILE))
        
        if file_exists:
            async with aiofiles.open(str(TRAINING_STATUS_FILE), 'r') as f:
                content = await f.read()
                data = json.loads(content)
                return {
                    "success": True,
                    "status": data
                }
        else:
            # If file doesn't exist, return idle status
            return {
                "success": True,
                "status": {
                    "status": "idle",
                    "progress": 0.0,
                    "current_epoch": 0,
                    "total_epochs": 0,
                    "loss": None,
                    "accuracy": None,
                    "message": "Ready to train",
                    "model_path": None
                }
            }
    except json.JSONDecodeError as e:
        # If JSON is corrupted, return idle status
        print(f"Error parsing training status JSON: {e}")
        return {
            "success": True,
            "status": {
                "status": "idle",
                "progress": 0.0,
                "current_epoch": 0,
                "total_epochs": 0,
                "loss": None,
                "accuracy": None,
                "message": "Ready to train",
                "model_path": None
            }
        }
    except Exception as e:
        # On any other error, return a safe default status
        print(f"Error reading training status: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": True,
            "status": {
                "status": "idle",
                "progress": 0.0,
                "current_epoch": 0,
                "total_epochs": 0,
                "loss": None,
                "accuracy": None,
                "message": "Ready to train",
                "model_path": None
            }
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
        save_training_status()
        return {"success": True, "message": "Training stopped"}
    else:
        raise HTTPException(status_code=400, detail="No training in progress")

@router.post("/reset")
async def reset_training_status():
    """
    Reset training status to idle (useful after completing a training session)
    """
    global training_status
    
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
    save_training_status()
    return {"success": True, "message": "Training status reset to idle"}

async def run_training(config: TrainingConfig, dataset_id: Optional[str] = None):
    """
    Background task to run model training
    """
    global training_status
    
    try:
        # Step 0: Initial verification
        training_status.status = "preparing"
        training_status.message = "Verifying training configuration..."
        training_status.progress = 5.0
        save_training_status()
        await send_training_update("preparing", 5.0, "Verifying training configuration...")
        await asyncio.sleep(0.5)  # Brief pause for UI update
        
        # Get dataset paths
        if dataset_id:
            dataset = dataset_service.get_dataset(dataset_id)
            if not dataset:
                raise Exception(f"Dataset {dataset_id} not found")
        else:
            dataset = dataset_service.get_active_dataset()
            if not dataset:
                raise Exception("No active dataset")
        
        dataset_path = dataset_service.get_dataset_path(dataset["id"])
        upload_dir = dataset_service.get_dataset_upload_dir(dataset["id"])
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        
        # Step 1: Prepare dataset
        training_status.message = "Preparing dataset and splitting images..."
        training_status.progress = 10.0
        save_training_status()
        await send_training_update("preparing", 10.0, "Preparing dataset and splitting images...")
        
        dataset_manager = DatasetManager(
            dataset_path=dataset_path,
            upload_dir=upload_dir,
            annotation_dir=annotation_dir
        )
        dataset_yaml_path = await dataset_manager.prepare_dataset(
            train_split=config.train_split,
            val_split=config.val_split
        )
        
        if not dataset_yaml_path:
            raise Exception("Failed to prepare dataset")
        
        # Get dataset stats for verification message
        dataset_stats = dataset_manager.get_dataset_stats()
        
        training_status.progress = 20.0
        training_status.message = f"Dataset prepared: {dataset_stats['train_images']} train, {dataset_stats['val_images']} val images"
        save_training_status()
        
        # Send WebSocket update
        await send_training_update("preparing", 20.0, f"✓ Dataset ready: {dataset_stats['train_images']} train, {dataset_stats['val_images']} val images")
        await asyncio.sleep(0.5)  # Brief pause for UI update
        
        # Step 2: Initialize trainer
        training_status.message = f"Initializing {config.model_type} model (downloading if needed)..."
        training_status.progress = 25.0
        save_training_status()
        await send_training_update("preparing", 25.0, f"Initializing {config.model_type} model (downloading if needed)...")
        
        trainer = SimpleTrainer()
        
        # Step 3: Start training - verification complete
        training_status.status = "training"
        training_status.message = f"Starting training: {config.model_type}, {config.epochs} epochs, batch size {config.batch_size}"
        training_status.progress = 25.0
        training_status.current_epoch = 0
        training_status.total_epochs = config.epochs
        save_training_status()
        
        # Send WebSocket update
        await send_training_update("training", 25.0, f"✓ Training started: {config.model_type} for {config.epochs} epochs", 0, config.epochs)
        
        # Sanitize model name
        sanitized_name = sanitize_model_name(config.model_name or "shrimp")
        
        # Train the model with progress callback
        model_path = await trainer.train(
            dataset_path=dataset_yaml_path,
            model_type=config.model_type,
            model_name=sanitized_name,
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
        # Preserve the last epoch number instead of resetting to 0
        # training_status.current_epoch should already be set from the last progress callback
        if training_status.current_epoch == 0:
            training_status.current_epoch = training_status.total_epochs  # Set to final epoch
        training_status.message = f"Training completed successfully! Model saved ({model_size:.2f} MB)"
        training_status.model_path = model_path
        save_training_status()
        print(f"[TRAIN STATUS] Training completed: final epoch={training_status.current_epoch}/{training_status.total_epochs}")
        
        # Send final WebSocket update
        await send_training_update("completed", 100.0, f"Training completed successfully! Model: {os.path.basename(model_path)}")
        
    except Exception as e:
        training_status.status = "failed"
        training_status.message = f"Training failed: {str(e)}"
        save_training_status()
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
            save_training_status()
        else:
            training_status.message = training_status.message or "Loading model..."
            training_status.progress = min(training_status.progress + 1.0, 30.0)  # Cap at 30% during init
            save_training_status()
    else:
        # Actual training epoch - ensure status is set to "training"
        training_status.status = "training"
        # Calculate progress (25% for prep, 75% for training)
        progress = 25.0 + (epoch / total_epochs) * 70.0
        accuracy = metrics.get('mAP50', 0.0) if metrics else None
        
        training_status.current_epoch = epoch
        training_status.total_epochs = total_epochs
        training_status.loss = loss if loss > 0 else training_status.loss  # Keep previous loss if invalid
        training_status.accuracy = accuracy
        training_status.progress = min(progress, 95.0)  # Cap at 95% until complete
        training_status.message = f"Epoch {epoch}/{total_epochs} - Loss: {loss:.4f}" if loss > 0 else f"Epoch {epoch}/{total_epochs}"
        
        # Print to console for debugging BEFORE saving
        print(f"[TRAIN STATUS] Updating: Epoch {epoch}/{total_epochs}, Loss: {loss:.4f}, Progress: {training_status.progress:.1f}%")
        
        save_training_status()  # Persist status update
        
        # Print confirmation after saving
        print(f"[TRAIN STATUS] Saved: current_epoch={training_status.current_epoch}, progress={training_status.progress:.1f}%")
    
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

async def get_annotation_stats(dataset_id: Optional[str] = None):
    """
    Helper function to get annotation statistics
    """
    try:
        # Get dataset
        if dataset_id:
            dataset = dataset_service.get_dataset(dataset_id)
            if not dataset:
                return {"stats": {"total_images": 0, "annotated_images": 0}}
        else:
            dataset = dataset_service.get_active_dataset()
            if not dataset:
                return {"stats": {"total_images": 0, "annotated_images": 0}}
        
        upload_dir = dataset_service.get_dataset_upload_dir(dataset["id"])
        annotation_dir = dataset_service.get_dataset_annotation_dir(dataset["id"])
        
        total_images = 0
        annotated_images = 0
        
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
        
        return {
            "stats": {
                "total_images": total_images,
                "annotated_images": annotated_images
            }
        }
    except Exception as e:
        return {"stats": {"total_images": 0, "annotated_images": 0}}
