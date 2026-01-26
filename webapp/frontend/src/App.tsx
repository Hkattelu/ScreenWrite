/**
 * Main App component with routing
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Home } from './pages/Home'
import { Workflow } from './pages/Workflow'
import { SyntaxGuide } from './pages/SyntaxGuide'
import './styles/index.css'

function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/workflow" element={<Workflow />} />
          <Route path="/syntax-guide" element={<SyntaxGuide />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        
        {/* Gentle Ko-fi Link */}
        <div className="fixed bottom-6 right-6 z-50">
          <a 
            href="https://ko-fi.com/glowstringman" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-md border border-gray-100 rounded-full shadow-sm hover:shadow-md hover:border-gray-200 transition-all group"
          >
            <span className="text-xl">☕</span>
            <span className="text-sm font-medium text-gray-500 group-hover:text-black transition-colors">
              Support on Ko-fi
            </span>
          </a>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
