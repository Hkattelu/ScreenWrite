import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import { BeatList } from '../components/BeatList'
import { ConfigPanel } from '../components/ConfigPanel'
import { exportFcpxml, updateBeats, updateConfig, getErrorMessage } from '../services/api'
import type { UploadResponse, Config, Beat } from '../types/models'
import { motion, AnimatePresence } from 'framer-motion'

type WorkflowStep = 'upload' | 'review' | 'configure' | 'export'

export function Workflow() {
  const location = useLocation()
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('upload')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [beats, setBeats] = useState<Beat[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [exportResult, setExportResult] = useState<any>(null)

  // Initialize from Home page if upload was done there
  useEffect(() => {
    const state = location.state as any
    if (state?.uploadData) {
      setSessionId(state.uploadData.sessionId)
      setBeats(state.uploadData.beats)
      setCurrentStep('review')
    }
  }, [])

  const handleUploadSuccess = (data: UploadResponse) => {
    setSessionId(data.sessionId)
    setBeats(data.beats)
    setError(null)
    setCurrentStep('review')
  }

  const handleBeatsUpdate = async (updatedBeats: Beat[]) => {
    setBeats(updatedBeats)
    if (sessionId) {
      try {
        await updateBeats(sessionId, updatedBeats)
      } catch (err) {
        setError(getErrorMessage(err))
      }
    }
  }

  const handleConfigChange = async (newConfig: Config) => {
    if (sessionId) {
      try {
        await updateConfig(sessionId, newConfig)
      } catch (err) {
        setError(getErrorMessage(err))
      }
    }
  }

  const handleExport = async () => {
    if (!sessionId) return

    setIsLoading(true)
    setError(null)

    try {
      const result = await exportFcpxml(sessionId, {
        filename: 'timeline.fcpxml',
      })
      setExportResult(result)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
    }
  }

  const steps: { id: WorkflowStep; label: string }[] = [
    { id: 'upload', label: 'Upload' },
    { id: 'review', label: 'Review' },
    { id: 'configure', label: 'Configure' },
    { id: 'export', label: 'Export' },
  ]

  const currentStepIndex = steps.findIndex((s) => s.id === currentStep)

  return (
    <div className="min-h-screen bg-white py-12">
      <div className="max-w-5xl mx-auto px-6">
        {/* Minimal Progress Indicator */}
        {sessionId && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12 flex items-center justify-between"
          >
            <div className="flex items-center gap-4">
              <span className="font-mono text-xs font-bold text-gray-300 uppercase tracking-widest">
                Step {currentStepIndex + 1} of {steps.length}
              </span>
              <h1 className="text-xl font-bold text-black tracking-tight uppercase">
                {steps[currentStepIndex].label}
              </h1>
            </div>
            
            <div className="flex gap-1">
              {steps.map((_, idx) => (
                <motion.div 
                  key={idx} 
                  initial={false}
                  animate={{ 
                    backgroundColor: idx <= currentStepIndex ? 'var(--brand-primary)' : '#f3f4f6',
                    width: idx === currentStepIndex ? 48 : 32 
                  }}
                  className="h-1.5 rounded-full transition-all duration-500"
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* Error display */}
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8 p-4 bg-red-50 border border-red-100 rounded-lg text-red-600 text-sm font-medium flex items-center gap-3 overflow-hidden"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Step content */}
        <AnimatePresence mode="wait">
          {currentStep === 'upload' && (
            <motion.div 
              key="upload"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="max-w-xl mx-auto py-12"
            >
              <div className="mb-8 flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Upload Script</h2>
                <Link 
                  to="/syntax-guide" 
                  className="text-gray-400 hover:text-black font-medium text-xs uppercase tracking-wider transition-colors"
                >
                  View Syntax Guide
                </Link>
              </div>
              <ScriptUpload onUploadSuccess={handleUploadSuccess} />
            </motion.div>
          )}

          {currentStep === 'review' && sessionId && (
            <motion.div 
              key="review"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="w-full"
            >
              <div className="pb-12">
                <BeatList beats={beats} onBeatsUpdate={handleBeatsUpdate} editable={true} />
              </div>
              
              {/* Minimal Footer Actions */}
              <div className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-xl border-t border-gray-100 py-4 px-6 z-20">
                <div className="max-w-5xl mx-auto flex justify-between items-center">
                  <span className="font-mono text-xs font-bold text-gray-400 uppercase tracking-widest">
                      {beats.length} Segments Parsed
                  </span>
                  <div className="flex gap-4">
                    <button
                      onClick={() => setCurrentStep('upload')}
                      className="px-6 py-2 text-sm font-bold text-gray-400 hover:text-black uppercase tracking-widest transition-colors"
                    >
                      Back
                    </button>
                    <button
                      onClick={() => setCurrentStep('configure')}
                      className="btn-primary py-2 px-8 text-sm uppercase tracking-widest"
                    >
                      Configure
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {currentStep === 'configure' && (
            <motion.div 
              key="configure"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="max-w-2xl mx-auto"
            >
              <ConfigPanel onConfigChange={handleConfigChange} isLoading={isLoading} />

              <div className="mt-12 flex gap-4 justify-between items-center">
                <button
                  onClick={() => setCurrentStep('review')}
                  className="px-6 py-2 text-sm font-bold text-gray-400 hover:text-black uppercase tracking-widest transition-colors"
                  disabled={isLoading}
                >
                  Back to Review
                </button>
                <button
                  onClick={() => setCurrentStep('export')}
                  className="btn-primary px-10 uppercase tracking-widest text-sm"
                  disabled={isLoading}
                >
                  Go to Export
                </button>
              </div>
            </motion.div>
          )}

          {currentStep === 'export' && (
            <motion.div 
              key="export"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="max-w-2xl mx-auto py-12"
            >
              <h2 className="text-3xl font-bold tracking-tighter mb-8">Generate Timeline</h2>

              {exportResult ? (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="space-y-8"
                >
                  <div className="p-8 bg-gray-50 rounded-2xl border border-gray-100">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      <h3 className="text-lg font-bold uppercase tracking-tight">Timeline Ready</h3>
                    </div>

                    <div className="grid grid-cols-2 gap-y-6 gap-x-12 mb-8">
                      <div>
                        <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Filename</span>
                        <p className="font-mono text-sm text-gray-900 truncate">{exportResult.filename}</p>
                      </div>
                      <div>
                        <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Segments</span>
                        <p className="font-mono text-sm text-gray-900">{exportResult.beatCount}</p>
                      </div>
                      <div>
                        <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Duration</span>
                        <p className="font-mono text-sm text-gray-900">{exportResult.estimatedDuration.toFixed(1)}s</p>
                      </div>
                      <div>
                        <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Size</span>
                        <p className="font-mono text-sm text-gray-900">{(exportResult.fileSize / 1024).toFixed(2)} KB</p>
                      </div>
                    </div>

                    <motion.a 
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      href={exportResult.downloadUrl} 
                      className="btn-success block text-center py-4 uppercase tracking-widest text-sm font-bold shadow-lg shadow-emerald-100"
                    >
                      Download FCPXML
                    </motion.a>
                  </div>

                  <button
                    onClick={() => {
                      setSessionId(null)
                      setCurrentStep('upload')
                      setBeats([])
                      setExportResult(null)
                    }}
                    className="w-full py-4 text-xs font-bold text-gray-400 hover:text-black uppercase tracking-widest transition-colors"
                  >
                    Start New Project
                  </button>
                </motion.div>
              ) : (
                <div className="space-y-8">
                  <p className="text-xl text-gray-500 font-light leading-relaxed">
                    Your {beats.length} segments are ready to be transformed into a DaVinci Resolve timeline.
                  </p>

                  <div className="bg-blue-50/50 p-6 rounded-xl border border-blue-100/50">
                    <p className="text-xs text-blue-600 font-medium leading-relaxed">
                      <span className="font-bold uppercase mr-2">Note:</span> 
                      Asset downloading happens in the background. You can preview and review
                      downloaded assets before finalizing.
                    </p>
                  </div>

                  <div className="flex gap-6 items-center pt-4">
                    <button
                      onClick={() => setCurrentStep('configure')}
                      className="text-sm font-bold text-gray-400 hover:text-black uppercase tracking-widest transition-colors"
                      disabled={isLoading}
                    >
                      Back
                    </button>
                    <motion.button
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      onClick={handleExport}
                      disabled={isLoading}
                      className="btn-primary flex-grow py-4 uppercase tracking-widest text-sm"
                    >
                      {isLoading ? 'Processing...' : 'Generate Timeline'}
                    </motion.button>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}