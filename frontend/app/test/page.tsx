'use client'

import { useState, useRef, useEffect } from 'react'
import { Upload, Download, Eye, Target, BarChart3, Zap } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'
import axios from 'axios'
import { getImageUrl } from '@/lib/config'

interface DetectionResult {
  x: number
  y: number
  width: number
  height: number
  confidence: number
  label: string
}

interface InferenceResponse {
  success: boolean
  total_shrimp: number
  detections: DetectionResult[]
  annotated_image_path: string | null
  processing_time: number
}

interface ModelInfo {
  filename: string
  path: string
  size: number
  size_mb: number
  modified: number
}

export default function TestPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [inferenceResult, setInferenceResult] = useState<InferenceResponse | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([])
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchAvailableModels()
  }, [])

  const fetchAvailableModels = async () => {
    try {
      const response = await axios.get('/api/inference/models/available')
      if (response.data.success) {
        setAvailableModels(response.data.models)
        if (response.data.models.length > 0) {
          setSelectedModel(response.data.models[0].filename)
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error)
      toast.error('Failed to load available models')
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setInferenceResult(null)
    }
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const file = event.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setInferenceResult(null)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const runInference = async () => {
    if (!selectedFile || !selectedModel) {
      toast.error('Please select an image and a model')
      return
    }

    setIsProcessing(true)
    try {
      const formData = new FormData()
      formData.append('image', selectedFile)
      formData.append('model_name', selectedModel)
      formData.append('confidence_threshold', confidenceThreshold.toString())

      const response = await axios.post('/api/inference/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.success) {
        setInferenceResult(response.data)
        toast.success(`Detected ${response.data.total_shrimp} shrimp`)
      } else {
        toast.error('Inference failed')
      }
    } catch (error: any) {
      console.error('Inference error:', error)
      toast.error(error.response?.data?.detail || 'Inference failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const downloadModel = async (modelFilename: string) => {
    try {
      const response = await axios.get(`/api/export/model/${modelFilename}`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', modelFilename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Model downloaded successfully')
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Failed to download model')
    }
  }

  const exportDataset = async () => {
    try {
      const response = await axios.post('/api/export/dataset', {
        include_images: true,
        include_annotations: true,
        include_models: true,
        include_dataset: true,
        format: 'yolo'
      }, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'shrimp_dataset.zip')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Dataset exported successfully')
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Failed to export dataset')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Test & Export</h1>
              <p className="text-gray-600 mt-1">Test your trained model and export results</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={exportDataset}
                className="btn-secondary flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export Dataset
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Model Selection and Settings */}
          <div className="lg:col-span-1">
            <div className="card mb-6">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Model Settings</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Model
                  </label>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="input-field"
                  >
                    <option value="">Choose a model...</option>
                    {availableModels.map((model) => (
                      <option key={model.filename} value={model.filename}>
                        {model.filename} ({model.size_mb}MB)
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confidence Threshold: {confidenceThreshold}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={confidenceThreshold}
                    onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Higher values = fewer but more confident detections
                  </p>
                </div>
                
                {selectedModel && (
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm font-medium text-blue-900">Selected Model</div>
                    <div className="text-xs text-blue-700">
                      {availableModels.find(m => m.filename === selectedModel)?.size_mb}MB
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Available Models */}
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <BarChart3 className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Available Models</h2>
              </div>
              
              <div className="space-y-2">
                {availableModels.map((model) => (
                  <div
                    key={model.filename}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {model.filename}
                      </div>
                      <div className="text-xs text-gray-500">
                        {model.size_mb}MB
                      </div>
                    </div>
                    <button
                      onClick={() => downloadModel(model.filename)}
                      className="btn-secondary text-xs px-2 py-1"
                    >
                      <Download className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Image Upload and Results */}
          <div className="lg:col-span-2">
            <div className="card mb-6">
              <div className="flex items-center gap-2 mb-4">
                <Upload className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Test Image</h2>
              </div>
              
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {previewUrl ? (
                  <div className="space-y-4">
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="max-h-64 mx-auto rounded-lg shadow-sm"
                    />
                    <div>
                      <p className="text-sm text-gray-600">
                        {selectedFile?.name}
                      </p>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setSelectedFile(null)
                          setPreviewUrl(null)
                          setInferenceResult(null)
                        }}
                        className="text-sm text-red-600 hover:text-red-800 mt-2"
                      >
                        Remove image
                      </button>
                    </div>
                  </div>
                ) : (
                  <div>
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-lg font-medium text-gray-900 mb-2">
                      Drop an image here or click to select
                    </p>
                    <p className="text-gray-600">
                      Test your trained model on a new image
                    </p>
                  </div>
                )}
              </div>
              
              {selectedFile && selectedModel && (
                <div className="mt-4">
                  <button
                    onClick={runInference}
                    disabled={isProcessing}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                  >
                    {isProcessing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        Run Detection
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
            
            {/* Results */}
            {inferenceResult && (
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <Eye className="w-5 h-5 text-gray-600" />
                  <h2 className="text-lg font-semibold text-gray-900">Detection Results</h2>
                </div>
                
                <div className="space-y-6">
                  {/* Summary */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {inferenceResult.total_shrimp}
                      </div>
                      <div className="text-sm text-green-700">Shrimp Detected</div>
                    </div>
                    
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {inferenceResult.processing_time.toFixed(2)}s
                      </div>
                      <div className="text-sm text-blue-700">Processing Time</div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {inferenceResult.detections.length}
                      </div>
                      <div className="text-sm text-purple-700">Total Detections</div>
                    </div>
                  </div>
                  
                  {/* Annotated Image */}
                  {inferenceResult.annotated_image_path && (
                    <div>
                      <h3 className="text-md font-medium text-gray-900 mb-2">
                        Annotated Result
                      </h3>
                      <img
                        src={getImageUrl(inferenceResult.annotated_image_path)}
                        alt="Detection result"
                        className="w-full rounded-lg shadow-sm"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement
                          target.style.display = 'none'
                          console.error('Failed to load annotated image')
                        }}
                      />
                    </div>
                  )}
                  
                  {/* Detection Details */}
                  {inferenceResult.detections.length > 0 && (
                    <div>
                      <h3 className="text-md font-medium text-gray-900 mb-2">
                        Detection Details
                      </h3>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {inferenceResult.detections.map((detection, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                          >
                            <span>
                              {detection.label} #{index + 1}
                            </span>
                            <span className="text-gray-600">
                              {(detection.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8">
          <Link href="/train" className="btn-secondary">
            ← Back to Training
          </Link>
          <Link href="/" className="btn-primary">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
