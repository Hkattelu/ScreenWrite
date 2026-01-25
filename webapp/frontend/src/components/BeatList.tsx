/**
 * Beat list display component
 *
 * Shows parsed beats from the script with editing capabilities
 */

import { useState } from 'react'
import type { Beat } from '../types/models'

interface BeatListProps {
  beats: Beat[]
  onBeatsUpdate?: (beats: Beat[]) => void
  editable?: boolean
}

export function BeatList({ beats, onBeatsUpdate, editable = false }: BeatListProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValues, setEditValues] = useState<Partial<Beat>>({})

  const handleEdit = (beat: Beat) => {
    setEditingId(beat.id)
    setEditValues(beat)
  }

  const handleSave = () => {
    if (!editingId || !onBeatsUpdate) return

    const updatedBeats = beats.map((b) => (b.id === editingId ? { ...b, ...editValues } : b))

    onBeatsUpdate(updatedBeats)
    setEditingId(null)
    setEditValues({})
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditValues({})
  }

  const totalDuration = beats.reduce((sum, b) => sum + b.duration, 0)

  return (
    <div className="w-full">
      {/* Summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-500">{beats.length}</div>
          <div className="text-gray-600">Beats</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-500">{totalDuration.toFixed(1)}</div>
          <div className="text-gray-600">Seconds</div>
        </div>
        <div className="card text-center">
          <div className="text-3xl font-bold text-blue-500">{(totalDuration / 60).toFixed(1)}</div>
          <div className="text-gray-600">Minutes</div>
        </div>
      </div>

      {/* Beat list */}
      <div className="space-y-4">
        {beats.map((beat, index) => (
          <div key={beat.id} className="card border-l-4 border-l-blue-500">
            {editingId === beat.id ? (
              // Edit mode
              <div className="space-y-4">
                <div>
                  <label className="label">Beat Text</label>
                  <textarea
                    value={editValues.text || ''}
                    onChange={(e) => setEditValues({ ...editValues, text: e.target.value })}
                    className="input w-full"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="label">Duration (seconds)</label>
                    <input
                      type="number"
                      value={editValues.duration || 0}
                      onChange={(e) => setEditValues({ ...editValues, duration: parseFloat(e.target.value) })}
                      className="input w-full"
                      step="0.1"
                    />
                  </div>
                  <div>
                    <label className="label">Stock Keyword</label>
                    <input
                      type="text"
                      value={editValues.stock_keyword || ''}
                      onChange={(e) => setEditValues({ ...editValues, stock_keyword: e.target.value })}
                      className="input w-full"
                    />
                  </div>
                </div>

                <div>
                  <label className="label">YouTube Search Phrase</label>
                  <input
                    type="text"
                    value={editValues.youtube_phrase || ''}
                    onChange={(e) => setEditValues({ ...editValues, youtube_phrase: e.target.value })}
                    className="input w-full"
                  />
                </div>

                <div className="flex gap-2 justify-end">
                  <button onClick={handleCancel} className="btn-secondary">
                    Cancel
                  </button>
                  <button onClick={handleSave} className="btn-primary">
                    Save
                  </button>
                </div>
              </div>
            ) : (
              // View mode
              <div>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-800">
                      Beat {index + 1}
                      {beat.header && <span className="text-gray-500 ml-2">• {beat.header}</span>}
                    </h3>
                    <p className="text-gray-600 mt-2">{beat.text}</p>
                  </div>
                  <span className="text-2xl font-bold text-blue-500 ml-4">{beat.duration.toFixed(1)}s</span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm mt-4 pt-4 border-t border-gray-200">
                  <div>
                    <span className="text-gray-500">Stock Keyword:</span>
                    <p className="font-medium text-gray-800">{beat.stock_keyword}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">YouTube Search:</span>
                    <p className="font-medium text-gray-800">{beat.youtube_phrase}</p>
                  </div>
                </div>

                {editable && (
                  <button
                    onClick={() => handleEdit(beat)}
                    className="mt-4 text-blue-500 hover:text-blue-700 text-sm font-medium"
                  >
                    Edit Beat
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
