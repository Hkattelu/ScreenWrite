/**
 * Configuration panel component
 *
 * Allows users to configure asset fetching options
 */

import { useState } from 'react'
import type { Config } from '../types/models'

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
            <div className="flex items-start gap-4">
              <div className="pt-1">
                <input
                  type="checkbox"
                  id="youtube_enabled"
                  checked={config.youtubeEnabled}
                  onChange={(e) => handleChange('youtubeEnabled', e.target.checked)}
                  disabled={isLoading}
                  className="w-5 h-5 text-black border-gray-300 rounded focus:ring-black transition-colors cursor-pointer"
                />
              </div>
              <div className="space-y-1">
                <label htmlFor="youtube_enabled" className="text-xl font-bold text-gray-900 cursor-pointer block tracking-tight">
                  YouTube Downloads
                </label>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Search and download specific clips from YouTube. No API key required.
                </p>
              </div>
            </div>

            {/* Pexels Section */}
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="pt-1">
                  <input
                    type="checkbox"
                    id="pexels_enabled"
                    checked={config.pexelsEnabled}
                    onChange={(e) => handleChange('pexelsEnabled', e.target.checked)}
                    disabled={isLoading}
                    className="w-5 h-5 text-black border-gray-300 rounded focus:ring-black transition-colors cursor-pointer"
                  />
                </div>
                <div className="space-y-1">
                  <label htmlFor="pexels_enabled" className="text-xl font-bold text-gray-900 cursor-pointer block tracking-tight">
                    Pexels Fallback
                  </label>
                  <p className="text-sm text-gray-500 leading-relaxed">
                    Use high-quality stock footage when specific YouTube clips aren't available.
                  </p>
                </div>
              </div>

              {config.pexelsEnabled && (
                <div className="pl-9">
                  <label htmlFor="pexels_key" className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">
                    Pexels API Key
                  </label>
                  <input
                    id="pexels_key"
                    type="password"
                    value={config.pexelsApiKey || ''}
                    onChange={(e) => handleChange('pexelsApiKey', e.target.value)}
                    disabled={isLoading}
                    placeholder="Optional (Free Tier)"
                    className="w-full p-3 bg-gray-50 border-0 rounded-lg text-gray-900 focus:ring-2 focus:ring-black font-mono text-sm placeholder:text-gray-300 transition-all"
                  />
                </div>
              )}
            </div>
          </div>
        </section>

        <hr className="border-gray-100" />

        {/* Group 2: Settings */}
        <section className="space-y-6">
          <div className="space-y-1">
            <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">System Settings</h3>
          </div>

          <div>
            <label className="block text-sm font-bold text-gray-900 mb-2">
              Output Directory
            </label>
            <div className="flex items-center gap-3">
              <button
                onClick={async () => {
                  try {
                    const dirHandle = await (window as any).showDirectoryPicker?.({ mode: 'readwrite' })
                    if (dirHandle) {
                      handleChange('outputDir', dirHandle.name)
                    }
                  } catch (error) {
                    if ((error as Error)?.name !== 'AbortError') {
                      console.error('Error selecting directory:', error)
                    }
                  }
                }}
                disabled={isLoading}
                className="px-4 py-2 bg-black text-white rounded-lg font-semibold text-sm hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                Browse Folder
              </button>
              <span className="text-sm text-gray-600 font-mono">
                {config.outputDir || 'No folder selected'}
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

