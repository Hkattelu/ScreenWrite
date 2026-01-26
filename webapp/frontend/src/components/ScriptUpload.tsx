/**
 * Script upload component
 *
 * Handles markdown file upload and displays parsed beats
 */

import { useState, useRef } from 'react'
import { uploadScript, getErrorMessage } from '../services/api'
import type { UploadResponse } from '../types/models'

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
    <div className="w-full">
      {/* Drop zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          group relative cursor-pointer
          border-2 border-dashed rounded-2xl p-16
          flex flex-col items-center justify-center
          transition-all duration-500 ease-out
          ${
            isDragging
              ? 'border-[var(--brand-primary)] bg-[var(--brand-primary)]/5 scale-[1.02] shadow-2xl shadow-[var(--brand-primary)]/10'
              : 'border-gray-200 hover:border-gray-300 bg-white/50 backdrop-blur-sm'
          }
        `}
      >
        <div className="text-center space-y-4">
          <div className={`
            text-5xl font-light transition-all duration-500
            ${isDragging ? 'text-[var(--brand-primary)] scale-125 rotate-90' : 'text-gray-300 group-hover:text-gray-400'}
          `}>
            +
          </div>
          
          <div className="space-y-1">
            <p className="text-xl font-bold text-gray-900 tracking-tight">
              {isLoading ? 'Processing Script...' : 'Drop script here'}
            </p>
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">
              Markdown or Text
            </p>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept=".md,.txt"
          onChange={handleFileInput}
          disabled={isLoading}
          className="hidden"
        />
      </div>

      {/* Minimal Error */}
      {error && (
        <div className="mt-6 text-center">
          <p className="text-sm font-medium text-red-600 bg-red-50 inline-block px-4 py-2 rounded-full border border-red-100 shadow-sm">{error}</p>
        </div>
      )}
    </div>
  )
}

