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
    <div className="w-full max-w-2xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6">Configure Asset Fetching</h2>

        {/* YouTube Configuration */}
        <div className="mb-8 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-3 mb-4">
            <input
              type="checkbox"
              id="youtube_enabled"
              checked={config.youtubeEnabled}
              onChange={(e) => handleChange('youtubeEnabled', e.target.checked)}
              disabled={isLoading}
              className="w-4 h-4 text-blue-500 rounded"
            />
            <label htmlFor="youtube_enabled" className="text-lg font-semibold text-gray-800 cursor-pointer">
              YouTube Downloads
            </label>
          </div>
          {config.youtubeEnabled && (
            <p className="text-sm text-gray-600 ml-7">
              Download B-roll clips from YouTube (via yt-dlp). No API key required.
            </p>
          )}
        </div>

        {/* Pexels Configuration */}
        <div className="mb-8 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-3 mb-4">
            <input
              type="checkbox"
              id="pexels_enabled"
              checked={config.pexelsEnabled}
              onChange={(e) => handleChange('pexelsEnabled', e.target.checked)}
              disabled={isLoading}
              className="w-4 h-4 text-blue-500 rounded"
            />
            <label htmlFor="pexels_enabled" className="text-lg font-semibold text-gray-800 cursor-pointer">
              Pexels Fallback
            </label>
          </div>

          {config.pexelsEnabled && (
            <div className="ml-7 space-y-3">
              <p className="text-sm text-gray-600">Use Pexels as fallback when YouTube clips aren't available.</p>

              <div>
                <label htmlFor="pexels_key" className="label">
                  Pexels API Key
                </label>
                <input
                  id="pexels_key"
                  type="password"
                  value={config.pexelsApiKey || ''}
                  onChange={(e) => handleChange('pexelsApiKey', e.target.value)}
                  disabled={isLoading}
                  placeholder="Optional - leave blank for free tier"
                  className="input w-full"
                />
                <p className="text-xs text-gray-500 mt-2">
                  Get a free API key at{' '}
                  <a href="https://www.pexels.com/api" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                    pexels.com/api
                  </a>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Output Directory */}
        <div className="mb-8">
          <label htmlFor="output_dir" className="label">
            Output Directory
          </label>
          <input
            id="output_dir"
            type="text"
            value={config.outputDir}
            onChange={(e) => handleChange('outputDir', e.target.value)}
            disabled={isLoading}
            placeholder="./output"
            className="input w-full"
          />
          <p className="text-xs text-gray-500 mt-2">Where to save downloaded assets and FCPXML file</p>
        </div>

        {/* Summary */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">Fetching Strategy</h3>
          <ol className="text-sm text-blue-800 list-decimal list-inside space-y-1">
            {config.youtubeEnabled && <li>Search and download from YouTube (yt-dlp)</li>}
            {config.pexelsEnabled && <li>Fall back to Pexels stock footage if YouTube unavailable</li>}
            <li>Skip beats without available assets</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
