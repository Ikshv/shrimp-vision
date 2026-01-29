'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

interface Dataset {
  id: string
  name: string
  description: string
  path: string
  created_at: string
  updated_at: string
  image_count: number
  annotation_count: number
}

interface DatasetContextType {
  datasets: Dataset[]
  activeDataset: Dataset | null
  isLoading: boolean
  refreshDatasets: () => Promise<void>
  setActiveDataset: (datasetId: string) => Promise<void>
  createDataset: (name: string, description?: string) => Promise<Dataset>
  deleteDataset: (datasetId: string) => Promise<void>
}

const DatasetContext = createContext<DatasetContextType | undefined>(undefined)

export function DatasetProvider({ children }: { children: ReactNode }) {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [activeDataset, setActiveDatasetState] = useState<Dataset | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshDatasets = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get('/api/datasets/list')
      if (response.data.success) {
        setDatasets(response.data.datasets)
        const active = response.data.datasets.find(
          (d: Dataset) => d.id === response.data.active_dataset_id
        )
        setActiveDatasetState(active || null)
      }
    } catch (error) {
      console.error('Error fetching datasets:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    refreshDatasets()
  }, [])

  const setActiveDataset = async (datasetId: string) => {
    try {
      await axios.post(`/api/datasets/${datasetId}/activate`)
      await refreshDatasets()
    } catch (error: any) {
      console.error('Error setting active dataset:', error)
      toast.error(error.response?.data?.detail || 'Failed to activate dataset')
      throw error
    }
  }

  const createDataset = async (name: string, description = '') => {
    try {
      const response = await axios.post('/api/datasets/create', { name, description })
      if (response.data.success) {
        await refreshDatasets()
        return response.data.dataset
      }
      throw new Error('Failed to create dataset')
    } catch (error: any) {
      console.error('Error creating dataset:', error)
      toast.error(error.response?.data?.detail || 'Failed to create dataset')
      throw error
    }
  }

  const deleteDataset = async (datasetId: string) => {
    try {
      await axios.delete(`/api/datasets/${datasetId}`)
      await refreshDatasets()
    } catch (error: any) {
      console.error('Error deleting dataset:', error)
      toast.error(error.response?.data?.detail || 'Failed to delete dataset')
      throw error
    }
  }

  return (
    <DatasetContext.Provider
      value={{
        datasets,
        activeDataset,
        isLoading,
        refreshDatasets,
        setActiveDataset,
        createDataset,
        deleteDataset,
      }}
    >
      {children}
    </DatasetContext.Provider>
  )
}

export function useDataset() {
  const context = useContext(DatasetContext)
  if (context === undefined) {
    throw new Error('useDataset must be used within a DatasetProvider')
  }
  return context
}


