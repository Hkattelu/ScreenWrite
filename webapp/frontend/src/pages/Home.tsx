/**
 * Home page
 *
 * Upload script directly with quick syntax reference
 */

import { Link } from 'react-router-dom'
import { ScriptUpload } from '../components/ScriptUpload'
import type { UploadResponse } from '../types/models'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

export function Home() {
  const navigate = useNavigate()

  const handleUploadSuccess = (data: UploadResponse) => {
    navigate('/workflow', { state: { initialStep: 'review', uploadData: data } })
  }

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-xl space-y-12"
      >
        {/* Minimal Header */}
        <div className="text-center space-y-2">
          <motion.h1 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-7xl font-extrabold tracking-tighter text-black"
          >
            ScreenWrite
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="text-lg text-gray-400 font-medium tracking-wide"
          >
            Script to Timeline
          </motion.p>
        </div>

        {/* Primary Action */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
        >
          <ScriptUpload onUploadSuccess={handleUploadSuccess} />
        </motion.div>

        {/* Footer Link */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          className="text-center"
        >
          <Link 
            to="/syntax-guide" 
            className="text-sm font-medium text-gray-400 hover:text-black transition-colors border-b border-transparent hover:border-gray-300 pb-0.5"
          >
            Syntax Guide
          </Link>
        </motion.div>
      </motion.div>
    </div>
  )
}



