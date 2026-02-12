import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, Loader2, AlertCircle, Film, Clock, Youtube, Image as ImageIcon } from 'lucide-react'

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
  onClose: () => void
  onAssetSelected: (beatId: string, filePath: string) => void
  onSearch?: (sessionId: string, beatId: string, customQuery?: string) => Promise<AssetCandidate[]>
  onDownload?: (sessionId: string, beatId: string, candidate: AssetCandidate) => Promise<string>
}

export function AssetSearchModal({
  sessionId,
  beatId,
  isOpen,
  onClose,
  onAssetSelected,
  onSearch,
  onDownload
}: AssetSearchModalProps) {
  const [candidates, setCandidates] = useState<AssetCandidate[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [customQuery, setCustomQuery] = useState('')
  const [selectedCandidate, setSelectedCandidate] = useState<AssetCandidate | null>(null)

  // Auto-search when modal opens
  useEffect(() => {
    if (isOpen && onSearch) {
      handleSearch()
    }
  }, [isOpen])

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
    setIsDownloading(true)
    setError(null)
    
    try {
      const filePath = await onDownload(sessionId, beatId, candidate)
      onAssetSelected(beatId, filePath)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download asset')
    } finally {
      setIsDownloading(false)
      setSelectedCandidate(null)
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
          <div className="p-6 border-b border-slate-100">
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
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-6">
            {/* Loading State */}
            {isSearching && (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 size={40} className="text-blue-600 animate-spin mb-4" />
                <p className="text-sm font-medium text-slate-600">Searching for assets...</p>
                <p className="text-xs text-slate-400 mt-1">This may take a few seconds</p>
              </div>
            )}

            {/* Error State */}
            {error && !isSearching && (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="w-16 h-16 rounded-2xl bg-red-50 flex items-center justify-center mb-4">
                  <AlertCircle size={32} className="text-red-500" />
                </div>
                <p className="text-sm font-medium text-slate-900 mb-2">Search Failed</p>
                <p className="text-xs text-slate-500 text-center max-w-md">{error}</p>
                <button
                  onClick={() => handleSearch(customQuery || undefined)}
                  className="mt-6 px-6 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-black transition-all active:scale-95"
                >
                  Try Again
                </button>
              </div>
            )}

            {/* Empty State */}
            {!isSearching && !error && candidates.length === 0 && (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
                  <Film size={32} className="text-slate-400" />
                </div>
                <p className="text-sm font-medium text-slate-900 mb-2">No Results</p>
                <p className="text-xs text-slate-500 text-center max-w-md">
                  Try searching with a custom query above
                </p>
              </div>
            )}

            {/* Thumbnail Grid */}
            {!isSearching && !error && candidates.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {candidates.map((candidate) => (
                  <button
                    key={candidate.id}
                    onClick={() => handleSelectCandidate(candidate)}
                    disabled={isDownloading}
                    className={`
                      group relative rounded-2xl overflow-hidden border-2 transition-all
                      ${selectedCandidate?.id === candidate.id 
                        ? 'border-blue-500 ring-4 ring-blue-500/20' 
                        : 'border-slate-200 hover:border-blue-400 hover:shadow-lg'}
                      ${isDownloading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                    `}
                  >
                    {/* Thumbnail */}
                    <div className="aspect-video bg-slate-100 relative overflow-hidden">
                      <img
                        src={candidate.thumbnail_url}
                        alt={candidate.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
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

                      {/* Downloading Overlay */}
                      {selectedCandidate?.id === candidate.id && isDownloading && (
                        <div className="absolute inset-0 bg-blue-600/90 backdrop-blur-sm flex items-center justify-center">
                          <Loader2 size={32} className="text-white animate-spin" />
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="p-3 bg-white">
                      <p className="text-xs font-medium text-slate-900 line-clamp-2 text-left">
                        {candidate.title}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Download Progress */}
            {isDownloading && selectedCandidate && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-xl">
                <div className="flex items-center gap-3">
                  <Loader2 size={20} className="text-blue-600 animate-spin" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-blue-900">Downloading asset...</p>
                    <p className="text-xs text-blue-600 mt-0.5">{selectedCandidate.title}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
