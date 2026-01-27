import { Play, Maximize2, RefreshCcw, Film } from 'lucide-react'
import { getMediaUrl } from '../services/api'
import type { Beat } from '../types/models'

interface BeatAssetProps {
  sessionId: string
  beatId: string
  assetPath?: string
  visualType?: Beat['visual_type']
  visualContent?: string
  isRefreshing: boolean
  onRefresh: (id: string) => void
  onMaximize: (id: string) => void
}

export function BeatAsset({
  sessionId,
  beatId,
  assetPath,
  visualType = 'auto',
  isRefreshing,
  onRefresh,
  onMaximize
}: BeatAssetProps) {
  
  // Default to video/b-roll behavior for now, until other types are implemented
  const showVideo = visualType === 'auto' || visualType === 'b-roll'

  if (showVideo) {
    if (assetPath) {
      return (
        <div className="relative group/asset">
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
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover/asset:opacity-100 transition-opacity flex items-center justify-center gap-4">
            <Play className="text-white fill-white" size={24} />
            <button 
              onClick={(e) => {
                e.stopPropagation()
                onMaximize(beatId)
              }}
              className="p-2 bg-white/20 hover:bg-white/40 backdrop-blur-md rounded-full text-white transition-all"
            >
              <Maximize2 size={16} />
            </button>
          </div>
          <button 
            onClick={() => onRefresh(beatId)}
            disabled={isRefreshing}
            className="absolute top-2 right-2 p-1.5 bg-white/90 backdrop-blur-md rounded-lg shadow-sm text-gray-600 hover:text-blue-600 transition-all active:scale-95 disabled:opacity-50"
            title="Refresh Footage"
          >
            <RefreshCcw size={12} className={isRefreshing ? 'animate-spin' : ''} />
          </button>
        </div>
      )
    }

    return (
      <div className="aspect-video flex flex-col items-center justify-center gap-2 p-6 text-center">
        <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
          {isRefreshing ? (
            <RefreshCcw size={14} className="text-blue-500 animate-spin" />
          ) : (
            <Film size={14} className="text-gray-300" />
          )}
        </div>
        <p className="text-xs font-bold text-gray-500 uppercase tracking-widest">
          {isRefreshing ? 'Downloading...' : 'No Preview Yet'}
        </p>
        {!isRefreshing && (
          <button 
            onClick={() => onRefresh(beatId)}
            className="text-xs font-black text-blue-500 uppercase tracking-tighter hover:underline"
          >
            Try fetching now
          </button>
        )}
      </div>
    )
  }

  // Placeholder for other types (Phase 2 & 3)
  return (
    <div className="aspect-video flex items-center justify-center bg-gray-50 border border-gray-100 rounded-xl">
      <p className="text-xs text-gray-400">Preview not available for {visualType}</p>
    </div>
  )
}
