/**
 * Syntax Guide page
 *
 * Complete markdown script syntax reference and best practices
 */

import { Link } from 'react-router-dom'

export function SyntaxGuide() {
  return (
    <div className="min-h-screen bg-white py-12 px-4">
      <div className="max-w-3xl mx-auto">
        <Link to="/" className="text-sm font-medium text-gray-400 hover:text-black mb-8 inline-block transition-colors">
          &larr; Back
        </Link>

        <header className="mb-16">
          <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 mb-6">Syntax Guide</h1>
          <p className="text-xl text-gray-500 leading-relaxed font-light">
            How to format your markdown scripts for optimal B-roll generation and timeline creation.
          </p>
        </header>

        <div className="space-y-16">
          
          {/* Section: Metadata */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Metadata</h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Define the context for your video at the very top of your file. This helps the AI understand the tone and topic.
            </p>
            <div className="bg-gray-900 rounded-lg p-6 font-mono text-sm text-gray-300 leading-normal overflow-x-auto shadow-sm">
{`Title: The Lost Art of Text-Based Game Walkthroughs
Hook: Welcome viewers. Today I'll take you through gaming history.
Channel: Gaming History
Duration: 12:30
Tags: gaming, history, walkthroughs`}
            </div>
            <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 gap-4">
               {['Title', 'Hook', 'Channel', 'Duration', 'Thumbnail', 'Tags'].map(key => (
                 <div key={key} className="flex items-baseline gap-2">
                   <span className="font-mono text-xs font-bold text-gray-400 uppercase">{key}</span>
                 </div>
               ))}
            </div>
          </section>

          <hr className="border-gray-100" />

          {/* Section: Structure */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Structure</h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Use standard Markdown headers to divide your script. These headers provide semantic context for the B-roll searcher.
            </p>
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-100 font-mono text-sm text-gray-800">
{`## Main Section
Write your script naturally here.

## Next Section
Continue your narrative.`}
            </div>
          </section>

          <hr className="border-gray-100" />

          {/* Section: B-Roll Instructions */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Visual Instructions</h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Explicitly request visuals using bracket notation with a <code className="font-mono text-black">@</code> prefix. Place instructions <strong>immediately before</strong> the text they relate to.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3">Syntax</h3>
                <code className="block bg-gray-50 p-3 rounded border border-gray-200 text-sm font-mono text-blue-600">
                  [@Action: Description]
                </code>
              </div>
              <div>
                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3">Supported Actions</h3>
                 <ul className="text-sm text-gray-600 space-y-1">
                   <li><span className="font-mono text-black font-medium">Image</span> — Static assets</li>
                   <li><span className="font-mono text-black font-medium">B-roll</span> — Video footage</li>
                   <li><span className="font-mono text-black font-medium">Annotation</span> — Text overlays</li>
                   <li><span className="font-mono text-black font-medium">Citation</span> — Source credits</li>
                 </ul>
              </div>
            </div>

            <div className="bg-gray-900 rounded-lg p-6 font-mono text-sm text-gray-300 leading-normal overflow-x-auto shadow-sm">
{`[@Image: old text-based walkthrough guide]
The walkthrough format has changed dramatically over the years.

[@Annotation: "1981 - First video game guidebook"]
The earliest instances of walkthroughs came from physical books.`}
            </div>
          </section>

          <hr className="border-gray-100" />

          {/* Section: Best Practices (Comparison) */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Writing for ScreenWrite</h2>
            
            <div className="grid md:grid-cols-2 gap-12">
              <div>
                <h3 className="text-emerald-600 font-bold mb-4 flex items-center gap-2">
                  <span>Specific & Visual</span>
                </h3>
                <div className="space-y-6">
                  <div>
                     <p className="text-sm text-gray-500 mb-2">Reference specific tools</p>
                     <p className="font-medium text-gray-900">"Open Visual Studio Code and create a new Python file"</p>
                  </div>
                  <div>
                     <p className="text-sm text-gray-500 mb-2">Describe user actions</p>
                     <p className="font-medium text-gray-900">"Click the green 'Run' button in the toolbar"</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-red-500 font-bold mb-4 flex items-center gap-2">
                  <span>Vague & Abstract</span>
                </h3>
                <div className="space-y-6 opacity-60">
                   <div>
                     <p className="text-sm text-gray-500 mb-2">Generic instructions</p>
                     <p className="font-medium text-gray-900">"Open your editor and create a new file"</p>
                  </div>
                  <div>
                     <p className="text-sm text-gray-500 mb-2">Abstract concepts</p>
                     <p className="font-medium text-gray-900">"Execute the program"</p>
                  </div>
                </div>
              </div>
            </div>
          </section>
          
        </div>
      </div>
    </div>
  )
}


