'use client'

import { useState, useEffect } from 'react'
import { Upload, Trash2, Eye, Download, ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import toast from 'react-hot-toast'
import axios from 'axios'
import { getImageUrl } from '@/lib/config'

interface ImageData {
  id: string
  filename: string
  width: number
  height: number
  format: string
  path: string
}

export default function GalleryPage() {
  const [images, setImages] = useState<ImageData[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedImages, setSelectedImages] = useState<Set<string>>(new Set())
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  useEffect(() => {
    fetchImages()
  }, [])

  const fetchImages = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/upload/list')
      if (response.data.success) {
        setImages(response.data.images)
      }
    } catch (error) {
      console.error('Error fetching images:', error)
      toast.error('Failed to load images')
    } finally {
      setLoading(false)
    }
  }

  const deleteImage = async (imageId: string) => {
    try {
      await axios.delete(`/api/upload/${imageId}`)
      setImages(images.filter(img => img.id !== imageId))
      setSelectedImages(prev => {
        const newSet = new Set(prev)
        newSet.delete(imageId)
        return newSet
      })
      toast.success('Image deleted successfully')
    } catch (error) {
      console.error('Error deleting image:', error)
      toast.error('Failed to delete image')
    }
  }

  const deleteSelectedImages = async () => {
    if (selectedImages.size === 0) return

    try {
      const deletePromises = Array.from(selectedImages).map(id => 
        axios.delete(`/api/upload/${id}`)
      )
      await Promise.all(deletePromises)
      
      setImages(images.filter(img => !selectedImages.has(img.id)))
      setSelectedImages(new Set())
      toast.success(`${selectedImages.size} images deleted successfully`)
    } catch (error) {
      console.error('Error deleting images:', error)
      toast.error('Failed to delete selected images')
    }
  }

  const toggleImageSelection = (imageId: string) => {
    setSelectedImages(prev => {
      const newSet = new Set(prev)
      if (newSet.has(imageId)) {
        newSet.delete(imageId)
      } else {
        newSet.add(imageId)
      }
      return newSet
    })
  }

  const selectAllImages = () => {
    setSelectedImages(new Set(images.map(img => img.id)))
  }

  const clearSelection = () => {
    setSelectedImages(new Set())
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] p-4 bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading images...</p>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Home
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Image Gallery</h1>
                <p className="text-gray-600">{images.length} images uploaded</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link
                href="/upload"
                className="btn-primary flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Upload More
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      {images.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedImages.size === images.length && images.length > 0}
                    onChange={selectedImages.size === images.length ? clearSelection : selectAllImages}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-600">
                    {selectedImages.size > 0 ? `${selectedImages.size} selected` : 'Select all'}
                  </span>
                </div>
                
                {selectedImages.size > 0 && (
                  <button
                    onClick={deleteSelectedImages}
                    className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete Selected ({selectedImages.size})
                  </button>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Images */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {images.length === 0 ? (
          <div className="text-center py-12">
            <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No images uploaded yet</h3>
            <p className="text-gray-600 mb-6">Upload your first images to get started with shrimp detection</p>
            <Link
              href="/upload"
              className="btn-primary inline-flex items-center gap-2"
            >
              <Upload className="w-4 h-4" />
              Upload Images
            </Link>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6'
            : 'space-y-4'
          }>
            {images.map((image) => (
              <div
                key={image.id}
                className={`bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow ${
                  selectedImages.has(image.id) ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                <div className="relative">
                  <img
                    src={getImageUrl(image.path)}
                    alt={image.filename}
                    className={`w-full object-cover ${
                      viewMode === 'grid' ? 'h-48' : 'h-32'
                    }`}
                  />
                  
                  {/* Selection checkbox */}
                  <div className="absolute top-2 left-2">
                    <input
                      type="checkbox"
                      checked={selectedImages.has(image.id)}
                      onChange={() => toggleImageSelection(image.id)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 w-4 h-4"
                    />
                  </div>
                  
                  {/* Actions */}
                  <div className="absolute top-2 right-2 flex space-x-1">
                    <button
                      onClick={() => deleteImage(image.id)}
                      className="p-1 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
                      title="Delete image"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                </div>
                
                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {image.filename}
                    </h3>
                    <span className="text-xs text-gray-500 uppercase">
                      {image.format}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>{image.width} × {image.height}</div>
                    <div className="flex items-center justify-between">
                      <span>ID: {image.id.slice(0, 8)}...</span>
                      <Link
                        href={`/annotate?image=${image.id}`}
                        className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                      >
                        <Eye className="w-3 h-3" />
                        Annotate
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
