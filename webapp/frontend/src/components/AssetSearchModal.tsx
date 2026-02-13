import { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, Loader2, AlertCircle, Film, Clock, Youtube, CheckCircle2, StopCircle, Zap, Globe, Sparkles } from 'lucide-react'
import type { DownloadProgress } from '../types/models'
import { cancelDownload } from '../services/api'

export interface AssetCandidate {
  id: string
  title: string
  thumbnail_url: string
  duration: number
  source: 'youtube' | 'pexels'
  metadata: Record<string, any>
}

interface AssetSearchModalProps {
  sessionId: string
  beatId: string
  isOpen: boolean
  initialQuery?: string
  downloadProgress?: DownloadProgress
  onClose: () => void
  onAssetSelected: (beatId: string, filePath: string) => void
  onSearch?: (sessionId: string, beatId: string, customQuery?: string) => Promise<AssetCandidate[]>
  onDownload?: (sessionId: string, beatId: string, candidate: AssetCandidate, updateBeatQuery?: boolean) => Promise<string>
}

export function AssetSearchModal({
  sessionId,
  beatId,
  isOpen,
  initialQuery = '',
  downloadProgress,
  onClose,
  onAssetSelected,
  onSearch,
  onDownload
}: AssetSearchModalProps) {
  const [candidates, setCandidates] = useState<AssetCandidate[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [customQuery, setCustomQuery] = useState(initialQuery)
  const [updateBeatQuery, setUpdateBeatQuery] = useState(false)
  const [selectedCandidate, setSelectedCandidate] = useState<AssetCandidate | null>(null)

  const isDownloading = downloadProgress && 
    ['starting', 'downloading', 'processing'].includes(downloadProgress.status)

  // Update custom query when initialQuery changes or modal opens
  useEffect(() => {
    if (isOpen) {
      setCustomQuery(initialQuery)
      setCandidates([])
      setError(null)
    }
  }, [isOpen, initialQuery])

  // Handle completion
  useEffect(() => {
    if (downloadProgress?.status === 'complete' && downloadProgress.file_path) {
      onAssetSelected(beatId, downloadProgress.file_path)
      // Delay closing slightly to show success state
      const timer = setTimeout(() => {
        onClose()
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [downloadProgress?.status])

  const handleSearch = async (query?: string) => {
    if (!onSearch) return
    
    setIsSearching(true)
    setError(null)
    setCandidates([])
    
    try {
      const results = await onSearch(sessionId, beatId, query)
      setCandidates(results)
      
      if (results.length === 0) {
        setError('No assets found. Try a different search query.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search for assets')
    } finally {
      setIsSearching(false)
    }
  }

  const handleSelectCandidate = async (candidate: AssetCandidate) => {
    if (!onDownload) return
    
    setSelectedCandidate(candidate)
    setError(null)
    
    try {
      // Only update beat query if a custom query was actually used and checkbox is checked
      const shouldUpdate = updateBeatQuery && !!customQuery.trim()
      await onDownload(sessionId, beatId, candidate, shouldUpdate)
      // Transition to downloading state (handled by props)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download asset')
      setSelectedCandidate(null)
    }
  }

  const handleCancel = async () => {
    try {
      await cancelDownload(sessionId, beatId)
    } catch (err) {
      console.error('Failed to cancel download', err)
    }
  }

  const formatDuration = (seconds: number): string => {
    if (!seconds || seconds <= 0) return 'LIVE / N/A'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-slate-900/80 backdrop-blur-md flex items-center justify-center p-4 md:p-8"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="bg-white rounded-[2rem] shadow-[0_32px_128px_-16px_rgba(0,0,0,0.3)] w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col border border-white/20"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header with colorful gradient */}
            <div className="relative overflow-hidden flex items-center justify-between p-8 border-b border-slate-100 bg-gradient-to-r from-blue-50/50 via-white to-purple-50/50">
              <div className="relative z-10 flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
                  <Search size={22} className="text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                    Search Assets
                    <Sparkles size={16} className="text-amber-400 fill-amber-400" />
                  </h2>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Acquire B-Roll & Visuals</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="relative z-10 w-12 h-12 rounded-2xl bg-white border border-slate-100 shadow-sm hover:border-slate-300 flex items-center justify-center text-slate-400 hover:text-slate-900 transition-all hover:rotate-90 active:scale-90"
                aria-label="Close"
              >
                <X size={22} />
              </button>
              
              {/* Background accent */}
              <div className="absolute -top-24 -right-24 w-64 h-64 bg-blue-400/5 blur-3xl rounded-full" />
              <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-purple-400/5 blur-3xl rounded-full" />
            </div>

            {/* Custom Query Input */}
            <div className="p-8 bg-slate-50/50 border-b border-slate-100 space-y-4">
              <div className="flex gap-4">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={customQuery}
                    onChange={(e) => setCustomQuery(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && customQuery.trim()) {
                        handleSearch(customQuery)
                      }
                    }}
                    placeholder="Describe the visual you need (e.g., 'Aerial shot of a busy city at night')..."
                    className="w-full pl-12 pr-4 py-4 bg-white border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:border-blue-500 focus:ring-8 focus:ring-blue-500/5 outline-none transition-all shadow-sm"
                  />
                  <Globe className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                </div>
                <button
                  onClick={() => customQuery.trim() && handleSearch(customQuery)}
                  disabled={isSearching || !customQuery.trim()}
                  className="px-8 py-4 bg-slate-900 text-white rounded-2xl text-sm font-black uppercase tracking-widest hover:bg-blue-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-xl shadow-slate-900/10 active:scale-95 flex items-center gap-3"
                >
                  {isSearching ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Searching
                    </>
                  ) : (
                    <>
                      <Zap size={18} className="fill-current" />
                      Search
                    </>
                  )}
                </button>
              </div>
              
              {customQuery.trim() && (
                <motion.label 
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-3 cursor-pointer w-fit px-4 py-2 bg-blue-50 rounded-xl border border-blue-100 group"
                >
                  <input 
                    type="checkbox" 
                    checked={updateBeatQuery}
                    onChange={(e) => setUpdateBeatQuery(e.target.checked)}
                    className="w-4 h-4 rounded-md border-slate-300 text-blue-600 focus:ring-blue-500 transition-colors"
                  />
                  <span className="text-[10px] text-blue-700 font-black uppercase tracking-widest group-hover:text-blue-900 transition-colors">Update beat description with this term</span>
                </motion.label>
              )}
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto p-8 bg-white scrollbar-thin">
              <AnimatePresence mode="wait">
                {isSearching ? (
                  <motion.div 
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                  >
                    {[...Array(6)].map((_, i) => (
                      <div key={i} className="aspect-video bg-slate-50 border border-slate-100 animate-pulse rounded-[1.5rem]" />
                    ))}
                  </motion.div>
                ) : error && candidates.length === 0 ? (
                  <motion.div 
                    key="error"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center justify-center py-24 text-center"
                  >
                    <div className="w-20 h-20 rounded-3xl bg-red-50 flex items-center justify-center mb-6 shadow-inner">
                      <AlertCircle size={40} className="text-red-500" />
                    </div>
                    <h3 className="text-lg font-black text-slate-900 mb-2 uppercase tracking-tight">Search Encountered a Problem</h3>
                    <p className="text-sm text-slate-500 max-w-md mb-10 font-medium">{error}</p>
                    <div className="flex gap-4">
                      <button
                        onClick={() => handleSearch(customQuery || undefined)}
                        className="px-8 py-3 bg-slate-900 text-white rounded-xl text-xs font-black uppercase tracking-widest hover:bg-black transition-all shadow-lg active:scale-95"
                      >
                        Retry Search
                      </button>
                      <button
                        onClick={onClose}
                        className="px-8 py-3 bg-slate-100 text-slate-500 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-slate-200 transition-all active:scale-95"
                      >
                        Dismiss
                      </button>
                    </div>
                  </motion.div>
                ) : candidates.length === 0 ? (
                  <motion.div 
                    key="empty"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center justify-center py-24 text-center"
                  >
                    <div className="w-20 h-20 rounded-[2rem] bg-slate-50 border border-slate-100 flex items-center justify-center mb-6 shadow-sm">
                      <Film size={40} className="text-slate-200" />
                    </div>
                    <h3 className="text-lg font-black text-slate-900 mb-2 uppercase tracking-tight">No Matches Found</h3>
                    <p className="text-sm text-slate-400 font-medium">
                      Try adjusting your keywords or using a broader description
                    </p>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="results"
                    initial="hidden"
                    animate="show"
                    variants={{
                      hidden: { opacity: 0 },
                      show: {
                        opacity: 1,
                        transition: {
                          staggerChildren: 0.05
                        }
                      }
                    }}
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                  >
                    {candidates.map((candidate) => {
                      const isSelected = (selectedCandidate?.id === candidate.id) || (downloadProgress?.candidate_id === candidate.id);
                      const isComplete = isSelected && downloadProgress?.status === 'complete';
                      
                      return (
                        <motion.button
                          key={candidate.id}
                          variants={{
                            hidden: { opacity: 0, y: 20 },
                            show: { opacity: 1, y: 0 }
                          }}
                          onClick={() => handleSelectCandidate(candidate)}
                          disabled={isDownloading || isComplete}
                          className={`
                            group relative rounded-[2rem] overflow-hidden border-2 transition-all duration-500 text-left bg-white
                            ${isSelected 
                              ? isComplete ? 'border-emerald-500 ring-8 ring-emerald-500/10 scale-[1.02]' : 'border-blue-500 ring-8 ring-blue-500/10 scale-[1.02]' 
                              : 'border-slate-100 hover:border-blue-400 hover:shadow-2xl hover:shadow-blue-500/10 hover:-translate-y-1'}
                            ${isDownloading || isComplete ? 'cursor-default' : 'cursor-pointer'}
                          `}
                        >
                          {/* Thumbnail */}
                          <div className="aspect-video bg-slate-900 relative overflow-hidden">
                            <img
                              src={candidate.thumbnail_url}
                              alt={candidate.title}
                              className={`w-full h-full object-cover transition-transform duration-700 ${!isSelected && 'group-hover:scale-110 opacity-90 group-hover:opacity-100'}`}
                              loading="lazy"
                            />
                            
                            {/* Duration Badge */}
                            <div className="absolute bottom-4 right-4 px-2 py-1 bg-black/80 backdrop-blur-md rounded-lg flex items-center gap-1.5 shadow-lg border border-white/10">
                              <Clock size={12} className="text-white/80" />
                              <span className="text-[10px] font-black text-white uppercase tracking-wider">
                                {formatDuration(candidate.duration)}
                              </span>
                            </div>

                            {/* Source Badge */}
                            <div className="absolute top-4 left-4 px-3 py-1.5 bg-white/95 backdrop-blur-md rounded-xl flex items-center gap-2 shadow-lg border border-slate-100">
                              {candidate.source === 'youtube' ? (
                                <Youtube size={14} className="text-red-600" />
                              ) : (
                                <Globe size={14} className="text-blue-500" />
                              )}
                              <span className="text-[9px] font-black text-slate-900 uppercase tracking-widest">
                                {candidate.source}
                              </span>
                            </div>

                            {/* Downloading/Complete Overlay */}
                            <AnimatePresence>
                              {isSelected && (
                                <motion.div 
                                  initial={{ opacity: 0 }}
                                  animate={{ opacity: 1 }}
                                  className={`absolute inset-0 flex flex-col items-center justify-center gap-4 ${isComplete ? 'bg-emerald-600/90' : 'bg-blue-600/90'} backdrop-blur-md transition-colors duration-500`}
                                >
                                  {isComplete ? (
                                    <motion.div
                                      initial={{ scale: 0.5, opacity: 0, rotate: -15 }}
                                      animate={{ scale: 1, opacity: 1, rotate: 0 }}
                                      transition={{ type: 'spring', damping: 10, stiffness: 200 }}
                                      className="flex flex-col items-center gap-3"
                                    >
                                      <div className="w-16 h-16 rounded-full bg-white flex items-center justify-center shadow-xl">
                                        <CheckCircle2 size={40} className="text-emerald-600" />
                                      </div>
                                      <p className="text-white text-xs font-black uppercase tracking-[0.3em]">Ready</p>
                                    </motion.div>
                                  ) : (
                                    <>
                                      <div className="relative">
                                        <Loader2 size={48} className="text-white animate-spin" strokeWidth={1.5} />
                                        <div className="absolute inset-0 flex items-center justify-center">
                                          <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                                        </div>
                                      </div>
                                      {downloadProgress && (
                                        <div className="text-center">
                                          <p className="text-white text-[10px] font-black uppercase tracking-[0.4em] mb-1">Downloading</p>
                                          <p className="text-white text-xl font-mono font-black">
                                            {downloadProgress.status === 'processing' ? '...' : `${Math.round(downloadProgress.percent)}%`}
                                          </p>
                                        </div>
                                      )}
                                    </>
                                  )}
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>

                          {/* Info */}
                          <div className="p-5 bg-white">
                            <p className={`text-xs font-bold leading-tight line-clamp-2 transition-colors duration-500 ${isSelected ? isComplete ? 'text-emerald-900' : 'text-blue-900' : 'text-slate-800'}`}>
                              {candidate.title}
                            </p>
                            <div className="mt-3 flex items-center justify-between">
                                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">
                                    {candidate.id.slice(0, 8)}
                                </span>
                                {!isSelected && <Zap size={12} className="text-slate-200 group-hover:text-blue-500 transition-colors" />}
                            </div>
                          </div>
                        </motion.button>
                      )
                    })}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Global Download Progress Bar (if modal content is scrolled) */}
              <AnimatePresence>
                {isDownloading && downloadProgress && (
                  <motion.div 
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 40 }}
                    className="sticky bottom-0 mt-12 p-8 bg-slate-900 rounded-[2.5rem] shadow-[0_32px_64px_rgba(0,0,0,0.4)] overflow-hidden"
                  >
                    <div className="flex items-center gap-6 relative z-10">
                      <div className="w-16 h-16 rounded-[1.5rem] bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/40">
                        <Loader2 size={32} className="text-white animate-spin" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h4 className="text-sm font-black text-white uppercase tracking-widest mb-1">
                                {downloadProgress.status === 'processing' ? 'Finalizing Bundle' : 'Acquiring Media'}
                            </h4>
                            <p className="text-[10px] text-blue-400 font-bold uppercase tracking-wider">
                                {downloadProgress.title || 'Selected Candidate'}
                            </p>
                          </div>
                          <div className="flex items-center gap-6">
                            <div className="text-right">
                                <p className="text-2xl font-mono text-white font-black leading-none">
                                    {Math.round(downloadProgress.percent)}%
                                </p>
                            </div>
                            <button 
                              onClick={handleCancel}
                              className="w-10 h-10 bg-white/10 hover:bg-red-500/20 rounded-xl text-white/40 hover:text-red-500 transition-all flex items-center justify-center border border-white/5"
                              title="Cancel Download"
                            >
                              <StopCircle size={20} />
                            </button>
                          </div>
                        </div>
                        <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden p-0.5">
                          <motion.div 
                            className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-blue-400 rounded-full shadow-[0_0_15px_rgba(59,130,246,0.5)]"
                            initial={{ width: 0 }}
                            animate={{ width: `${downloadProgress.percent}%` }}
                            transition={{ duration: 0.5, ease: "easeOut" }}
                          />
                        </div>
                      </div>
                    </div>
                    {/* Subtle progress background */}
                    <motion.div 
                      className="absolute inset-0 bg-blue-500/10 pointer-events-none"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      style={{ width: `${downloadProgress.percent}%` }}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )

  return createPortal(modalContent, document.body)
}

