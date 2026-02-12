import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, Loader2, AlertCircle, Film, Clock, Youtube, Image as ImageIcon, CheckCircle2, StopCircle } from 'lucide-react'
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
  downloadProgress,
  onClose,
  onAssetSelected,
  onSearch,
  onDownload
}: AssetSearchModalProps) {
  const [candidates, setCandidates] = useState<AssetCandidate[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [customQuery, setCustomQuery] = useState('')
  const [updateBeatQuery, setUpdateBeatQuery] = useState(false)
  const [selectedCandidate, setSelectedCandidate] = useState<AssetCandidate | null>(null)

  const isDownloading = downloadProgress && 
    ['starting', 'downloading', 'processing'].includes(downloadProgress.status)

  // Auto-search when modal opens
  useEffect(() => {
    if (isOpen && onSearch) {
      handleSearch()
    }
  }, [isOpen])

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
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-3xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                <Search size={20} className="text-blue-600" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900">Search Assets</h2>
                <p className="text-xs text-slate-500">Select an asset for this beat</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-xl hover:bg-slate-100 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors"
              aria-label="Close"
            >
              <X size={20} />
            </button>
          </div>

          {/* Custom Query Input */}
          <div className="p-6 border-b border-slate-100 space-y-3">
            <div className="flex gap-3">
              <input
                type="text"
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && customQuery.trim()) {
                    handleSearch(customQuery)
                  }
                }}
                placeholder="Enter custom search query..."
                className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 focus:bg-white focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all"
              />
              <button
                onClick={() => customQuery.trim() && handleSearch(customQuery)}
                disabled={isSearching || !customQuery.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
              >
                {isSearching ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  'Search'
                )}
              </button>
            </div>
            
            {customQuery.trim() && (
              <label className="flex items-center gap-2 cursor-pointer w-fit">
                <input 
                  type="checkbox" 
                  checked={updateBeatQuery}
                  onChange={(e) => setUpdateBeatQuery(e.target.checked)}
                  className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-xs text-slate-600 font-medium">Update beat with this search term on download</span>
              </label>
            )}
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <AnimatePresence mode="wait">
              {isSearching ? (
                <motion.div 
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                >
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="aspect-video bg-slate-100 animate-pulse rounded-2xl" />
                  ))}
                </motion.div>
              ) : error && candidates.length === 0 ? (
                <motion.div 
                  key="error"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col items-center justify-center py-20"
                >
                  <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mb-4">
                    <AlertCircle size={32} className="text-red-500" />
                  </div>
                  <p className="text-sm font-medium text-slate-900 mb-2">Search Failed</p>
                  <p className="text-xs text-slate-500 text-center max-w-md mb-6">{error}</p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleSearch(customQuery || undefined)}
                      className="px-6 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-black transition-all active:scale-95"
                    >
                      Retry Search
                    </button>
                    <button
                      onClick={onClose}
                      className="px-6 py-2 bg-slate-100 text-slate-600 rounded-xl text-xs font-bold hover:bg-slate-200 transition-all active:scale-95"
                    >
                      Cancel
                    </button>
                  </div>
                </motion.div>
              ) : candidates.length === 0 ? (
                <motion.div 
                  key="empty"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col items-center justify-center py-20"
                >
                  <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
                    <Film size={32} className="text-slate-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-900 mb-2">No Results</p>
                  <p className="text-xs text-slate-500 text-center max-w-md">
                    Try searching with a custom query above
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
                  className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
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
                          group relative rounded-2xl overflow-hidden border-2 transition-all text-left
                          ${isSelected 
                            ? isComplete ? 'border-green-500 ring-4 ring-green-500/10' : 'border-blue-500 ring-4 ring-blue-500/20' 
                            : 'border-slate-200 hover:border-blue-400 hover:shadow-lg'}
                          ${isDownloading || isComplete ? 'cursor-default' : 'cursor-pointer'}
                        `}
                      >
                        {/* Thumbnail */}
                        <div className="aspect-video bg-slate-100 relative overflow-hidden">
                          <img
                            src={candidate.thumbnail_url}
                            alt={candidate.title}
                            className={`w-full h-full object-cover transition-transform duration-500 ${!isSelected && 'group-hover:scale-110'}`}
                            loading="lazy"
                          />
                          
                          {/* Duration Badge */}
                          <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/80 backdrop-blur-sm rounded-lg flex items-center gap-1">
                            <Clock size={12} className="text-white" />
                            <span className="text-xs font-bold text-white">
                              {formatDuration(candidate.duration)}
                            </span>
                          </div>

                          {/* Source Badge */}
                          <div className="absolute top-2 left-2 px-2 py-1 bg-white/90 backdrop-blur-sm rounded-lg flex items-center gap-1">
                            {candidate.source === 'youtube' ? (
                              <Youtube size={12} className="text-red-600" />
                            ) : (
                              <ImageIcon size={12} className="text-green-600" />
                            )}
                            <span className="text-[10px] font-bold text-slate-700 uppercase">
                              {candidate.source}
                            </span>
                          </div>

                          {/* Downloading/Complete Overlay */}
                          <AnimatePresence>
                            {isSelected && (
                              <motion.div 
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className={`absolute inset-0 flex flex-col items-center justify-center gap-2 ${isComplete ? 'bg-green-600/90' : 'bg-blue-600/90'} backdrop-blur-sm`}
                              >
                                {isComplete ? (
                                  <motion.div
                                    initial={{ scale: 0.5, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ type: 'spring', damping: 12 }}
                                  >
                                    <CheckCircle2 size={40} className="text-white" />
                                  </motion.div>
                                ) : (
                                  <>
                                    <Loader2 size={32} className="text-white animate-spin" />
                                    {downloadProgress && (
                                      <p className="text-white text-[10px] font-black uppercase tracking-widest">
                                        {downloadProgress.status === 'processing' ? 'Processing' : `${Math.round(downloadProgress.percent)}%`}
                                      </p>
                                    )}
                                  </>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>

                        {/* Info */}
                        <div className="p-3 bg-white">
                          <p className={`text-xs font-medium line-clamp-2 ${isSelected ? isComplete ? 'text-green-900' : 'text-blue-900' : 'text-slate-900'}`}>
                            {candidate.title}
                          </p>
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
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="mt-8 p-6 bg-slate-900 rounded-3xl shadow-2xl overflow-hidden relative"
                >
                  <div className="flex items-center gap-4 relative z-10">
                    <div className="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center">
                      <Loader2 size={24} className="text-blue-400 animate-spin" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-bold text-white tracking-wide">
                          {downloadProgress.status === 'processing' ? 'Processing video...' : 'Downloading asset...'}
                        </p>
                        <div className="flex items-center gap-3">
                          <p className="text-xs font-mono text-blue-400 font-bold">
                            {Math.round(downloadProgress.percent)}%
                          </p>
                          <button 
                            onClick={handleCancel}
                            className="p-1 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors"
                            title="Cancel Download"
                          >
                            <StopCircle size={16} />
                          </button>
                        </div>
                      </div>
                      <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <motion.div 
                          className="h-full bg-blue-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${downloadProgress.percent}%` }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                      <p className="text-[10px] text-white/40 mt-2 truncate font-medium uppercase tracking-wider">
                        {downloadProgress.title || 'Selected Candidate'}
                      </p>
                    </div>
                  </div>
                  {/* Subtle progress background */}
                  <div 
                    className="absolute inset-0 bg-blue-500/5 transition-all duration-300"
                    style={{ width: `${downloadProgress.percent}%` }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
