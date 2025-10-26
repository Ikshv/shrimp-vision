'use client'

import { useState, useEffect, useRef } from 'react'
import { ArrowLeft, ArrowRight, Save, Target, RotateCcw, X } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'
import axios from 'axios'
import { getImageUrl } from '@/lib/config'

interface ImageData {
  id: string
  filename: string
  original_name: string
  width: number
  height: number
  path: string
}

interface BoundingBox {
  x: number
  y: number
  width: number
  height: number
  label: string
  confidence: number
}

interface Annotation {
  image_id: string
  image_filename: string
  image_width: number
  image_height: number
  bounding_boxes: BoundingBox[]
  total_shrimp: number
}

export default function AnnotatePage() {
  const [images, setImages] = useState<ImageData[]>([])
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const [boundingBoxes, setBoundingBoxes] = useState<BoundingBox[]>([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [currentBox, setCurrentBox] = useState<Partial<BoundingBox> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchImages()
  }, [])

  useEffect(() => {
    if (images.length > 0) {
      loadCurrentImageAnnotation()
    }
  }, [currentImageIndex, images])

  const fetchImages = async () => {
    try {
      const response = await axios.get('/api/upload/list')
      if (response.data.success) {
        setImages(response.data.images)
        setIsLoading(false)
      }
    } catch (error) {
      console.error('Error fetching images:', error)
      toast.error('Failed to load images')
      setIsLoading(false)
    }
  }

  const loadCurrentImageAnnotation = async () => {
    if (images.length === 0) return
    
    const currentImage = images[currentImageIndex]
    try {
      const response = await axios.get(`/api/annotate/${currentImage.id}`)
      if (response.data.success && response.data.annotation) {
        setBoundingBoxes(response.data.annotation.bounding_boxes || [])
      } else {
        setBoundingBoxes([])
      }
    } catch (error) {
      console.error('Error loading annotation:', error)
      setBoundingBoxes([])
    }
  }

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !imageRef.current) return
    
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY
    
    // Normalize coordinates
    const normalizedX = x / canvas.width
    const normalizedY = y / canvas.height
    
    setIsDrawing(true)
    setCurrentBox({
      x: normalizedX,
      y: normalizedY,
      width: 0,
      height: 0,
      label: 'shrimp',
      confidence: 1.0
    })
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !currentBox || !canvasRef.current) return
    
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY
    
    // Normalize coordinates
    const normalizedX = x / canvas.width
    const normalizedY = y / canvas.height
    
    const width = normalizedX - currentBox.x!
    const height = normalizedY - currentBox.y!
    
    setCurrentBox(prev => ({
      ...prev,
      width: Math.abs(width),
      height: Math.abs(height),
      x: width < 0 ? normalizedX : prev!.x,
      y: height < 0 ? normalizedY : prev!.y
    }))
    
    drawCanvas()
  }

  const handleMouseUp = () => {
    if (!isDrawing || !currentBox) return
    
    // Only add box if it has minimum size
    if (currentBox.width! > 0.01 && currentBox.height! > 0.01) {
      setBoundingBoxes(prev => [...prev, currentBox as BoundingBox])
    }
    
    setIsDrawing(false)
    setCurrentBox(null)
    drawCanvas()
  }

  const drawCanvas = () => {
    if (!canvasRef.current || !imageRef.current) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Draw existing bounding boxes
    ctx.strokeStyle = '#10B981'
    ctx.lineWidth = 2
    ctx.fillStyle = 'rgba(16, 185, 129, 0.1)'
    
    const allBoxes = currentBox ? [...boundingBoxes, currentBox] : boundingBoxes
    allBoxes.forEach((box, index) => {
      const x = box.x! * canvas.width
      const y = box.y! * canvas.height
      const width = box.width! * canvas.width
      const height = box.height! * canvas.height
      
      // Draw rectangle
      ctx.fillRect(x, y, width, height)
      ctx.strokeRect(x, y, width, height)
      
      // Draw label
      ctx.fillStyle = '#10B981'
      ctx.font = '14px Arial'
      ctx.fillText(`${box.label} ${index + 1}`, x, y - 5)
      ctx.fillStyle = 'rgba(16, 185, 129, 0.1)'
    })
  }

  const deleteBox = (index: number) => {
    setBoundingBoxes(prev => prev.filter((_, i) => i !== index))
    drawCanvas()
  }

  const saveAnnotation = async () => {
    if (images.length === 0) return
    
    const currentImage = images[currentImageIndex]
    setIsSaving(true)
    
    try {
      const annotation: Annotation = {
        image_id: currentImage.id,
        image_filename: currentImage.filename,
        image_width: currentImage.width,
        image_height: currentImage.height,
        bounding_boxes: boundingBoxes,
        total_shrimp: boundingBoxes.length
      }
      
      const response = await axios.post('/api/annotate/save', annotation)
      if (response.data.success) {
        toast.success(`Saved ${boundingBoxes.length} shrimp annotations`)
      }
    } catch (error) {
      console.error('Error saving annotation:', error)
      toast.error('Failed to save annotation')
    } finally {
      setIsSaving(false)
    }
  }

  const nextImage = () => {
    if (currentImageIndex < images.length - 1) {
      setCurrentImageIndex(prev => prev + 1)
    }
  }

  const prevImage = () => {
    if (currentImageIndex > 0) {
      setCurrentImageIndex(prev => prev - 1)
    }
  }

  const resetAnnotation = () => {
    setBoundingBoxes([])
    drawCanvas()
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading images...</p>
        </div>
      </div>
    )
  }

  if (images.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="card text-center py-12">
            <Target className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No images to annotate</h3>
            <p className="text-gray-600 mb-6">
              Upload some images first before you can start annotating.
            </p>
            <Link href="/upload" className="btn-primary">
              Upload Images
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const currentImage = images[currentImageIndex]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Annotate Shrimp</h1>
              <p className="text-gray-600 mt-1">
                Draw bounding boxes around shrimp in the images
              </p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={resetAnnotation}
                className="btn-secondary flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
              <button
                onClick={saveAnnotation}
                disabled={isSaving}
                className="btn-primary flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Image Annotation Area */}
          <div className="lg:col-span-3">
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  {currentImage.original_name}
                </h2>
                <div className="text-sm text-gray-600">
                  {currentImageIndex + 1} of {images.length}
                </div>
              </div>
              
              <div 
                ref={containerRef}
                className="relative border rounded-lg overflow-hidden bg-gray-100"
                style={{ aspectRatio: '16/9' }}
              >
                <img
                  ref={imageRef}
                  src={getImageUrl(currentImage.path)}
                  alt={currentImage.original_name}
                  className="w-full h-full object-contain"
                  onLoad={() => {
                    if (canvasRef.current && imageRef.current) {
                      const canvas = canvasRef.current
                      const img = imageRef.current
                      canvas.width = img.offsetWidth
                      canvas.height = img.offsetHeight
                      drawCanvas()
                    }
                  }}
                />
                <canvas
                  ref={canvasRef}
                  className="absolute top-0 left-0 cursor-crosshair"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                />
              </div>
              
              <div className="mt-4 flex justify-between items-center">
                <button
                  onClick={prevImage}
                  disabled={currentImageIndex === 0}
                  className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowLeft className="w-4 h-4" />
                  Previous
                </button>
                <button
                  onClick={nextImage}
                  disabled={currentImageIndex === images.length - 1}
                  className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Annotation Panel */}
          <div className="lg:col-span-1">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Annotations
              </h3>
              
              <div className="space-y-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {boundingBoxes.length}
                  </div>
                  <div className="text-sm text-green-700">
                    Shrimp Detected
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium text-gray-900">Instructions:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Click and drag to draw boxes</li>
                    <li>• Label each shrimp individually</li>
                    <li>• Save annotations regularly</li>
                    <li>• Use Previous/Next to navigate</li>
                  </ul>
                </div>
                
                {boundingBoxes.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Bounding Boxes:</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {boundingBoxes.map((box, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                        >
                          <span>{box.label} #{index + 1}</span>
                          <button
                            onClick={() => deleteBox(index)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8">
          <Link href="/upload" className="btn-secondary">
            ← Back to Upload
          </Link>
          <Link href="/train" className="btn-primary">
            Train Model →
          </Link>
        </div>
      </div>
    </div>
  )
}
