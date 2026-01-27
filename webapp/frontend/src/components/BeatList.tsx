/**
 * Beat list display component
 *
 * Shows parsed beats from the script with editing capabilities
 */

import { useState, useEffect } from 'react'
import type { Beat } from '../types/models'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Clock, 
  Youtube, 
  Image, 
  Zap, 
  Slash, 
  CheckCircle2, 
  Edit3,
  Check,
  Film,
  RefreshCcw,
  Play,
  Maximize2
} from 'lucide-react'
import { refreshBeatAsset, getMediaUrl } from '../services/api'

interface BeatListProps {
  sessionId: string
  beats: Beat[]
  assets?: Record<string, string>
  onBeatsUpdate?: (beats: Beat[]) => void
  editable?: boolean
  reviewedIds?: Set<string>
  onToggleReviewed?: (id: string) => void
}

type VisualSourceMode = 'auto' | 'youtube' | 'stock' | 'none'

export function BeatList({ 
  sessionId,
  beats, 
  assets = {},
  onBeatsUpdate, 
  editable = false,
  reviewedIds = new Set(),
  onToggleReviewed
}: BeatListProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [lightboxId, setLightboxId] = useState<string | null>(null)
  const [refreshingIds, setRefreshingIds] = useState<Set<string>>(new Set())
  const [editValues, setEditValues] = useState<Partial<Beat>>({})
  const [sourceMode, setSourceMode] = useState<VisualSourceMode>('auto')

  const handleMarkAllReviewed = () => {
    if (!onToggleReviewed) return
    beats.forEach(beat => {
      if (!reviewedIds.has(beat.id)) {
        onToggleReviewed(beat.id)
      }
    })
  }

  const handleRefresh = async (beatId: string) => {
    setRefreshingIds(prev => new Set(prev).add(beatId))
    try {
      await refreshBeatAsset(sessionId, beatId)
      // The parent will poll for status/state updates
    } catch (err) {
      console.error("Failed to refresh beat", err)
    } finally {
      // Keep refreshing state for a bit to show activity
      setTimeout(() => {
        setRefreshingIds(prev => {
          const next = new Set(prev)
          next.delete(beatId)
          return next
        })
      }, 2000)
    }
  }

  const getModeFromBeat = (beat: Partial<Beat>): VisualSourceMode => {
    const hasStock = !!beat.stock_keyword?.trim()
    const hasYoutube = !!beat.youtube_phrase?.trim()

    if (!hasStock && !hasYoutube) return 'none'
    if (hasStock && !hasYoutube) return 'stock'
    if (!hasStock && hasYoutube) return 'youtube'
    return 'auto'
  }

  const handleSkip = (beat: Beat) => {
    if (!onBeatsUpdate) return

    const updatedBeats = beats.map((b) => {
      if (b.id === beat.id) {
        return { ...b, stock_keyword: '', youtube_phrase: '' }
      }
      return b
    })

    onBeatsUpdate(updatedBeats)
    
    if (onToggleReviewed && !reviewedIds.has(beat.id)) {
      onToggleReviewed(beat.id)
    }
  }

  const handleEdit = (beat: Beat) => {
    setEditingId(beat.id)
    setEditValues(beat)
    setSourceMode(getModeFromBeat(beat))
  }

  const handleSave = () => {
    if (!editingId || !onBeatsUpdate) return

    const finalValues = { ...editValues }
    if (sourceMode === 'none') {
      finalValues.stock_keyword = ''
      finalValues.youtube_phrase = ''
    } else if (sourceMode === 'youtube') {
      finalValues.stock_keyword = ''
    } else if (sourceMode === 'stock') {
      finalValues.youtube_phrase = ''
    }

    const updatedBeats = beats.map((b) => (b.id === editingId ? { ...b, ...finalValues } : b))

    onBeatsUpdate(updatedBeats)
    setEditingId(null)
    setEditValues({})
    
    if (onToggleReviewed && !reviewedIds.has(editingId)) {
      onToggleReviewed(editingId)
    }
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

  return (
    <div className="w-full">
      {/* Refined Summary Header */}
      <div className="flex items-center gap-10 py-6 border-b border-gray-100 mb-8 sticky top-16 bg-white/90 backdrop-blur-md z-20">
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 text-gray-900">
            <span className="text-xl font-bold leading-none">{beats.length}</span>
            <Film size={14} className="text-gray-400" />
          </div>
          <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Segments</span>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 text-gray-900">
            <span className="text-xl font-bold leading-none">{formatDuration(totalDuration)}</span>
            <Clock size={14} className="text-gray-400" />
          </div>
          <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Duration</span>
        </div>
        <div className="flex flex-col ml-auto">
          <div className="flex items-center gap-1.5 text-blue-600">
            <span className="text-xl font-bold leading-none">{reviewedIds.size}/{beats.length}</span>
            <CheckCircle2 size={14} />
          </div>
          <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Reviewed</span>
        </div>
        
        {reviewedIds.size < beats.length && (
          <button 
            onClick={handleMarkAllReviewed}
            className="flex items-center gap-2 px-4 py-2 bg-gray-50 hover:bg-gray-100 text-[10px] font-black uppercase tracking-widest text-gray-500 hover:text-gray-900 rounded-lg transition-all border border-gray-100"
          >
            Mark all reviewed
          </button>
        )}
      </div>

      {/* Beat list */}
      <div className="space-y-3">
        {beats.map((beat, index) => {
          const viewMode = getModeFromBeat(beat)
          const isReviewed = reviewedIds.has(beat.id)
          const isEditing = editingId === beat.id

          return (
            <motion.div 
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              key={beat.id} 
              className={`
                relative group rounded-2xl transition-all duration-300
                ${isEditing ? 'bg-white ring-1 ring-gray-200 shadow-xl p-6 z-10' : 'bg-white p-4 border border-gray-100 hover:border-gray-200'}
                ${isReviewed && !isEditing ? 'bg-gray-50/50' : ''}
              `}
            >
              <AnimatePresence mode="wait">
                {isEditing ? (
                  // ... edit mode remains largely the same but with better styling ...
                  <motion.div 
                    key="edit"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-6"
                  >
                    <div className="flex items-center justify-between">
                       <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                         <Edit3 size={16} className="text-blue-500" />
                         Edit Segment #{index + 1}
                       </h3>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                       <div className="space-y-5">
                          <div>
                            <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">Script Content</label>
                            <textarea
                              value={editValues.text || ''}
                              onChange={(e) => setEditValues({ ...editValues, text: e.target.value })}
                              className="w-full p-4 bg-gray-50 border border-gray-100 rounded-xl text-sm leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-500/10 resize-none"
                              rows={3}
                            />
                          </div>
                          
                          <div>
                            <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">Duration (s)</label>
                            <div className="flex items-center gap-4">
                              <input
                                type="range"
                                min="0.5"
                                max="30"
                                step="0.5"
                                value={editValues.duration || 0}
                                onChange={(e) => setEditValues({ ...editValues, duration: parseFloat(e.target.value) })}
                                className="flex-grow accent-blue-600 h-1 bg-gray-100 rounded-full"
                              />
                              <span className="font-mono text-sm font-bold w-12 text-center">{editValues.duration}s</span>
                            </div>
                          </div>
                       </div>

                       <div className="space-y-5">
                          <div>
                            <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">Visual Source</label>
                            <div className="grid grid-cols-4 gap-1 bg-gray-100 p-1 rounded-xl">
                              {(['auto', 'youtube', 'stock', 'none'] as const).map((m) => {
                                const Icon = m === 'youtube' ? Youtube : m === 'stock' ? Image : m === 'auto' ? Zap : Slash
                                return (
                                  <button
                                    key={m}
                                    onClick={() => setSourceMode(m)}
                                    className={`flex flex-col items-center gap-1 py-2 text-[9px] font-bold uppercase tracking-wider rounded-lg transition-all ${
                                      sourceMode === m 
                                        ? 'bg-white text-blue-600 shadow-sm' 
                                        : 'text-gray-400 hover:text-gray-600'
                                    }`}
                                  >
                                    <Icon size={12} />
                                    {m}
                                  </button>
                                )
                              })}
                            </div>
                          </div>

                          <div className="space-y-3">
                            {(sourceMode === 'auto' || sourceMode === 'youtube') && (
                              <div>
                                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">YouTube Phrase</label>
                                <input
                                  type="text"
                                  value={editValues.youtube_phrase || ''}
                                  onChange={(e) => setEditValues({ ...editValues, youtube_phrase: e.target.value })}
                                  className="w-full px-3 py-2 bg-gray-50 border border-gray-100 rounded-lg text-xs font-mono"
                                  placeholder="Keywords..."
                                />
                              </div>
                            )}

                            {(sourceMode === 'auto' || sourceMode === 'stock') && (
                              <div>
                                <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5 block">Stock Keywords</label>
                                <input
                                  type="text"
                                  value={editValues.stock_keyword || ''}
                                  onChange={(e) => setEditValues({ ...editValues, stock_keyword: e.target.value })}
                                  className="w-full px-3 py-2 bg-gray-50 border border-gray-100 rounded-lg text-xs font-mono"
                                  placeholder="Keywords..."
                                />
                              </div>
                            )}
                          </div>
                       </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-2">
                      <button onClick={handleCancel} className="px-4 py-2 text-xs font-bold text-gray-400 hover:text-gray-900 transition-colors">Discard</button>
                      <button onClick={handleSave} className="bg-blue-600 text-white py-2 px-6 rounded-lg text-xs font-bold hover:bg-blue-700 transition-all flex items-center gap-2 shadow-sm">
                        Apply changes
                        <Check size={14} />
                      </button>
                    </div>
                  </motion.div>
                ) : (
                  <div className="flex items-stretch gap-6">
                    <button 
                      onClick={() => onToggleReviewed?.(beat.id)}
                      className={`
                        w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 border flex-shrink-0 mt-1
                        ${isReviewed 
                          ? 'bg-blue-50 border-blue-100 text-blue-600' 
                          : 'bg-white border-gray-100 text-gray-200 hover:border-gray-200 shadow-sm'}
                      `}
                    >
                      <CheckCircle2 size={18} strokeWidth={isReviewed ? 3 : 2} />
                    </button>

                    <div className="flex-grow min-w-0 py-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono text-[10px] font-bold text-gray-300">#{String(index + 1).padStart(2, '0')}</span>
                        {beat.header && (
                          <span className="text-[9px] font-bold uppercase tracking-wider text-blue-500 bg-blue-50 px-2 py-0.5 rounded-full">
                            {beat.header}
                          </span>
                        )}
                        <span className="text-[9px] font-bold text-gray-400 flex items-center gap-1 px-2 py-0.5 bg-gray-50 rounded-full">
                          <Clock size={10} />
                          {beat.duration.toFixed(1)}s
                        </span>
                        <div className={`
                          flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider border
                          ${viewMode === 'none' ? 'bg-gray-50 text-gray-400 border-gray-100' :
                            viewMode === 'auto' ? 'bg-blue-50 text-blue-500 border-blue-100' :
                            viewMode === 'youtube' ? 'bg-red-50 text-red-500 border-red-100' :
                            'bg-emerald-50 text-emerald-600 border-emerald-100'}
                        `}>
                          {viewMode}
                        </div>
                      </div>

                      <p className={`text-sm leading-relaxed transition-all duration-300 mb-4 ${isReviewed ? 'text-gray-500' : 'text-gray-900 font-medium'}`}>
                        {beat.text}
                      </p>
                      
                      {/* Asset Preview Section */}
                      {viewMode !== 'none' && (
                        <div className="relative rounded-xl overflow-hidden bg-gray-50 border border-gray-100 max-w-sm">
                          {assets[beat.id] ? (
                            <div className="relative group/asset">
                              <video 
                                src={getMediaUrl(sessionId, assets[beat.id])} 
                                className="w-full aspect-video object-cover"
                                preload="metadata"
                                onMouseOver={(e) => e.currentTarget.play()}
                                onMouseOut={(e) => {
                                  e.currentTarget.pause()
                                  e.currentTarget.currentTime = 0
                                }}
                                muted
                                loop
                              />
                              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/asset:opacity-100 transition-opacity flex items-center justify-center gap-4">
                                <Play className="text-white fill-white" size={24} />
                                <button 
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    setLightboxId(beat.id)
                                  }}
                                  className="p-2 bg-white/20 hover:bg-white/40 backdrop-blur-md rounded-full text-white transition-all"
                                >
                                  <Maximize2 size={16} />
                                </button>
                              </div>
                              <button 
                                onClick={() => handleRefresh(beat.id)}
                                disabled={refreshingIds.has(beat.id)}
                                className="absolute top-2 right-2 p-1.5 bg-white/90 backdrop-blur-md rounded-lg shadow-sm text-gray-600 hover:text-blue-600 transition-all active:scale-95 disabled:opacity-50"
                                title="Refresh Footage"
                              >
                                <RefreshCcw size={12} className={refreshingIds.has(beat.id) ? 'animate-spin' : ''} />
                              </button>
                            </div>
                          ) : (
                            <div className="aspect-video flex flex-col items-center justify-center gap-2 p-6 text-center">
                              <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                                {refreshingIds.has(beat.id) ? (
                                  <RefreshCcw size={14} className="text-blue-500 animate-spin" />
                                ) : (
                                  <Film size={14} className="text-gray-300" />
                                )}
                              </div>
                              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                                {refreshingIds.has(beat.id) ? 'Downloading...' : 'No Preview Yet'}
                              </p>
                              {!refreshingIds.has(beat.id) && (
                                <button 
                                  onClick={() => handleRefresh(beat.id)}
                                  className="text-[9px] font-black text-blue-500 uppercase tracking-tighter hover:underline"
                                >
                                  Try fetching now
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                      
                      {!isReviewed && viewMode !== 'none' && (
                        <div className="flex flex-wrap gap-1.5 mt-4">
                          {beat.youtube_phrase && (viewMode === 'auto' || viewMode === 'youtube') && (
                            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-100 text-[10px] font-mono font-semibold text-gray-500">
                              <Youtube size={12} />
                              {beat.youtube_phrase}
                            </span>
                          )}
                          {beat.stock_keyword && (viewMode === 'auto' || viewMode === 'stock') && (
                            <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-gray-100 text-[10px] font-mono font-semibold text-gray-500">
                              <Image size={12} />
                              {beat.stock_keyword}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {editable && (
                      <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-all duration-200 border-l border-gray-100 pl-4 py-1">
                        <button
                          onClick={() => handleEdit(beat)}
                          className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-all"
                          title="Edit Segment"
                        >
                          <Edit3 size={14} />
                        </button>
                        
                        {viewMode !== 'none' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleSkip(beat)
                            }}
                            className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all"
                            title="Skip Visuals (None)"
                          >
                            <Slash size={14} />
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>

      {/* Fullscreen Lightbox */}
      <AnimatePresence>
        {lightboxId && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex flex-col items-center justify-center p-8 md:p-20"
            onClick={() => setLightboxId(null)}
          >
            <button 
              className="absolute top-8 right-8 text-white/40 hover:text-white transition-colors"
              onClick={() => setLightboxId(null)}
            >
              <Slash size={32} strokeWidth={1} />
            </button>
            
            <div className="w-full max-w-6xl aspect-video rounded-3xl overflow-hidden shadow-2xl border border-white/10 bg-black" onClick={e => e.stopPropagation()}>
              <video 
                src={getMediaUrl(sessionId, assets[lightboxId] || '')} 
                className="w-full h-full object-contain"
                controls
                autoPlay
              />
            </div>
            
            <div className="mt-12 text-center space-y-2">
              <p className="text-white font-medium text-lg">
                {beats.find(b => b.id === lightboxId)?.text}
              </p>
              <p className="text-white/40 font-mono text-xs uppercase tracking-[0.2em]">
                {assets[lightboxId]?.split(/[\\/]/).pop()}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
