import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class DatasetService:
    """
    Service for managing multiple datasets
    Each dataset has its own directory structure for uploads, annotations, and training data
    """
    
    def __init__(self):
        self.datasets_dir = "datasets"
        self.metadata_file = os.path.join(self.datasets_dir, "metadata.json")
        self._ensure_datasets_dir()
        self._ensure_default_dataset()
    
    def _ensure_datasets_dir(self):
        """Create datasets directory if it doesn't exist"""
        os.makedirs(self.datasets_dir, exist_ok=True)
        if not os.path.exists(self.metadata_file):
            self._save_metadata({"datasets": [], "active_dataset_id": None})
    
    def _ensure_default_dataset(self):
        """Create a default dataset if none exists and migrate existing data"""
        metadata = self._load_metadata()
        
        # If no datasets exist, create default and migrate existing data
        if len(metadata["datasets"]) == 0:
            # Check if old static/uploads or static/annotations exist
            has_existing_data = (
                os.path.exists("static/uploads") and len(os.listdir("static/uploads")) > 0
            ) or (
                os.path.exists("static/annotations") and len(os.listdir("static/annotations")) > 0
            )
            
            if has_existing_data:
                # Create default dataset and migrate
                default_dataset = self.create_dataset("Default Dataset", "Migrated from existing data")
                self._migrate_existing_data(default_dataset["id"])
            else:
                # Just create empty default dataset
                default_dataset = self.create_dataset("Default Dataset", "Default dataset for shrimp images")
    
    def _migrate_existing_data(self, dataset_id: str):
        """Migrate existing uploads and annotations to a dataset"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return
        
        import shutil
        
        # Migrate uploads to images directory
        old_uploads = "static/uploads"
        new_images = os.path.join(dataset["path"], "images")
        os.makedirs(new_images, exist_ok=True)
        
        if os.path.exists(old_uploads):
            for filename in os.listdir(old_uploads):
                # Skip temp files and annotated images - they shouldn't be in uploads
                if filename.startswith('temp_'):
                    continue
                if filename.endswith('_annotated.jpg') or filename.endswith('_annotated.webp') or filename.endswith('_annotated.png') or filename.endswith('_annotated.jpeg'):
                    continue
                
                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                    src = os.path.join(old_uploads, filename)
                    dst = os.path.join(new_images, filename)
                    if os.path.isfile(src):
                        try:
                            shutil.move(src, dst)
                        except Exception as e:
                            print(f"Warning: Could not migrate {filename}: {e}")
        
        # Migrate annotations
        old_annotations = "static/annotations"
        new_annotations = os.path.join(dataset["path"], "annotations")
        os.makedirs(new_annotations, exist_ok=True)
        
        if os.path.exists(old_annotations):
            for filename in os.listdir(old_annotations):
                if filename.endswith('.json'):
                    src = os.path.join(old_annotations, filename)
                    dst = os.path.join(new_annotations, filename)
                    if os.path.isfile(src):
                        try:
                            shutil.move(src, dst)
                        except Exception as e:
                            print(f"Warning: Could not migrate {filename}: {e}")
        
        # Update stats after migration
        self.update_dataset_stats(dataset_id)
    
    def _load_metadata(self) -> Dict:
        """Load dataset metadata from JSON file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                return {"datasets": [], "active_dataset_id": None}
        return {"datasets": [], "active_dataset_id": None}
    
    def _save_metadata(self, metadata: Dict):
        """Save dataset metadata to JSON file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def create_dataset(self, name: str, description: str = "") -> Dict:
        """Create a new dataset"""
        metadata = self._load_metadata()
        
        # Generate unique ID
        dataset_id = f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create directory structure
        # Structure: datasets/{id}/
        #   - images/          (uploaded images)
        #   - annotations/     (annotation JSON files)
        #   - dataset/         (prepared training data)
        #     - images/train/  (training images)
        #     - images/val/    (validation images)
        #     - labels/train/  (training labels)
        #     - labels/val/    (validation labels)
        dataset_path = os.path.join(self.datasets_dir, dataset_id)
        os.makedirs(os.path.join(dataset_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "annotations"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "dataset", "images", "train"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "dataset", "images", "val"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "dataset", "labels", "train"), exist_ok=True)
        os.makedirs(os.path.join(dataset_path, "dataset", "labels", "val"), exist_ok=True)
        
        dataset_info = {
            "id": dataset_id,
            "name": name,
            "description": description,
            "path": dataset_path,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "image_count": 0,
            "annotation_count": 0
        }
        
        metadata["datasets"].append(dataset_info)
        
        # Set as active if it's the first dataset
        if metadata["active_dataset_id"] is None:
            metadata["active_dataset_id"] = dataset_id
        
        self._save_metadata(metadata)
        try:
            from services.dataset_manifest import load_manifest
            load_manifest(dataset_path)
        except Exception as e:
            print(f"Warning: could not seed dataset_manifest.yaml: {e}")
        return dataset_info
    
    def list_datasets(self) -> List[Dict]:
        """List all datasets"""
        metadata = self._load_metadata()
        # Update stats for all datasets
        for dataset in metadata["datasets"]:
            self.update_dataset_stats(dataset["id"])
        return metadata["datasets"]
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset by ID"""
        metadata = self._load_metadata()
        for dataset in metadata["datasets"]:
            if dataset["id"] == dataset_id:
                return dataset
        return None
    
    def get_active_dataset(self) -> Optional[Dict]:
        """Get the currently active dataset"""
        metadata = self._load_metadata()
        active_id = metadata.get("active_dataset_id")
        if active_id:
            dataset = self.get_dataset(active_id)
            if dataset:
                return dataset
        # If no active dataset, try to get first dataset
        if len(metadata["datasets"]) > 0:
            first_dataset = metadata["datasets"][0]
            metadata["active_dataset_id"] = first_dataset["id"]
            self._save_metadata(metadata)
            return first_dataset
        return None
    
    def set_active_dataset(self, dataset_id: str) -> bool:
        """Set the active dataset"""
        metadata = self._load_metadata()
        if self.get_dataset(dataset_id):
            metadata["active_dataset_id"] = dataset_id
            self._save_metadata(metadata)
            return True
        return False
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset (cannot delete active dataset)"""
        metadata = self._load_metadata()
        if metadata.get("active_dataset_id") == dataset_id:
            return False  # Cannot delete active dataset
        
        dataset = self.get_dataset(dataset_id)
        if dataset:
            # Remove directory
            import shutil
            if os.path.exists(dataset["path"]):
                shutil.rmtree(dataset["path"])
            
            # Remove from metadata
            metadata["datasets"] = [d for d in metadata["datasets"] if d["id"] != dataset_id]
            self._save_metadata(metadata)
            return True
        return False
    
    def update_dataset_stats(self, dataset_id: str):
        """Update image and annotation counts for a dataset"""
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return
        
        images_dir = os.path.join(dataset["path"], "images")
        annotations_dir = os.path.join(dataset["path"], "annotations")
        
        # Count images, excluding temp files and annotated images
        image_count = 0
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                # Skip temporary files (they should be in temp/ directory, but check just in case)
                if filename.startswith('temp_'):
                    continue
                # Skip annotated images (they should be in temp/ directory, but check just in case)
                if filename.endswith('_annotated.jpg') or filename.endswith('_annotated.webp') or filename.endswith('_annotated.png') or filename.endswith('_annotated.jpeg'):
                    continue
                # Only count valid image files
                if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.heic', '.heif', '.webp', '.gif']):
                    image_count += 1
        
        # Count annotation files
        annotation_count = 0
        if os.path.exists(annotations_dir):
            annotation_count = len([f for f in os.listdir(annotations_dir) if f.endswith('.json')])
        
        # Update metadata
        metadata = self._load_metadata()
        for d in metadata["datasets"]:
            if d["id"] == dataset_id:
                d["image_count"] = image_count
                d["annotation_count"] = annotation_count
                d["updated_at"] = datetime.now().isoformat()
                break
        
        self._save_metadata(metadata)
    
    def get_dataset_upload_dir(self, dataset_id: Optional[str] = None) -> str:
        """Get the images directory for a dataset (where uploaded images are stored)"""
        if dataset_id:
            dataset = self.get_dataset(dataset_id)
        else:
            dataset = self.get_active_dataset()
        
        if not dataset:
            # Fallback to old location for backward compatibility
            return "static/uploads"
        
        return os.path.join(dataset["path"], "images")
    
    def get_dataset_annotation_dir(self, dataset_id: Optional[str] = None) -> str:
        """Get the annotation directory for a dataset"""
        if dataset_id:
            dataset = self.get_dataset(dataset_id)
        else:
            dataset = self.get_active_dataset()
        
        if not dataset:
            # Fallback to old location for backward compatibility
            return "static/annotations"
        
        return os.path.join(dataset["path"], "annotations")
    
    def get_dataset_path(self, dataset_id: Optional[str] = None) -> Optional[str]:
        """Get the dataset path for training"""
        if dataset_id:
            dataset = self.get_dataset(dataset_id)
        else:
            dataset = self.get_active_dataset()
        
        if not dataset:
            return None
        
        return os.path.join(dataset["path"], "dataset")

