import { useRef } from 'react'
import { Play, Maximize2, RefreshCcw, Film, Type, Quote, Image as ImageIcon, Upload } from 'lucide-react'
import { getMediaUrl } from '../services/api'
import type { Beat } from '../types/models'

interface BeatAssetProps {
  sessionId: string
  beatId: string
  assetPath?: string
  visualType?: Beat['visual_type']
  visualContent?: string
  isRefreshing: boolean
  reviewed?: boolean
  onRefresh: (id: string) => void
  onMaximize: (id: string) => void
}

export function BeatAsset({
  sessionId,
  beatId,
  assetPath,
  visualType = 'auto',
  visualContent,
  isRefreshing,
  reviewed = false,
  onRefresh,
  onMaximize
}: BeatAssetProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

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
      <div className={`aspect-video flex flex-col items-center justify-center gap-4 bg-purple-50 border border-purple-100 rounded-2xl p-8 text-center group transition-all duration-700 ${reviewed ? 'opacity-30 grayscale blur-[2px]' : ''}`}>
        <div className="w-12 h-12 rounded-2xl bg-white border border-purple-100 flex items-center justify-center text-purple-600 shadow-sm group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
          <Type size={20} strokeWidth={2.5} />
        </div>
        <div className="space-y-2">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-purple-400">Layer Type</span>
          <p className="text-sm font-black text-purple-900 tracking-tight uppercase">ANNOTATION</p>
          {visualContent && (
            <p className="text-xs text-purple-700 font-bold mt-2 leading-relaxed max-w-[240px] mx-auto bg-white/50 px-3 py-1.5 rounded-xl border border-purple-100/50">
              "{visualContent}"
            </p>
          )}
        </div>
      </div>
    )
  }

  if (visualType === 'citation') {
    return (
      <div className={`aspect-video flex flex-col items-center justify-center gap-4 bg-amber-50 border border-amber-100 rounded-2xl p-8 text-center group transition-all duration-700 ${reviewed ? 'opacity-30 grayscale blur-[2px]' : ''}`}>
        <div className="w-12 h-12 rounded-2xl bg-white border border-amber-100 flex items-center justify-center text-amber-600 shadow-sm group-hover:scale-110 group-hover:-rotate-3 transition-all duration-500">
          <Quote size={20} strokeWidth={2.5} />
        </div>
        <div className="space-y-2">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-amber-400">Reference</span>
          <p className="text-sm font-black text-amber-900 tracking-tight uppercase">CITATION</p>
          {visualContent && (
            <p className="text-xs text-amber-700 font-bold mt-2 leading-relaxed max-w-[240px] mx-auto bg-white/50 px-3 py-1.5 rounded-xl border border-amber-100/50">
              {visualContent}
            </p>
          )}
        </div>
      </div>
    )
  }

  if (visualType === 'image') {
    return (
      <div 
        onClick={handleUploadClick}
        className={`aspect-video flex flex-col items-center justify-center gap-4 bg-indigo-50/30 border-2 border-dashed border-indigo-200 rounded-2xl p-8 text-center group relative cursor-pointer hover:bg-indigo-50 hover:border-indigo-400 focus:outline-none focus:ring-8 focus:ring-indigo-500/5 focus:border-indigo-500/40 transition-all duration-500 ${reviewed ? 'opacity-30 grayscale blur-[2px] pointer-events-none' : ''}`}
        role="button"
        aria-label="Upload image asset"
        tabIndex={reviewed ? -1 : 0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleUploadClick(e)
          }
        }}
      >
        <div className="w-14 h-14 rounded-3xl bg-white border border-indigo-100 flex items-center justify-center text-indigo-500 shadow-md group-hover:scale-110 group-hover:shadow-xl group-hover:text-indigo-600 transition-all duration-500">
          <ImageIcon size={24} strokeWidth={2.5} />
        </div>
        <div className="space-y-4">
          <div className="space-y-1">
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-indigo-400">Input Needed</span>
            <p className="text-sm font-black text-indigo-900 tracking-tight uppercase group-hover:text-indigo-700 transition-colors">Static Image</p>
          </div>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
            disabled={reviewed}
          />
          <div className="flex items-center gap-2.5 px-5 py-2.5 bg-indigo-600 rounded-xl shadow-lg shadow-indigo-500/20 text-xs font-black text-white group-hover:bg-indigo-700 transition-all active:scale-95">
            <Upload size={14} strokeWidth={3} />
            Upload Asset
          </div>
        </div>
      </div>
    )
  }

  // Default to video/b-roll behavior for now, until other types are implemented
  const showVideo = visualType === 'auto' || visualType === 'b-roll'

  if (showVideo) {
    if (assetPath) {
      return (
        <div className={`relative group/asset transition-all duration-700 overflow-hidden ${reviewed ? 'opacity-30 grayscale blur-[2px]' : ''}`}>
          <video 
            src={getMediaUrl(sessionId, assetPath)} 
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
          <div className="absolute inset-0 bg-slate-900/60 opacity-0 group-hover/asset:opacity-100 group-focus-within/asset:opacity-100 transition-all duration-500 flex items-center justify-center gap-6 backdrop-blur-[2px]">
            <div className="w-16 h-16 rounded-full bg-white/10 border border-white/20 flex items-center justify-center backdrop-blur-md">
              <Play className="text-white fill-white translate-x-0.5" size={32} />
            </div>
            <button 
              onClick={(e) => {
                e.stopPropagation()
                onMaximize(beatId)
              }}
              className="w-12 h-12 bg-white hover:bg-white/90 text-slate-900 rounded-full flex items-center justify-center shadow-xl transition-all hover:scale-110 active:scale-90 focus:outline-none focus:ring-4 focus:ring-white/20"
              aria-label="Maximize video preview"
            >
              <Maximize2 size={20} strokeWidth={2.5} />
            </button>
          </div>
          <button 
            onClick={() => onRefresh(beatId)}
            disabled={isRefreshing}
            className="absolute top-4 right-4 p-2 bg-white/95 backdrop-blur-xl rounded-xl shadow-xl text-slate-600 hover:text-blue-600 focus:text-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-500/20 transition-all active:scale-90 disabled:opacity-50"
            title="Refresh Footage"
            aria-label="Refresh footage"
          >
            <RefreshCcw size={14} strokeWidth={2.5} className={isRefreshing ? 'animate-spin' : ''} />
          </button>
        </div>
      )
    }

    return (
      <div className="aspect-video flex flex-col items-center justify-center gap-4 p-8 text-center bg-slate-50/50">
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-500 ${isRefreshing ? 'bg-blue-50 text-blue-500 shadow-inner' : 'bg-white border border-slate-100 text-slate-200 shadow-sm'}`}>
          {isRefreshing ? (
            <RefreshCcw size={20} strokeWidth={2.5} className="animate-spin" />
          ) : (
            <Film size={20} strokeWidth={2.5} />
          )}
        </div>
        <div className="space-y-1">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
            {isRefreshing ? 'Processing' : 'Asset Status'}
          </p>
          <p className="text-xs font-black text-slate-800 uppercase tracking-widest">
            {isRefreshing ? 'Downloading...' : 'No Preview Available'}
          </p>
        </div>
        {!isRefreshing && (
          <button 
            onClick={() => onRefresh(beatId)}
            className="mt-2 px-5 py-2 bg-white border border-slate-200 rounded-xl text-[10px] font-black text-blue-600 uppercase tracking-widest hover:border-blue-400 hover:bg-blue-50 transition-all active:scale-95 shadow-sm"
          >
            Fetch Asset
          </button>
        )}
      </div>
    )
  }

  // Placeholder for other types (Phase 3)
  return (
    <div className="aspect-video flex items-center justify-center bg-gray-50 border border-gray-100 rounded-xl">
      <p className="text-xs text-gray-400">Preview not available for {visualType}</p>
    </div>
  )
}