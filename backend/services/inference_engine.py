import os
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from ultralytics import YOLO
from PIL import Image
import json

class InferenceEngine:
    """
    Handles model inference for shrimp detection
    """
    
    def __init__(self):
        self.models_dir = "models"
        self.current_model = None
        self.current_model_path = None

    @staticmethod
    def _class_label_from_yolo_names(names: Any, class_id: int) -> Optional[str]:
        """Map YOLO class index to label; handles dict (int/str keys), list, and tuple."""
        if names is None:
            return None
        if isinstance(names, (list, tuple)):
            if 0 <= class_id < len(names):
                return str(names[class_id])
            return None
        if isinstance(names, dict):
            if class_id in names:
                return str(names[class_id])
            sk = str(class_id)
            if sk in names:
                return str(names[sk])
            try:
                fi = float(class_id)
                if fi == int(fi) and int(fi) in names:
                    return str(names[int(fi)])
            except (TypeError, ValueError):
                pass
        return None
    
    async def predict(
        self,
        image_path: str,
        model_name: Optional[str] = None,
        confidence_threshold: float = 0.5,
        save_annotated: bool = True
    ) -> Dict[str, Any]:
        """
        Run inference on an image to detect shrimp
        """
        try:
            # Load model if not already loaded or if different model requested
            if not self.current_model or (model_name and model_name != os.path.basename(self.current_model_path)):
                model_path = self._get_model_path(model_name)
                if not model_path:
                    raise ValueError("No trained model found")
                
                self.current_model = YOLO(model_path)
                self.current_model_path = model_path
            
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Run inference
            results = self.current_model(image, conf=confidence_threshold)
            
            # Get class names from the model (YOLO stores them in the model)
            # The model's class names should match what was in dataset.yaml
            model_class_names = self.current_model.names if hasattr(self.current_model, 'names') else None
            
            # Process results
            detections = []
            total_shrimp = 0
            
            # Track all detected classes for debugging
            detected_classes = {}
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Convert to normalized coordinates
                        img_height, img_width = image.shape[:2]
                        x_norm = x1 / img_width
                        y_norm = y1 / img_height
                        width_norm = (x2 - x1) / img_width
                        height_norm = (y2 - y1) / img_height
                        
                        label = self._class_label_from_yolo_names(model_class_names, class_id)
                        if label:
                            print(f"[INFERENCE] Model predicts class_id {class_id} = '{label}' (confidence: {confidence:.3f})")
                        else:
                            from config.classes import get_class_by_id
                            class_info = get_class_by_id(class_id)
                            label = class_info["name"] if class_info else f"class_{class_id}"
                            print(f"[INFERENCE] Fallback label for class_id {class_id} = '{label}' (confidence: {confidence:.3f})")
                        
                        # Track detected classes for debugging
                        if label not in detected_classes:
                            detected_classes[label] = 0
                        detected_classes[label] += 1
                        
                        detection = {
                            "x": x_norm,
                            "y": y_norm,
                            "width": width_norm,
                            "height": height_norm,
                            "confidence": confidence,
                            "label": label,
                            "class_id": class_id
                        }
                        
                        detections.append(detection)
                        total_shrimp += 1
            
            # Log detected classes for debugging
            if detected_classes:
                print(f"[INFERENCE] Detected classes: {detected_classes}")
                print(f"[INFERENCE] Model class names: {model_class_names}")
            
            # Create annotated image if requested
            annotated_image_path = None
            if save_annotated and detections:
                annotated_image_path = self._create_annotated_image(
                    image, detections, image_path
                )
            
            return {
                "success": True,
                "total_shrimp": total_shrimp,
                "detections": detections,
                "annotated_image_path": annotated_image_path,
                "model_used": os.path.basename(self.current_model_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_shrimp": 0,
                "detections": [],
                "annotated_image_path": None
            }
    
    def _get_model_path(self, model_name: Optional[str] = None) -> Optional[str]:
        """
        Get the path to the model file
        """
        if model_name:
            # Use specific model (basename only; avoid path traversal)
            safe_name = os.path.basename(model_name)
            model_path = os.path.join(self.models_dir, safe_name)
            if os.path.exists(model_path):
                return model_path
        
        # Newest .pt by mtime — matches SimpleTrainer output (e.g. shrimp_yolov8n.pt)
        if os.path.exists(self.models_dir):
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.pt')]
            if model_files:
                model_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.models_dir, x)), reverse=True)
                return os.path.join(self.models_dir, model_files[0])
        
        return None
    
    def _create_annotated_image(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]],
        original_path: str
    ) -> str:
        """
        Create an annotated image with bounding boxes
        """
        try:
            # Create a copy of the image for annotation
            annotated_image = image.copy()
            
            # Get class colors for visualization
            from config.classes import get_class_by_name

            def _color_for_label(name: str) -> tuple:
                info = get_class_by_name(name)
                if info and info.get("color"):
                    return info["color"]
                h = abs(hash(name)) % (256 * 256 * 256)
                r, g, b = (h >> 16) & 255, (h >> 8) & 255, h & 255
                if r + g + b < 80:
                    r, g, b = 200, 200, 100
                return f"#{r:02x}{g:02x}{b:02x}"
            
            # Draw bounding boxes
            for detection in detections:
                x = int(detection["x"] * image.shape[1])
                y = int(detection["y"] * image.shape[0])
                width = int(detection["width"] * image.shape[1])
                height = int(detection["height"] * image.shape[0])
                
                label = detection.get('label', 'object')
                color_hex = _color_for_label(label)
                # Convert hex color (#RRGGBB) to BGR for OpenCV
                # Remove '#' if present and convert to RGB integers
                hex_clean = color_hex.lstrip('#')
                r = int(hex_clean[0:2], 16)
                g = int(hex_clean[2:4], 16)
                b = int(hex_clean[4:6], 16)
                color_bgr = (b, g, r)  # OpenCV uses BGR format
                
                # Draw rectangle with class-specific color
                cv2.rectangle(annotated_image, (x, y), (x + width, y + height), color_bgr, 2)
                
                # Draw label with confidence (use original label, not overwritten one)
                original_label = detection.get('label', 'shrimp')
                label_text = f"{original_label}: {detection['confidence']:.2f}"
                label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                
                # Draw label background with class-specific color
                cv2.rectangle(
                    annotated_image,
                    (x, y - label_size[1] - 10),
                    (x + label_size[0], y),
                    color_bgr,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    annotated_image,
                    label_text,
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    2
                )
            
            # Add total count
            count_text = f"Detections: {len(detections)}"
            cv2.putText(
                annotated_image,
                count_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )
            
            # Save annotated image to temp directory (not in uploads)
            # Use absolute path to backend/temp directory
            backend_dir = Path(__file__).parent.parent
            temp_dir = str(backend_dir / "temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            original_filename = os.path.basename(original_path)
            name, ext = os.path.splitext(original_filename)
            # Remove temp_ prefix if present
            if name.startswith('temp_'):
                name = name[5:]  # Remove 'temp_' prefix
            annotated_filename = f"{name}_annotated{ext}"
            annotated_path = os.path.join(temp_dir, annotated_filename)
            
            cv2.imwrite(annotated_path, annotated_image)
            
            return annotated_path
            
        except Exception as e:
            print(f"Error creating annotated image: {str(e)}")
            return None
    
    def get_latest_model(self) -> Optional[str]:
        """
        Get the filename of the latest trained model
        """
        model_path = self._get_model_path()
        if model_path:
            return os.path.basename(model_path)
        return None
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available trained models
        """
        models = []
        
        if os.path.exists(self.models_dir):
            for filename in os.listdir(self.models_dir):
                if filename.endswith('.pt'):
                    model_path = os.path.join(self.models_dir, filename)
                    file_size = os.path.getsize(model_path)
                    mod_time = os.path.getmtime(model_path)
                    
                    models.append({
                        "filename": filename,
                        "path": model_path,
                        "size": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified": mod_time
                    })
            
            # Sort by modification time (newest first)
            models.sort(key=lambda x: x["modified"], reverse=True)
        
        return models
    
    def get_model_stats(self) -> Dict[str, Any]:
        """
        Get statistics about available models
        """
        models = self.list_available_models()
        
        stats = {
            "total_models": len(models),
            "latest_model": models[0]["filename"] if models else None,
            "total_size_mb": sum(model["size_mb"] for model in models),
            "models": models
        }
        
        return stats
    
    def validate_model(self, model_name: str) -> Dict[str, Any]:
        """
        Validate a model file
        """
        validation_result = {
            "valid": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            model_path = os.path.join(self.models_dir, model_name)
            
            if not os.path.exists(model_path):
                validation_result["errors"].append("Model file not found")
                return validation_result
            
            # Try to load the model
            try:
                model = YOLO(model_path)
                validation_result["valid"] = True
                validation_result["warnings"].append("Model loaded successfully")
            except Exception as e:
                validation_result["errors"].append(f"Cannot load model: {str(e)}")
            
            # Check file size
            file_size = os.path.getsize(model_path)
            if file_size < 1024 * 1024:  # Less than 1MB
                validation_result["warnings"].append("Model file seems unusually small")
            
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    async def batch_predict(
        self,
        image_paths: List[str],
        model_name: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Run inference on multiple images
        """
        results = []
        
        for image_path in image_paths:
            result = await self.predict(
                image_path=image_path,
                model_name=model_name,
                confidence_threshold=confidence_threshold,
                save_annotated=False  # Don't save annotated images for batch processing
            )
            results.append(result)
        
        return results
