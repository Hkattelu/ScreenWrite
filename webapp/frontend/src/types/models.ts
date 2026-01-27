/**
 * TypeScript types for ScreenWrite web app
 */

export interface Beat {
  id: string
  text: string
  duration: number
  stock_keyword: string
  youtube_phrase: string
  header?: string
  reviewed?: boolean
}

export interface UploadResponse {
  sessionId: string
  beats: Beat[]
  summary: {
    totalBeats: number
    estimatedDuration: number
    warnings: string[]
  }
}

export interface SessionState {
  sessionId: string
  status: 'initialized' | 'configured' | 'fetching' | 'complete' | 'error'
  config: {
    youtube_enabled?: boolean
    pexels_enabled?: boolean
    pexels_api_key?: string
    output_dir?: string
  }
  beats: Beat[]
  assets: Record<string, string>
}

export interface Config {
  youtubeEnabled: boolean
  pexelsEnabled: boolean
  pexelsApiKey?: string
  outputDir?: string
}

export interface Asset {
  id: string
  beatId: string
  source: 'youtube' | 'pexels'
  title: string
  thumbnail?: string
  url: string
  duration: number
  fileSize?: number
  status: 'pending' | 'downloading' | 'success' | 'failed'
}

export interface ExportResponse {
  sessionId: string
  fcpxmlPath: string
  downloadUrl: string
  filename: string
  assetCount: number
  beatCount: number
  estimatedDuration: number
  fileSize: number
  generatedAt: string
}

export interface ProgressUpdate {
  type: 'progress' | 'complete' | 'error'
  data: {
    currentBeat: number
    totalBeats: number
    successCount: number
    failureCount: number
    message?: string
  }
}

