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
    <div className="min-h-screen bg-brand-surface relative overflow-hidden flex flex-col items-center justify-center p-4">
      {/* Immersive Animated Background */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        {/* Shape 1: Deep Violet */}
        <motion.div 
          animate={{ 
            scale: [1, 1.4, 1.1],
            x: [0, 100, -50, 0],
            y: [0, -50, 100, 0]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] rounded-full bg-brand-primary/30 blur-[100px]" 
        />
        {/* Shape 2: Vibrant Teal */}
        <motion.div 
          animate={{ 
            scale: [1.2, 1, 1.3],
            x: [0, -120, 80, 0],
            y: [0, 100, -40, 0]
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-[-15%] right-[-5%] w-[70%] h-[70%] rounded-full bg-brand-highlight/20 blur-[120px]" 
        />
        {/* Shape 3: Sunset Orange */}
        <motion.div 
          animate={{ 
            scale: [0.8, 1.2, 0.9],
            x: [0, 150, -100, 0],
            y: [0, 80, -120, 0]
          }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-brand-accent/25 blur-[90px]" 
        />
        {/* Shape 4: Soft Glow Center */}
        <div className="absolute inset-0 bg-white/20 backdrop-overlay" />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-2xl relative z-10"
      >
        <div className="bg-white/40 backdrop-blur-3xl border border-white/40 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] rounded-[40px] p-12 md:p-20 space-y-16">
          {/* Minimal Header */}
          <div className="text-center space-y-4">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <h1 className="text-8xl font-black tracking-tightest text-black leading-none">
                Screen<span className="text-brand-primary inline-block transform -rotate-2 hover:rotate-0 transition-transform duration-500">Write</span>
              </h1>
            </motion.div>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="text-xl text-gray-500 font-bold tracking-widest uppercase opacity-80"
            >
              The Creative Video Engine
            </motion.p>
          </div>

          {/* Primary Action */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            <ScriptUpload onUploadSuccess={handleUploadSuccess} />
          </motion.div>

          {/* Footer Link */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 1 }}
            className="text-center pt-4"
          >
            <Link 
              to="/syntax-guide" 
              className="group inline-flex items-center gap-2 text-xs font-black uppercase tracking-widest text-gray-400 hover:text-brand-primary transition-all"
            >
              <span>Explore the syntax</span>
              <span className="w-12 h-px bg-gray-200 group-hover:w-16 group-hover:bg-brand-primary transition-all duration-500" />
            </Link>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}