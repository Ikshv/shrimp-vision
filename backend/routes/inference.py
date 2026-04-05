from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import uuid
import json
import time
from PIL import Image
import aiofiles
from services.inference_engine import InferenceEngine
from services.dataset_manifest import parse_composite_yolo_slug

# Create a global inference engine instance to maintain state between requests
inference_engine = None

def get_inference_engine():
    global inference_engine
    if inference_engine is None:
        inference_engine = InferenceEngine()
    return inference_engine

router = APIRouter()

class DetectionResult(BaseModel):
    x: float
    y: float
    width: float
    height: float
    confidence: float
    label: str
    base_label: Optional[str] = None
    color: Optional[str] = None
    attributes: List[str] = Field(default_factory=list)

class InferenceResponse(BaseModel):
    success: bool
    total_shrimp: int
    detections: List[DetectionResult]
    annotated_image_path: Optional[str]
    processing_time: float
    model_used: Optional[str] = None

@router.post("/predict", response_model=InferenceResponse)
async def predict_shrimp(
    image: UploadFile = File(...),
    model_name: Optional[str] = Form(None),
    confidence_threshold: str = Form("0.5")
):
    """
    Run inference on an uploaded image to detect and count shrimp
    """
    try:
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create temp directory if it doesn't exist
        # Use absolute path to backend/temp directory
        from pathlib import Path
        backend_dir = Path(__file__).parent.parent
        temp_dir_path = backend_dir / "temp"
        temp_dir = str(temp_dir_path)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Clean up old temp files before running inference (older than 5 minutes)
        try:
            if temp_dir_path.exists():
                current_time = time.time()
                cleaned_count = 0
                for file in temp_dir_path.iterdir():
                    if file.is_file():
                        # Remove files older than 5 minutes
                        try:
                            if current_time - file.stat().st_mtime > 300:
                                file.unlink()
                                cleaned_count += 1
                        except Exception as e:
                            # Ignore errors during cleanup - don't break inference
                            pass
                if cleaned_count > 0:
                    print(f"🧹 Cleaned up {cleaned_count} old temp files before inference")
        except Exception as e:
            # Don't fail inference if cleanup has issues
            print(f"Warning: Could not clean temp files: {e}")
        
        # Generate unique filename for the uploaded image
        file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        temp_filename = f"temp_{uuid.uuid4()}{file_extension}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # Save uploaded image temporarily
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        try:
            # Get the inference engine instance
            engine = get_inference_engine()
            
            # Get the latest model if no specific model is provided
            if not model_name:
                model_name = engine.get_latest_model()
                if not model_name:
                    raise HTTPException(status_code=404, detail="No trained model found")
            
            # Run inference
            start_time = time.time()
            
            # Convert confidence threshold to float
            try:
                confidence_threshold_float = float(confidence_threshold)
            except (ValueError, TypeError):
                confidence_threshold_float = 0.5
            
            result = await engine.predict(
                image_path=temp_path,
                model_name=model_name,
                confidence_threshold=confidence_threshold_float
            )

            if result.get("success") is False:
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error") or "Inference failed",
                )
            
            processing_time = time.time() - start_time
            
            # Convert detections to response format
            detections = []
            for detection in result.get('detections', []):
                parsed = parse_composite_yolo_slug(detection["label"])
                detections.append(DetectionResult(
                    x=detection['x'],
                    y=detection['y'],
                    width=detection['width'],
                    height=detection['height'],
                    confidence=detection['confidence'],
                    label=detection['label'],
                    base_label=parsed.get("base_label"),
                    color=parsed.get("color"),
                    attributes=list(parsed.get("attributes") or []),
                ))
            
            # Generate annotated image path (if annotated image was created)
            annotated_image_path = None
            if result.get('annotated_image_path'):
                # Annotated images are saved to temp directory, convert to URL path
                # Use /temp/ path to match the route handler
                annotated_basename = os.path.basename(result['annotated_image_path'])
                annotated_image_path = f"/temp/{annotated_basename}"
            
            return InferenceResponse(
                success=True,
                total_shrimp=result.get('total_shrimp', 0),
                detections=detections,
                annotated_image_path=annotated_image_path,
                processing_time=processing_time,
                model_used=result.get('model_used', 'unknown')
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@router.post("/batch-predict")
async def batch_predict(
    images: List[UploadFile] = File(...),
    model_name: Optional[str] = None,
    confidence_threshold: float = 0.5
):
    """
    Run inference on multiple images
    """
    try:
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")
        
        results = []
        errors = []
        
        # Initialize inference engine
        inference_engine = InferenceEngine()
        
        # Get the latest model if no specific model is provided
        if not model_name:
            model_name = inference_engine.get_latest_model()
            if not model_name:
                raise HTTPException(status_code=404, detail="No trained model found")
        
        for image in images:
            try:
                # Validate image file
                if not image.content_type or not image.content_type.startswith('image/'):
                    errors.append(f"{image.filename}: Not a valid image file")
                    continue
                
                # Create temp directory if it doesn't exist
                # Use absolute path to backend/temp directory
                backend_dir = Path(__file__).parent.parent
                temp_dir_path = backend_dir / "temp"
                temp_dir = str(temp_dir_path)
                os.makedirs(temp_dir, exist_ok=True)
                
                # Clean up old temp files before running inference (older than 5 minutes)
                if temp_dir_path.exists():
                    current_time = time.time()
                    cleaned_count = 0
                    for file in temp_dir_path.iterdir():
                        if file.is_file():
                            # Remove files older than 5 minutes
                            if current_time - file.stat().st_mtime > 300:
                                try:
                                    file.unlink()
                                    cleaned_count += 1
                                except Exception as e:
                                    print(f"Error cleaning up temp file {file.name}: {e}")
                    if cleaned_count > 0:
                        print(f"🧹 Cleaned up {cleaned_count} old temp files before batch inference")
                
                # Generate unique filename
                file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
                temp_filename = f"temp_{uuid.uuid4()}{file_extension}"
                temp_path = os.path.join(temp_dir, temp_filename)
                
                # Save uploaded image temporarily
                async with aiofiles.open(temp_path, 'wb') as f:
                    content = await image.read()
                    await f.write(content)
                
                try:
                    # Run inference
                    import time
                    start_time = time.time()
                    
                    result = await inference_engine.predict(
                        image_path=temp_path,
                        model_name=model_name,
                        confidence_threshold=confidence_threshold
                    )
                    
                    processing_time = time.time() - start_time
                    
                    # Convert detections to response format
                    detections = []
                    for detection in result.get('detections', []):
                        parsed = parse_composite_yolo_slug(detection["label"])
                        detections.append({
                            "x": detection['x'],
                            "y": detection['y'],
                            "width": detection['width'],
                            "height": detection['height'],
                            "confidence": detection['confidence'],
                            "label": detection['label'],
                            "base_label": parsed.get("base_label"),
                            "color": parsed.get("color"),
                            "attributes": list(parsed.get("attributes") or []),
                        })
                    
                    results.append({
                        "filename": image.filename,
                        "total_shrimp": result.get('total_shrimp', 0),
                        "detections": detections,
                        "processing_time": processing_time,
                        "success": True
                    })
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                errors.append(f"{image.filename}: {str(e)}")
        
        return {
            "success": True,
            "results": results,
            "errors": errors,
            "total_processed": len(results),
            "total_errors": len(errors)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch inference failed: {str(e)}")

@router.get("/models/available")
async def get_available_models():
    """
    Get list of available trained models for inference
    """
    try:
        inference_engine = InferenceEngine()
        models = inference_engine.list_available_models()
        
        return {
            "success": True,
            "models": models
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")

@router.get("/stats")
async def get_inference_stats():
    """
    Get inference statistics and model performance metrics
    """
    try:
        inference_engine = InferenceEngine()
        stats = inference_engine.get_model_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inference stats: {str(e)}")
