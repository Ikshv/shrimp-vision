'use client'

import { useState, useEffect, useRef } from 'react'
import { Activity, CheckCircle, XCircle, Clock } from 'lucide-react'

interface TrainingProgressProps {
  isVisible: boolean
  onClose: () => void
}

interface TrainingUpdate {
  type: string
  status: string
  progress: number
  message: string
  current_epoch: number
  total_epochs: number
  loss: number | null
  accuracy: number | null
}

export default function TrainingProgress({ isVisible, onClose }: TrainingProgressProps) {
  const [trainingData, setTrainingData] = useState<TrainingUpdate | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const prevStatusRef = useRef<string | undefined>(undefined)
  const prevEpochRef = useRef<number | undefined>(undefined)

  useEffect(() => {
    if (!isVisible) {
      // Reset refs when modal closes
      prevStatusRef.current = undefined
      prevEpochRef.current = undefined
      return
    }
    
    // Use polling for reliable updates
    const pollTrainingStatus = async () => {
      try {
        const response = await fetch('/api/train/status')
        const data = await response.json()
        
        if (data.success && data.status) {
          const status = data.status
          
          setTrainingData(status)
          
          // Add to logs - only add new entries when status changes or epoch changes
          const shouldLog = 
            prevStatusRef.current !== status.status || 
            prevEpochRef.current !== status.current_epoch ||
            (status.status === 'preparing' && prevStatusRef.current !== 'preparing') ||
            (status.status === 'training' && prevEpochRef.current === undefined)
          
          if (shouldLog) {
            let logMessage = `[${new Date().toLocaleTimeString()}] ${status.message}`
            
            // Add more detail for training epochs
            if (status.status === 'training' && status.current_epoch > 0) {
              logMessage += ` - Epoch ${status.current_epoch}/${status.total_epochs}`
              if (status.loss !== null && status.loss !== undefined) {
                logMessage += ` - Loss: ${status.loss.toFixed(4)}`
              }
            }
            
            setLogs(prev => {
              // Don't duplicate the same log message
              if (prev.length > 0 && prev[prev.length - 1] === logMessage) {
                return prev
              }
              const newLogs = [...prev, logMessage]
              return newLogs.slice(-50) // Keep last 50 logs for more history
            })
            
            prevStatusRef.current = status.status
            prevEpochRef.current = status.current_epoch
          }
        }
      } catch (error) {
        console.error('Error polling training status:', error)
      }
    }
    
    // Poll every 1 second for fast updates during training
    const interval = setInterval(pollTrainingStatus, 1000)
    
    // Initial poll immediately
    pollTrainingStatus()
    
    return () => {
      clearInterval(interval)
    }
  }, [isVisible])

  if (!isVisible) return null

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'preparing':
        return <Clock className="h-4 w-4 text-blue-500" />
      case 'training':
        return <Activity className="h-4 w-4 text-green-500 animate-pulse" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'preparing':
        return 'bg-blue-100 text-blue-800'
      case 'training':
        return 'bg-green-100 text-green-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="w-full max-w-2xl max-h-[80vh] overflow-hidden bg-white rounded-lg shadow-xl">
        <div className="flex flex-row items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            {getStatusIcon(trainingData?.status || 'idle')}
            Training Progress
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>
        
        <div className="p-6 space-y-4">
          {/* Status and Progress */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(trainingData?.status || 'idle')}`}>
                {trainingData?.status?.toUpperCase() || 'IDLE'}
              </span>
              <span className="text-sm text-gray-600">
                {trainingData?.progress?.toFixed(1) || 0}%
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${trainingData?.progress || 0}%` }}
              ></div>
            </div>
            
            <p className="text-sm text-gray-600">
              {trainingData?.message || 'Ready to train'}
            </p>
          </div>

          {/* Training Details */}
          {(trainingData?.status === 'preparing' || trainingData?.status === 'training' || trainingData?.status === 'completed') && (
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-700">Epochs</p>
                <p className="text-lg font-semibold">
                  {trainingData?.current_epoch || 0} / {trainingData?.total_epochs || 0}
                </p>
                {trainingData?.status === 'training' && trainingData?.total_epochs > 0 && (
                  <p className="text-xs text-gray-500 mt-1">
                    {Math.round(((trainingData.current_epoch || 0) / trainingData.total_epochs) * 100)}% complete
                  </p>
                )}
              </div>
              
              {trainingData?.loss !== null && trainingData?.loss !== undefined && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Loss</p>
                  <p className="text-lg font-semibold">
                    {trainingData.loss.toFixed(4)}
                  </p>
                </div>
              )}
              
              {trainingData?.accuracy !== null && trainingData?.accuracy !== undefined && (
                <div>
                  <p className="text-sm font-medium text-gray-700">Accuracy (mAP50)</p>
                  <p className="text-lg font-semibold">
                    {(trainingData.accuracy * 100).toFixed(1)}%
                  </p>
                </div>
              )}
              
              {trainingData?.status === 'preparing' && (
                <div className="col-span-2">
                  <p className="text-sm font-medium text-gray-700">Status</p>
                  <p className="text-sm text-gray-600">
                    Preparing dataset and initializing model...
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Training Logs */}
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Training Logs</h4>
            <div className="bg-black text-green-400 p-3 rounded-lg h-48 overflow-y-auto font-mono text-xs">
              {logs.map((log, index) => (
                <div key={index} className="mb-1">
                  {log}
                </div>
              ))}
            </div>
          </div>

          {/* Close button for completed/failed training */}
          {(trainingData?.status === 'completed' || trainingData?.status === 'failed') && (
            <div className="flex justify-end">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Close
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
