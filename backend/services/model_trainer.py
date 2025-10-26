import os
import asyncio
import threading
from typing import Optional, Callable, Dict, Any
from ultralytics import YOLO
import torch
from pathlib import Path
import time

class ModelTrainer:
    """
    Handles YOLO model training with progress tracking
    """
    
    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Check if CUDA is available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        # Training state
        self.is_training = False
        self.training_thread = None
    
    async def train(
        self,
        dataset_path: str,
        model_type: str = "yolov8n",
        epochs: int = 100,
        batch_size: int = 16,
        image_size: int = 640,
        learning_rate: float = 0.01,
        progress_callback: Optional[Callable] = None
    ) -> str:
        """
        Train a YOLO model with the given parameters
        """
        try:
            # Validate dataset
            if not os.path.exists(dataset_path):
                raise ValueError(f"Dataset not found: {dataset_path}")
            
            # Check if already training
            if self.is_training:
                raise ValueError("Training already in progress")
            
            self.is_training = True
            
            # Run training in a separate thread to prevent blocking
            result = await self._run_training_thread(
                dataset_path, model_type, epochs, batch_size, 
                image_size, learning_rate, progress_callback
            )
            
            return result
            
        except Exception as e:
            self.is_training = False
            print(f"Training error: {str(e)}")
            raise e
    
    async def _run_training_thread(
        self,
        dataset_path: str,
        model_type: str,
        epochs: int,
        batch_size: int,
        image_size: int,
        learning_rate: float,
        progress_callback: Optional[Callable]
    ) -> str:
        """
        Run training in a separate thread to prevent blocking the main thread
        """
        result_container = {"result": None, "error": None}
        
        def training_worker():
            try:
                # Load the model
                model = YOLO(f"{model_type}.pt")
                
                # Training parameters
                train_params = {
                    'data': dataset_path,
                    'epochs': epochs,
                    'batch': batch_size,
                    'imgsz': image_size,
                    'lr0': learning_rate,
                    'device': self.device,
                    'project': self.models_dir,
                    'name': f'shrimp_detection_{model_type}',
                    'exist_ok': True,
                    'save': True,
                    'save_period': 10,  # Save checkpoint every 10 epochs
                    'patience': 20,  # Early stopping patience
                    'verbose': True,
                    'workers': 1,  # Reduce workers to prevent issues
                    'amp': False,  # Disable automatic mixed precision
                }
                
                # Start training
                print(f"Starting training with parameters: {train_params}")
                results = model.train(**train_params)
                
                # Get the path to the best model
                model_name = f'shrimp_detection_{model_type}'
                best_model_path = os.path.join(self.models_dir, model_name, 'weights', 'best.pt')
                
                if not os.path.exists(best_model_path):
                    # Fallback to last.pt if best.pt doesn't exist
                    best_model_path = os.path.join(self.models_dir, model_name, 'weights', 'last.pt')
                
                if not os.path.exists(best_model_path):
                    raise ValueError("Trained model not found")
                
                # Copy the best model to the main models directory for easy access
                final_model_path = os.path.join(self.models_dir, f"shrimp_detection_{model_type}_best.pt")
                import shutil
                shutil.copy2(best_model_path, final_model_path)
                
                print(f"Training completed. Model saved to: {final_model_path}")
                result_container["result"] = final_model_path
                
            except Exception as e:
                print(f"Training thread error: {str(e)}")
                result_container["error"] = str(e)
            finally:
                self.is_training = False
        
        # Start training thread
        self.training_thread = threading.Thread(target=training_worker)
        self.training_thread.daemon = True
        self.training_thread.start()
        
        # Wait for training to complete
        while self.training_thread.is_alive():
            await asyncio.sleep(1)
        
        # Check for errors
        if result_container["error"]:
            raise Exception(result_container["error"])
        
        return result_container["result"]
    
    def get_available_models(self) -> list:
        """
        Get list of available pre-trained models
        """
        return [
            "yolov8n",  # nano - fastest, smallest
            "yolov8s",  # small
            "yolov8m",  # medium
            "yolov8l",  # large
            "yolov8x"   # extra large - most accurate
        ]
    
    def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """
        Get information about a specific model type
        """
        model_info = {
            "yolov8n": {
                "name": "YOLOv8 Nano",
                "description": "Fastest and smallest model, good for real-time applications",
                "parameters": "3.2M",
                "size": "6.2MB",
                "speed": "Fastest",
                "accuracy": "Good"
            },
            "yolov8s": {
                "name": "YOLOv8 Small",
                "description": "Balanced speed and accuracy",
                "parameters": "11.2M",
                "size": "21.5MB",
                "speed": "Fast",
                "accuracy": "Better"
            },
            "yolov8m": {
                "name": "YOLOv8 Medium",
                "description": "Good balance of speed and accuracy",
                "parameters": "25.9M",
                "size": "49.7MB",
                "speed": "Medium",
                "accuracy": "Good"
            },
            "yolov8l": {
                "name": "YOLOv8 Large",
                "description": "Higher accuracy, slower inference",
                "parameters": "43.7M",
                "size": "83.7MB",
                "speed": "Slow",
                "accuracy": "Better"
            },
            "yolov8x": {
                "name": "YOLOv8 Extra Large",
                "description": "Highest accuracy, slowest inference",
                "parameters": "68.2M",
                "size": "130.5MB",
                "speed": "Slowest",
                "accuracy": "Best"
            }
        }
        
        return model_info.get(model_type, {
            "name": "Unknown Model",
            "description": "Model information not available",
            "parameters": "Unknown",
            "size": "Unknown",
            "speed": "Unknown",
            "accuracy": "Unknown"
        })
    
    def validate_training_setup(self, dataset_path: str) -> Dict[str, Any]:
        """
        Validate that the training setup is correct
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if dataset.yaml exists
            if not os.path.exists(dataset_path):
                validation_result["valid"] = False
                validation_result["errors"].append(f"Dataset file not found: {dataset_path}")
                return validation_result
            
            # Check if CUDA is available
            if not torch.cuda.is_available():
                validation_result["warnings"].append("CUDA not available - training will use CPU (slower)")
            
            # Check available disk space
            import shutil
            free_space = shutil.disk_usage(self.models_dir).free
            free_space_gb = free_space / (1024**3)
            
            if free_space_gb < 2:
                validation_result["warnings"].append(f"Low disk space: {free_space_gb:.1f}GB available (recommend at least 2GB)")
            
            # Check if we can load a YOLO model
            try:
                model = YOLO("yolov8n.pt")
                validation_result["valid"] = True
            except Exception as e:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Cannot load YOLO model: {str(e)}")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def get_training_recommendations(self, dataset_size: int) -> Dict[str, Any]:
        """
        Get training recommendations based on dataset size
        """
        recommendations = {
            "model_type": "yolov8n",
            "epochs": 100,
            "batch_size": 16,
            "learning_rate": 0.01,
            "image_size": 640,
            "notes": []
        }
        
        if dataset_size < 50:
            recommendations["model_type"] = "yolov8n"
            recommendations["epochs"] = 200
            recommendations["batch_size"] = 8
            recommendations["notes"].append("Small dataset - using nano model with more epochs")
        elif dataset_size < 200:
            recommendations["model_type"] = "yolov8s"
            recommendations["epochs"] = 150
            recommendations["batch_size"] = 16
            recommendations["notes"].append("Medium dataset - using small model")
        else:
            recommendations["model_type"] = "yolov8m"
            recommendations["epochs"] = 100
            recommendations["batch_size"] = 32
            recommendations["notes"].append("Large dataset - using medium model")
        
        return recommendations
