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
        <Link to="/" className="text-sm font-bold uppercase tracking-widest text-gray-400 hover:text-[var(--brand-primary)] mb-12 inline-block transition-colors border-b-2 border-transparent hover:border-[var(--brand-primary)] pb-1">
          &larr; Back to Editor
        </Link>

        <header className="mb-20">
          <h1 className="text-6xl font-extrabold tracking-tighter text-gray-900 mb-6">Syntax Guide</h1>
          <p className="text-xl text-gray-500 leading-relaxed font-light uppercase tracking-tight">
            Structure your markdown for <span className="text-[var(--brand-primary)] font-bold">ScreenWrite</span>.
          </p>
        </header>

        <div className="space-y-16">
          
          {/* Section: Metadata */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Metadata</h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Define the context for your video at the very top of your file. This helps the AI understand the tone and topic.
            </p>
            <div className="bg-gray-900 rounded-lg p-6 font-mono text-sm text-gray-300 leading-normal overflow-x-auto shadow-sm whitespace-break-spaces">
{`Title: The Lost Art of Text-Based Game Walkthroughs
Hook: Welcome viewers. Today I'll take you through gaming history.
Channel: Gaming History
Duration: 12:30
Tags: gaming, history, walkthroughs`}
            </div>
            
            <div className="mt-8 border border-gray-100 rounded-2xl overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-gray-700">Key</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-gray-700">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {[
                    { key: 'Title', desc: 'Primary video title and context' },
                    { key: 'Hook', desc: 'Opening statement or catchphrase' },
                    { key: 'Channel', desc: 'Your brand or channel name' },
                    { key: 'Duration', desc: 'Target length (e.g. 10:00)' },
                    { key: 'Thumbnail', desc: 'Visual concept for the thumbnail' },
                    { key: 'Tags', desc: 'Comma-separated search keywords' },
                  ].map((item) => (
                    <tr key={item.key}>
                      <td className="px-6 py-4 font-mono text-sm text-black font-bold">{item.key}</td>
                      <td className="px-6 py-4 text-sm text-gray-600 font-medium">{item.desc}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <hr className="border-gray-700" />

          {/* Section: Structure */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Structure</h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Use standard Markdown headers to divide your script. These headers provide semantic context for the B-roll searcher.
            </p>
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-100 font-mono text-sm text-gray-800 whitespace-break-spaces">
{`## Main Section
Write your script naturally here.
## Next Section
Continue your narrative.`}
            </div>
          </section>

          <hr className="border-gray-700" />

          {/* Section: B-Roll Instructions */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Visual Instructions</h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Explicitly request visuals using bracket notation with a <code className="font-mono text-black">@</code> prefix. Place instructions <strong>immediately before</strong> the text they relate to.
            </p>
            
            <div className="border border-gray-100 rounded-2xl overflow-hidden mb-8">
              <table className="w-full text-left border-collapse">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-gray-700">Action</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-gray-700">Description</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-gray-700">Example</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  <tr>
                    <td className="px-6 py-4 font-mono text-sm text-brand-primary font-bold">@B-roll</td>
                    <td className="px-6 py-4 text-sm text-gray-600 font-medium">Video footage</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-gray-400">[@B-roll: sunset]</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 font-mono text-sm text-brand-primary font-bold">@Image</td>
                    <td className="px-6 py-4 text-sm text-gray-600 font-medium">Static assets</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-gray-400">[@Image: logo]</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 font-mono text-sm text-brand-primary font-bold">@Annotation</td>
                    <td className="px-6 py-4 text-sm text-gray-600 font-medium">Text overlays</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-gray-400">[@Annotation: "Title"]</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 font-mono text-sm text-brand-primary font-bold">@Citation</td>
                    <td className="px-6 py-4 text-sm text-gray-600 font-medium">Source credits</td>
                    <td className="px-6 py-4 font-mono text-[11px] text-gray-400">[@Citation: Wikipedia]</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="bg-gray-900 rounded-lg p-6 font-mono text-sm text-gray-300 leading-normal overflow-x-auto shadow-sm">
{`[@Image: old text-based walkthrough guide]\n\nThe walkthrough format has changed dramatically over the years.\n\n[@Annotation: "1981 - First video game guidebook"]\n\nThe earliest instances of walkthroughs came from physical books.`}
            </div>
          </section>
          
        </div>
      </div>
    </div>
  )
}


