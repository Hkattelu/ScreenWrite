/**
 * Home page
 *
 * Upload script directly with quick syntax reference
 */

import { Link } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import type { UploadResponse } from '../types/models'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export function Home() {
  const navigate = useNavigate()
  const [showUpload, setShowUpload] = useState(false)

  const handleUploadSuccess = (data: UploadResponse) => {
    navigate('/workflow', { state: { initialStep: 'review', uploadData: data } })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 py-12">
      <div className="max-w-4xl mx-auto px-4">
        {/* Hero section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">Footage</h1>
          <p className="text-xl text-gray-700 mb-8">
            Convert markdown scripts into DaVinci Resolve timelines with automatic B-roll.
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="card text-center">
            <div className="text-4xl mb-3">📝</div>
            <h3 className="text-lg font-semibold mb-2">Write Scripts</h3>
            <p className="text-gray-600 text-sm">
              Simple markdown format with sections and descriptions.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-3">🎬</div>
            <h3 className="text-lg font-semibold mb-2">Auto B-roll</h3>
            <p className="text-gray-600 text-sm">
              YouTube and Pexels integration for automatic footage.
            </p>
          </div>

          <div className="card text-center">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="text-lg font-semibold mb-2">Export Timeline</h3>
            <p className="text-gray-600 text-sm">
              FCPXML ready to import into DaVinci Resolve.
            </p>
          </div>
        </div>

        {/* Upload section */}
        <div className="card mb-12">
          <h2 className="text-2xl font-bold mb-6">Upload Your Script</h2>
          
          {!showUpload ? (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Format (Markdown)</h3>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`## Introduction
This is the opening scene. We need
footage of a sunrise over mountains.

## Main Section  
Show people working in a modern office.
Quick cuts of collaboration and teamwork.

## Conclusion
End with an inspiring shot at sunset.`}
                </pre>
                <p className="text-sm text-gray-600 mb-3">
                  Each section starts with a header (##). Include 13-25 words for optimal 5-10 second segments.
                </p>
                <Link 
                  to="/syntax-guide" 
                  className="text-blue-600 hover:text-blue-800 font-semibold text-sm inline-flex items-center gap-1"
                >
                  📖 View Complete Syntax Guide
                </Link>
              </div>

              <div className="border-t pt-6">
                <button
                  onClick={() => setShowUpload(true)}
                  className="btn-primary text-lg px-8 py-3 mb-4 w-full"
                >
                  Upload Script
                </button>
                <p className="text-sm text-gray-600 text-center">
                  Supports .md and .txt files (max 16MB)
                </p>
              </div>
            </div>
          ) : (
            <div>
              <ScriptUpload onUploadSuccess={handleUploadSuccess} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
