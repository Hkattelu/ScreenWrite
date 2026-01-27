import { useState, useEffect, useMemo } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import { BeatList } from '../components/BeatList'
import { ConfigPanel } from '../components/ConfigPanel'
import { exportFcpxml, updateBeats, updateConfig, getErrorMessage, getSession, fetchAssets, getStatus } from '../services/api'
import type { UploadResponse, Config, Beat } from '../types/models'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle2, 
  ChevronRight,
  ArrowLeft,
  ArrowRight,
  Info,
  Save,
  Loader2,
  Film
} from 'lucide-react'

type WorkflowStep = 'upload' | 'review' | 'configure' | 'export'

function FetchStatusPoller({ sessionId, onComplete }: { sessionId: string | null, onComplete: () => void }) {
  const [status, setStatus] = useState<any>(null)
  const [shouldPoll, setShouldPoll] = useState(false)

  // First, fetch initial status to see if we need to poll
  useEffect(() => {
    if (!sessionId) return

    const fetchInitialStatus = async () => {
      try {
        const data = await getStatus(sessionId)
        setStatus(data)
        // Only start polling if status is 'fetching'
        setShouldPoll(data.status === 'fetching')
      } catch (e) {
        console.error("Error fetching initial status", e)
      }
    }

    fetchInitialStatus()
  }, [sessionId])

  // Poll only when fetching
  useEffect(() => {
    if (!sessionId || !shouldPoll) return

    const interval = setInterval(async () => {
      try {
        const data = await getStatus(sessionId)
        setStatus(data)
        if (data.status === 'complete' || data.status === 'error') {
          setShouldPoll(false)
        }
      } catch (e) {
        console.error("Polling error", e)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [sessionId, shouldPoll])

  if (!status || status.status === 'initialized' || status.status === 'configured') return null

  if (status.status === 'fetching') {
    return (
      <div className="mb-8 p-6 bg-blue-50 border border-blue-100 rounded-2xl flex items-center gap-4">
        <Loader2 size={24} className="text-blue-600 animate-spin" />
        <div>
          <h4 className="text-sm font-bold text-blue-900">Downloading Assets...</h4>
          <p className="text-xs text-blue-600 mt-1">Found {status.assetCount} assets so far. This usually takes 1-2 minutes.</p>
        </div>
      </div>
    )
  }

  if (status.status === 'complete' || status.status === 'exported') {
    return (
      <div className="mb-8 p-6 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center gap-4">
        <CheckCircle2 size={24} className="text-emerald-600" />
        <div>
          <h4 className="text-sm font-bold text-emerald-900">Downloads Complete</h4>
          <p className="text-xs text-emerald-600 mt-1">{status.assetCount} assets are ready for your timeline.</p>
        </div>
      </div>
    )
  }

  return null
}

export function Workflow() {
  const location = useLocation()
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('upload')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [beats, setBeats] = useState<Beat[]>([])
  const [assets, setAssets] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [exportResult, setExportResult] = useState<any>(null)
  
  const [reviewedIds, setReviewedIds] = useState<Set<string>>(new Set())

  // Handle initial load and session restoration
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    const urlSessionId = params.get('session')
    const state = location.state as any

    if (state?.uploadData) {
      setSessionId(state.uploadData.sessionId)
      setBeats(state.uploadData.beats)
      // Assets might be empty initially
      setAssets(state.uploadData.assets || {})
      setCurrentStep('review')
      // Update URL without reloading
      navigate(`/workflow?session=${state.uploadData.sessionId}`, { replace: true, state })
    } else if (urlSessionId) {
      // Load existing session from API
      loadExistingSession(urlSessionId)
    }
  }, [])

  // Poll for session updates while in review/export steps to show previews
  useEffect(() => {
    if (!sessionId || (currentStep !== 'review' && currentStep !== 'export')) return

    const pollSession = async () => {
      try {
        const data = await getSession(sessionId)
        if (data.beats) setBeats(data.beats)
        if (data.assets) setAssets(data.assets)
      } catch (err) {
        console.error("Polling error", err)
      }
    }

    const interval = setInterval(pollSession, 5000)
    return () => clearInterval(interval)
  }, [sessionId, currentStep])

  const loadExistingSession = async (id: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getSession(id)
      setSessionId(data.sessionId)
      setBeats(data.beats)
      setAssets(data.assets || {})
      
      // Restore reviewed state from beats
      const restoredReviewed = new Set(
        data.beats
          .filter(b => b.reviewed)
          .map(b => b.id)
      )
      setReviewedIds(restoredReviewed)
      
      setCurrentStep('review')
    } catch (err) {
      setError("Could not find session. It might have expired or been deleted.")
      setCurrentStep('upload')
      navigate('/workflow', { replace: true })
    } finally {
      setIsLoading(false)
    }
  }

  const handleUploadSuccess = (data: UploadResponse) => {
    setSessionId(data.sessionId)
    setBeats(data.beats)
    setError(null)
    setCurrentStep('review')
    navigate(`/workflow?session=${data.sessionId}`, { replace: true })
  }

  const handleBeatsUpdate = async (updatedBeats: Beat[]) => {
    setBeats(updatedBeats)
    if (sessionId) {
      setIsSaving(true)
      try {
        await updateBeats(sessionId, updatedBeats)
        setTimeout(() => setIsSaving(false), 800)
      } catch (err) {
        setError(getErrorMessage(err))
        setIsSaving(false)
      }
    }
  }

  const handleConfigChange = async (newConfig: Config) => {
    if (sessionId) {
      setIsSaving(true)
      try {
        await updateConfig(sessionId, newConfig)
        setTimeout(() => setIsSaving(false), 800)
      } catch (err) {
        setError(getErrorMessage(err))
        setIsSaving(false)
      }
    }
  }

  const handleFetchAssets = async () => {
    if (!sessionId) return
    setIsLoading(true)
    setError(null)
    try {
      await fetchAssets(sessionId)
      // Polling for status update would be ideal here, 
      // but for now we'll rely on the user refreshing or a basic timeout
      // In a real app, use SWR or React Query with polling
      
      // Temporary: move to export step immediately, backend runs in background
      // Ideally show a progress bar
      setCurrentStep('export')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setIsLoading(false)
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
  
  const isReviewComplete = useMemo(() => {
    return beats.length > 0 && reviewedIds.size === beats.length
  }, [reviewedIds, beats.length])

  return (
    <div className="min-h-screen bg-white">
      {/* Streamlined Header */}
      <div className="border-b border-gray-100 sticky top-0 z-30 bg-white/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="group flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-black flex items-center justify-center group-hover:bg-blue-600 transition-colors">
                <Film size={14} className="text-white" />
              </div>
              <span className="font-bold text-sm tracking-tight text-gray-900">
                ScreenWrite
              </span>
            </Link>
            
            <AnimatePresence>
              {isSaving && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-1.5 text-[10px] font-medium text-gray-400"
                >
                  <Save size={12} className="animate-pulse" />
                  Saving...
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          <nav className="flex items-center gap-1">
            {steps.map((step, idx) => {
              const isPast = idx < currentStepIndex
              const isCurrent = idx === currentStepIndex
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`
                    text-[11px] font-semibold tracking-wide px-3 py-1 rounded-lg transition-all
                    ${isCurrent ? 'text-blue-600 bg-blue-50' : isPast ? 'text-gray-900' : 'text-gray-400'}
                  `}>
                    {step.label}
                  </div>
                  {idx < steps.length - 1 && (
                    <ChevronRight size={12} className="text-gray-200 mx-0.5" />
                  )}
                </div>
              )
            })}
          </nav>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Loading Overlay */}
        <AnimatePresence>
          {isLoading && currentStep === 'upload' && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-white/60 backdrop-blur-sm flex items-center justify-center"
            >
              <div className="flex flex-col items-center gap-4">
                <Loader2 size={32} className="text-blue-600 animate-spin" />
                <p className="text-sm font-bold text-gray-900 tracking-tight">Restoring Session...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error display */}
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-8 p-3 bg-red-50 border border-red-100 rounded-xl text-red-600 text-xs font-medium flex items-center gap-2"
            >
              <Info size={14} />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {currentStep === 'upload' && (
            <motion.div 
              key="upload"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="max-w-xl mx-auto py-12"
            >
              <div className="mb-10 text-center">
                <h2 className="text-2xl font-bold mb-2">Upload Script</h2>
                <p className="text-gray-500 text-sm">Markdown files are parsed into editable segments.</p>
              </div>
              <ScriptUpload onUploadSuccess={handleUploadSuccess} />
            </motion.div>
          )}

          {currentStep === 'review' && sessionId && (
            <motion.div 
              key="review"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <BeatList 
                sessionId={sessionId}
                beats={beats} 
                assets={assets}
                onBeatsUpdate={handleBeatsUpdate} 
                editable={true}
                reviewedIds={reviewedIds}
                onToggleReviewed={(id) => {
                  const next = new Set(reviewedIds)
                  const isReviewed = !next.has(id)
                  
                  if (next.has(id)) next.delete(id)
                  else next.add(id)
                  setReviewedIds(next)
                  
                  // Persist reviewed state to backend by updating the beat
                  const updatedBeats = beats.map(b => 
                    b.id === id ? { ...b, reviewed: isReviewed } : b
                  )
                  handleBeatsUpdate(updatedBeats)
                }}
              />
              
              <div className="mt-12 pt-8 border-t border-gray-100 flex items-center justify-between">
                <button
                  onClick={() => setCurrentStep('upload')}
                  className="flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-900"
                >
                  <ArrowLeft size={16} />
                  Back to Upload
                </button>
                
                <div className="flex items-center gap-6">
                  {!isReviewComplete && (
                    <span className="text-[11px] font-medium text-amber-600 flex items-center gap-1.5">
                      <Info size={14} />
                      Review all segments to proceed
                    </span>
                  )}
                  <button
                    disabled={!isReviewComplete}
                    onClick={() => setCurrentStep('configure')}
                    className={`
                      px-8 py-3 rounded-xl text-sm font-semibold transition-all flex items-center gap-2
                      ${isReviewComplete 
                        ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm' 
                        : 'bg-gray-100 text-gray-400 cursor-not-allowed'}
                    `}
                  >
                    Configure Pipeline
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {currentStep === 'configure' && (
            <motion.div 
              key="configure"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="max-w-2xl mx-auto"
            >
              <div className="mb-10">
                <h2 className="text-2xl font-bold mb-1">Configuration</h2>
                <p className="text-gray-500 text-sm">Adjust search sources and output settings.</p>
              </div>

              <div className="bg-gray-50/50 p-8 rounded-2xl border border-gray-100">
                <ConfigPanel onConfigChange={handleConfigChange} isLoading={isLoading} />
              </div>

              <div className="mt-10 flex items-center justify-between">
                <button
                  onClick={() => setCurrentStep('review')}
                  className="flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-900"
                  disabled={isLoading}
                >
                  <ArrowLeft size={16} />
                  Back to Review
                </button>
                <button
                  onClick={handleFetchAssets}
                  className="bg-gray-900 text-white px-8 py-3 rounded-xl text-sm font-semibold hover:bg-black transition-all flex items-center gap-2"
                  disabled={isLoading}
                >
                  {isLoading ? 'Starting Downloads...' : 'Fetch Assets & Continue'}
                  <ArrowRight size={16} />
                </button>
              </div>
            </motion.div>
          )}

          {currentStep === 'export' && (
            <motion.div 
              key="export"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="max-w-2xl mx-auto"
            >
              <div className="text-center mb-10">
                <h2 className="text-2xl font-bold mb-2">Ready for Export</h2>
                <p className="text-gray-500 text-sm">Generate your FCPXML timeline.</p>
              </div>

              {/* Status Polling for Fetching */}
              <FetchStatusPoller sessionId={sessionId} onComplete={() => {}} />

              {exportResult ? (
                <div className="p-8 bg-gray-50 border border-gray-100 rounded-2xl">
                  <div className="flex items-center gap-2 mb-8 text-emerald-600">
                    <CheckCircle2 size={20} />
                    <span className="font-bold text-sm">Generation Complete</span>
                  </div>

                  <div className="grid grid-cols-2 gap-8 mb-10">
                    <div>
                      <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Timeline</span>
                      <p className="text-sm font-medium text-gray-900 truncate">{exportResult.filename}</p>
                    </div>
                    <div>
                      <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Duration</span>
                      <p className="text-sm font-medium text-gray-900">{exportResult.estimatedDuration.toFixed(1)}s</p>
                    </div>
                  </div>

                  <a 
                    href={exportResult.downloadUrl} 
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-center py-3 rounded-xl font-bold text-sm block transition-all shadow-sm"
                  >
                    Download FCPXML
                  </a>

                  <button
                    onClick={() => {
                      setSessionId(null)
                      setCurrentStep('upload')
                      setBeats([])
                      setExportResult(null)
                      setReviewedIds(new Set())
                    }}
                    className="w-full mt-6 text-xs font-semibold text-gray-400 hover:text-gray-900 transition-colors"
                  >
                    Start a New Project
                  </button>
                </div>
              ) : (
                <div className="space-y-8">
                  <div className="bg-white p-8 border border-gray-100 rounded-2xl shadow-sm">
                    <p className="text-gray-600 leading-relaxed">
                      Final step: transform your <span className="font-bold text-gray-900">{beats.length} reviewed segments</span> into a high-quality timeline file.
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-4">
                    <button
                      onClick={() => setCurrentStep('configure')}
                      className="text-sm font-medium text-gray-500 hover:text-gray-900"
                      disabled={isLoading}
                    >
                      Back
                    </button>
                    <button
                      onClick={handleExport}
                      disabled={isLoading}
                      className="bg-blue-600 text-white px-10 py-3 rounded-xl font-bold text-sm hover:bg-blue-700 transition-all shadow-sm disabled:bg-gray-100 disabled:text-gray-400"
                    >
                      {isLoading ? 'Generating...' : 'Generate FCPXML'}
                    </button>
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