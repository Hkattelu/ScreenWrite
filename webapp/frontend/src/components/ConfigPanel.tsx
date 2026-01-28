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
    <div className="w-full max-w-2xl mx-auto py-6">
      <div className="space-y-16">
        
        {/* Group 1: Sources */}
        <section className="space-y-10">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Visual Sources</h3>
            <p className="text-xs text-gray-400">Select where ScreenWrite should look for footage.</p>
          </div>

                    <div className="space-y-12">

                      {/* YouTube Section */}

                      <button 
                        type="button"
                        role="switch"
                        aria-checked={config.youtubeEnabled}
                        className={`w-full flex items-start gap-6 p-6 rounded-2xl border text-left transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/10 ${config.youtubeEnabled ? 'bg-white border-blue-100 shadow-sm' : 'bg-gray-50/50 border-gray-100 opacity-60'}`}
                        onClick={() => handleChange('youtubeEnabled', !config.youtubeEnabled)}
                      >
                        <div className="pt-1">
                          <div className={`w-12 h-6 rounded-full relative transition-colors duration-300 ${config.youtubeEnabled ? 'bg-blue-600' : 'bg-gray-200'}`}>
                            <motion.div 
                              animate={{ x: config.youtubeEnabled ? 24 : 0 }}
                              className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-sm" 
                            />
                          </div>
                        </div>
                        <div className="space-y-1">
                          <label className="text-xl font-bold text-gray-900 block tracking-tight cursor-pointer">
                            YouTube Downloads
                          </label>
                          <p className="text-sm text-gray-500 leading-relaxed">
                            Search and download specific clips from YouTube. No API key required.
                          </p>
                        </div>
                      </button>

                      {/* Pexels Section */}

                      <div className="space-y-6">
                        <button 
                          type="button"
                          role="switch"
                          aria-checked={config.pexelsEnabled}
                          className={`w-full flex items-start gap-6 p-6 rounded-2xl border text-left transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-500/10 ${config.pexelsEnabled ? 'bg-white border-blue-100 shadow-sm' : 'bg-gray-50/50 border-gray-100 opacity-60'}`}
                          onClick={() => handleChange('pexelsEnabled', !config.pexelsEnabled)}
                        >
                          <div className="pt-1">
                            <div className={`w-12 h-6 rounded-full relative transition-colors duration-300 ${config.pexelsEnabled ? 'bg-blue-600' : 'bg-gray-200'}`}>
                              <motion.div 
                                animate={{ x: config.pexelsEnabled ? 24 : 0 }}
                                className="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-sm" 
                              />
                            </div>
                          </div>
                          <div className="space-y-1">
                            <label className="text-xl font-bold text-gray-900 block tracking-tight cursor-pointer">
                              Pexels Fallback
                            </label>
                            <p className="text-sm text-gray-500 leading-relaxed">
                              Use high-quality stock footage when specific YouTube clips aren't available.
                            </p>
                          </div>
                        </button>

          

                        {config.pexelsEnabled && (

                          <motion.div 

                            initial={{ opacity: 0, y: -10 }}

                            animate={{ opacity: 1, y: 0 }}

                            className="pl-6"

                          >

                            <label htmlFor="pexels_key" className="block text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-3 ml-1">

                              Pexels API Key

                            </label>

                            <input

                              id="pexels_key"

                              type="password"

                              value={config.pexelsApiKey || ''}

                              onChange={(e) => handleChange('pexelsApiKey', e.target.value)}

                              onClick={e => e.stopPropagation()}

                              disabled={isLoading}

                              placeholder="Enter your free API key..."

                              className="w-full p-4 bg-gray-50 border border-gray-100 rounded-xl text-gray-900 focus:ring-2 focus:ring-blue-500/10 focus:bg-white focus:border-blue-200 font-mono text-sm placeholder:text-gray-300 transition-all outline-none"

                            />

                          </motion.div>

                        )}

                      </div>

                    </div>

          
        </section>

        <hr className="border-gray-100" />


      </div>
    </div>
  )
}

