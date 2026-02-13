import { useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Maximize2, RefreshCcw, Film, Type, Quote, Image as ImageIcon, Upload, Check, StopCircle } from 'lucide-react'
import { getMediaUrl, searchAssets, downloadAsset, type AssetCandidate, cancelDownload } from '../services/api'
import type { Beat, DownloadProgress } from '../types/models'
import { AssetSearchModal } from './AssetSearchModal'

interface BeatAssetProps {
  sessionId: string
  beatId: string
  assetPath?: string | string[]
  downloadProgress?: DownloadProgress
  visualType?: Beat['visual_type']
  visualContent?: string
  youtubePhrase?: string
  stockKeyword?: string
  isRefreshing: boolean
  isSaving?: boolean
  reviewed?: boolean
  onMaximize: (id: string, path?: string) => void
  onSelect?: (id: string, path: string) => void
  onAssetDownloaded?: (beatId: string, filePath: string) => void
  onDownloadAsset?: (beatId: string, candidate: AssetCandidate, updateBeatQuery?: boolean) => Promise<void>
}

export function BeatAsset({
  sessionId,
  beatId,
  assetPath,
  downloadProgress,
  visualType = 'auto',
  visualContent,
  youtubePhrase,
  stockKeyword,
  isRefreshing,
  isSaving = false,
  reviewed = false,
  onMaximize,
  onSelect,
  onAssetDownloaded,
  onDownloadAsset
}: BeatAssetProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  
  const isDownloading = downloadProgress && 
    ['starting', 'downloading', 'processing'].includes(downloadProgress.status)

  const paths = Array.isArray(assetPath) ? assetPath : (assetPath ? [assetPath] : [])
  const currentPath = paths[0] || undefined

  const handleSearchAssets = async (
    sessionId: string,
    beatId: string,
    customQuery?: string
  ): Promise<AssetCandidate[]> => {
    try {
      return await searchAssets(sessionId, beatId, customQuery)
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to search assets')
    }
  }

  const handleDownloadAsset = async (
    sessionId: string,
    beatId: string,
    candidate: AssetCandidate,
    updateBeatQuery?: boolean
  ): Promise<string> => {
    try {
      if (onDownloadAsset) {
        // Use parent handler for optimistic updates
        await onDownloadAsset(beatId, candidate, updateBeatQuery)
        return '' // Path update handled via props
      }
      
      // Fallback: Background download started via API directly
      await downloadAsset(sessionId, beatId, candidate, updateBeatQuery)
      return '' // Path will be updated via session polling
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to download asset')
    }
  }

  const handleCancel = async () => {
    try {
      await cancelDownload(sessionId, beatId)
    } catch (err) {
      console.error('Failed to cancel download', err)
    }
  }

  const handleAssetSelected = (beatId: string, filePath: string) => {
    if (onAssetDownloaded) {
      onAssetDownloaded(beatId, filePath)
    }
  }

  const handleOpenModal = () => {
    setIsModalOpen(true)
  }

  const handleUploadClick = (e: React.MouseEvent | React.KeyboardEvent) => {

    // Prevent upload if reviewed (optional, but good UX)
    if (reviewed) return
    e.stopPropagation() // Prevent row click if any
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      console.log('Selected file:', e.target.files[0].name)
      // Future: Implement upload logic here
    }
  }
  
  if (visualType === 'annotation') {
    return (
      <div className={`flex items-center gap-3 px-4 py-3 bg-purple-50/50 border border-purple-100/50 rounded-xl transition-all ${reviewed ? 'opacity-30 grayscale' : ''}`}>
        <Type size={14} className="text-purple-500" />
        <div className="flex flex-col">
          <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wider">Annotation</span>
          {visualContent && <p className="text-xs font-medium text-purple-700 italic">"{visualContent}"</p>}
        </div>
      </div>
    )
  }

  if (visualType === 'citation') {
    return (
      <div className={`flex items-center gap-3 px-4 py-3 bg-amber-50/50 border border-amber-100/50 rounded-xl transition-all ${reviewed ? 'opacity-30 grayscale' : ''}`}>
        <Quote size={14} className="text-amber-500" />
        <div className="flex flex-col">
          <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">Citation</span>
          {visualContent && <p className="text-xs font-medium text-amber-700">{visualContent}</p>}
        </div>
      </div>
    )
  }

  if (visualType === 'image') {
    return (
      <div 
        onClick={handleUploadClick}
        className={`flex items-center gap-4 px-4 py-3 bg-slate-50 border border-dashed border-slate-200 rounded-xl group cursor-pointer hover:border-blue-400 transition-all ${reviewed ? 'opacity-30 grayscale pointer-events-none' : ''}`}
        role="button"
        aria-label="Upload image"
        tabIndex={reviewed ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') handleUploadClick(e)
        }}
      >
        <ImageIcon size={16} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
        <div className="flex-grow">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Static Image</span>
          <p className="text-xs font-medium text-slate-600">Click to upload asset</p>
        </div>
        <input type="file" ref={fileInputRef} className="hidden" accept="image/*" onChange={handleFileChange} disabled={reviewed} />
        <Upload size={14} className="text-slate-300 group-hover:text-blue-500" />
      </div>
    )
  }

  // Default to video/b-roll behavior for now, until other types are implemented
  const showVideo = visualType === 'auto' || visualType === 'b-roll'

  if (showVideo) {
    if (paths.length > 0) {
      return (
        <>
          <div className={`flex flex-col gap-4 transition-all duration-700 ${reviewed ? 'opacity-30 grayscale blur-[2px]' : ''}`}>
            <div className="relative group/asset overflow-hidden rounded-2xl bg-black shadow-md">
              <video 
                key={currentPath}
                src={getMediaUrl(sessionId, currentPath || '')} 
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
              <div className="absolute inset-0 bg-slate-900/40 opacity-0 group-hover/asset:opacity-100 transition-all duration-300 flex items-center justify-center gap-4">
                <button 
                  onClick={(e) => {
                    e.stopPropagation()
                    onMaximize(beatId, currentPath)
                  }}
                  className="w-10 h-10 bg-white text-slate-900 rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-all"
                  aria-label="Maximize"
                >
                  <Maximize2 size={18} />
                </button>
              </div>
              <button 
                onClick={handleOpenModal}
                disabled={isRefreshing || isDownloading}
                className="absolute top-3 right-3 p-1.5 bg-white/90 backdrop-blur-md rounded-lg shadow-sm text-slate-600 hover:text-blue-600 transition-all disabled:opacity-50"
                title="Search for new asset"
              >
                <RefreshCcw size={14} className={isRefreshing || isDownloading ? 'animate-spin' : ''} />
              </button>
            </div>

            {/* Improved Candidate Gallery */}
            {paths.length > 1 && (
              <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                {paths.map((path, idx) => (
                  <button
                    key={path}
                    onClick={() => onSelect?.(beatId, path)}
                    className={`relative flex-shrink-0 w-32 aspect-video rounded-xl overflow-hidden border-2 transition-all ${idx === 0 ? 'border-blue-500 ring-2 ring-blue-500/10' : 'border-slate-100 hover:border-slate-300 opacity-70 hover:opacity-100'}`}
                  >
                    <video 
                      src={getMediaUrl(sessionId, path)} 
                      className="w-full h-full object-cover"
                      preload="metadata"
                    />
                    {idx === 0 && (
                      <div className="absolute top-1 right-1 bg-blue-500 text-white p-0.5 rounded-full">
                        <Check size={8} strokeWidth={4} />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <AssetSearchModal
            sessionId={sessionId}
            beatId={beatId}
            isOpen={isModalOpen}
            initialQuery={(visualType as any) === 'stock' ? stockKeyword : (youtubePhrase || visualContent || '')}
            onClose={() => setIsModalOpen(false)}
            onAssetSelected={handleAssetSelected}
            onSearch={handleSearchAssets}
            onDownload={handleDownloadAsset}
            downloadProgress={downloadProgress}
          />
        </>
      )
    }

    return (
      <>
        <div className="aspect-video flex flex-col items-center justify-center gap-4 p-8 text-center bg-slate-50/50">
          <AnimatePresence mode="wait">
            {downloadProgress?.status === 'complete' ? (
              <motion.div 
                key="success"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="flex flex-col items-center gap-2"
              >
                <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center shadow-lg shadow-green-500/20">
                  <Check size={24} className="text-white" strokeWidth={3} />
                </div>
                <p className="text-[10px] font-black text-green-600 uppercase tracking-widest">Download Ready</p>
              </motion.div>
            ) : (
              <motion.div 
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center gap-4"
              >
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 ${isRefreshing || isSaving || isDownloading ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30' : 'bg-white border border-slate-100 text-slate-200 shadow-sm'}`}>
                  {isRefreshing || isSaving || isDownloading ? (
                    <RefreshCcw size={20} strokeWidth={3} className="animate-spin" />
                  ) : (
                    <Film size={20} strokeWidth={2.5} />
                  )}
                </div>
                <div className="space-y-1 w-full max-w-[200px]">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
                    {isSaving ? 'Saving Changes' : isDownloading ? 'Downloading' : isRefreshing ? 'Refreshing' : 'Asset Status'}
                  </p>
                  {isDownloading ? (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-black text-slate-800 uppercase tracking-widest">
                          {downloadProgress?.status === 'processing' ? 'Processing...' : `${Math.round(downloadProgress?.percent || 0)}%`}
                        </p>
                        <button 
                          onClick={handleCancel}
                          className="p-1 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-red-500 transition-colors"
                          title="Cancel Download"
                        >
                          <StopCircle size={14} />
                        </button>
                      </div>
                      <div className="w-full h-1 bg-slate-100 rounded-full overflow-hidden">
                        <motion.div 
                          className="h-full bg-blue-500 transition-all duration-300" 
                          style={{ width: `${downloadProgress?.percent || 0}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs font-black text-slate-800 uppercase tracking-widest">
                      {isSaving ? 'Please Wait...' : isRefreshing ? 'Processing...' : 'No Preview Available'}
                    </p>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {!isRefreshing && !isSaving && !isDownloading && downloadProgress?.status !== 'complete' && (
            <button 
              onClick={handleOpenModal}
              className="mt-2 px-6 py-2.5 bg-blue-600 text-white rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-700 transition-all active:scale-95 shadow-lg shadow-blue-500/20 border border-blue-400/20"
            >
              Fetch Asset
            </button>
          )}
          {isSaving && (
            <p className="text-[9px] text-slate-400 font-medium">
              Saving beat data before fetch...
            </p>
          )}
          {downloadProgress?.status === 'error' && (
            <p className="text-[9px] text-red-500 font-medium">
              {downloadProgress.error || 'Download failed'}
            </p>
          )}
        </div>
        
        <AssetSearchModal
          sessionId={sessionId}
          beatId={beatId}
          isOpen={isModalOpen}
          initialQuery={(visualType as any) === 'stock' ? stockKeyword : (youtubePhrase || visualContent || '')}
          onClose={() => setIsModalOpen(false)}
          onAssetSelected={handleAssetSelected}
          onSearch={handleSearchAssets}
          onDownload={handleDownloadAsset}
          downloadProgress={downloadProgress}
        />
      </>
    )
  }

  // Placeholder for other types (Phase 3)
  return (
    <>
      <div className="aspect-video flex items-center justify-center bg-gray-50 border border-gray-100 rounded-xl">
        <p className="text-xs text-gray-400">Preview not available for {visualType}</p>
      </div>
      
      <AssetSearchModal
        sessionId={sessionId}
        beatId={beatId}
        isOpen={isModalOpen}
        initialQuery={visualType === 'stock' ? stockKeyword : (youtubePhrase || visualContent || '')}
        onClose={() => setIsModalOpen(false)}
        onAssetSelected={handleAssetSelected}
        onSearch={handleSearchAssets}
        onDownload={handleDownloadAsset}
        downloadProgress={downloadProgress}
      />
    </>
  )
}