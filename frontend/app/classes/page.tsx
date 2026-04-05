'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useDataset } from '@/contexts/DatasetContext'
import { ArrowLeft, Plus, Trash2, ChevronUp, ChevronDown, Save, Tags, Loader2, Palette, ListTree } from 'lucide-react'

interface DetectionClassRow {
  name: string
  display_name: string
  color: string
  description: string
}

interface ColorAttributeRow {
  name: string
  display_name: string
  color: string
  description: string
}

interface AdditionalAttributeRow {
  name: string
  display_name: string
  description: string
}

export default function ClassesPage() {
  const { activeDataset, isLoading: dsLoading } = useDataset()
  const [rows, setRows] = useState<DetectionClassRow[]>([])
  const [colorRows, setColorRows] = useState<ColorAttributeRow[]>([])
  const [additionalRows, setAdditionalRows] = useState<AdditionalAttributeRow[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const fetchLabels = useCallback(async () => {
    if (!activeDataset) {
      setRows([])
      setColorRows([])
      setAdditionalRows([])
      setLoading(false)
      return
    }
    try {
      setLoading(true)
      const res = await axios.get(`/api/datasets/${activeDataset.id}/classes`)
      if (res.data.success) {
        setRows(res.data.detection_classes || [])
        setColorRows(res.data.color_attributes || [])
        setAdditionalRows(res.data.additional_attributes || [])
      }
    } catch (e) {
      console.error(e)
      toast.error('Failed to load dataset labels')
    } finally {
      setLoading(false)
    }
  }, [activeDataset])

  useEffect(() => {
    fetchLabels()
  }, [fetchLabels])

  const updateRow = (i: number, field: keyof DetectionClassRow, value: string) => {
    setRows((prev) => prev.map((r, j) => (j === i ? { ...r, [field]: value } : r)))
  }

  const updateColorRow = (i: number, field: keyof ColorAttributeRow, value: string) => {
    setColorRows((prev) => prev.map((r, j) => (j === i ? { ...r, [field]: value } : r)))
  }

  const updateAdditionalRow = (i: number, field: keyof AdditionalAttributeRow, value: string) => {
    setAdditionalRows((prev) => prev.map((r, j) => (j === i ? { ...r, [field]: value } : r)))
  }

  const addRow = () => {
    setRows((prev) => [
      ...prev,
      {
        name: `class_${prev.length + 1}`,
        display_name: `Class ${prev.length + 1}`,
        color: '#6B7280',
        description: '',
      },
    ])
  }

  const addColorRow = () => {
    setColorRows((prev) => [
      ...prev,
      {
        name: `color_${prev.length + 1}`,
        display_name: `Color ${prev.length + 1}`,
        color: '#6B7280',
        description: '',
      },
    ])
  }

  const addAdditionalRow = () => {
    setAdditionalRows((prev) => [
      ...prev,
      {
        name: `tag_${prev.length + 1}`,
        display_name: `Tag ${prev.length + 1}`,
        description: '',
      },
    ])
  }

  const removeRow = (i: number) => {
    if (rows.length <= 1) {
      toast.error('At least one detection class is required')
      return
    }
    setRows((prev) => prev.filter((_, j) => j !== i))
  }

  const removeColorRow = (i: number) => {
    setColorRows((prev) => prev.filter((_, j) => j !== i))
  }

  const removeAdditionalRow = (i: number) => {
    setAdditionalRows((prev) => prev.filter((_, j) => j !== i))
  }

  const moveClass = (i: number, dir: -1 | 1) => {
    const j = i + dir
    if (j < 0 || j >= rows.length) return
    setRows((prev) => {
      const next = [...prev]
      const t = next[i]
      next[i] = next[j]
      next[j] = t
      return next
    })
  }

  const moveColors = (i: number, dir: -1 | 1) => {
    const j = i + dir
    if (j < 0 || j >= colorRows.length) return
    setColorRows((prev) => {
      const next = [...prev]
      const t = next[i]
      next[i] = next[j]
      next[j] = t
      return next
    })
  }

  const moveAdditional = (i: number, dir: -1 | 1) => {
    const j = i + dir
    if (j < 0 || j >= additionalRows.length) return
    setAdditionalRows((prev) => {
      const next = [...prev]
      const t = next[i]
      next[i] = next[j]
      next[j] = t
      return next
    })
  }

  const save = async () => {
    if (!activeDataset) return
    setSaving(true)
    try {
      const trimmedClasses = rows.map((r) => ({
        ...r,
        name: r.name.trim(),
        display_name: r.display_name.trim(),
        description: r.description.trim(),
      }))
      const trimmedColors = colorRows.map((r) => ({
        ...r,
        name: r.name.trim(),
        display_name: r.display_name.trim(),
        description: r.description.trim(),
      }))
      const trimmedAdd = additionalRows.map((r) => ({
        ...r,
        name: r.name.trim(),
        display_name: r.display_name.trim(),
        description: r.description.trim(),
      }))
      await axios.put(`/api/datasets/${activeDataset.id}/classes`, {
        detection_classes: trimmedClasses,
        color_attributes: trimmedColors,
        additional_attributes: trimmedAdd,
      })
      toast.success('Detection classes and attributes saved')
      await fetchLabels()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      const d = err.response?.data?.detail
      toast.error(typeof d === 'string' ? d : 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  if (dsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-10 h-10 animate-spin text-primary-600" />
      </div>
    )
  }

  if (!activeDataset) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-2xl mx-auto card text-center py-12">
          <Tags className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">No active dataset</h1>
          <p className="text-gray-600 mb-6">Create or activate a dataset from the home page trainer flow.</p>
          <Link href="/" className="btn-primary inline-flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back home
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-start gap-3">
              <Tags className="w-8 h-8 text-primary-600 shrink-0 mt-1" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Detection classes</h1>
                <p className="text-gray-600 mt-1">
                  Dataset: <span className="font-medium text-gray-800">{activeDataset.name}</span>
                </p>
                <p className="text-sm text-gray-500 mt-2 max-w-2xl">
                  One place to edit <strong>YOLO labels</strong> (slug, names, box color, notes) and the
                  optional <strong>color</strong> / <strong>extra</strong> tags available on every box in
                  Annotate. Save once at the top.
                </p>
                <nav className="flex flex-wrap gap-2 mt-4" aria-label="Jump to subsection">
                  <a
                    href="#subsection-yolo"
                    className="inline-flex items-center rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-50"
                  >
                    YOLO labels
                  </a>
                  <a
                    href="#section-color-tags"
                    className="inline-flex items-center rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-50"
                  >
                    Color tags
                  </a>
                  <a
                    href="#section-extra-tags"
                    className="inline-flex items-center rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-50"
                  >
                    Extra attributes
                  </a>
                </nav>
              </div>
            </div>
            <button
              type="button"
              onClick={save}
              disabled={saving || loading}
              className="btn-primary flex items-center justify-center gap-2 shrink-0"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-10 h-10 animate-spin text-primary-600" />
          </div>
        ) : (
          <section
            id="section-detection"
            className="card border-2 border-primary-100 shadow-md scroll-mt-28 space-y-10"
          >
            <div id="subsection-yolo" className="scroll-mt-32">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Tags className="w-5 h-5 text-primary-600" />
                  YOLO detection labels ({rows.length})
                </h2>
                <button type="button" onClick={addRow} className="btn-secondary text-sm flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add class
                </button>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                Each row is trained as one YOLO class. Edit <strong>slug</strong> (id in files),{' '}
                <strong>display name</strong>, <strong>box outline color</strong> in Annotate, and{' '}
                <strong>description</strong> (notes for your team). Reorder with arrows — that changes
                class indices; slugs on existing boxes are remapped when you save.
              </p>
              <div className="space-y-3">
                {rows.map((row, i) => (
                  <div
                    key={`c-${i}-${row.name}`}
                    className="rounded-lg border border-gray-200 bg-white p-4 flex flex-col lg:flex-row gap-4 lg:items-start"
                  >
                    <div className="flex items-center gap-2 text-sm text-gray-500 shrink-0 w-24">
                      <span className="font-mono font-medium text-primary-700">#{i}</span>
                      <div className="flex flex-col gap-1">
                        <button
                          type="button"
                          onClick={() => moveClass(i, -1)}
                          disabled={i === 0}
                          className="p-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                          aria-label="Move up"
                        >
                          <ChevronUp className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => moveClass(i, 1)}
                          disabled={i === rows.length - 1}
                          className="p-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                          aria-label="Move down"
                        >
                          <ChevronDown className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 min-w-0">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Slug</label>
                        <input
                          className="input-field w-full text-sm font-mono"
                          value={row.name}
                          onChange={(e) => updateRow(i, 'name', e.target.value)}
                          spellCheck={false}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Display name</label>
                        <input
                          className="input-field w-full text-sm"
                          value={row.display_name}
                          onChange={(e) => updateRow(i, 'display_name', e.target.value)}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Box color (Annotate)</label>
                        <div className="flex gap-2">
                          <input
                            type="color"
                            className="h-10 w-14 rounded border border-gray-300 cursor-pointer"
                            value={row.color}
                            onChange={(e) => updateRow(i, 'color', e.target.value)}
                          />
                          <input
                            className="input-field flex-1 text-sm font-mono"
                            value={row.color}
                            onChange={(e) => updateRow(i, 'color', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                          Description / attributes (notes)
                        </label>
                        <textarea
                          className="input-field w-full text-sm min-h-[4rem] resize-y"
                          value={row.description}
                          onChange={(e) => updateRow(i, 'description', e.target.value)}
                          placeholder="e.g. adult stage, visible eggs, …"
                        />
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeRow(i)}
                      className="btn-danger text-sm flex items-center gap-1 shrink-0 self-start"
                      disabled={rows.length <= 1}
                    >
                      <Trash2 className="w-4 h-4" />
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <hr className="border-gray-200" />

            <div id="section-color-tags" className="scroll-mt-32">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <h3 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                  <Palette className="w-5 h-5 text-rose-600" />
                  Optional color tags ({colorRows.length})
                </h3>
                <button
                  type="button"
                  onClick={addColorRow}
                  className="btn-secondary text-sm flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add color tag
                </button>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                Part of this dataset’s detection setup: one optional color per box in Annotate. Not YOLO
                classes. Empty list hides the color picker.
              </p>
              <div className="space-y-3">
                {colorRows.length === 0 && (
                  <p className="text-sm text-gray-500 italic rounded-lg border border-dashed border-gray-200 p-4 bg-gray-50">
                    No color tags — add one above, or leave empty to hide color in Annotate.
                  </p>
                )}
                {colorRows.map((row, i) => (
                  <div
                    key={`col-${i}-${row.name}`}
                    className="rounded-lg border border-gray-200 bg-white p-4 flex flex-col lg:flex-row gap-4 lg:items-start"
                  >
                    <div className="flex items-center gap-2 text-sm text-gray-500 shrink-0 w-24">
                      <span className="font-mono text-gray-400">{i + 1}</span>
                      <div className="flex flex-col gap-1">
                        <button
                          type="button"
                          onClick={() => moveColors(i, -1)}
                          disabled={i === 0}
                          className="p-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                        >
                          <ChevronUp className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => moveColors(i, 1)}
                          disabled={i === colorRows.length - 1}
                          className="p-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                        >
                          <ChevronDown className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 min-w-0">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Slug</label>
                        <input
                          className="input-field w-full text-sm font-mono"
                          value={row.name}
                          onChange={(e) => updateColorRow(i, 'name', e.target.value)}
                          spellCheck={false}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Display name</label>
                        <input
                          className="input-field w-full text-sm"
                          value={row.display_name}
                          onChange={(e) => updateColorRow(i, 'display_name', e.target.value)}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Swatch</label>
                        <div className="flex gap-2">
                          <input
                            type="color"
                            className="h-10 w-14 rounded border border-gray-300 cursor-pointer"
                            value={row.color}
                            onChange={(e) => updateColorRow(i, 'color', e.target.value)}
                          />
                          <input
                            className="input-field flex-1 text-sm font-mono"
                            value={row.color}
                            onChange={(e) => updateColorRow(i, 'color', e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                        <input
                          className="input-field w-full text-sm"
                          value={row.description}
                          onChange={(e) => updateColorRow(i, 'description', e.target.value)}
                        />
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeColorRow(i)}
                      className="btn-danger text-sm flex items-center gap-1 shrink-0 self-start"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <hr className="border-gray-200" />

            <div id="section-extra-tags" className="scroll-mt-32">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                <h3 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                  <ListTree className="w-5 h-5 text-violet-600" />
                  Optional extra attributes ({additionalRows.length})
                </h3>
                <button
                  type="button"
                  onClick={addAdditionalRow}
                  className="btn-secondary text-sm flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add tag
                </button>
              </div>
              <p className="text-sm text-gray-500 mb-4">
                Multi-select tags per box (e.g. berried, healthy). Same page as your classes — not separate
                YOLO classes.
              </p>
              <div className="space-y-3">
                {additionalRows.length === 0 && (
                  <p className="text-sm text-gray-500 italic rounded-lg border border-dashed border-gray-200 p-4 bg-gray-50">
                    No extra tags — add tags here to show them in Annotate.
                  </p>
                )}
                {additionalRows.map((row, i) => (
                  <div
                    key={`a-${i}-${row.name}`}
                    className="rounded-lg border border-gray-200 bg-white p-4 flex flex-col lg:flex-row gap-4 lg:items-start"
                  >
                    <div className="flex items-center gap-2 text-sm text-gray-500 shrink-0 w-24">
                      <span className="font-mono text-gray-400">{i + 1}</span>
                      <div className="flex flex-col gap-1">
                        <button
                          type="button"
                          onClick={() => moveAdditional(i, -1)}
                          disabled={i === 0}
                          className="p-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                        >
                          <ChevronUp className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => moveAdditional(i, 1)}
                          disabled={i === additionalRows.length - 1}
                          className="p-1 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                        >
                          <ChevronDown className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 min-w-0">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Slug</label>
                        <input
                          className="input-field w-full text-sm font-mono"
                          value={row.name}
                          onChange={(e) => updateAdditionalRow(i, 'name', e.target.value)}
                          spellCheck={false}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Display name</label>
                        <input
                          className="input-field w-full text-sm"
                          value={row.display_name}
                          onChange={(e) => updateAdditionalRow(i, 'display_name', e.target.value)}
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
                        <textarea
                          className="input-field w-full text-sm min-h-[3rem] resize-y"
                          value={row.description}
                          onChange={(e) => updateAdditionalRow(i, 'description', e.target.value)}
                        />
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeAdditionalRow(i)}
                      className="btn-danger text-sm flex items-center gap-1 shrink-0 self-start"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        <div className="flex justify-between pt-8 border-t border-gray-200 mt-8">
          <Link href="/" className="btn-secondary inline-flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Home
          </Link>
          <Link href="/annotate" className="btn-primary">
            Annotate →
          </Link>
        </div>
      </div>
    </div>
  )
}
