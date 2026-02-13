/**
 * Beat list display component
 *
 * Shows parsed beats from the script with editing capabilities
 */

import { useState, useRef, useEffect } from 'react'
import type { Beat } from '../types/models'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Slash, 
  CheckCircle2, 
  Edit3
} from 'lucide-react'
import { getMediaUrl, type AssetCandidate } from '../services/api'
import { BeatAsset } from './BeatAsset'
import type { DownloadProgress } from '../types/models'

interface BeatListProps {
  sessionId: string
  beats: Beat[]
  assets?: Record<string, string | string[]>
  downloadProgress?: Record<string, DownloadProgress>
  onBeatsUpdate?: (beats: Beat[]) => Promise<void> | void
  onAssetsUpdate?: (assets: Record<string, string | string[]>) => void
  onDownloadAsset?: (beatId: string, candidate: AssetCandidate, updateBeatQuery?: boolean) => Promise<void>
  editable?: boolean
  reviewedIds?: Set<string>
  onToggleReviewed?: (id: string) => void
  onToggleAllReviewed?: () => void
}

type VisualSourceMode = 'auto' | 'youtube' | 'stock' | 'none'

export function BeatList({
  sessionId,
  beats, 
  assets = {},
  downloadProgress = {},
  onBeatsUpdate, 
  onAssetsUpdate,
  onDownloadAsset,
  editable = false,
  reviewedIds = new Set(),
  onToggleReviewed,
  onToggleAllReviewed
}: BeatListProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [lightboxId, setLightboxId] = useState<string | null>(null)
  const [lightboxPath, setLightboxPath] = useState<string | null>(null)
  const [savingIds, setSavingIds] = useState<Set<string>>(new Set())
  const [editValues, setEditValues] = useState<Partial<Beat>>({})
  const [sourceMode, setSourceMode] = useState<VisualSourceMode>('auto')
  const listRef = useRef<HTMLDivElement>(null)


  // Keyboard navigation for ArrowUp/ArrowDown
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (editingId) return // Don't interfere while editing

      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const focusableElements = listRef.current?.querySelectorAll('[data-beat-container]')
        if (!focusableElements) return

        const currentIndex = Array.from(focusableElements).findIndex(el => el.contains(document.activeElement))
        
        let nextIndex = -1
        if (e.key === 'ArrowDown') {
          nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0
        } else {
          nextIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1
        }

        if (nextIndex !== -1) {
          e.preventDefault()
          const nextElement = focusableElements[nextIndex] as HTMLElement
          // Find the first focusable element inside the container (the toggle button)
          const firstFocusable = nextElement.querySelector('button, input, textarea') as HTMLElement
          firstFocusable?.focus()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [beats.length, editingId])

  const handleMarkAllReviewed = () => {
    if (onToggleAllReviewed) {
      onToggleAllReviewed()
    } else if (onToggleReviewed) {
      beats.forEach(beat => {
        if (!reviewedIds.has(beat.id)) {
          onToggleReviewed(beat.id)
        }
      })
    }
  }

  const handleAssetSelect = (beatId: string, selectedPath: string) => {
    if (!onAssetsUpdate) return
    
    const currentAssets = assets[beatId]
    if (!currentAssets || !Array.isArray(currentAssets)) return

    // Move selected path to the front of the array
    const newPaths = [
      selectedPath,
      ...currentAssets.filter(p => p !== selectedPath)
    ]

    const updatedAssets = { ...assets, [beatId]: newPaths }
    onAssetsUpdate(updatedAssets)
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

  const handleSave = async () => {
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

    // Mark beat as saving
    setSavingIds(prev => new Set(prev).add(editingId))
    
    try {
      // Wait for the save to complete
      await onBeatsUpdate(updatedBeats)
      
      setEditingId(null)
      setEditValues({})
      
      if (onToggleReviewed && !reviewedIds.has(editingId)) {
        onToggleReviewed(editingId)
      }
    } catch (err) {
      console.error("Failed to save beat", err)
    } finally {
      // Remove from saving state after a short delay
      setTimeout(() => {
        setSavingIds(prev => {
          const next = new Set(prev)
          next.delete(editingId)
          return next
        })
      }, 500)
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditValues({})
  }

  const totalDuration = beats.reduce((sum, b) => sum + b.duration, 0)
  const formatDuration = (sec: number) => {
    if (!sec || sec <= 0) return 'LIVE / N/A'
    const m = Math.floor(sec / 60)
    const s = Math.floor(sec % 60)
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  return (
    <div className="w-full relative">
      {/* Simplified Summary Header */}
      <div className="flex items-center gap-10 py-6 border-b border-slate-100 mb-8 sticky top-16 bg-white/95 backdrop-blur-md z-20">
        <div className="flex flex-col">
          <span className="text-xl font-bold text-slate-900 leading-none">{beats.length}</span>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Segments</span>
        </div>
        <div className="flex flex-col">
          <span className="text-xl font-bold text-slate-900 leading-none">{formatDuration(totalDuration)}</span>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Duration</span>
        </div>
        <div className="flex flex-col ml-auto">
          <span className="text-xl font-bold text-blue-600 leading-none">{reviewedIds.size}/{beats.length}</span>
          <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider mt-1">Reviewed</span>
        </div>
        
        {reviewedIds.size < beats.length && (
          <button 
            onClick={handleMarkAllReviewed}
            className="flex items-center gap-2 px-6 py-2 bg-slate-900 hover:bg-black text-[11px] font-bold uppercase tracking-wider text-white rounded-xl transition-all active:scale-95 ml-4"
          >
            Approve All
          </button>
        )}
      </div>

      {/* Main Content Area with Timeline */}
      <div className="relative pl-16 md:pl-28 pt-4">
        {/* Timeline Head (Start) */}
        <div className="absolute left-8 md:left-14 -top-2 flex flex-col items-center -translate-x-1/2">
          <div className="w-2 h-2 rounded-full bg-slate-200 ring-4 ring-white" />
          <span className="text-[8px] font-black text-slate-300 uppercase tracking-[0.3em] mt-2">START</span>
        </div>

        {/* Vertical Timeline Track */}
        <div className="absolute left-8 md:left-14 top-2 bottom-6 w-0.5 bg-slate-100 -translate-x-1/2 z-0" />
        
        {/* Progress Fill */}
        <motion.div 
          className="absolute left-8 md:left-14 top-2 w-0.5 bg-blue-500 z-10 origin-top -translate-x-1/2 shadow-[0_0_10px_rgba(59,130,246,0.5)]"
          initial={{ scaleY: 0 }}
          animate={{ scaleY: beats.length > 0 ? (reviewedIds.size / beats.length) : 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          style={{ height: 'calc(100% - 32px)' }}
        />

        {/* Timeline Tail (End) */}
        <div className="absolute left-8 md:left-14 -bottom-2 flex flex-col items-center -translate-x-1/2 z-0">
          <span className="text-[8px] font-black text-slate-400 uppercase tracking-[0.3em] mb-2">END</span>
          <div className="w-3 h-3 rounded-full bg-slate-200 border-2 border-white" />
        </div>

        {/* Beat list */}
        <div className="space-y-10" ref={listRef}>
          {beats.map((beat, index) => {
            const viewMode = getModeFromBeat(beat)
            const isReviewed = reviewedIds.has(beat.id)
            const isEditing = editingId === beat.id
            
            // Calculate startTime by summing previous beat durations
            const startTime = beats.slice(0, index).reduce((sum, b) => sum + b.duration, 0)

            // Color mapping based on viewMode
            const nodeColors = {
              none: { bg: 'oklch(0.7 0.01 250)', border: 'oklch(0.8 0.01 250)', pulse: 'oklch(0.7 0.01 250)' },
              auto: { bg: 'oklch(0.6 0.2 250)', border: 'oklch(0.5 0.2 250)', pulse: 'oklch(0.6 0.2 250)' },
              youtube: { bg: 'oklch(0.6 0.2 20)', border: 'oklch(0.5 0.2 20)', pulse: 'oklch(0.6 0.2 20)' },
              stock: { bg: 'oklch(0.6 0.2 150)', border: 'oklch(0.5 0.2 150)', pulse: 'oklch(0.6 0.2 150)' }
            }
            const currentColors = nodeColors[viewMode]

            return (
              <div key={beat.id} className="relative">
                {/* Timeline Node & Timestamp */}
                <div className="absolute -left-16 md:-left-28 top-8 flex flex-col items-center w-16 md:w-28 z-20">
                  <div className="relative flex items-center justify-center h-12 w-full">
                    {/* Timestamp Label */}
                    <div className="absolute -left-2 md:left-2 top-1/2 -translate-y-1/2 -translate-x-full pr-3 hidden md:block">
                      <span className={`text-[11px] font-mono font-black tabular-nums transition-colors duration-500 ${isReviewed ? 'text-slate-300' : 'text-slate-400'}`}>
                        {formatDuration(startTime)}
                      </span>
                    </div>

                    <div className="relative flex items-center justify-center">
                      <motion.div 
                        initial={false}
                        animate={{ 
                          scale: isReviewed ? 1.4 : 1,
                          backgroundColor: isReviewed ? 'oklch(0.6 0.18 250)' : currentColors.bg,
                          borderColor: isReviewed ? 'oklch(0.5 0.2 250)' : currentColors.border
                        }}
                        className={`
                          w-4 h-4 rounded-full border-2 border-white shadow-sm transition-colors duration-300 z-30
                          ${isReviewed ? 'shadow-[0_0_20px_rgba(59,130,246,0.6)]' : ''}
                        `}
                      />
                      {/* Ring for active/unreviewed items */}
                      {!isReviewed && (
                        <motion.div 
                          animate={{ scale: [1, 2.5, 1], opacity: [0.4, 0, 0.4] }}
                          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                          style={{ backgroundColor: currentColors.pulse }}
                          className="absolute inset-0 w-4 h-4 rounded-full opacity-20"
                        />
                      )}
                    </div>
                    
                    {/* Connection line from node to card */}
                    <div className={`
                      absolute left-[50%] right-0 h-px transition-all duration-700 
                      ${isReviewed ? 'bg-blue-200 scale-x-100' : 'bg-slate-200 scale-x-75 opacity-50'}
                      origin-left
                    `} />
                  </div>
                </div>

                <motion.div 
                  layout
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  data-beat-container={index}
                  className={`
                    relative group rounded-3xl transition-all duration-500 overflow-hidden
                    ${isEditing ? 'bg-white ring-1 ring-slate-200 shadow-2xl p-8 z-10 scale-[1.02]' : 'bg-white p-6 border border-slate-100 hover:border-slate-200 focus-within:border-blue-300'}
                    ${isReviewed && !isEditing ? 'bg-slate-50/40 border-slate-100 opacity-80' : 'shadow-sm hover:shadow-md'}
                  `}
                >
                  <AnimatePresence mode="wait">
                    {isEditing ? (
                      <motion.div 
                        key="edit"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-8"
                      >
                        <div className="flex items-center justify-between">
                          <h3 className="text-base font-bold text-slate-900 flex items-center gap-3">
                            <Edit3 size={18} className="text-blue-500" />
                            Edit Segment {index + 1}
                          </h3>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                          <div className="space-y-6">
                            <div>
                              <label className="text-xs font-bold text-slate-400 mb-3 block">Narrative</label>
                              <textarea
                                value={editValues.text || ''}
                                onChange={(e) => setEditValues({ ...editValues, text: e.target.value })}
                                className="w-full p-5 bg-slate-50 border border-slate-200 rounded-2xl text-sm leading-relaxed text-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/5 focus:bg-white transition-all resize-none font-medium"
                                rows={4}
                              />
                            </div>
                            
                            <div>
                              <div className="flex items-center justify-between mb-3">
                                <label className="text-xs font-bold text-slate-400 block">Duration</label>
                                <span className="text-sm font-bold text-blue-600">{editValues.duration}s</span>
                              </div>
                              <input
                                type="range"
                                min="0.5"
                                max="30"
                                step="0.5"
                                value={editValues.duration || 0}
                                onChange={(e) => setEditValues({ ...editValues, duration: parseFloat(e.target.value) })}
                                className="w-full accent-blue-600 h-1.5 bg-slate-100 rounded-full cursor-pointer"
                              />
                            </div>
                          </div>

                          <div className="space-y-6">
                            <div>
                              <label className="text-xs font-bold text-slate-400 mb-3 block">Source</label>
                              <div className="grid grid-cols-4 gap-1.5 bg-slate-100 p-1 rounded-2xl">
                                {(['auto', 'youtube', 'stock', 'none'] as const).map((m) => {
                                  return (
                                    <button
                                      key={m}
                                      onClick={() => setSourceMode(m)}
                                      className={`py-2.5 text-[10px] font-bold uppercase tracking-wider rounded-xl transition-all ${
                                        sourceMode === m 
                                          ? 'bg-white text-blue-600 shadow-sm' 
                                          : 'text-slate-400 hover:text-slate-600'
                                      }`}
                                    >
                                      {m}
                                    </button>
                                  )
                                })}
                              </div>
                            </div>

                            <div className="space-y-4">
                              {(sourceMode === 'auto' || sourceMode === 'youtube') && (
                                <input
                                  type="text"
                                  value={editValues.youtube_phrase || ''}
                                  onChange={(e) => setEditValues({ ...editValues, youtube_phrase: e.target.value })}
                                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:bg-white outline-none transition-all"
                                  placeholder="YouTube Search..."
                                />
                              )}

                              {(sourceMode === 'auto' || sourceMode === 'stock') && (
                                <input
                                  type="text"
                                  value={editValues.stock_keyword || ''}
                                  onChange={(e) => setEditValues({ ...editValues, stock_keyword: e.target.value })}
                                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:bg-white outline-none transition-all"
                                  placeholder="Stock Keywords..."
                                />
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex justify-end gap-3 pt-4">
                          <button onClick={handleCancel} className="px-6 py-2.5 text-xs font-bold text-slate-400 hover:text-slate-600">Cancel</button>
                          <button onClick={handleSave} className="bg-blue-600 text-white py-2.5 px-8 rounded-xl text-xs font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-500/20 active:scale-95">
                            Save Changes
                          </button>
                        </div>
                      </motion.div>
                    ) : (
                      <div className="flex items-start gap-8">
                        <button 
                          onClick={() => onToggleReviewed?.(beat.id)}
                          aria-label={isReviewed ? "Unapprove" : "Approve"}
                          className={`
                            w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 border-2 flex-shrink-0 mt-1
                            ${isReviewed 
                              ? 'bg-blue-600 border-blue-600 text-white' 
                              : 'bg-white border-slate-200 text-slate-300 hover:border-blue-400 hover:text-blue-500'}
                          `}
                        >
                          <CheckCircle2 size={20} strokeWidth={isReviewed ? 3 : 2} />
                        </button>

                        <div className="flex-grow min-w-0">
                          <div className="flex flex-wrap items-center gap-2 mb-3">
                            <span className="text-[11px] font-bold text-slate-300">#{index + 1}</span>
                            {beat.header && (
                              <span className="text-[10px] font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-lg">
                                {beat.header}
                              </span>
                            )}
                            <span className="text-[10px] font-bold text-slate-400 bg-slate-50 px-2 py-0.5 rounded-lg">
                              {beat.duration.toFixed(1)}s
                            </span>
                            {isReviewed && (
                              <span className="text-[10px] font-bold text-blue-600 uppercase tracking-widest ml-auto">Approved</span>
                            )}
                          </div>

                          <p className={`text-base leading-relaxed transition-all duration-500 mb-6 break-words ${isReviewed ? 'text-slate-400 font-medium' : 'text-slate-800 font-medium'}`}>
                            {beat.text}
                          </p>
                          
                          {viewMode !== 'none' && (
                            <div className="transition-all duration-500">
                              <BeatAsset 
                                sessionId={sessionId}
                                beatId={beat.id}
                                assetPath={assets[beat.id]}
                                downloadProgress={downloadProgress[beat.id]}
                                visualType={beat.visual_type}
                                visualContent={beat.visual_content}
                                youtubePhrase={beat.youtube_phrase}
                                stockKeyword={beat.stock_keyword}
                                isRefreshing={false}
                                isSaving={savingIds.has(beat.id)}
                                reviewed={isReviewed}
                                onMaximize={(id, path) => {
                                  setLightboxId(id)
                                  setLightboxPath(path || null)
                                }}
                                onSelect={handleAssetSelect}
                                onDownloadAsset={onDownloadAsset}
                                onAssetDownloaded={(beatId, filePath) => {
                                  // Update assets state when a new asset is downloaded
                                  if (onAssetsUpdate) {
                                    const updatedAssets = { ...assets, [beatId]: filePath }
                                    onAssetsUpdate(updatedAssets)
                                  }
                                }}
                              />
                            </div>
                          )}
                        </div>

                        {editable && (
                          <div className="flex flex-col gap-2 opacity-0 group-hover:opacity-100 transition-all duration-300 pt-1">
                            <button
                              onClick={() => handleEdit(beat)}
                              className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-300 hover:text-blue-600 hover:bg-blue-50"
                              title="Edit"
                            >
                              <Edit3 size={16} />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                handleSkip(beat)
                              }}
                              className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-300 hover:text-red-500 hover:bg-red-50"
                              title="Skip"
                            >
                              <Slash size={16} />
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </div>
            )
          })}
        </div>
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
              aria-label="Close lightbox"
            >
              <Slash size={32} strokeWidth={1} />
            </button>
            
            <div className="w-full max-w-6xl aspect-video rounded-3xl overflow-hidden shadow-2xl border border-white/10 bg-black" onClick={e => e.stopPropagation()}>
              <video 
                src={getMediaUrl(sessionId, lightboxPath || '')} 
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
                {(lightboxPath || '').split(/[\/]/).pop()}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
