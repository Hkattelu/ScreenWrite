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
    <div className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center p-4" style={{ backgroundColor: 'var(--brand-surface)' }}>
      {/* Immersive Animated Background */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        {/* Shape 1: Deep Violet */}
        <motion.div 
          animate={{ 
            scale: [1, 1.2, 1],
            x: ['-10%', '10%', '-5%'],
            y: ['-10%', '5%', '-10%']
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-0 left-0 w-[80vw] h-[80vh] rounded-full filter blur-[60px]" 
          style={{ backgroundColor: 'var(--brand-primary)', opacity: 0.5 }}
        />
        {/* Shape 2: Vibrant Teal */}
        <motion.div 
          animate={{ 
            scale: [1.1, 0.9, 1.2],
            x: ['10%', '-15%', '10%'],
            y: ['10%', '20%', '10%']
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-0 right-0 w-[90vw] h-[90vh] rounded-full filter blur-[80px]" 
          style={{ backgroundColor: 'var(--brand-highlight)', opacity: 0.4 }}
        />
        {/* Shape 3: Sunset Orange */}
        <motion.div 
          animate={{ 
            scale: [0.9, 1.3, 1],
            x: ['20%', '-10%', '20%'],
            y: ['-20%', '10%', '-20%']
          }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/4 right-0 w-[50vw] h-[50vh] rounded-full filter blur-[50px]" 
          style={{ backgroundColor: 'var(--brand-accent)', opacity: 0.45 }}
        />
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-2xl relative z-10"
      >
        <div className="bg-white/60 backdrop-blur-2xl border border-white/40 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] rounded-[40px] p-12 md:p-20 space-y-16">
          {/* Minimal Header */}
          <div className="text-center space-y-4">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <h1 
                className="text-8xl font-medium tracking-tight text-black leading-none"
                style={{ fontFamily: "'Charter', 'Bitstream Charter', 'Sitka Text', Cambria, serif" }}
              >
                Screen<span className="text-brand-primary italic inline-block transform -rotate-2 hover:rotate-0 transition-transform duration-500">Write</span>
              </h1>
            </motion.div>
            <motion.p 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="text-xl text-gray-500 font-bold tracking-[0.2em] uppercase opacity-80"
            >
              B-roll made easy
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
              className="inline-flex items-center gap-3 px-8 py-4 bg-black text-white rounded-full text-xs font-black uppercase tracking-widest hover:bg-brand-primary transition-all duration-300 shadow-xl shadow-black/10"
            >
              <span>Explore the syntax</span>
              <span className="w-8 h-px bg-white/30" />
            </Link>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}