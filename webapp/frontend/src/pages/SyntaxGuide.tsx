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
          Learn how to write markdown scripts that generate optimal B-roll and timelines.
        </p>

        {/* Basic Structure Section */}
        <div className="card mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Basic Structure</h2>
          <p className="text-gray-700 mb-4">
            Scripts use standard markdown with headers and paragraphs:
          </p>
          <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm mb-4">
{`# Main Title

## Section Header

Your script content goes here. Write naturally as you would speak in your video.

## Another Section

Continue with more content. Each paragraph will be analyzed for visual keywords.`}
          </pre>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li>Use <code className="bg-gray-100 px-2 py-1 rounded">#</code> for the main title</li>
            <li>Use <code className="bg-gray-100 px-2 py-1 rounded">##</code> for section headers</li>
            <li>Write naturally as you would speak</li>
            <li>Include visual keywords (specific tools, objects, actions)</li>
          </ul>
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
              </ul>
            </div>
          </div>
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
