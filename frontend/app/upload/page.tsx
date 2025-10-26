'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image as ImageIcon, CheckCircle, AlertCircle, Grid3X3 } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'
import axios from 'axios'
import { getImageUrl } from '@/lib/config'

interface UploadedImage {
  id: string
  filename: string
  original_name: string
  size: number
  width: number
  height: number
  format: string
  path: string
}

export default function UploadPage() {
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    setIsUploading(true)
    setUploadProgress(0)

    const formData = new FormData()
    acceptedFiles.forEach((file) => {
      formData.append('files', file)
    })

    try {
      const response = await axios.post('/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            setUploadProgress(progress)
          }
        },
      })

      if (response.data.success) {
        setUploadedImages(prev => [...prev, ...response.data.uploaded])
        toast.success(`Successfully uploaded ${response.data.uploaded.length} images`)
        
        if (response.data.errors.length > 0) {
          response.data.errors.forEach((error: string) => {
            toast.error(error)
          })
        }
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload images')
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/bmp': ['.bmp'],
      'image/tiff': ['.tiff', '.tif'],
      'image/heic': ['.heic', '.heif'],
      'image/webp': ['.webp'],
      'image/gif': ['.gif']
    },
    multiple: true,
    disabled: isUploading
  })

  const deleteImage = async (imageId: string) => {
    try {
      await axios.delete(`/api/upload/${imageId}`)
      setUploadedImages(prev => prev.filter(img => img.id !== imageId))
      toast.success('Image deleted successfully')
    } catch (error) {
      console.error('Delete error:', error)
      toast.error('Failed to delete image')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Upload Images</h1>
              <p className="text-gray-600 mt-1">Upload aquarium images for shrimp detection training</p>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/gallery" className="btn-secondary flex items-center gap-2">
                <Grid3X3 className="w-4 h-4" />
                View Gallery
              </Link>
              <Link href="/annotate" className="btn-primary">
                Next: Annotate
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Area */}
        <div className="card mb-8">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors duration-200 ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            } ${isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            {isUploading ? (
              <div>
                <p className="text-lg font-medium text-gray-900 mb-2">Uploading...</p>
                <div className="progress-bar mb-2">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600">{uploadProgress}% complete</p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop images here' : 'Drag & drop images here'}
                </p>
            <p className="text-gray-600 mb-4">
              or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Supports: JPG, PNG, HEIC, WebP, GIF, BMP, TIFF (max 10MB each)
            </p>
            <p className="text-xs text-blue-600 mt-2">
              📱 iPhone photos (HEIC) are fully supported!
            </p>
              </div>
            )}
          </div>
        </div>

        {/* Uploaded Images Grid */}
        {uploadedImages.length > 0 && (
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Uploaded Images ({uploadedImages.length})
              </h2>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Ready for annotation
              </div>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {uploadedImages.map((image) => (
                <div key={image.id} className="group relative">
                  <div className="aspect-square rounded-lg overflow-hidden bg-gray-100">
                    <img
                      src={getImageUrl(image.path)}
                      alt={image.original_name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                  
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {image.original_name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {image.width} × {image.height} • {formatFileSize(image.size)}
                    </p>
                  </div>
                  
                  <button
                    onClick={() => deleteImage(image.id)}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {uploadedImages.length === 0 && !isUploading && (
          <div className="card text-center py-12">
            <ImageIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No images uploaded yet</h3>
            <p className="text-gray-600 mb-6">
              Upload some aquarium images to get started with shrimp detection training.
            </p>
            <div className="text-sm text-gray-500">
              <p className="mb-2">Recommended image specifications:</p>
              <ul className="space-y-1">
                <li>• High resolution (at least 640×640 pixels)</li>
                <li>• Good lighting and contrast</li>
                <li>• Clear view of shrimp in the image</li>
                <li>• Multiple angles and positions</li>
              </ul>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8">
          <Link href="/" className="btn-secondary">
            ← Back to Home
          </Link>
          {uploadedImages.length > 0 && (
            <Link href="/annotate" className="btn-primary">
              Start Annotation →
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
