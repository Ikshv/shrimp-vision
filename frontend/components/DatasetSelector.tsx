'use client'

import { useState } from 'react'
import { useDataset } from '@/contexts/DatasetContext'
import Link from 'next/link'
import { Database, Plus, Check, X, Loader2, Tags } from 'lucide-react'
import toast from 'react-hot-toast'

export default function DatasetSelector() {
  const {
    datasets,
    activeDataset,
    setActiveDataset,
    createDataset,
    deleteDataset,
    isLoading,
  } = useDataset()

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newDatasetName, setNewDatasetName] = useState('')
  const [newDatasetDescription, setNewDatasetDescription] = useState('')
  const [isCreating, setIsCreating] = useState(false)

  const handleCreateDataset = async () => {
    if (!newDatasetName.trim()) {
      toast.error('Dataset name is required')
      return
    }

    setIsCreating(true)
    try {
      await createDataset(newDatasetName.trim(), newDatasetDescription.trim())
      toast.success(`Dataset "${newDatasetName}" created`)
      setShowCreateModal(false)
      setNewDatasetName('')
      setNewDatasetDescription('')
    } catch (error) {
      // Error already handled in context
    } finally {
      setIsCreating(false)
    }
  }

  const handleSetActive = async (datasetId: string) => {
    try {
      await setActiveDataset(datasetId)
      toast.success('Dataset activated')
    } catch (error) {
      // Error already handled in context
    }
  }

  const handleDelete = async (datasetId: string, datasetName: string) => {
    if (!confirm(`Are you sure you want to delete "${datasetName}"? This cannot be undone.`)) {
      return
    }

    try {
      await deleteDataset(datasetId)
      toast.success('Dataset deleted')
    } catch (error) {
      // Error already handled in context
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-primary-600" />
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Database className="w-5 h-5" />
          Datasets
        </h2>
        <div className="flex flex-wrap gap-2">
          <Link
            href="/classes"
            className="btn-secondary flex items-center gap-2"
            title="Edit detection classes, optional color tags, and extra attributes for this dataset"
          >
            <Tags className="w-4 h-4" />
            Labels &amp; attributes
          </Link>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Dataset
          </button>
        </div>
      </div>

      {datasets.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No datasets yet. Create your first dataset to get started!</p>
        </div>
      ) : (
        <div className="space-y-2">
          {datasets.map((dataset) => (
            <div
              key={dataset.id}
              className={`p-4 border rounded-lg ${
                activeDataset?.id === dataset.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium">{dataset.name}</h3>
                    {activeDataset?.id === dataset.id && (
                      <span className="px-2 py-0.5 text-xs bg-primary-500 text-white rounded">
                        Active
                      </span>
                    )}
                  </div>
                  {dataset.description && (
                    <p className="text-sm text-gray-600 mb-2">{dataset.description}</p>
                  )}
                  <div className="flex gap-4 text-sm text-gray-500">
                    <span>{dataset.image_count} images</span>
                    <span>{dataset.annotation_count} annotations</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {activeDataset?.id !== dataset.id && (
                    <>
                      <button
                        onClick={() => handleSetActive(dataset.id)}
                        className="btn-secondary text-sm flex items-center gap-1"
                      >
                        <Check className="w-4 h-4" />
                        Activate
                      </button>
                      <button
                        onClick={() => handleDelete(dataset.id, dataset.name)}
                        className="btn-danger text-sm flex items-center gap-1"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Dataset Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Create New Dataset</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Dataset Name *</label>
                <input
                  type="text"
                  value={newDatasetName}
                  onChange={(e) => setNewDatasetName(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="e.g., Shrimp Tank A"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !isCreating) {
                      handleCreateDataset()
                    }
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description (optional)</label>
                <textarea
                  value={newDatasetDescription}
                  onChange={(e) => setNewDatasetDescription(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Describe this dataset..."
                />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => {
                  setShowCreateModal(false)
                  setNewDatasetName('')
                  setNewDatasetDescription('')
                }}
                className="btn-secondary flex-1"
                disabled={isCreating}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateDataset}
                className="btn-primary flex-1"
                disabled={isCreating}
              >
                {isCreating ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


