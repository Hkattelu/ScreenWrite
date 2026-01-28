/**
 * Configuration panel component
 *
 * Allows users to configure asset fetching options
 */

import { useState } from 'react'
import type { Config } from '../types/models'
import { motion } from 'framer-motion'

interface ConfigPanelProps {
  onConfigChange: (config: Config) => void
  isLoading?: boolean
}

export function ConfigPanel({ onConfigChange, isLoading = false }: ConfigPanelProps) {
  const [config, setConfig] = useState<Config>({
    youtubeEnabled: true,
    pexelsEnabled: true,
    pexelsApiKey: '',
    outputDir: './output',
  })

  const handleChange = (key: keyof Config, value: any) => {
    const newConfig = { ...config, [key]: value }
    setConfig(newConfig)
    onConfigChange(newConfig)
  }

  return (
    <div className="w-full max-w-2xl mx-auto py-8">
      <div className="space-y-20">
        
        {/* Group 1: Sources */}
        <section className="space-y-12">
          <div className="space-y-2">
            <h3 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">Cinematic Sources</h3>
            <p className="text-sm font-medium text-slate-500">Choose your preferred acquisition channels for footage.</p>
          </div>

                    <div className="space-y-14">

                      {/* YouTube Section */}

                      <button 
                        type="button"
                        role="switch"
                        aria-checked={config.youtubeEnabled}
                        className={`w-full flex items-start gap-8 p-8 rounded-[32px] border-2 text-left transition-all duration-500 focus:outline-none focus:ring-8 focus:ring-blue-500/5 ${config.youtubeEnabled ? 'bg-white border-blue-500 shadow-xl shadow-blue-500/5 scale-[1.02]' : 'bg-slate-50/50 border-slate-100 opacity-60'}`}
                        onClick={() => handleChange('youtubeEnabled', !config.youtubeEnabled)}
                      >
                        <div className="pt-2">
                          <div className={`w-14 h-7 rounded-full relative transition-all duration-500 ${config.youtubeEnabled ? 'bg-blue-600 shadow-inner' : 'bg-slate-200'}`}>
                            <motion.div 
                              animate={{ x: config.youtubeEnabled ? 28 : 0 }}
                              transition={{ type: "spring", stiffness: 500, damping: 30 }}
                              className="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-lg" 
                            />
                          </div>
                        </div>
                        <div className="space-y-2">
                          <label className="text-2xl font-black text-slate-900 block tracking-tight cursor-pointer">
                            YouTube Downloads
                          </label>
                          <p className={`text-sm leading-relaxed font-medium transition-colors duration-500 ${config.youtubeEnabled ? 'text-slate-600' : 'text-slate-400'}`}>
                            Acquire specific cinematic clips directly from the source. No API key required.
                          </p>
                        </div>
                      </button>

                      {/* Pexels Section */}

                      <div className="space-y-8">
                        <button 
                          type="button"
                          role="switch"
                          aria-checked={config.pexelsEnabled}
                          className={`w-full flex items-start gap-8 p-8 rounded-[32px] border-2 text-left transition-all duration-500 focus:outline-none focus:ring-8 focus:ring-blue-500/5 ${config.pexelsEnabled ? 'bg-white border-blue-500 shadow-xl shadow-blue-500/5 scale-[1.02]' : 'bg-slate-50/50 border-slate-100 opacity-60'}`}
                          onClick={() => handleChange('pexelsEnabled', !config.pexelsEnabled)}
                        >
                          <div className="pt-2">
                            <div className={`w-14 h-7 rounded-full relative transition-all duration-500 ${config.pexelsEnabled ? 'bg-blue-600 shadow-inner' : 'bg-slate-200'}`}>
                              <motion.div 
                                animate={{ x: config.pexelsEnabled ? 28 : 0 }}
                                transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                className="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow-lg" 
                              />
                            </div>
                          </div>
                          <div className="space-y-2">
                            <label className="text-2xl font-black text-slate-900 block tracking-tight cursor-pointer">
                              Stock Fallback
                            </label>
                            <p className={`text-sm leading-relaxed font-medium transition-colors duration-500 ${config.pexelsEnabled ? 'text-slate-600' : 'text-slate-400'}`}>
                              Leverage Pexels for high-quality atmospheric footage when specific clips are unavailable.
                            </p>
                          </div>
                        </button>

          

                        {config.pexelsEnabled && (

                          <motion.div 

                            initial={{ opacity: 0, y: -20 }}

                            animate={{ opacity: 1, y: 0 }}

                            className="pl-8 space-y-4"

                          >

                            <label htmlFor="pexels_key" className="block text-[11px] font-black text-slate-400 uppercase tracking-[0.3em] ml-2">

                              Pexels API Key

                            </label>

                            <input

                              id="pexels_key"

                              type="password"

                              value={config.pexelsApiKey || ''}

                              onChange={(e) => handleChange('pexelsApiKey', e.target.value)}

                              onClick={e => e.stopPropagation()}

                              disabled={isLoading}

                              placeholder="Paste your Pexels token here..."

                              className="w-full p-5 bg-slate-50 border-2 border-slate-100 rounded-2xl text-slate-900 focus:ring-8 focus:ring-blue-500/5 focus:bg-white focus:border-blue-500/40 font-mono text-sm placeholder:text-slate-300 transition-all outline-none"

                            />

                          </motion.div>

                        )}

                      </div>

                    </div>

          
        </section>

        <hr className="border-slate-100" />


      </div>
    </div>

  )
}

