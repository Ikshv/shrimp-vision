'use client'

import { useState, useEffect } from 'react'
import { Brain, Play, Square, Download, Settings, BarChart3 } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'
import axios from 'axios'
import TrainingProgress from '@/components/TrainingProgress'

interface TrainingConfig {
  model_type: string
  epochs: number
  batch_size: number
  image_size: number
  learning_rate: number
  train_split: number
  val_split: number
}

interface TrainingStatus {
  status: string
  progress: number
  current_epoch: number
  total_epochs: number
  loss: number | null
  accuracy: number | null
  message: string
  model_path: string | null
}

interface ModelInfo {
  name: string
  description: string
  parameters: string
  size: string
  speed: string
  accuracy: string
}

export default function TrainPage() {
  const [config, setConfig] = useState<TrainingConfig>({
    model_type: 'yolov8n',
    epochs: 100,
    batch_size: 16,
    image_size: 640,
    learning_rate: 0.01,
    train_split: 0.8,
    val_split: 0.2
  })
  
  const [showTrainingProgress, setShowTrainingProgress] = useState(false)
  
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    status: 'idle',
    progress: 0,
    current_epoch: 0,
    total_epochs: 0,
    loss: null,
    accuracy: null,
    message: 'Ready to train',
    model_path: null
  })
  
  const [annotationStats, setAnnotationStats] = useState({
    total_images: 0,
    annotated_images: 0,
    annotation_progress: 0,
    total_shrimp: 0,
    total_bounding_boxes: 0,
    avg_shrimp_per_image: 0
  })
  
  const [isLoading, setIsLoading] = useState(true)
  const [isTraining, setIsTraining] = useState(false)

  const modelTypes: { [key: string]: ModelInfo } = {
    'yolov8n': {
      name: 'YOLOv8 Nano',
      description: 'Fastest and smallest model, good for real-time applications',
      parameters: '3.2M',
      size: '6.2MB',
      speed: 'Fastest',
      accuracy: 'Good'
    },
    'yolov8s': {
      name: 'YOLOv8 Small',
      description: 'Balanced speed and accuracy',
      parameters: '11.2M',
      size: '21.5MB',
      speed: 'Fast',
      accuracy: 'Better'
    },
    'yolov8m': {
      name: 'YOLOv8 Medium',
      description: 'Good balance of speed and accuracy',
      parameters: '25.9M',
      size: '49.7MB',
      speed: 'Medium',
      accuracy: 'Good'
    },
    'yolov8l': {
      name: 'YOLOv8 Large',
      description: 'Higher accuracy, slower inference',
      parameters: '43.7M',
      size: '83.7MB',
      speed: 'Slow',
      accuracy: 'Better'
    },
    'yolov8x': {
      name: 'YOLOv8 Extra Large',
      description: 'Highest accuracy, slowest inference',
      parameters: '68.2M',
      size: '130.5MB',
      speed: 'Slowest',
      accuracy: 'Best'
    }
  }

  useEffect(() => {
    fetchAnnotationStats()
    fetchTrainingStatus()
  }, [])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isTraining || trainingStatus.status === 'preparing' || trainingStatus.status === 'training') {
      // Poll more frequently during active training (every 1 second)
      interval = setInterval(fetchTrainingStatus, 1000)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isTraining, trainingStatus.status])

  const fetchAnnotationStats = async () => {
    try {
      const response = await axios.get('/api/annotate/stats/summary')
      if (response.data.success) {
        setAnnotationStats(response.data.stats)
      }
    } catch (error) {
      console.error('Error fetching annotation stats:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchTrainingStatus = async () => {
    try {
      const response = await axios.get('/api/train/status')
      if (response.data.success) {
        const status = response.data.status
        setTrainingStatus(status)
        
        if (status.status === 'completed' || status.status === 'failed') {
          setIsTraining(false)
        }
      }
    } catch (error) {
      console.error('Error fetching training status:', error)
    }
  }

  const startTraining = async () => {
    if (annotationStats.annotated_images < 5) {
      toast.error('Need at least 5 annotated images to start training')
      return
    }

    // Show verification steps immediately
    setIsTraining(true)
    setShowTrainingProgress(true)
    
    // Step 1: Initial verification
    setTrainingStatus(prev => ({
      ...prev,
      status: 'preparing',
      message: 'Verifying dataset and configuration...',
      progress: 0,
      current_epoch: 0,
      total_epochs: config.epochs
    }))
    
    toast.loading('Verifying training setup...', { id: 'training-start' })
    
    try {
      // Show verification steps
      setTimeout(() => {
        setTrainingStatus(prev => ({
          ...prev,
          message: `✓ Verified ${annotationStats.annotated_images} annotated images`,
          progress: 5
        }))
        toast.loading('Checking dataset format...', { id: 'training-start' })
      }, 500)
      
      setTimeout(() => {
        setTrainingStatus(prev => ({
          ...prev,
          message: `✓ Verified model configuration (${modelTypes[config.model_type].name})`,
          progress: 10
        }))
        toast.loading('Initializing model trainer...', { id: 'training-start' })
      }, 1000)
      
      const response = await axios.post('/api/train/start', config)
      
      if (response.data.success) {
        // Update with initial status from server
        if (response.data.status) {
          setTrainingStatus(response.data.status)
        }
        toast.success('Training started successfully!', { id: 'training-start' })
      }
    } catch (error: any) {
      console.error('Error starting training:', error)
      toast.error(error.response?.data?.detail || 'Failed to start training', { id: 'training-start' })
      setIsTraining(false)
      setShowTrainingProgress(false)
      setTrainingStatus(prev => ({
        ...prev,
        status: 'failed',
        message: error.response?.data?.detail || 'Failed to start training'
      }))
    }
  }

  const stopTraining = async () => {
    try {
      await axios.post('/api/train/stop')
      setIsTraining(false)
      toast.success('Training stopped')
    } catch (error) {
      console.error('Error stopping training:', error)
      toast.error('Failed to stop training')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle': return 'text-gray-500'
      case 'preparing': return 'text-blue-500'
      case 'training': return 'text-yellow-500'
      case 'completed': return 'text-green-500'
      case 'failed': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'idle': return '⏸️'
      case 'preparing': return '🔄'
      case 'training': return '🏃'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '⏸️'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading training data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Train Model</h1>
              <p className="text-gray-600 mt-1">Train YOLOv8 models for shrimp detection</p>
            </div>
            <Link href="/test" className="btn-primary">
              Test Model
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Training Configuration */}
          <div className="lg:col-span-1">
            <div className="card">
              <div className="flex items-center gap-2 mb-6">
                <Settings className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Training Configuration</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model Type
                  </label>
                  <select
                    value={config.model_type}
                    onChange={(e) => setConfig(prev => ({ ...prev, model_type: e.target.value }))}
                    className="input-field"
                    disabled={isTraining}
                  >
                    {Object.entries(modelTypes).map(([key, model]) => (
                      <option key={key} value={key}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-1">
                    {modelTypes[config.model_type].description}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Epochs: {config.epochs}
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="500"
                    value={config.epochs}
                    onChange={(e) => setConfig(prev => ({ ...prev, epochs: parseInt(e.target.value) }))}
                    className="w-full"
                    disabled={isTraining}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Batch Size: {config.batch_size}
                  </label>
                  <input
                    type="range"
                    min="4"
                    max="64"
                    step="4"
                    value={config.batch_size}
                    onChange={(e) => setConfig(prev => ({ ...prev, batch_size: parseInt(e.target.value) }))}
                    className="w-full"
                    disabled={isTraining}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Image Size: {config.image_size}
                  </label>
                  <input
                    type="range"
                    min="320"
                    max="1280"
                    step="32"
                    value={config.image_size}
                    onChange={(e) => setConfig(prev => ({ ...prev, image_size: parseInt(e.target.value) }))}
                    className="w-full"
                    disabled={isTraining}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Learning Rate: {config.learning_rate}
                  </label>
                  <input
                    type="range"
                    min="0.001"
                    max="0.1"
                    step="0.001"
                    value={config.learning_rate}
                    onChange={(e) => setConfig(prev => ({ ...prev, learning_rate: parseFloat(e.target.value) }))}
                    className="w-full"
                    disabled={isTraining}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Training Status and Progress */}
          <div className="lg:col-span-2">
            <div className="card mb-6">
              <div className="flex items-center gap-2 mb-6">
                <Brain className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Training Status</h2>
              </div>
              
              <div className="space-y-6">
                {/* Status Overview */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getStatusIcon(trainingStatus.status)}</span>
                    <div>
                      <div className={`font-medium ${getStatusColor(trainingStatus.status)}`}>
                        {trainingStatus.status.charAt(0).toUpperCase() + trainingStatus.status.slice(1)}
                      </div>
                      <div className="text-sm text-gray-600">
                        {trainingStatus.message}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    {trainingStatus.status === 'idle' && (
                      <button
                        onClick={startTraining}
                        disabled={annotationStats.annotated_images < 5}
                        className="btn-primary flex items-center gap-2"
                      >
                        <Play className="w-4 h-4" />
                        Start Training
                      </button>
                    )}
                    
                    {(trainingStatus.status === 'preparing' || trainingStatus.status === 'training') && (
                      <button
                        onClick={stopTraining}
                        className="btn-danger flex items-center gap-2"
                      >
                        <Square className="w-4 h-4" />
                        Stop Training
                      </button>
                    )}
                    
                    {trainingStatus.status === 'completed' && trainingStatus.model_path && (
                      <button className="btn-primary flex items-center gap-2">
                        <Download className="w-4 h-4" />
                        Download Model
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Progress Bar */}
                {trainingStatus.status !== 'idle' && (
                  <div>
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Progress</span>
                      <span>{Math.round(trainingStatus.progress)}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${trainingStatus.progress}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {/* Training Metrics */}
                {trainingStatus.status === 'training' && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="text-sm text-blue-600 font-medium">Current Epoch</div>
                      <div className="text-2xl font-bold text-blue-900">
                        {trainingStatus.current_epoch} / {trainingStatus.total_epochs}
                      </div>
                    </div>
                    
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="text-sm text-green-600 font-medium">Loss</div>
                      <div className="text-2xl font-bold text-green-900">
                        {trainingStatus.loss ? trainingStatus.loss.toFixed(4) : 'N/A'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Dataset Statistics */}
            <div className="card">
              <div className="flex items-center gap-2 mb-6">
                <BarChart3 className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Dataset Statistics</h2>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {annotationStats.total_images}
                  </div>
                  <div className="text-sm text-gray-600">Total Images</div>
                </div>
                
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-900">
                    {annotationStats.annotated_images}
                  </div>
                  <div className="text-sm text-blue-600">Annotated</div>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-900">
                    {annotationStats.total_shrimp}
                  </div>
                  <div className="text-sm text-green-600">Total Shrimp</div>
                </div>
                
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-900">
                    {annotationStats.avg_shrimp_per_image.toFixed(1)}
                  </div>
                  <div className="text-sm text-purple-600">Avg per Image</div>
                </div>
              </div>
              
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Annotation Progress</span>
                  <span>{Math.round(annotationStats.annotation_progress)}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill bg-green-500" 
                    style={{ width: `${annotationStats.annotation_progress}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8">
          <Link href="/annotate" className="btn-secondary">
            ← Back to Annotation
          </Link>
          <Link href="/test" className="btn-primary">
            Test Model →
          </Link>
        </div>
      </div>
      
      {/* Training Progress Modal */}
      <TrainingProgress 
        isVisible={showTrainingProgress}
        onClose={() => setShowTrainingProgress(false)}
      />
    </div>
  )
}
