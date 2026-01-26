/**
 * Main workflow page
 *
 * Multi-step wizard for the entire video generation process
 */

import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import { BeatList } from '../components/BeatList'
import { ConfigPanel } from '../components/ConfigPanel'
import { exportFcpxml, updateBeats, updateConfig, getErrorMessage } from '../services/api'
import type { UploadResponse, Config, Beat } from '../types/models'

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

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Step indicator */}
        {sessionId && (
          <div className="mb-12">
            <div className="flex justify-between mb-8">
              {steps.map((step, idx) => (
                <div key={step.id} className="flex-1">
                  <div
                    className={`flex items-center ${
                      idx < steps.length - 1 ? 'pb-4' : ''
                    }`}
                  >
                    <button
                      onClick={() => {
                        const stepIndex = steps.findIndex((s) => s.id === step.id)
                        const currentIndex = steps.findIndex((s) => s.id === currentStep)
                        if (stepIndex <= currentIndex) {
                          setCurrentStep(step.id)
                        }
                      }}
                      className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-colors ${
                        currentStep === step.id
                          ? 'bg-blue-500 text-white'
                          : steps.findIndex((s) => s.id === step.id) < steps.findIndex((s) => s.id === currentStep)
                            ? 'bg-green-500 text-white'
                            : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {steps.findIndex((s) => s.id === step.id) < steps.findIndex((s) => s.id === currentStep) ? '✓' : idx + 1}
                    </button>
                    <span className="ml-2 font-medium text-gray-700">{step.label}</span>
                  </div>
                  {idx < steps.length - 1 && (
                    <div
                      className={`h-12 w-1 ml-5 ${
                        steps.findIndex((s) => s.id === step.id) < steps.findIndex((s) => s.id === currentStep)
                          ? 'bg-green-500'
                          : 'bg-gray-200'
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-medium">Error: {error}</p>
          </div>
        )}

        {/* Step content */}
         {currentStep === 'upload' && (
           <div>
             <div className="mb-6 flex items-center justify-between">
               <h2 className="text-2xl font-bold">Upload Your Script</h2>
               <Link 
                 to="/syntax-guide" 
                 className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
               >
                 📖 View Syntax Guide
               </Link>
             </div>
             <ScriptUpload onUploadSuccess={handleUploadSuccess} />
           </div>
         )}

        {currentStep === 'review' && sessionId && (
          <div className="max-w-4xl mx-auto">
             {/* Header */}
            <div className="mb-8 flex items-end justify-between px-4">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Review Beats</h2>
                <p className="text-gray-500 mt-2">Fine-tune your script segments before generation.</p>
              </div>
            </div>

            {/* List Container */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200">
              <div className="px-6 pb-6 pt-2">
                 <BeatList beats={beats} onBeatsUpdate={handleBeatsUpdate} editable={true} />
              </div>
              
              {/* Footer Actions */}
              <div className="bg-gray-50 px-6 py-4 border-t border-gray-100 flex gap-4 justify-between items-center rounded-b-2xl">
                 <span className="text-sm text-gray-400 font-medium">
                    {beats.length} segments ready
                 </span>
                 <div className="flex gap-4">
                  <button
                    onClick={() => setCurrentStep('upload')}
                    className="px-6 py-2.5 rounded-lg font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-200 transition-colors"
                  >
                    Back
                  </button>
                  <button
                    onClick={() => setCurrentStep('configure')}
                    className="px-6 py-2.5 rounded-lg font-medium text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition-all hover:shadow-md"
                  >
                    Continue
                  </button>
                 </div>
              </div>
            </div>
          </div>
        )}

        {currentStep === 'configure' && (
          <div>
            <ConfigPanel onConfigChange={handleConfigChange} isLoading={isLoading} />

            <div className="max-w-2xl mx-auto mt-6 flex gap-4 justify-end">
              <button
                onClick={() => setCurrentStep('review')}
                className="btn-secondary"
                disabled={isLoading}
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep('export')}
                className="btn-primary"
                disabled={isLoading}
              >
                Proceed to Export
              </button>
            </div>
          </div>
        )}

        {currentStep === 'export' && (
          <div className="card max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Generate Timeline</h2>

            {exportResult ? (
              <div>
                <div className="p-6 bg-green-50 border border-green-200 rounded-lg mb-6">
                  <h3 className="text-lg font-semibold text-green-900 mb-2">✓ Timeline Generated Successfully</h3>
                  <p className="text-green-800 mb-4">Your FCPXML file is ready to download and import into DaVinci Resolve.</p>

                  <div className="grid grid-cols-2 gap-4 text-sm mb-6">
                    <div>
                      <span className="text-green-700 font-medium">File:</span>
                      <p className="text-green-900">{exportResult.filename}</p>
                    </div>
                    <div>
                      <span className="text-green-700 font-medium">Beats:</span>
                      <p className="text-green-900">{exportResult.beatCount}</p>
                    </div>
                    <div>
                      <span className="text-green-700 font-medium">Duration:</span>
                      <p className="text-green-900">{exportResult.estimatedDuration.toFixed(1)}s</p>
                    </div>
                    <div>
                      <span className="text-green-700 font-medium">File Size:</span>
                      <p className="text-green-900">{(exportResult.fileSize / 1024).toFixed(2)} KB</p>
                    </div>
                  </div>

                  <a href={exportResult.downloadUrl} className="btn-success inline-block">
                    Download FCPXML
                  </a>
                </div>

                <button
                  onClick={() => {
                    setSessionId(null)
                    setCurrentStep('upload')
                    setBeats([])
                    setExportResult(null)
                  }}
                  className="btn-primary w-full"
                >
                  Start New Project
                </button>
              </div>
            ) : (
              <div>
                <p className="text-gray-700 mb-6">
                  Ready to generate your FCPXML timeline? Your {beats.length} beats will be processed and formatted
                  for DaVinci Resolve.
                </p>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> Asset downloading happens in the background. You can preview and review
                    downloaded assets before finalizing.
                  </p>
                </div>

                <div className="flex gap-4 justify-end">
                  <button
                    onClick={() => setCurrentStep('configure')}
                    className="btn-secondary"
                    disabled={isLoading}
                  >
                    Back
                  </button>
                  <button
                    onClick={handleExport}
                    disabled={isLoading}
                    className="btn-primary"
                  >
                    {isLoading ? 'Generating...' : 'Generate Timeline'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
