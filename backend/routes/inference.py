from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import json
from PIL import Image
import aiofiles
from services.inference_engine import InferenceEngine

router = APIRouter()

class DetectionResult(BaseModel):
    x: float
    y: float
    width: float
    height: float
    confidence: float
    label: str

class InferenceResponse(BaseModel):
    success: bool
    total_shrimp: int
    detections: List[DetectionResult]
    annotated_image_path: Optional[str]
    processing_time: float

@router.post("/predict", response_model=InferenceResponse)
async def predict_shrimp(
    image: UploadFile = File(...),
    model_name: Optional[str] = None,
    confidence_threshold: float = 0.5
):
    """
    Run inference on an uploaded image to detect and count shrimp
    """
    try:
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename for the uploaded image
        file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        temp_filename = f"temp_{uuid.uuid4()}{file_extension}"
        temp_path = f"static/uploads/{temp_filename}"
        
        # Save uploaded image temporarily
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await image.read()
            await f.write(content)
        
        try:
            # Initialize inference engine
            inference_engine = InferenceEngine()
            
            # Get the latest model if no specific model is provided
            if not model_name:
                model_name = inference_engine.get_latest_model()
                if not model_name:
                    raise HTTPException(status_code=404, detail="No trained model found")
            
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
                detections.append(DetectionResult(
                    x=detection['x'],
                    y=detection['y'],
                    width=detection['width'],
                    height=detection['height'],
                    confidence=detection['confidence'],
                    label=detection['label']
                ))
            
            # Generate annotated image path
            annotated_image_path = None
            if result.get('annotated_image_path'):
                annotated_image_path = f"/static/uploads/{os.path.basename(result['annotated_image_path'])}"
            
            return InferenceResponse(
                success=True,
                total_shrimp=result.get('total_shrimp', 0),
                detections=detections,
                annotated_image_path=annotated_image_path,
                processing_time=processing_time
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
                
                # Generate unique filename
                file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
                temp_filename = f"temp_{uuid.uuid4()}{file_extension}"
                temp_path = f"static/uploads/{temp_filename}"
                
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
                        detections.append({
                            "x": detection['x'],
                            "y": detection['y'],
                            "width": detection['width'],
                            "height": detection['height'],
                            "confidence": detection['confidence'],
                            "label": detection['label']
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
