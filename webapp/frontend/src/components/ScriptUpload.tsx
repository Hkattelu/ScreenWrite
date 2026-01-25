/**
 * Script upload component
 *
 * Handles markdown file upload and displays parsed beats
 */

import { useState, useRef } from 'react'
import { uploadScript, getErrorMessage } from '../services/api'
import type { Beat, UploadResponse } from '../types/models'

interface ScriptUploadProps {
  onUploadSuccess: (data: UploadResponse) => void
}

export function ScriptUpload({ onUploadSuccess }: ScriptUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFile(files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file: File) => {
    // Validate file type
    if (!file.name.endsWith('.md') && !file.name.endsWith('.txt')) {
      setError('Please upload a .md or .txt file')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await uploadScript(file)
      onUploadSuccess(response)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Upload Your Script</h2>

        {/* Drop zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'
          }`}
        >
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-4"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20a4 4 0 004 4h24a4 4 0 004-4V20m-8-12l-5.293-5.293a1 1 0 00-1.414 0L12 9m14-1v6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          <p className="text-gray-700 font-medium mb-2">Drop your markdown script here</p>
          <p className="text-gray-500 text-sm mb-4">or</p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".md,.txt"
            onChange={handleFileInput}
            disabled={isLoading}
            className="hidden"
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="btn-primary"
          >
            {isLoading ? 'Uploading...' : 'Choose File'}
          </button>

          <p className="text-gray-500 text-xs mt-4">Markdown (.md) or Text (.txt) files only</p>
        </div>

        {/* Error message */}
        {error && <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">{error}</div>}

        {/* Help text */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Script Format</h3>
          <p className="text-sm text-blue-800">
            Your markdown should have headers (##) for sections and text content describing the footage you need for
            each segment. Duration is calculated automatically.
          </p>
        </div>
      </div>
    </div>
  )
}
