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

type VisualSourceMode = 'auto' | 'youtube' | 'stock' | 'none'

export function BeatList({ beats, onBeatsUpdate, editable = false }: BeatListProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValues, setEditValues] = useState<Partial<Beat>>({})
  const [sourceMode, setSourceMode] = useState<VisualSourceMode>('auto')

  const getModeFromBeat = (beat: Partial<Beat>): VisualSourceMode => {
    const hasStock = !!beat.stock_keyword?.trim()
    const hasYoutube = !!beat.youtube_phrase?.trim()

    if (!hasStock && !hasYoutube) return 'none'
    if (hasStock && !hasYoutube) return 'stock'
    if (!hasStock && hasYoutube) return 'youtube'
    return 'auto'
  }

  const handleEdit = (beat: Beat) => {
    setEditingId(beat.id)
    setEditValues(beat)
    setSourceMode(getModeFromBeat(beat))
  }

  const handleSave = () => {
    if (!editingId || !onBeatsUpdate) return

    // Enforce mode by clearing irrelevant fields
    const finalValues = { ...editValues }
    
    if (sourceMode === 'none') {
      finalValues.stock_keyword = ''
      finalValues.youtube_phrase = ''
    } else if (sourceMode === 'youtube') {
      finalValues.stock_keyword = ''
    } else if (sourceMode === 'stock') {
      finalValues.youtube_phrase = ''
    }
    // 'auto' keeps both values (if user entered them)

    const updatedBeats = beats.map((b) => (b.id === editingId ? { ...b, ...finalValues } : b))

    onBeatsUpdate(updatedBeats)
    setEditingId(null)
    setEditValues({})
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditValues({})
  }

  const totalDuration = beats.reduce((sum, b) => sum + b.duration, 0)
  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60)
    const s = Math.floor(sec % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const getSourceDescription = (mode: VisualSourceMode) => {
    switch (mode) {
      case 'auto': return 'Try YouTube first, then fallback to Stock.'
      case 'youtube': return 'Only search YouTube. No fallback.'
      case 'stock': return 'Only search Stock footage. No YouTube.'
      case 'none': return 'No visuals. Timeline will be empty.'
    }
  }

  return (
    <div className="w-full">
      {/* Minimal Summary Header */}
      <div className="flex items-center justify-between py-4 border-b border-gray-200 mb-6 sticky top-0 bg-white/90 backdrop-blur-sm z-10">
        <div className="flex items-baseline gap-6">
          <div>
            <span className="text-3xl font-light tracking-tight text-gray-900">{beats.length}</span>
            <span className="text-sm font-medium text-gray-400 uppercase tracking-wider ml-2">Beats</span>
          </div>
          <div className="h-8 w-px bg-gray-200" />
          <div>
            <span className="text-3xl font-light tracking-tight text-gray-900">{formatDuration(totalDuration)}</span>
            <span className="text-sm font-medium text-gray-400 uppercase tracking-wider ml-2">Total Time</span>
          </div>
        </div>
      </div>

      {/* Beat list */}
      <div className="divide-y divide-gray-100">
        {beats.map((beat, index) => {
          // Determine display mode for View State
          const viewMode = getModeFromBeat(beat)

          return (
            <div 
              key={beat.id} 
              className={`
                group py-6 px-4 rounded-xl transition-all duration-200 -mx-4
                ${editingId === beat.id ? 'bg-white' : 'hover:bg-gray-50 active:bg-gray-100/50 active:scale-[0.998] cursor-default'}
              `}
            >
              {editingId === beat.id ? (
                // Edit mode (Inline Form)
                <div className="bg-white p-6 shadow-xl rounded-lg border border-gray-100 ring-1 ring-black/5">
                  <div className="space-y-6">
                    {/* Content Section */}
                    <div>
                      <label className="label">Script Content</label>
                      <textarea
                        value={editValues.text || ''}
                        onChange={(e) => setEditValues({ ...editValues, text: e.target.value })}
                        className="w-full p-3 bg-gray-50 border-0 rounded-md text-gray-900 focus:ring-2 focus:ring-black font-medium text-lg resize-none"
                        rows={3}
                        placeholder="Script text..."
                      />
                    </div>

                    {/* Source Selector */}
                    <div>
                       <label className="label">Visual Source</label>
                       <div className="flex bg-gray-100 p-1 rounded-lg mb-2">
                         {(['auto', 'youtube', 'stock', 'none'] as const).map((m) => (
                           <button
                            key={m}
                            onClick={() => setSourceMode(m)}
                            className={`flex-1 py-1.5 text-xs font-bold uppercase tracking-wider rounded-md transition-all ${
                              sourceMode === m 
                                ? 'bg-white text-black shadow-sm' 
                                : 'text-gray-400 hover:text-gray-600'
                            }`}
                           >
                             {m === 'youtube' ? 'YouTube Only' : m === 'stock' ? 'Stock Only' : m}
                           </button>
                         ))}
                       </div>
                       <p className="text-xs text-gray-500 font-medium">
                         {getSourceDescription(sourceMode)}
                       </p>
                    </div>

                    {/* Dynamic Inputs */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {(sourceMode === 'auto' || sourceMode === 'youtube') && (
                        <div>
                          <label className="label">YouTube Search Phrase</label>
                          <input
                            type="text"
                            value={editValues.youtube_phrase || ''}
                            onChange={(e) => setEditValues({ ...editValues, youtube_phrase: e.target.value })}
                            className="w-full p-2 bg-gray-50 border-0 rounded-md font-mono text-sm"
                            placeholder="e.g. nature documentary"
                          />
                        </div>
                      )}

                      {(sourceMode === 'auto' || sourceMode === 'stock') && (
                        <div>
                          <label className="label">Stock Keyword</label>
                          <input
                            type="text"
                            value={editValues.stock_keyword || ''}
                            onChange={(e) => setEditValues({ ...editValues, stock_keyword: e.target.value })}
                            className="w-full p-2 bg-gray-50 border-0 rounded-md font-mono text-sm"
                            placeholder="e.g. landscape"
                          />
                        </div>
                      )}
                      
                      {/* Duration is always visible */}
                      <div>
                        <label className="label">Duration (s)</label>
                        <input
                          type="number"
                          value={editValues.duration || 0}
                          onChange={(e) => setEditValues({ ...editValues, duration: parseFloat(e.target.value) })}
                          className="w-full p-2 bg-gray-50 border-0 rounded-md font-mono text-sm"
                          step="0.1"
                        />
                      </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-2">
                      <button 
                        onClick={handleCancel}
                        className="px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                      >
                        Cancel
                      </button>
                      <button 
                        onClick={handleSave}
                        className="btn-primary py-2 text-sm"
                      >
                        Save Changes
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                // View mode
                <div className="flex flex-col md:flex-row gap-6 items-start">
                  {/* Column 1: Index & Time */}
                  <div className="md:w-24 flex-shrink-0 flex md:flex-col items-center md:items-start gap-2 pt-1">
                    <span className="font-mono text-xs text-gray-300">#{String(index + 1).padStart(2, '0')}</span>
                    <span className="font-mono text-sm font-bold text-gray-900 bg-gray-100 px-2 py-0.5 rounded">
                      {beat.duration.toFixed(1)}s
                    </span>
                  </div>

                  {/* Column 2: Content */}
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      {beat.header && (
                        <h4 className="font-bold text-xs uppercase tracking-widest text-blue-600">
                          {beat.header}
                        </h4>
                      )}
                      {/* Source Badge */}
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded border ${
                        viewMode === 'none' ? 'bg-red-50 text-red-400 border-red-100' :
                        viewMode === 'auto' ? 'bg-gray-100 text-gray-500 border-gray-200' :
                        viewMode === 'youtube' ? 'bg-red-50 text-red-600 border-red-100' :
                        'bg-emerald-50 text-emerald-600 border-emerald-100'
                      }`}>
                        {viewMode === 'none' ? 'NO B-ROLL' : viewMode}
                      </span>
                    </div>

                    <p className="text-lg text-gray-900 leading-relaxed font-medium">
                      {beat.text}
                    </p>
                    
                    {/* Metadata Tags */}
                    {viewMode !== 'none' && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {beat.stock_keyword && (viewMode === 'auto' || viewMode === 'stock') && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-50 text-gray-500 border border-gray-100 font-mono">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5"></span>
                            {beat.stock_keyword}
                          </span>
                        )}
                        {beat.youtube_phrase && (viewMode === 'auto' || viewMode === 'youtube') && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-50 text-gray-500 border border-gray-100 font-mono">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-400 mr-1.5"></span>
                            {beat.youtube_phrase}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Column 3: Actions */}
                  {editable && (
                    <div className="md:w-20 flex-shrink-0 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => handleEdit(beat)}
                        className="text-sm font-medium text-gray-400 hover:text-black hover:underline underline-offset-4 decoration-gray-300"
                      >
                        Edit
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}


