import os
import subprocess
import asyncio
import threading
from typing import Optional, Callable, Dict, Any
from pathlib import Path

class SimpleTrainer:
    """
    Simple, robust YOLO trainer that runs training in a separate process
    """
    
    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Training state
        self.is_training = False
        self.training_process = None
    
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
        Train a YOLO model using a separate process
        """
        try:
            # Check if already training
            if self.is_training:
                raise ValueError("Training already in progress")
            
            self.is_training = True
            
            # Run training in a separate process
            result = await self._run_training_process(
                dataset_path, model_type, epochs, batch_size, 
                image_size, learning_rate, progress_callback
            )
            
            return result
            
        except Exception as e:
            self.is_training = False
            print(f"Training error: {str(e)}")
            raise e
    
    async def _run_training_process(
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
        Run training in a separate process to prevent crashes
        """
        result_container = {"result": None, "error": None}
        
        def training_worker():
            try:
                # Create a simple training script
                training_script = f"""
import os
import sys
from ultralytics import YOLO
import shutil

# Training parameters
dataset_path = "{dataset_path}"
model_type = "{model_type}"
epochs = {epochs}
batch_size = {batch_size}
image_size = {image_size}
learning_rate = {learning_rate}
models_dir = "{self.models_dir}"

try:
    # Load the model
    model = YOLO(f"{{model_type}}.pt")
    
    # Training parameters
    train_params = {{
        'data': dataset_path,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': image_size,
        'lr0': learning_rate,
        'device': 'cpu',  # Use CPU to prevent issues
        'project': models_dir,
        'name': f'shrimp_detection_{{model_type}}',
        'exist_ok': True,
        'save': True,
        'save_period': 10,
        'patience': 20,
        'verbose': True,
        'workers': 1,
        'amp': False,
    }}
    
    print(f"Starting training with parameters: {{train_params}}")
    results = model.train(**train_params)
    
    # Get the path to the best model
    model_name = f'shrimp_detection_{{model_type}}'
    best_model_path = os.path.join(models_dir, model_name, 'weights', 'best.pt')
    
    if not os.path.exists(best_model_path):
        best_model_path = os.path.join(models_dir, model_name, 'weights', 'last.pt')
    
    if not os.path.exists(best_model_path):
        raise ValueError("Trained model not found")
    
    # Copy the best model to the main models directory
    final_model_path = os.path.join(models_dir, f"shrimp_detection_{{model_type}}_best.pt")
    shutil.copy2(best_model_path, final_model_path)
    
    print(f"Training completed. Model saved to: {{final_model_path}}")
    print(f"SUCCESS:{{final_model_path}}")
    
except Exception as e:
    print(f"Training error: {{str(e)}}")
    print(f"ERROR:{{str(e)}}")
    sys.exit(1)
"""
                
                # Write training script to temporary file
                script_path = "temp_training_script.py"
                with open(script_path, 'w') as f:
                    f.write(training_script)
                
                # Run training script
                import sys
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read output line by line
                for line in process.stdout:
                    print(line.strip())
                    if line.startswith("SUCCESS:"):
                        result_container["result"] = line.split("SUCCESS:")[1].strip()
                    elif line.startswith("ERROR:"):
                        result_container["error"] = line.split("ERROR:")[1].strip()
                    elif "Epoch" in line and "/" in line:
                        # Extract epoch information for progress updates
                        try:
                            parts = line.split()
                            if len(parts) >= 2:
                                epoch_info = parts[1]  # e.g., "1/3"
                                if "/" in epoch_info:
                                    current_epoch, total_epochs = epoch_info.split("/")
                                    # Send progress update via WebSocket
                                    import asyncio
                                    from routes.websocket import send_training_update
                                    
                                    progress = 20.0 + (int(current_epoch) / int(total_epochs)) * 70.0
                                    asyncio.create_task(send_training_update(
                                        "training", 
                                        progress, 
                                        f"Training epoch {current_epoch}/{total_epochs}",
                                        int(current_epoch),
                                        int(total_epochs)
                                    ))
                        except:
                            pass  # Ignore parsing errors
                
                # Wait for process to complete
                process.wait()
                
                # Clean up
                if os.path.exists(script_path):
                    os.remove(script_path)
                
                if process.returncode != 0 and not result_container["result"]:
                    result_container["error"] = "Training process failed"
                
            except Exception as e:
                print(f"Training worker error: {str(e)}")
                result_container["error"] = str(e)
            finally:
                self.is_training = False
        
        # Start training thread
        training_thread = threading.Thread(target=training_worker)
        training_thread.daemon = True
        training_thread.start()
        
        # Wait for training to complete
        while training_thread.is_alive():
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
