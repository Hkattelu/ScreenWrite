/**
 * Script upload component
 *
 * Handles markdown file upload and displays parsed beats
 */

import { useState, useRef } from 'react'
import { uploadScript, getErrorMessage } from '../services/api'
import type { UploadResponse } from '../types/models'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, AlertCircle, FilePlus, Sparkles } from 'lucide-react'

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
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          group relative cursor-pointer
          border border-dashed rounded-2xl p-12
          flex flex-col items-center justify-center
          transition-all duration-300
          ${
            isDragging
              ? 'border-blue-500 bg-blue-50/30 shadow-sm'
              : 'border-gray-200 hover:border-gray-300 bg-white'
          }
        `}
      >
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div 
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center space-y-4"
            >
              <div className="relative mx-auto w-10 h-10">
                <motion.div 
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 border-2 border-blue-500/10 border-t-blue-500 rounded-full"
                />
              </div>
              <p className="text-sm font-semibold text-gray-900">Processing script...</p>
            </motion.div>
          ) : (
            <motion.div 
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center space-y-4"
            >
              <div className={`
                w-12 h-12 rounded-xl flex items-center justify-center mx-auto transition-all duration-300
                ${isDragging ? 'bg-blue-500 text-white' : 'bg-gray-50 text-gray-400 group-hover:bg-gray-100 group-hover:text-gray-600'}
              `}>
                {isDragging ? <Upload size={20} /> : <FilePlus size={20} />}
              </div>
              
              <div className="space-y-1">
                <p className="text-sm font-bold text-gray-900">
                  {isDragging ? 'Drop script to upload' : 'Select a script to get started'}
                </p>
                <p className="text-xs text-gray-400">
                  Markdown (.md) or Text (.txt)
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <input
          ref={fileInputRef}
          type="file"
          accept=".md,.txt"
          onChange={handleFileInput}
          disabled={isLoading}
          className="hidden"
        />
      </motion.div>

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 flex items-center justify-center gap-2 text-red-600 bg-red-50 py-2 px-4 rounded-xl border border-red-100 text-xs font-medium"
          >
             <AlertCircle size={14} />
             {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
