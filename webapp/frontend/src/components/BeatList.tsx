/**
 * Beat list display component
 *
 * Shows parsed beats from the script with editing capabilities
 */

import { useState, useRef, useEffect } from 'react'
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
  Quote,
  Type
} from 'lucide-react'
import { refreshBeatAsset, getMediaUrl } from '../services/api'
import { BeatAsset } from './BeatAsset'

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
    } catch (err) {
      console.error("Failed to refresh beat", err)
    } finally {
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
    <div className="w-full relative">
      {/* Refined Summary Header */}
      <div className="flex items-center gap-10 py-6 border-b border-slate-100 mb-8 sticky top-16 bg-white/95 backdrop-blur-md z-20">
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-900">
            <span className="text-2xl font-black leading-none tracking-tight">{beats.length}</span>
            <Film size={16} className="text-slate-400" />
          </div>
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Segments</span>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-900">
            <span className="text-2xl font-black leading-none tracking-tight">{formatDuration(totalDuration)}</span>
            <Clock size={16} className="text-slate-400" />
          </div>
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Duration</span>
        </div>
        <div className="flex flex-col ml-auto">
          <div className="flex items-center gap-1.5 text-blue-600">
            <span className="text-2xl font-black leading-none tracking-tight">{reviewedIds.size}/{beats.length}</span>
            <CheckCircle2 size={16} />
          </div>
          <span className="text-[10px] font-black text-blue-400 uppercase tracking-[0.2em]">Reviewed</span>
        </div>
        
        <div className="hidden md:flex items-center gap-4 px-5 py-2.5 bg-slate-50 rounded-2xl border border-slate-100">
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Controls</span>
          <div className="flex gap-1.5">
            <kbd className="px-2 py-1 rounded-lg border border-slate-200 bg-white text-[10px] font-black text-slate-500 shadow-sm">↑</kbd>
            <kbd className="px-2 py-1 rounded-lg border border-slate-200 bg-white text-[10px] font-black text-slate-500 shadow-sm">↓</kbd>
          </div>
        </div>

        {reviewedIds.size < beats.length && (
          <button 
            onClick={handleMarkAllReviewed}
            aria-label="Mark all segments as reviewed"
            className="flex items-center gap-2 px-6 py-2.5 bg-slate-900 hover:bg-black text-[11px] font-black uppercase tracking-widest text-white rounded-xl transition-all shadow-lg shadow-slate-200 hover:shadow-slate-300 focus:ring-4 focus:ring-slate-500/10 active:scale-95"
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
                    ${isEditing ? 'bg-white ring-1 ring-slate-200 shadow-2xl p-8 z-10 scale-[1.02]' : 'bg-white p-6 border border-slate-100 hover:border-slate-200 focus-within:border-blue-300 focus-within:ring-8 focus-within:ring-blue-500/5'}
                    ${isReviewed && !isEditing ? 'bg-slate-50/60 border-slate-100 scale-[0.98] opacity-80' : 'shadow-sm hover:shadow-md'}
                  `}
                >
                  {/* Cinematic Watermark for Reviewed Items */}
                  <AnimatePresence>
                    {isReviewed && !isEditing && (
                      <motion.div
                        initial={{ opacity: 0, scale: 1.1 }}
                        animate={{ opacity: 0.03, scale: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute right-0 bottom-0 pointer-events-none select-none overflow-hidden h-full flex items-end"
                        style={{ fontFamily: "'Inter', sans-serif" }}
                      >
                        <span className="text-[160px] font-black italic tracking-tighter leading-[0.8] translate-y-12 translate-x-12 uppercase">
                          Done
                        </span>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <AnimatePresence mode="wait">
                    {isEditing ? (
                      <motion.div 
                        key="edit"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-8"
                      >
                        <div className="flex items-center justify-between">
                          <h3 className="text-base font-black text-slate-900 flex items-center gap-3">
                            <Edit3 size={20} className="text-blue-500" />
                            Refine Segment #{index + 1}
                          </h3>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                          <div className="space-y-6">
                            <div>
                              <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3 block">Script Narrative</label>
                              <textarea
                                value={editValues.text || ''}
                                onChange={(e) => setEditValues({ ...editValues, text: e.target.value })}
                                className="w-full p-5 bg-slate-50 border border-slate-100 rounded-2xl text-sm leading-relaxed text-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/5 focus:bg-white focus:border-blue-500/20 transition-all resize-none font-medium"
                                rows={4}
                              />
                            </div>
                            
                            <div>
                              <div className="flex items-center justify-between mb-3">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] block">Target Duration</label>
                                <span className="font-mono text-sm font-black text-blue-600 bg-blue-50 px-2 py-0.5 rounded-lg">{editValues.duration}s</span>
                              </div>
                              <div className="flex items-center gap-4">
                                <input
                                  type="range"
                                  min="0.5"
                                  max="30"
                                  step="0.5"
                                  value={editValues.duration || 0}
                                  onChange={(e) => setEditValues({ ...editValues, duration: parseFloat(e.target.value) })}
                                  className="flex-grow accent-blue-600 h-1.5 bg-slate-100 rounded-full cursor-pointer"
                                />
                              </div>
                            </div>
                          </div>

                          <div className="space-y-6">
                            <div>
                              <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3 block">Visual Strategy</label>
                              <div className="grid grid-cols-4 gap-1.5 bg-slate-100 p-1.5 rounded-2xl">
                                {(['auto', 'youtube', 'stock', 'none'] as const).map((m) => {
                                  const Icon = m === 'youtube' ? Youtube : m === 'stock' ? Image : m === 'auto' ? Zap : Slash
                                  return (
                                    <button
                                      key={m}
                                      onClick={() => setSourceMode(m)}
                                      className={`flex flex-col items-center gap-2 py-3 text-[10px] font-black uppercase tracking-wider rounded-xl transition-all ${
                                        sourceMode === m 
                                          ? 'bg-white text-blue-600 shadow-md ring-1 ring-slate-200' 
                                          : 'text-slate-400 hover:text-slate-600 hover:bg-slate-200/50'
                                      }`}
                                    >
                                      <Icon size={14} />
                                      {m}
                                    </button>
                                  )
                                })}
                              </div>
                            </div>

                            <div className="space-y-4">
                              {(sourceMode === 'auto' || sourceMode === 'youtube') && (
                                <div>
                                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2 block">YouTube Search</label>
                                  <input
                                    type="text"
                                    value={editValues.youtube_phrase || ''}
                                    onChange={(e) => setEditValues({ ...editValues, youtube_phrase: e.target.value })}
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-mono font-bold text-slate-700 focus:bg-white focus:border-blue-500/20 focus:ring-4 focus:ring-blue-500/5 outline-none transition-all"
                                    placeholder="High-energy cinematic..."
                                  />
                                </div>
                              )}

                              {(sourceMode === 'auto' || sourceMode === 'stock') && (
                                <div>
                                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2 block">Stock Keywords</label>
                                  <input
                                    type="text"
                                    value={editValues.stock_keyword || ''}
                                    onChange={(e) => setEditValues({ ...editValues, stock_keyword: e.target.value })}
                                    className="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-xs font-mono font-bold text-slate-700 focus:bg-white focus:border-blue-500/20 focus:ring-4 focus:ring-blue-500/5 outline-none transition-all"
                                    placeholder="aerial, drone, city..."
                                  />
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        <div className="flex justify-end gap-4 pt-4">
                          <button onClick={handleCancel} className="px-6 py-2.5 text-[11px] font-black text-slate-400 hover:text-slate-900 transition-colors uppercase tracking-widest">Discard</button>
                          <button onClick={handleSave} className="bg-blue-600 text-white py-3 px-8 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-blue-700 transition-all flex items-center gap-2 shadow-lg shadow-blue-500/20 active:scale-95">
                            Save Segment
                            <Check size={16} strokeWidth={3} />
                          </button>
                        </div>
                      </motion.div>
                    ) : (
                      <div className="flex items-stretch gap-8">
                        <button 
                          onClick={() => onToggleReviewed?.(beat.id)}
                          aria-label={`Mark beat ${index + 1} as ${isReviewed ? 'unreviewed' : 'reviewed'}`}
                          className={`
                            w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-500 border-2 flex-shrink-0 mt-1 focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-90
                            ${isReviewed 
                              ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-500/30' 
                              : 'bg-white border-slate-200 text-slate-400 hover:border-blue-400 hover:text-blue-500 shadow-sm'}
                          `}
                        >
                          <CheckCircle2 size={24} strokeWidth={isReviewed ? 3 : 2} />
                        </button>

                        <div className="flex-grow min-w-0 py-1">
                          <div className="flex flex-wrap items-center gap-3 mb-4">
                            <span className="font-mono text-xs font-black text-slate-300">#{String(index + 1).padStart(2, '0')}</span>
                            {isReviewed && !isEditing && (
                              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white bg-blue-600 px-3 py-1 rounded-lg shadow-sm shadow-blue-500/20">
                                Approved
                              </span>
                            )}
                            {beat.header && (
                              <span className="text-[10px] font-black uppercase tracking-widest text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
                                {beat.header}
                              </span>
                            )}
                            <span className="text-[10px] font-black text-slate-500 flex items-center gap-1.5 px-3 py-1 bg-slate-50 rounded-full border border-slate-100">
                              <Clock size={11} />
                              {beat.duration.toFixed(1)}s
                            </span>
                            {beat.visual_type && beat.visual_type !== 'auto' && beat.visual_type !== 'b-roll' && (
                              <span className={`
                                text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full flex items-center gap-1.5 border
                                ${beat.visual_type === 'annotation' ? 'bg-purple-50 text-purple-600 border-purple-100' :
                                  beat.visual_type === 'citation' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                                  'bg-indigo-50 text-indigo-600 border-indigo-100'}
                              `}>
                                {beat.visual_type === 'annotation' ? <Type size={11} /> :
                                 beat.visual_type === 'citation' ? <Quote size={11} /> :
                                 <Image size={11} />}
                                {beat.visual_type}
                              </span>
                            )}
                            <div className={`
                              flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border
                              ${viewMode === 'none' ? 'bg-slate-50 text-slate-400 border-slate-100' :
                                viewMode === 'auto' ? 'bg-blue-50 text-blue-500 border-blue-100' :
                                viewMode === 'youtube' ? 'bg-red-50 text-red-500 border-red-100' :
                                'bg-emerald-50 text-emerald-600 border-emerald-100'}
                            `}>
                              {viewMode}
                            </div>
                          </div>

                          <p className={`text-base leading-relaxed transition-all duration-500 mb-6 max-w-2xl ${isReviewed ? 'text-slate-400 font-medium italic line-through decoration-slate-200 decoration-2' : 'text-slate-800 font-semibold'}`}>
                            {beat.text}
                          </p>
                          
                          {/* Asset Preview Section - Replaced with BeatAsset */}
                          {viewMode !== 'none' && (
                            <div className={`relative rounded-3xl overflow-hidden bg-slate-100 border border-slate-200 max-w-md shadow-inner transition-all duration-500 ${isReviewed ? 'grayscale opacity-60' : ''}`}>
                              <BeatAsset 
                                sessionId={sessionId}
                                beatId={beat.id}
                                assetPath={assets[beat.id]}
                                visualType={beat.visual_type}
                                visualContent={beat.visual_content}
                                isRefreshing={refreshingIds.has(beat.id)}
                                reviewed={isReviewed}
                                onRefresh={handleRefresh}
                                onMaximize={(id) => setLightboxId(id)}
                              />
                            </div>
                          )}
                          
                          {!isReviewed && viewMode !== 'none' && (
                            <div className="flex flex-wrap gap-2 mt-6">
                              {beat.youtube_phrase && (viewMode === 'auto' || viewMode === 'youtube') && (
                                <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-100 text-[10px] font-mono font-black text-slate-500 uppercase tracking-tight">
                                  <Youtube size={12} className="text-red-500" />
                                  {beat.youtube_phrase}
                                </span>
                              )}
                              {beat.stock_keyword && (viewMode === 'auto' || viewMode === 'stock') && (
                                <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-100 text-[10px] font-mono font-black text-slate-500 uppercase tracking-tight">
                                  <Image size={12} className="text-emerald-500" />
                                  {beat.stock_keyword}
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        {editable && (
                          <div className="flex flex-col gap-3 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-all duration-300 border-l border-slate-100 pl-6 py-2">
                            <button
                              onClick={() => handleEdit(beat)}
                              aria-label="Edit beat"
                              className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-blue-600 hover:bg-blue-50 focus:bg-blue-50 focus:text-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-500/10 transition-all"
                              title="Edit Segment"
                            >
                              <Edit3 size={18} />
                            </button>
                            
                            {viewMode !== 'none' && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleSkip(beat)
                                }}
                                aria-label="Disable visuals for this beat"
                                className="w-10 h-10 rounded-xl flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 focus:bg-red-50 focus:text-red-500 focus:outline-none focus:ring-4 focus:ring-red-500/10 transition-all"
                                title="Skip Visuals (None)"
                              >
                                <Slash size={18} />
                              </button>
                            )}
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
                {assets[lightboxId]?.split(/[\/]/).pop()}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
