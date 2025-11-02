import os
import json
import shutil
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image

class DatasetManager:
    """
    Manages dataset preparation, splitting, and format conversion
    """
    
    def __init__(self):
        self.dataset_dir = "dataset"
        self.images_dir = os.path.join(self.dataset_dir, "images")
        self.labels_dir = os.path.join(self.dataset_dir, "labels")
        self.train_images_dir = os.path.join(self.images_dir, "train")
        self.val_images_dir = os.path.join(self.images_dir, "val")
        self.train_labels_dir = os.path.join(self.labels_dir, "train")
        self.val_labels_dir = os.path.join(self.labels_dir, "val")
        
        # Create directories
        for dir_path in [self.train_images_dir, self.val_images_dir, self.train_labels_dir, self.val_labels_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    async def prepare_dataset(self, train_split: float = 0.8, val_split: float = 0.2) -> Optional[str]:
        """
        Prepare dataset by splitting images and annotations into train/val sets
        """
        try:
            # Clear existing dataset
            self._clear_dataset()
            
            # Get all annotated images
            annotated_images = self._get_annotated_images()
            
            if not annotated_images:
                print("No annotated images found")
                return None
            
            # Shuffle the list for random splitting
            random.shuffle(annotated_images)
            
            # Calculate split indices
            total_images = len(annotated_images)
            train_count = int(total_images * train_split)
            
            # Split into train and validation sets
            train_images = annotated_images[:train_count]
            val_images = annotated_images[train_count:]
            
            # Process training images
            for image_info in train_images:
                await self._process_image_for_dataset(image_info, "train")
            
            # Process validation images
            for image_info in val_images:
                await self._process_image_for_dataset(image_info, "val")
            
            # Create dataset.yaml file
            dataset_yaml_path = self._create_dataset_yaml()
            
            print(f"Dataset prepared: {len(train_images)} train, {len(val_images)} val images")
            return dataset_yaml_path
            
        except Exception as e:
            print(f"Error preparing dataset: {str(e)}")
            return None
    
    def _get_annotated_images(self) -> List[Dict[str, Any]]:
        """
        Get list of all annotated images with their metadata
        """
        annotated_images = []
        
        # Get all annotation files
        annotations_dir = "static/annotations"
        if not os.path.exists(annotations_dir):
            return annotated_images
        
        for annotation_file in os.listdir(annotations_dir):
            if not annotation_file.endswith('.json'):
                continue
            
            annotation_path = os.path.join(annotations_dir, annotation_file)
            image_id = annotation_file.replace('.json', '')
            
            try:
                with open(annotation_path, 'r') as f:
                    annotation_data = json.load(f)
                
                # Check if corresponding image exists
                image_filename = annotation_data.get('image_filename')
                if not image_filename:
                    continue
                
                image_path = os.path.join("static/uploads", image_filename)
                if not os.path.exists(image_path):
                    continue
                
                annotated_images.append({
                    'image_id': image_id,
                    'image_filename': image_filename,
                    'image_path': image_path,
                    'annotation_data': annotation_data
                })
                
            except Exception as e:
                print(f"Error reading annotation {annotation_file}: {str(e)}")
                continue
        
        return annotated_images
    
    async def _process_image_for_dataset(self, image_info: Dict[str, Any], split: str):
        """
        Process a single image for the dataset (copy image and create YOLO label)
        """
        try:
            image_filename = image_info['image_filename']
            image_path = image_info['image_path']
            annotation_data = image_info['annotation_data']
            
            # Copy image to appropriate split directory
            if split == "train":
                dest_image_path = os.path.join(self.train_images_dir, image_filename)
            else:
                dest_image_path = os.path.join(self.val_images_dir, image_filename)
            
            shutil.copy2(image_path, dest_image_path)
            
            # Create YOLO format label file
            label_filename = image_filename.rsplit('.', 1)[0] + '.txt'
            if split == "train":
                label_path = os.path.join(self.train_labels_dir, label_filename)
            else:
                label_path = os.path.join(self.val_labels_dir, label_filename)
            
            # Convert annotations to YOLO format
            yolo_annotations = self._convert_to_yolo_format(annotation_data)
            
            with open(label_path, 'w') as f:
                f.write('\n'.join(yolo_annotations))
            
        except Exception as e:
            print(f"Error processing image {image_info['image_filename']}: {str(e)}")
    
    def _convert_to_yolo_format(self, annotation_data: Dict[str, Any]) -> List[str]:
        """
        Convert annotation data to YOLO format with multi-class support
        """
        yolo_annotations = []
        
        image_width = annotation_data.get('image_width', 1)
        image_height = annotation_data.get('image_height', 1)
        
        for bbox in annotation_data.get('bounding_boxes', []):
            # Convert normalized coordinates to YOLO format
            x_center = bbox['x'] + bbox['width'] / 2
            y_center = bbox['y'] + bbox['height'] / 2
            width = bbox['width']
            height = bbox['height']
            
            # YOLO format: class_id x_center y_center width height (all normalized)
            # Use class_id from bbox, fallback to 0 for backward compatibility
            class_id = bbox.get('class_id', 0)
            yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
            yolo_annotations.append(yolo_line)
        
        return yolo_annotations
    
    def _create_dataset_yaml(self) -> str:
        """
        Create dataset.yaml file for YOLO training with multi-class support
        """
        from config.classes import get_class_names, get_num_classes
        
        class_names = get_class_names()
        num_classes = get_num_classes()
        
        dataset_yaml_content = f"""
# Shrimp Detection Dataset Configuration
path: {os.path.abspath(self.dataset_dir)}
train: images/train
val: images/val

# Classes
nc: {num_classes}  # number of classes
names: {class_names}  # class names
"""
        
        dataset_yaml_path = os.path.join(self.dataset_dir, "dataset.yaml")
        with open(dataset_yaml_path, 'w') as f:
            f.write(dataset_yaml_content.strip())
        
        return dataset_yaml_path
    
    def _clear_dataset(self):
        """
        Clear existing dataset files
        """
        try:
            # Remove existing files in dataset directories
            for dir_path in [self.train_images_dir, self.val_images_dir, self.train_labels_dir, self.val_labels_dir]:
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
        except Exception as e:
            print(f"Error clearing dataset: {str(e)}")
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the prepared dataset
        """
        stats = {
            "train_images": 0,
            "val_images": 0,
            "train_labels": 0,
            "val_labels": 0,
            "total_images": 0,
            "total_labels": 0
        }
        
        try:
            # Count training images
            if os.path.exists(self.train_images_dir):
                stats["train_images"] = len([f for f in os.listdir(self.train_images_dir) 
                                           if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'])])
            
            # Count validation images
            if os.path.exists(self.val_images_dir):
                stats["val_images"] = len([f for f in os.listdir(self.val_images_dir) 
                                         if any(f.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'])])
            
            # Count training labels
            if os.path.exists(self.train_labels_dir):
                stats["train_labels"] = len([f for f in os.listdir(self.train_labels_dir) if f.endswith('.txt')])
            
            # Count validation labels
            if os.path.exists(self.val_labels_dir):
                stats["val_labels"] = len([f for f in os.listdir(self.val_labels_dir) if f.endswith('.txt')])
            
            stats["total_images"] = stats["train_images"] + stats["val_images"]
            stats["total_labels"] = stats["train_labels"] + stats["val_labels"]
            
        except Exception as e:
            print(f"Error getting dataset stats: {str(e)}")
        
        return stats
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Validate the prepared dataset
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            stats = self.get_dataset_stats()
            
            # Check if we have images
            if stats["total_images"] == 0:
                validation_result["valid"] = False
                validation_result["errors"].append("No images found in dataset")
            
            # Check if we have labels
            if stats["total_labels"] == 0:
                validation_result["valid"] = False
                validation_result["errors"].append("No labels found in dataset")
            
            # Check if train/val split is reasonable
            if stats["train_images"] == 0:
                validation_result["valid"] = False
                validation_result["errors"].append("No training images found")
            
            if stats["val_images"] == 0:
                validation_result["warnings"].append("No validation images found - consider adding more data")
            
            # Check if number of images matches number of labels
            if stats["train_images"] != stats["train_labels"]:
                validation_result["warnings"].append(f"Training images ({stats['train_images']}) don't match training labels ({stats['train_labels']})")
            
            if stats["val_images"] != stats["val_labels"]:
                validation_result["warnings"].append(f"Validation images ({stats['val_images']}) don't match validation labels ({stats['val_labels']})")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
