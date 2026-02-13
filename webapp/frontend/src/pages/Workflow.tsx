import { useState, useEffect, useMemo } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import { BeatList } from '../components/BeatList'
import { ConfigPanel } from '../components/ConfigPanel'
import { exportFcpxml, updateBeats, updateConfig, getErrorMessage, getSession, fetchAssets, getStatus, updateAssets, downloadAsset, type AssetCandidate } from '../services/api'
import type { UploadResponse, Config, Beat, DownloadProgress } from '../types/models'
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

function FetchStatusPoller({ sessionId }: { sessionId: string | null }) {
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
      <div className="mb-10 p-8 bg-blue-50/50 border border-blue-100 rounded-3xl flex items-center gap-6 shadow-sm">
        <div className="w-12 h-12 rounded-2xl bg-white border border-blue-100 flex items-center justify-center shadow-sm">
          <Loader2 size={24} className="text-blue-600 animate-spin" strokeWidth={3} />
        </div>
        <div>
          <h4 className="text-base font-black text-blue-900 tracking-tight">Acquiring Assets</h4>
          <p className="text-xs text-blue-600/80 font-bold mt-1 uppercase tracking-wider">Found {status.assetCount} assets • Processing...</p>
        </div>
      </div>
    )
  }

  if (status.status === 'complete' || status.status === 'exported') {
    return (
      <div className="mb-10 p-8 bg-emerald-50/50 border border-emerald-100 rounded-3xl flex items-center gap-6 shadow-sm">
        <div className="w-12 h-12 rounded-2xl bg-white border border-emerald-100 flex items-center justify-center shadow-sm">
          <CheckCircle2 size={24} className="text-emerald-600" strokeWidth={3} />
        </div>
        <div>
          <h4 className="text-base font-black text-emerald-900 tracking-tight">Downloads Finished</h4>
          <p className="text-xs text-emerald-600/80 font-bold mt-1 uppercase tracking-wider">{status.assetCount} high-quality assets prepared</p>
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
  const [assets, setAssets] = useState<Record<string, string | string[]>>({})
  const [downloadProgress, setDownloadProgress] = useState<Record<string, DownloadProgress>>({})
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
      setDownloadProgress(state.uploadData.download_progress || {})
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
        if (data.download_progress) {
          // Merge with local state to preserve optimistic updates
          setDownloadProgress(prev => {
            const next = { ...prev }
            // Only update if backend has newer info or we aren't in a transient state
            Object.entries(data.download_progress || {}).forEach(([beatId, progress]) => {
              // Always trust backend for error/complete
              // For processing, trust backend
              // For starting, maybe trust local?
              next[beatId] = progress as DownloadProgress
            })
            return next
          })
        }
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
      setDownloadProgress(data.download_progress || {})
      
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

  const handleAssetsUpdate = async (updatedAssets: Record<string, string | string[]>) => {
    setAssets(updatedAssets)
    if (sessionId) {
      setIsSaving(true)
      try {
        await updateAssets(sessionId, updatedAssets)
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

  const handleDownloadAsset = async (beatId: string, candidate: AssetCandidate, updateBeatQuery?: boolean) => {
    if (!sessionId) return

    // Optimistic update
    setDownloadProgress(prev => ({
      ...prev,
      [beatId]: {
        status: 'starting',
        percent: 0,
        candidate_id: candidate.id,
        title: candidate.title,
        updated_at: new Date().toISOString()
      }
    }))

    try {
      const filePath = await downloadAsset(sessionId, beatId, candidate, updateBeatQuery)
      
      // Update assets map immediately
      setAssets(prev => ({ ...prev, [beatId]: filePath }))

      // Update progress to complete
      setDownloadProgress(prev => ({
        ...prev,
        [beatId]: {
          status: 'complete',
          percent: 100,
          candidate_id: candidate.id,
          title: candidate.title,
          file_path: filePath,
          updated_at: new Date().toISOString()
        }
      }))
      
    } catch (err) {
      setDownloadProgress(prev => ({
        ...prev,
        [beatId]: {
          status: 'error',
          percent: 0,
          candidate_id: candidate.id,
          title: candidate.title,
          error: getErrorMessage(err),
          updated_at: new Date().toISOString()
        }
      }))
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
    // Relaxed: Require at least 5 approvals or 100% if total < 5
    const minRequired = Math.min(beats.length, 5)
    return beats.length > 0 && reviewedIds.size >= minRequired
  }, [reviewedIds, beats.length])

  return (
    <div className="min-h-screen bg-white">
      {/* Streamlined Header */}
      <div className="border-b border-slate-100 sticky top-0 z-30 bg-white/90 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="group flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center group-hover:bg-blue-600 transition-all duration-500 shadow-lg shadow-slate-200 group-hover:shadow-blue-500/20 group-hover:scale-110 group-hover:rotate-3">
                <Film size={18} className="text-white" />
              </div>
              <span className="font-black text-base tracking-tighter text-slate-900 uppercase">
                Screen<span className="text-blue-600 italic">Write</span>
              </span>
            </Link>
            
            <AnimatePresence>
              {isSaving && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-100"
                >
                  <Save size={12} className="animate-pulse" />
                  Auto-Saving
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          <nav className="flex items-center gap-2">
            {steps.map((step, idx) => {
              const isPast = idx < currentStepIndex
              const isCurrent = idx === currentStepIndex
              
              return (
                <div key={step.id} className="flex items-center gap-2">
                  <div className={`
                    text-[10px] font-black uppercase tracking-[0.2em] px-4 py-1.5 rounded-xl transition-all duration-500
                    ${isCurrent ? 'text-blue-600 bg-blue-50 shadow-sm ring-1 ring-blue-100' : isPast ? 'text-slate-900 bg-slate-50' : 'text-slate-300'}
                  `}>
                    {step.label}
                  </div>
                  {idx < steps.length - 1 && (
                    <ChevronRight size={14} className="text-slate-200" />
                  )}
                </div>
              )
            })}
          </nav>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Loading Overlay */}
        <AnimatePresence>
          {isLoading && currentStep === 'upload' && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-white/70 backdrop-blur-md flex items-center justify-center"
            >
              <div className="flex flex-col items-center gap-6">
                <div className="w-16 h-16 rounded-3xl bg-blue-50 flex items-center justify-center shadow-inner">
                  <Loader2 size={32} className="text-blue-600 animate-spin" strokeWidth={3} />
                </div>
                <p className="text-base font-black text-slate-900 tracking-tight uppercase tracking-[0.2em]">Restoring Session</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error display */}
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mb-10 p-5 bg-red-50 border border-red-100 rounded-2xl text-red-600 text-[11px] font-black uppercase tracking-widest flex items-center gap-3 shadow-lg shadow-red-500/5"
            >
              <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-sm">
                <Info size={16} strokeWidth={3} />
              </div>
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {currentStep === 'upload' && (
            <motion.div 
              key="upload"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.02 }}
              className="max-w-xl mx-auto py-12"
            >
              <div className="mb-14 text-center">
                <h2 className="text-4xl font-black mb-4 tracking-tighter text-slate-900">Upload Script</h2>
                <p className="text-slate-400 text-base font-medium max-w-sm mx-auto leading-relaxed">Your Markdown sequence will be parsed into cinematic beats.</p>
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
                downloadProgress={downloadProgress}
                onBeatsUpdate={handleBeatsUpdate} 
                onAssetsUpdate={handleAssetsUpdate}
                onDownloadAsset={handleDownloadAsset}
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
                onToggleAllReviewed={() => {
                  const next = new Set(beats.map(b => b.id))
                  setReviewedIds(next)
                  const updatedBeats = beats.map(b => ({ ...b, reviewed: true }))
                  handleBeatsUpdate(updatedBeats)
                }}
              />
              
              <div className="mt-20 pt-10 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => setCurrentStep('upload')}
                  className="group flex items-center gap-3 text-xs font-black text-slate-400 hover:text-slate-900 transition-all uppercase tracking-widest"
                >
                  <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
                    <ArrowLeft size={16} strokeWidth={3} />
                  </div>
                  Cancel Session
                </button>
                
                <div className="flex items-center gap-8">
                  {!isReviewComplete && (
                    <span className="text-[10px] font-black text-amber-500 flex items-center gap-2 uppercase tracking-widest bg-amber-50 px-4 py-2 rounded-xl border border-amber-100 shadow-sm">
                      <Info size={14} strokeWidth={3} />
                      Review {Math.max(0, Math.min(beats.length, 5) - reviewedIds.size)} more to proceed
                    </span>
                  )}
                  {isReviewComplete && reviewedIds.size < beats.length && (
                    <span className="text-[10px] font-black text-emerald-500 flex items-center gap-2 uppercase tracking-widest bg-emerald-50 px-4 py-2 rounded-xl border border-emerald-100 shadow-sm">
                      <CheckCircle2 size={14} strokeWidth={3} />
                      Minimum review met
                    </span>
                  )}
                  <button
                    disabled={!isReviewComplete}
                    onClick={() => setCurrentStep('configure')}
                    className={`
                      px-10 py-4 rounded-2xl text-xs font-black uppercase tracking-widest transition-all flex items-center gap-3 shadow-xl active:scale-95
                      ${isReviewComplete 
                        ? 'bg-blue-600 text-white hover:bg-blue-700 shadow-blue-500/20' 
                        : 'bg-slate-100 text-slate-300 cursor-not-allowed shadow-none'}
                    `}
                  >
                    Set Pipeline
                    <ArrowRight size={18} strokeWidth={3} />
                  </button>
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
              className="max-w-2xl mx-auto"
            >
              <div className="mb-14">
                <h2 className="text-4xl font-black mb-3 tracking-tighter text-slate-900">Configuration</h2>
                <p className="text-slate-400 text-base font-medium">Fine-tune your acquisition sources and output settings.</p>
              </div>

              <div className="bg-slate-50/30 p-10 rounded-[32px] border border-slate-100 shadow-inner">
                <ConfigPanel onConfigChange={handleConfigChange} isLoading={isLoading} />
              </div>

              <div className="mt-14 flex items-center justify-between">
                <button
                  onClick={() => setCurrentStep('review')}
                  className="group flex items-center gap-3 text-xs font-black text-slate-400 hover:text-slate-900 transition-all uppercase tracking-widest"
                  disabled={isLoading}
                >
                  <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
                    <ArrowLeft size={16} strokeWidth={3} />
                  </div>
                  Back
                </button>
                <button
                  onClick={handleFetchAssets}
                  className="bg-slate-900 text-white px-10 py-4 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-black transition-all flex items-center gap-3 shadow-2xl shadow-slate-200 active:scale-95 disabled:bg-slate-100 disabled:text-slate-300"
                  disabled={isLoading}
                >
                  {isLoading ? 'Initializing...' : 'Run Pipeline'}
                  <ArrowRight size={18} strokeWidth={3} />
                </button>
              </div>
            </motion.div>
          )}

          {currentStep === 'export' && (
            <motion.div 
              key="export"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-2xl mx-auto"
            >
              <div className="text-center mb-14">
                <h2 className="text-4xl font-black mb-3 tracking-tighter text-slate-900">Timeline Ready</h2>
                <p className="text-slate-400 text-base font-medium">Generate your FCPXML production bundle.</p>
              </div>

              {/* Status Polling for Fetching */}
              <FetchStatusPoller sessionId={sessionId} />

              {exportResult ? (
                <div className="p-10 bg-white border border-slate-100 rounded-[32px] shadow-2xl shadow-slate-200">
                  <div className="flex items-center gap-3 mb-10 text-emerald-600 bg-emerald-50 w-fit px-4 py-2 rounded-xl border border-emerald-100">
                    <CheckCircle2 size={20} strokeWidth={3} />
                    <span className="font-black text-[10px] uppercase tracking-[0.2em]">Generation Successful</span>
                  </div>

                  <div className="grid grid-cols-2 gap-10 mb-12">
                    <div className="space-y-2">
                      <span className="block text-[10px] font-black text-slate-400 uppercase tracking-widest">Master File</span>
                      <p className="text-sm font-black text-slate-900 truncate bg-slate-50 px-3 py-2 rounded-lg border border-slate-100">{exportResult.filename}</p>
                    </div>
                    <div className="space-y-2">
                      <span className="block text-[10px] font-black text-slate-400 uppercase tracking-widest">Total Length</span>
                      <p className="text-sm font-black text-slate-900 bg-slate-50 px-3 py-2 rounded-lg border border-slate-100">{exportResult.estimatedDuration.toFixed(1)}s</p>
                    </div>
                  </div>

                  <a 
                    href={exportResult.downloadUrl} 
                    className="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-center py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] block transition-all shadow-xl shadow-emerald-500/20 active:scale-[0.98]"
                  >
                    Download FCPXML Bundle
                  </a>

                  <button
                    onClick={() => {
                      setSessionId(null)
                      setCurrentStep('upload')
                      setBeats([])
                      setExportResult(null)
                      setReviewedIds(new Set())
                    }}
                    className="w-full mt-8 text-[10px] font-black text-slate-300 hover:text-slate-900 uppercase tracking-widest transition-colors"
                  >
                    Archive and Start New Project
                  </button>
                </div>
              ) : (
                <div className="space-y-10">
                  <div className="bg-slate-50/50 p-10 border border-slate-100 rounded-[32px] shadow-inner">
                    <p className="text-slate-600 text-lg font-medium leading-relaxed">
                      Final step: merge your <span className="font-black text-slate-900 underline decoration-blue-500 decoration-2 underline-offset-4">{beats.length} cinematic beats</span> into a professional production timeline.
                    </p>
                  </div>

                  <div className="flex items-center justify-between pt-6">
                    <button
                      onClick={() => setCurrentStep('configure')}
                      className="group flex items-center gap-3 text-xs font-black text-slate-400 hover:text-slate-900 transition-all uppercase tracking-widest"
                      disabled={isLoading}
                    >
                      <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center group-hover:bg-slate-100 transition-colors">
                        <ArrowLeft size={16} strokeWidth={3} />
                      </div>
                      Back
                    </button>
                    <button
                      onClick={handleExport}
                      disabled={isLoading}
                      className="bg-blue-600 text-white px-12 py-5 rounded-2xl font-black text-xs uppercase tracking-[0.2em] hover:bg-blue-700 transition-all shadow-xl shadow-blue-500/20 disabled:bg-slate-100 disabled:text-slate-300 disabled:shadow-none active:scale-95"
                    >
                      {isLoading ? 'Generating Bundle...' : 'Bake Timeline'}
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