/**
 * Home page
 *
 * Introduction and workflow overview
 */

import { Link } from 'react-router-dom'

export function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
      <div className="max-w-4xl mx-auto px-4 py-20">
        {/* Hero section */}
        <div className="text-center mb-20">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">Footage</h1>
          <p className="text-xl text-gray-700 mb-8">
            Convert your markdown video scripts into professional DaVinci Resolve timelines with automatic B-roll.
          </p>

          <Link to="/workflow" className="btn-primary text-lg px-8 py-3 inline-block">
            Get Started
          </Link>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          <div className="card">
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-2">Write Scripts</h3>
            <p className="text-gray-600">
              Use simple markdown format to describe your video segments and B-roll needs.
            </p>
          </div>

          <div className="card">
            <div className="text-4xl mb-4">🎬</div>
            <h3 className="text-xl font-semibold mb-2">Auto-Fetch B-roll</h3>
            <p className="text-gray-600">
              Automatically download footage from YouTube and Pexels based on your script descriptions.
            </p>
          </div>

          <div className="card">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-2">Generate Timelines</h3>
            <p className="text-gray-600">
              Create FCPXML files that import directly into DaVinci Resolve with all assets organized.
            </p>
          </div>
        </div>

        {/* Workflow steps */}
        <div className="card">
          <h2 className="text-3xl font-bold mb-8 text-center">How It Works</h2>

          <div className="space-y-8">
            {[
              {
                num: '1',
                title: 'Upload Script',
                desc: 'Upload your markdown script describing the video segments and footage needs.',
              },
              {
                num: '2',
                title: 'Review Beats',
                desc: 'Preview auto-parsed beats with durations, keywords, and search queries.',
              },
              {
                num: '3',
                title: 'Configure',
                desc: 'Set up YouTube/Pexels preferences and API keys (if using Pexels).',
              },
              {
                num: '4',
                title: 'Fetch Assets',
                desc: 'Start automatic B-roll downloading with real-time progress tracking.',
              },
              {
                num: '5',
                title: 'Review Results',
                desc: 'See all downloaded assets and preview them before finalizing.',
              },
              {
                num: '6',
                title: 'Export Timeline',
                desc: 'Generate FCPXML and download for immediate import into DaVinci Resolve.',
              },
            ].map((step, idx) => (
              <div key={idx} className="flex gap-6">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">
                    {step.num}
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{step.title}</h3>
                  <p className="text-gray-600 mt-1">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Link to="/workflow" className="btn-primary text-lg px-8 py-3 inline-block">
              Start Building Your Timeline
            </Link>
          </div>
        </div>

        {/* Script format info */}
        <div className="mt-20 card">
          <h2 className="text-2xl font-bold mb-4">Script Format</h2>
          <p className="text-gray-700 mb-6">Your markdown script should look like this:</p>

          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-6">
{`## Introduction
This is the opening scene. We need
footage of a sunrise over mountains
with a peaceful vibe.

## Main Section  
Show people working in a modern office.
Quick cuts of collaboration, computers,
and teamwork.

## Conclusion
End with an inspiring shot of the team
looking out over the city at sunset.`}
          </pre>

          <p className="text-gray-600">
            Each section starts with a header (##) and is followed by a description. The system automatically calculates
            durations and generates search keywords for B-roll.
          </p>
        </div>
      </div>
    </div>
  )
}
