/**
 * API client service for ScreenWrite web app
 */

import axios, { AxiosError } from 'axios'
import type { Beat, Config, ExportResponse, SessionState, UploadResponse, SessionListItem } from '../types/models'


const API_BASE = '/api'

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

/**
 * Upload and parse a markdown script
 */
export async function uploadScript(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * Process the onboarding sample script
 */
export async function uploadSample(): Promise<UploadResponse> {
  const response = await apiClient.post<UploadResponse>('/upload/sample')
  return response.data
}

/**
 * Get current session state
 */
export async function getSession(sessionId: string): Promise<SessionState> {
  const response = await apiClient.get<SessionState>(`/session/${sessionId}`)
  return response.data
}

/**
 * Update session configuration
 */
export async function updateConfig(sessionId: string, config: Config): Promise<{ success: boolean }> {
  const response = await apiClient.put(`/session/${sessionId}/config`, {
    youtubeEnabled: config.youtubeEnabled,
    pexelsEnabled: config.pexelsEnabled,
    pexelsApiKey: config.pexelsApiKey,
    outputDir: config.outputDir,
  })
  return response.data
}

/**
 * Update beats for a session
 */
export async function updateBeats(sessionId: string, beats: Beat[]): Promise<{ success: boolean }> {
  const response = await apiClient.put(`/session/${sessionId}/beats`, { beats })
  return response.data
}

/**
 * Update assets for a session (e.g. selection)
 */
export async function updateAssets(sessionId: string, assets: Record<string, string | string[]>): Promise<{ success: boolean }> {
  const response = await apiClient.put(`/session/${sessionId}/assets`, { assets })
  return response.data
}

/**
 * Get session status
 */
export async function getStatus(
  sessionId: string,
): Promise<{
  sessionId: string
  status: string
  beatCount: number
  assetCount: number
}> {
  const response = await apiClient.get(`/session/${sessionId}/status`)
  return response.data
}

/**
 * Delete a session
 */
export async function deleteSession(sessionId: string): Promise<{ success: boolean }> {
  const response = await apiClient.delete(`/session/${sessionId}/delete`)
  return response.data
}

/**
 * Export FCPXML
 */
export async function exportFcpxml(
  sessionId: string,
  options?: { filename?: string; resolveIntegration?: boolean },
): Promise<ExportResponse> {
  const response = await apiClient.post<ExportResponse>(`/session/${sessionId}/export`, options || {})
  return response.data
}

/**
 * Trigger asset fetching
 */
export async function fetchAssets(sessionId: string): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post(`/session/${sessionId}/fetch`)
  return response.data
}

/**
 * Trigger single asset refresh
 */
export async function refreshBeatAsset(sessionId: string, beatId: string): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post(`/session/${sessionId}/fetch/${beatId}`)
  return response.data
}

/**
 * Get media URL for a file
 */
export function getMediaUrl(sessionId: string, filename: string): string {
  if (!filename) return ''
  // If it's already a full URL, return it
  if (filename.startsWith('http')) return filename
  // Otherwise, construct the media API URL
  const baseName = filename.split(/[\\/]/).pop() || filename
  return `/api/session/${sessionId}/media/${baseName}`
}

/**
 * List all sessions (recent projects)
 */
export async function listSessions(): Promise<SessionListItem[]> {
  const response = await apiClient.get<{ sessions: SessionListItem[] }>('/sessions')
  return response.data.sessions
}

/**
 * Search for asset candidates without downloading
 */
export async function searchAssets(
  sessionId: string,
  beatId: string,
  customQuery?: string
): Promise<AssetCandidate[]> {
  const response = await apiClient.post(`/session/${sessionId}/search/${beatId}`, {
    custom_query: customQuery,
  }, {
    timeout: 30000 // 30 second timeout for search operations
  })
  return response.data.candidates || []
}

/**
 * Download a specific asset candidate
 */
export async function downloadAsset(
  sessionId: string,
  beatId: string,
  candidate: AssetCandidate,
  updateBeatQuery?: boolean
): Promise<string> {
  const response = await apiClient.post(`/session/${sessionId}/download/${beatId}`, {
    candidate_id: candidate.id,
    source: candidate.source,
    metadata: candidate.metadata,
    update_beat_query: updateBeatQuery
  })
  return response.data.file_path
}

/**
 * Cancel an ongoing download
 */
export async function cancelDownload(
  sessionId: string,
  beatId: string
): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post(`/session/${sessionId}/cancel/${beatId}`)
  return response.data
}

/**
 * Asset candidate interface
 */
export interface AssetCandidate {
  id: string
  title: string
  thumbnail_url: string
  duration: number
  source: 'youtube' | 'pexels'
  metadata: Record<string, any>
}

/**
 * Search for videos in Simple B-Roll mode
 */
export async function searchSimpleBRoll(query: string): Promise<AssetCandidate[]> {
  const response = await apiClient.post<{ success: boolean; candidates: AssetCandidate[] }>('/simple-broll/search', {
    query,
  })
  return response.data.candidates || []
}

/**
 * Download a segment of a video in Simple B-Roll mode
 * Returns a Blob that can be saved as a file
 */
export async function downloadSimpleBRoll(candidate: AssetCandidate, startTime: number, duration: number): Promise<Blob> {
  const response = await apiClient.post('/simple-broll/download', {
    candidate,
    start_time: startTime,
    duration,
  }, {
    responseType: 'blob',
    timeout: 120000 // 2 minute timeout for download + processing
  })
  return response.data
}

/**
 * Handle API errors with user-friendly messages
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ error?: string }>
    return axiosError.response?.data?.error || axiosError.message || 'An error occurred'
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An unexpected error occurred'
}

