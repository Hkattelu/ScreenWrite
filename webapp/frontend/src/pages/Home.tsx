/**
 * Home page
 *
 * Upload script directly with quick syntax reference
 */

import { Link } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import type { UploadResponse } from '../types/models'
import { useNavigate } from 'react-router-dom'

export function Home() {
  const navigate = useNavigate()

  const handleUploadSuccess = (data: UploadResponse) => {
    navigate('/workflow', { state: { initialStep: 'review', uploadData: data } })
  }

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-xl space-y-12">
        {/* Minimal Header */}
        <div className="text-center space-y-2">
          <h1 className="text-6xl font-extrabold tracking-tighter text-black">
            ScreenWrite
          </h1>
          <p className="text-lg text-gray-400 font-medium tracking-wide">
            Script to Timeline
          </p>
        </div>

        {/* Primary Action */}
        <ScriptUpload onUploadSuccess={handleUploadSuccess} />

        {/* Footer Link */}
        <div className="text-center">
          <Link 
            to="/syntax-guide" 
            className="text-sm font-medium text-gray-400 hover:text-black transition-colors border-b border-transparent hover:border-gray-300 pb-0.5"
          >
            Syntax Guide
          </Link>
        </div>
      </div>
    </div>
  )
}


