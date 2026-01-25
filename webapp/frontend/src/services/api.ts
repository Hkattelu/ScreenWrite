/**
 * API client service for footage web app
 */

import axios, { AxiosError } from 'axios'
import type { Beat, Config, ExportResponse, SessionState, UploadResponse } from '../types/models'

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
