/**
 * Syntax Guide page
 *
 * Complete markdown script syntax reference and best practices
 */

export function SyntaxGuide() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Markdown Script Syntax Guide</h1>
        <p className="text-xl text-gray-700 mb-12">
          Learn how to write markdown scripts that generate optimal B-roll and timelines with our enhanced format.
        </p>

        {/* Metadata Section */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Metadata (Top of File)</h2>
          <p className="text-gray-700 mb-4">
            Start your script with metadata that provides context for B-roll generation:
          </p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`Title: The Lost Art of Text-Based Game Walkthroughs
Hook: Welcome viewers. Today I'll take you through gaming history.
Channel: Gaming History
Duration: 12:30
Tags: gaming, history, walkthroughs`}
          </pre>
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-4">
            <p className="font-semibold text-gray-900 mb-3">Supported Metadata Keys:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              {[
                { key: 'Title', desc: 'Video title (primary context)' },
                { key: 'Hook', desc: 'Opening/hook statement' },
                { key: 'Channel', desc: 'Your channel name' },
                { key: 'Duration', desc: 'Estimated video length' },
                { key: 'Thumbnail', desc: 'Thumbnail concept' },
                { key: 'Tags', desc: 'Content tags' },
              ].map((item, idx) => (
                <div key={idx}>
                  <code className="bg-gray-200 px-2 py-1 rounded font-mono text-xs">{item.key}</code>
                  <p className="text-gray-700 text-xs mt-1">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Basic Structure Section */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Basic Structure</h2>
          <p className="text-gray-700 mb-4">
            After metadata, use headers to organize your content:
          </p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`## Main Section

Your script content goes here. Write naturally as you would speak in your video.

## Another Section

Continue with more content. Each paragraph will be analyzed for visual keywords.`}
          </pre>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>Use <code className="bg-gray-100 px-2 py-1 rounded">##</code> (H2) for main sections</li>
            <li>Use <code className="bg-gray-100 px-2 py-1 rounded">###</code> (H3) for subsections</li>
            <li>Write naturally as you would speak</li>
            <li>Include visual keywords (specific tools, objects, actions)</li>
            <li>Headers provide context that influences B-roll selection</li>
          </ul>
        </div>

        {/* B-Roll Instructions Section */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">B-Roll Instructions</h2>
          <p className="text-gray-700 mb-4">
            Use bracket notation to specify what visuals should accompany your text:
          </p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`[action: description]`}
          </pre>

          <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Supported Actions</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm mb-6">
              <thead className="bg-gray-200">
                <tr>
                  <th className="px-3 py-2 text-left font-semibold">Action</th>
                  <th className="px-3 py-2 text-left font-semibold">Purpose</th>
                  <th className="px-3 py-2 text-left font-semibold">Example</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-300">
                {[
                  { action: 'Image', purpose: 'Images, screenshots, diagrams, UI', example: '[Image: game menu screenshots]' },
                  { action: 'B-roll', purpose: 'Video footage, interviews, gameplay', example: '[B-roll: person playing game]' },
                  { action: 'Annotation', purpose: 'Prominent on-screen text/labels', example: '[Annotation: "Est. 1981"]' },
                  { action: 'Citation', purpose: 'Source attribution (bottom left)', example: '[Citation: Wikipedia - History]' },
                ].map((item, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-50' : ''}>
                    <td className="px-3 py-2"><code className="bg-gray-200 px-2 py-1 rounded text-xs font-mono">{item.action}</code></td>
                    <td className="px-3 py-2 text-gray-700">{item.purpose}</td>
                    <td className="px-3 py-2 text-gray-600 font-mono text-xs">{item.example}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-3">Instruction Examples</h3>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`[Image: old text-based walkthrough guide]
The walkthrough format has changed dramatically over the years.

[Annotation: "1981 - First video game guidebook"]
The earliest instances of walkthroughs came from physical books.

[B-roll: person reading guide book at desk]
These guides were carefully crafted with precision.

[Image: GameFAQs.com interface with guides listed]
The internet changed everything about how we access walkthroughs.

[Citation: GameFAQs Archive - https://gamefaqs.gamespot.com]`}
          </pre>

          <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Chaining Instructions</h3>
          <p className="text-gray-700 mb-3">Combine multiple instructions together for complex sequences:</p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`[Image: screenshots of multiple walkthroughs]

[Image: browser tabs with different guides]
[Annotation: "Est. 2000s - Peak of text-based walkthroughs"]
[Citation: Game Archive - source.org]`}
          </pre>
        </div>

        {/* Timing Section */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Timing and Beat Generation</h2>
          <p className="text-gray-700 mb-4">
            The system uses <strong>2.5 words per second</strong> to calculate beat duration:
          </p>
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 rounded">
            <p className="text-gray-900 font-semibold mb-2">Optimal Range: 13-25 words per beat</p>
            <p className="text-gray-700">This translates to 5-10 second video segments</p>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-3">Example:</h3>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`## Getting Started with Python

First, you need to install Python on your computer. Visit the official Python website and download the latest version for your operating system.`}
          </pre>
          <p className="text-gray-700 mb-2">Becomes <strong>2 beats</strong>:</p>
          <ul className="list-disc list-inside text-gray-700 space-y-1 ml-2">
            <li>Beat 1: "First, you need to install Python on your computer." (10 words ≈ 4 seconds)</li>
            <li>Beat 2: "Visit the official Python website and download the latest version for your operating system." (15 words ≈ 6 seconds)</li>
          </ul>
        </div>

        {/* Visual Keywords Section */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Including Visual Keywords</h2>
          <p className="text-gray-700 mb-4">
            The system generates search queries based on keywords in your script. More specific keywords = better B-roll matches.
          </p>

          <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">What Works Well</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {[
              { title: 'Specific Software', examples: 'Visual Studio Code, Photoshop, Chrome' },
              { title: 'Concrete Actions', examples: 'typing, clicking, installing, downloading' },
              { title: 'Visible Objects', examples: 'keyboard, screen, mouse, computer' },
              { title: 'Technical Terms', examples: 'terminal, code, website, application' },
            ].map((item, idx) => (
              <div key={idx} className="bg-green-50 p-4 rounded-lg border border-green-200">
                <p className="font-semibold text-gray-900 mb-2">{item.title}</p>
                <p className="text-gray-700 text-sm">{item.examples}</p>
              </div>
            ))}
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-3">Good vs Bad Examples</h3>
          <div className="space-y-4">
            <div>
              <p className="text-green-700 font-semibold mb-2">✅ Good - Specific and Visual:</p>
              <pre className="bg-green-50 text-green-900 p-4 rounded-lg overflow-x-auto text-sm border-l-4 border-green-500">
{`Open Visual Studio Code and create a new Python file. Click the green 'Run' button in the toolbar to execute the program.`}
              </pre>
            </div>
            <div>
              <p className="text-red-700 font-semibold mb-2">❌ Poor - Abstract and Vague:</p>
              <pre className="bg-red-50 text-red-900 p-4 rounded-lg overflow-x-auto text-sm border-l-4 border-red-500">
{`Open your editor and execute the program.`}
              </pre>
            </div>
          </div>
        </div>

        {/* Writing Style Tips */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Writing Style Tips</h2>
          <div className="space-y-6">
            {[
              {
                title: 'Be Specific About Tools',
                good: 'Open Visual Studio Code and create a new Python file',
                bad: 'Open your editor and create a new file',
              },
              {
                title: 'Mention Visual Elements',
                good: 'Click the green "Run" button in the toolbar',
                bad: 'Execute the program',
              },
              {
                title: 'Include Step-by-Step Actions',
                good: 'Right-click on the desktop and select "New Folder"',
                bad: 'Create a new folder',
              },
              {
                title: 'Reference UI Elements',
                good: 'In the sidebar, expand the "Files" panel',
                bad: 'Look at the file structure',
              },
            ].map((tip, idx) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-semibold text-gray-900 mb-2">{tip.title}</h4>
                <div className="space-y-2 text-sm">
                  <div className="bg-green-50 p-2 rounded">
                    <span className="text-green-700 font-semibold">✅ </span>
                    <span className="text-gray-700">{tip.good}</span>
                  </div>
                  <div className="bg-red-50 p-2 rounded">
                    <span className="text-red-700 font-semibold">❌ </span>
                    <span className="text-gray-700">{tip.bad}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* B-Roll Instruction Placement */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">B-Roll Instruction Placement</h2>
          <p className="text-gray-700 mb-4">
            Instructions are linked to the text that follows them:
          </p>
          
          <h3 className="text-lg font-semibold text-gray-900 mb-3">✅ Correct Placement</h3>
          <pre className="bg-green-50 text-green-900 p-4 rounded-lg overflow-x-auto text-sm mb-6 border-l-4 border-green-500">
{`[Show: old arcade cabinet]
Arcade cabinets of the 80s didn't come with instructions.

[Annotation: "Year: 1983"]
This was the golden age of arcade gaming.`}
          </pre>

          <h3 className="text-lg font-semibold text-gray-900 mb-3">❌ Incorrect Placement</h3>
          <pre className="bg-red-50 text-red-900 p-4 rounded-lg overflow-x-auto text-sm border-l-4 border-red-500">
{`[Show: random footage]
Text that has nothing to do with the instruction above.
This creates confusing associations.`}
          </pre>

          <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">💡 Key Rules</h3>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>Place instructions <strong>immediately before</strong> the text they accompany</li>
            <li>Instructions apply to the paragraph following them</li>
            <li>Multiple instructions can be chained together</li>
            <li>Be specific - don't use vague descriptions like "stuff" or "things"</li>
            <li>Use consistent capitalization: <code className="bg-gray-100 px-2 py-1 rounded text-xs">[Action: description]</code></li>
          </ul>
        </div>

        {/* Instruction Type Examples */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Instruction Type Examples</h2>
          <div className="space-y-6">
            {[
              {
                title: 'Image - For Visual Content',
                good: '[Image: Python.org homepage with download button]\nVisit the official Python website and download the latest version.',
                bad: '[Image: website]\nVisit the official Python website.',
              },
              {
                title: 'Annotation - For Prominent On-Screen Text',
                good: '[Annotation: "Python 3.12 - Latest Version"]\nMake sure you install the latest stable version.',
                bad: '[Annotation: "Latest"]\nGet the latest version.',
              },
              {
                title: 'B-roll - For Video Footage (including interviews)',
                good: '[B-roll: person typing code in VS Code and executing program]\nType your Python code carefully and run it.',
                bad: '[B-roll: person at computer]\nWrite your code.',
              },
              {
                title: 'Citation - For Source Attribution',
                good: '[Citation: Python Official Site - https://python.org]\nCrediting the source of information.',
                bad: '[Citation: website]\nSource reference.',
              },
            ].map((example, idx) => (
              <div key={idx} className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-semibold text-gray-900 mb-3">{example.title}</h4>
                <div className="space-y-2 text-sm">
                  <div className="bg-green-50 p-3 rounded border-l-2 border-green-500">
                    <span className="text-green-700 font-semibold">✅ Specific: </span>
                    <pre className="mt-2 text-xs bg-green-100 p-2 rounded overflow-x-auto">{example.good}</pre>
                  </div>
                  <div className="bg-red-50 p-3 rounded border-l-2 border-red-500">
                    <span className="text-red-700 font-semibold">❌ Vague: </span>
                    <pre className="mt-2 text-xs bg-red-100 p-2 rounded overflow-x-auto">{example.bad}</pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Best Practices */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Best Practices</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-green-700 text-lg mb-4">✅ Do's</h3>
              <ul className="space-y-2 text-gray-700">
                <li>✓ Write as you would speak in the video</li>
                <li>✓ Include specific software and tool names</li>
                <li>✓ Mention visual elements (buttons, menus, windows)</li>
                <li>✓ Use action verbs (click, type, drag, select)</li>
                <li>✓ Reference colors, positions, and UI elements</li>
                <li>✓ Keep sections focused on single topics</li>
                <li>✓ Use consistent terminology throughout</li>
                <li>✓ Place instructions before their associated text</li>
                <li>✓ Be specific in instruction descriptions</li>
                <li>✓ Use proper capitalization: <code className="bg-gray-100 px-1 rounded text-xs">[Action: ...]</code></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-red-700 text-lg mb-4">❌ Don'ts</h3>
              <ul className="space-y-2 text-gray-700">
                <li>✗ Write overly long paragraphs (&gt;50 words)</li>
                <li>✗ Use only abstract concepts without visuals</li>
                <li>✗ Include complex formatting (tables, code blocks)</li>
                <li>✗ Write exclusively in passive voice</li>
                <li>✗ Use vague references ("this", "that", "it")</li>
                <li>✗ Include placeholder text like "[TODO]"</li>
                <li>✗ Use vague instructions like <code className="bg-gray-100 px-1 rounded text-xs">[Show: stuff]</code></li>
                <li>✗ Mix capitalization: <code className="bg-gray-100 px-1 rounded text-xs">[show: ...]</code> or <code className="bg-gray-100 px-1 rounded text-xs">Show:</code></li>
                <li>✗ Leave orphaned instructions disconnected from text</li>
                <li>✗ Over-instruct every sentence</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Complete Template */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Complete Script Template</h2>
          <p className="text-gray-700 mb-4">
            A full template combining all elements for a professional video script:
          </p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`Title: Python Beginners Tutorial
Hook: Learn Python from scratch in 15 minutes
Channel: Tech Tutorials
Duration: 15:00
Tags: python, tutorial, programming

## Motivation

Why should you learn Python? It's one of the most popular languages.

## Content

### Part 1: Installation

[Image: Python.org homepage]
First, visit the official Python website and download the latest version.

[Image: installer wizard dialog]
Run the installation wizard and follow the prompts to complete setup.

[Annotation: "Python 3.12 recommended"]
Make sure you install the latest stable version available.

[Citation: Python.org - Official Downloads]

### Part 2: Your First Program

[Image: text editor with code]
Create a new file called hello.py and write your first program.

[B-roll: person typing code, terminal executing]
Type the print statement to display text on the screen.

[Image: terminal output showing result]
Run your script and see the result appear in the terminal.

## Call to Action

Subscribe for more Python tutorials and programming content!

## Sources

- [Official Python Site](https://python.org)
- [Python Documentation](https://docs.python.org)`}
          </pre>
        </div>

        {/* Common Patterns */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Common Script Patterns</h2>

          <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Tutorial Structure</h3>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-6">
{`# [Technology] Tutorial: [Topic]

## Introduction
Brief overview of what you'll learn and why it's useful.

## Prerequisites
What viewers need before starting (software, knowledge, etc.).

## Step 1: [Action]
Detailed instructions with specific steps and visual cues.

## Step 2: [Next Action]
Continue with logical progression.

## Troubleshooting
Common issues and solutions.

## Conclusion
Summary and next steps.`}
          </pre>

          <h3 className="text-lg font-semibold text-gray-900 mb-3 mt-6">Product Demo Structure</h3>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
{`# [Product Name] Demo: [Feature]

## Overview
What the product does and key benefits.

## Getting Started
How to access and initial setup.

## Key Features
Demonstrate main functionality with specific actions.

## Use Cases
Real-world examples and scenarios.

## Wrap Up
Summary and call-to-action.`}
          </pre>
        </div>

        {/* Troubleshooting */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Troubleshooting</h2>
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Problem: Beats Are Too Short (&lt; 5 seconds)</h3>
              <p className="text-gray-700 mb-3">Write longer sentences or combine related ideas:</p>
              <div className="space-y-2 text-sm">
                <div className="bg-red-50 p-3 rounded">
                  <span className="text-red-700 font-semibold">❌ </span>
                  <span className="text-gray-700">Install Python. Open the terminal. Run the command.</span>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <span className="text-green-700 font-semibold">✅ </span>
                  <span className="text-gray-700">Install Python from the official website, then open your terminal and run the python --version command to verify the installation.</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Problem: Beats Are Too Long (&gt; 10 seconds)</h3>
              <p className="text-gray-700 mb-3">Break complex ideas into simpler sentences:</p>
              <div className="space-y-2 text-sm">
                <div className="bg-red-50 p-3 rounded">
                  <span className="text-red-700 font-semibold">❌ </span>
                  <span className="text-gray-700">Navigate to the Python website, download the installer, run the installation wizard, accept the license, choose your directory, and wait for completion.</span>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <span className="text-green-700 font-semibold">✅ </span>
                  <span className="text-gray-700">Navigate to the Python website and download the installer. Run the installation wizard and follow the prompts to complete the setup.</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Problem: B-Roll Queries Are Too Generic</h3>
              <p className="text-gray-700 mb-3">Include more specific visual keywords:</p>
              <div className="space-y-2 text-sm">
                <div className="bg-red-50 p-3 rounded">
                  <span className="text-red-700 font-semibold">❌ </span>
                  <span className="text-gray-700">We'll work on the project now.</span>
                </div>
                <div className="bg-green-50 p-3 rounded">
                  <span className="text-green-700 font-semibold">✅ </span>
                  <span className="text-gray-700">Open Visual Studio Code and create a new React project using the terminal.</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Key Principles */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Key Principles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                icon: '💬',
                title: 'Write Conversationally',
                desc: 'Use natural speech patterns as if you\'re talking to the viewer.',
              },
              {
                icon: '🎯',
                title: 'Include Visual Keywords',
                desc: 'Mention concrete objects, actions, and concepts for B-roll generation.',
              },
              {
                icon: '📝',
                title: 'Use Descriptive Language',
                desc: 'Help the system understand what visuals would be relevant.',
              },
              {
                icon: '🏗️',
                title: 'Structure with Headers',
                desc: 'Use # and ## to organize content and provide context.',
              },
            ].map((principle, idx) => (
              <div key={idx} className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="text-3xl mb-2">{principle.icon}</div>
                <p className="font-semibold text-gray-900 mb-2">{principle.title}</p>
                <p className="text-gray-700 text-sm">{principle.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
