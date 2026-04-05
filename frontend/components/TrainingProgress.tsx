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
  const lastKnownStatusRef = useRef<TrainingUpdate | null>(null) // Keep last known good status

  useEffect(() => {
    if (!isVisible) {
      prevStatusRef.current = undefined
      prevEpochRef.current = undefined
      return
    }

    let cancelled = false
    let timeoutId: ReturnType<typeof setTimeout> | null = null

    const scheduleNext = (delayMs: number) => {
      if (cancelled) return
      if (timeoutId !== null) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      timeoutId = setTimeout(() => {
        timeoutId = null
        void runPoll()
      }, delayMs)
    }

    const runPoll = async () => {
      if (cancelled) return

      try {
        const controller = new AbortController()
        const watchdog = setTimeout(() => controller.abort(), 8000)

        const response = await fetch('/api/train/status', {
          signal: controller.signal,
          cache: 'no-cache',
          headers: { 'Cache-Control': 'no-cache', Accept: 'application/json' },
        })

        clearTimeout(watchdog)

        const raw = await response.text()
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${raw.slice(0, 200)}`)
        }

        let data: { success?: boolean; status?: TrainingUpdate }
        try {
          data = JSON.parse(raw)
        } catch {
          console.error('Training status: non-JSON response', raw.slice(0, 120))
          throw new Error('Invalid JSON from /api/train/status')
        }

        if (data.success && data.status) {
          const status = data.status as TrainingUpdate

          lastKnownStatusRef.current = status
          setTrainingData(status)

          const shouldLog =
            prevStatusRef.current !== status.status ||
            prevEpochRef.current !== status.current_epoch ||
            (status.status === 'preparing' && prevStatusRef.current !== 'preparing') ||
            (status.status === 'training' && prevEpochRef.current === undefined)

          if (shouldLog) {
            let logMessage = `[${new Date().toLocaleTimeString()}] ${status.message}`

            if (status.status === 'training' && status.current_epoch > 0) {
              logMessage += ` - Epoch ${status.current_epoch}/${status.total_epochs}`
              if (status.loss !== null && status.loss !== undefined) {
                logMessage += ` - Loss: ${status.loss.toFixed(4)}`
              }
            }

            setLogs((prev) => {
              if (prev.length > 0 && prev[prev.length - 1] === logMessage) {
                return prev
              }
              return [...prev, logMessage].slice(-50)
            })

            prevStatusRef.current = status.status
            prevEpochRef.current = status.current_epoch
          }

          // Stop hammering the API once training is done (or idle with modal still open)
          const terminal =
            status.status === 'completed' ||
            status.status === 'failed' ||
            status.status === 'idle'
          if (terminal) {
            return
          }
        }
      } catch (error: unknown) {
        const err = error as { name?: string; message?: string }
        if (lastKnownStatusRef.current) {
          setTrainingData(lastKnownStatusRef.current)
        }
        if (
          err.name !== 'AbortError' &&
          err.message !== 'socket hang up' &&
          !String(err.message).includes('ECONNRESET')
        ) {
          console.error('Error polling training status:', error)
        }
      }

      if (!cancelled) {
        scheduleNext(1000)
      }
    }

    void runPoll()

    return () => {
      cancelled = true
      if (timeoutId !== null) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
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
