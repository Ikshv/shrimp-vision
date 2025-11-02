import os
import subprocess
import asyncio
import threading
import queue
import re
from typing import Optional, Callable, Dict, Any
from pathlib import Path
import torch

class SimpleTrainer:
    """
    Simple, robust YOLO trainer that runs training in a separate process
    """
    
    def __init__(self):
        # Use absolute path for models directory (relative to backend directory)
        backend_dir = Path(__file__).parent.parent
        self.models_dir = str(backend_dir / "models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Training state
        self.is_training = False
        self.training_process = None
        self.progress_queue = queue.Queue()
        
        # Check if CUDA is available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"SimpleTrainer initialized - Using device: {self.device}")
    
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
        backend_dir = Path(__file__).parent.parent
        
        # Make dataset path absolute if it's relative
        if not os.path.isabs(dataset_path):
            dataset_path = str(backend_dir / dataset_path)
        
        def training_worker():
            try:
                # Get absolute paths
                abs_models_dir = os.path.abspath(self.models_dir)
                abs_dataset_path = os.path.abspath(dataset_path)
                
                # Create a simple training script with absolute paths
                training_script = f"""
import os
import sys
from ultralytics import YOLO
import shutil
import traceback

# Training parameters - use absolute paths
dataset_path = r"{abs_dataset_path}"
model_type = "{model_type}"
epochs = {epochs}
batch_size = {batch_size}
image_size = {image_size}
learning_rate = {learning_rate}
models_dir = r"{abs_models_dir}"
device = "{self.device}"

print(f"Models directory: {{models_dir}}")
print(f"Dataset path: {{dataset_path}}")
print(f"Device: {{device}}")

try:
    # Load the model
    print(f"Loading model: {{model_type}}.pt")
    model = YOLO(f"{{model_type}}.pt")
    
    # Training parameters
    train_params = {{
        'data': dataset_path,
        'epochs': epochs,
        'batch': batch_size,
        'imgsz': image_size,
        'lr0': learning_rate,
        'device': device,
        'project': models_dir,
        'name': f'shrimp_detection_{{model_type}}',
        'exist_ok': True,
        'save': True,
        'save_period': 10,
        'patience': 50,
        'verbose': True,
        'workers': 4 if device == 'cuda' else 2,
        'amp': device == 'cuda',
    }}
    
    print(f"Starting training with parameters:")
    print(f"  Epochs: {{epochs}}")
    print(f"  Batch size: {{batch_size}}")
    print(f"  Image size: {{image_size}}")
    print(f"  Learning rate: {{learning_rate}}")
    print(f"  Device: {{device}}")
    print(f"  Project: {{models_dir}}")
    
    # Start training - this will output progress to stdout
    results = model.train(**train_params)
    
    # Training completed - find the best model
    model_name = f'shrimp_detection_{{model_type}}'
    weights_dir = os.path.join(models_dir, model_name, 'weights')
    
    print(f"Looking for trained model in: {{weights_dir}}")
    
    # Try to find best.pt first
    best_model_path = os.path.join(weights_dir, 'best.pt')
    if not os.path.exists(best_model_path):
        print("best.pt not found, trying last.pt")
        best_model_path = os.path.join(weights_dir, 'last.pt')
    
    if not os.path.exists(best_model_path):
        # List what files exist
        if os.path.exists(weights_dir):
            files = os.listdir(weights_dir)
            print(f"Available files in weights directory: {{files}}")
        else:
            print(f"Weights directory does not exist: {{weights_dir}}")
            # Check if the run directory exists
            run_dir = os.path.join(models_dir, model_name)
            if os.path.exists(run_dir):
                print(f"Run directory exists: {{run_dir}}")
                for root, dirs, files in os.walk(run_dir):
                    print(f"  {{root}}: dirs={{dirs}}, files={{files[:10]}}")
        
        raise ValueError(f"Trained model not found at {{best_model_path}}")
    
    print(f"Found trained model: {{best_model_path}}")
    
    # Copy the best model to the main models directory with a simple name
    final_model_path = os.path.join(models_dir, f"shrimp_detection_{{model_type}}_best.pt")
    shutil.copy2(best_model_path, final_model_path)
    
    print(f"Model copied to: {{final_model_path}}")
    print(f"Model size: {{os.path.getsize(final_model_path) / (1024*1024):.2f}} MB")
    print(f"SUCCESS:{{final_model_path}}")
    
except Exception as e:
    error_msg = f"Training error: {{str(e)}}"
    print(error_msg)
    print("Traceback:")
    traceback.print_exc()
    print(f"ERROR:{{error_msg}}")
    sys.exit(1)
"""
                
                # Write training script to temporary file in backend directory
                script_path = str(backend_dir / "temp_training_script.py")
                with open(script_path, 'w') as f:
                    f.write(training_script)
                
                print(f"Training script written to: {script_path}")
                
                # Run training script
                import sys
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=str(backend_dir)  # Run from backend directory
                )
                
                # Read output line by line and parse progress
                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    
                    print(line)
                    
                    # Check for success
                    if line.startswith("SUCCESS:"):
                        result_container["result"] = line.split("SUCCESS:")[1].strip()
                    
                    # Check for error
                    elif line.startswith("ERROR:"):
                        result_container["error"] = line.split("ERROR:")[1].strip()
                    
                    # Parse YOLO training output for progress
                    # YOLO outputs various formats, check every line
                    
                    # Only parse actual training epochs, not validation or other progress
                    # Look for lines like "Epoch   1/100" or "      1/100" (with spaces before)
                    # or "Epoch 1/100:" (with colon after)
                    
                    # Skip validation lines, model transfer lines, etc.
                    skip_indicators = ['class', 'images', 'instances', 'transferred', 'validating', 'scanning', 'cache']
                    if any(skip in line.lower() for skip in skip_indicators):
                        # But check if it's a training epoch line that contains these words
                        epoch_indicators = ['box_loss', 'gpu_mem', f'/{epochs}', f'/{epochs}:']
                        if not ('epoch' in line.lower() and any(ind in line for ind in epoch_indicators)):
                            continue
                    
                    # Pattern 1: "Epoch   1/100" or "      1/100" (with leading spaces/tabs)
                    epoch_match = re.search(r'(?:Epoch\s+|^\s+)(\d+)/(\d+)', line)
                    
                    # Pattern 2: "1/100:" with colon (YOLO training format)
                    if not epoch_match:
                        epoch_match = re.search(r'(\d+)/(\d+):', line)
                    
                    # Pattern 3: Check if it's in a training context
                    if epoch_match:
                        current_epoch = int(epoch_match.group(1))
                        total_epochs = int(epoch_match.group(2))
                        
                        # Validate: 
                        # - Total epochs should match the expected count (or be close, allow some variance)
                        # - Should be in a reasonable range
                        # - Should not be validation epochs (1/1 is usually validation)
                        is_training_epoch = (
                            total_epochs == epochs or  # Exact match
                            (abs(total_epochs - epochs) <= 10 and total_epochs > 10)  # Close match
                        )
                        
                        # Skip validation epochs (usually 1/1)
                        is_validation = (current_epoch == 1 and total_epochs == 1 and 'class' in line.lower())
                        
                        if is_training_epoch and not is_validation and 0 < current_epoch <= total_epochs:
                            self.progress_queue.put({
                                'type': 'epoch',
                                'current_epoch': current_epoch,
                                'total_epochs': total_epochs
                            })
                            print(f"[YOLO] Parsed training epoch: {current_epoch}/{total_epochs}")
                    
                    # Also check for download progress
                    if 'downloading' in line.lower() and '%' in line:
                        # Extract download percentage if available
                        pct_match = re.search(r'(\d+)%', line)
                        if pct_match:
                            download_pct = int(pct_match.group(1))
                            # Send initialization progress (25-30% for download)
                            self.progress_queue.put({
                                'type': 'init_progress',
                                'progress': 25.0 + (download_pct * 0.05),  # 25-30%
                                'message': f'Downloading model: {download_pct}%'
                            })
                    
                    # Try to extract loss (multiple patterns) - check every line
                    loss_match = None
                    # Pattern 1: "loss=0.5234" or "loss= 0.5234"
                    loss_match = re.search(r'loss\s*=\s*([\d.]+)', line, re.IGNORECASE)
                    if not loss_match:
                        # Pattern 2: "train/loss 0.5234" or "train loss 0.5234"
                        loss_match = re.search(r'train[/\s]loss\s+([\d.]+)', line, re.IGNORECASE)
                    if not loss_match:
                        # Pattern 3: Loss in parentheses or brackets
                        loss_match = re.search(r'\(loss[:\s]+([\d.]+)\)', line, re.IGNORECASE)
                    if not loss_match:
                        # Pattern 4: Loss at end of line after comma or space
                        loss_match = re.search(r'loss[:,\s]+([\d.]+\d)', line, re.IGNORECASE)
                    
                    if loss_match:
                        try:
                            loss = float(loss_match.group(1))
                            # Sanity check: loss should be reasonable (0.001 to 100)
                            if 0.001 <= loss <= 100:
                                self.progress_queue.put({
                                    'type': 'loss',
                                    'loss': loss
                                })
                                print(f"[YOLO] Parsed loss: {loss:.4f}")
                        except (ValueError, IndexError):
                            pass  # Ignore invalid loss values
                
                # Wait for process to complete
                return_code = process.wait()
                
                # Clean up script
                if os.path.exists(script_path):
                    os.remove(script_path)
                
                # Check for errors
                if return_code != 0 and not result_container["result"]:
                    if not result_container["error"]:
                        result_container["error"] = f"Training process failed with return code {return_code}"
                
            except Exception as e:
                print(f"Training worker error: {str(e)}")
                import traceback
                traceback.print_exc()
                result_container["error"] = str(e)
            finally:
                self.is_training = False
        
        # Start training thread
        training_thread = threading.Thread(target=training_worker)
        training_thread.daemon = True
        training_thread.start()
        
        # Monitor progress and send updates
        async def progress_monitor():
            """Monitor progress queue and send updates"""
            current_info = {'current_epoch': 0, 'total_epochs': epochs, 'loss': 0.0}
            last_epoch_sent = 0
            
            while training_thread.is_alive():
                try:
                    # Process all queued updates (non-blocking)
                    updates_processed = 0
                    while updates_processed < 10:  # Process up to 10 updates per cycle
                        try:
                            update = self.progress_queue.get(timeout=0.1)
                            if update['type'] == 'epoch':
                                current_info['current_epoch'] = update['current_epoch']
                                current_info['total_epochs'] = update['total_epochs']
                                # Send update immediately when epoch changes
                                if current_info['current_epoch'] > last_epoch_sent:
                                    last_epoch_sent = current_info['current_epoch']
                                    if progress_callback:
                                        await progress_callback(
                                            current_info['current_epoch'],
                                            current_info['total_epochs'],
                                            current_info['loss'],
                                            {}
                                        )
                                        print(f"Sent epoch update: {current_info['current_epoch']}/{current_info['total_epochs']}")
                            elif update['type'] == 'loss':
                                current_info['loss'] = update['loss']
                                # Send update with new loss value
                                if progress_callback and current_info['current_epoch'] > 0:
                                    await progress_callback(
                                        current_info['current_epoch'],
                                        current_info['total_epochs'],
                                        current_info['loss'],
                                        {}
                                    )
                            elif update['type'] == 'init_progress':
                                # Send initialization progress updates (model download, etc.)
                                if progress_callback:
                                    # Send via callback - it will handle updating the message
                                    await progress_callback(
                                        0,
                                        epochs,
                                        0.0,
                                        {'init_message': update.get('message', 'Loading...')}
                                    )
                            updates_processed += 1
                        except queue.Empty:
                            break
                    
                    await asyncio.sleep(0.2)  # Check very frequently for real-time updates
                except Exception as e:
                    print(f"Progress monitor error: {str(e)}")
                    import traceback
                    traceback.print_exc()
        
        # Run progress monitor in parallel
        monitor_task = asyncio.create_task(progress_monitor())
        
        # Wait for training to complete
        while training_thread.is_alive():
            await asyncio.sleep(1)
        
        # Cancel monitor
        monitor_task.cancel()
        
        # Check for errors
        if result_container["error"]:
            raise Exception(result_container["error"])
        
        if not result_container["result"]:
            raise Exception("Training completed but no model file was produced")
        
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