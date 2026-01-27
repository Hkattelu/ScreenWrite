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
        
        {/* Editorial Support Link */}
        <div className="fixed bottom-8 right-8 z-50">
          <a 
            href="https://ko-fi.com/glowstringman" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-4 group"
          >
            <div className="h-px w-8 bg-gray-200 group-hover:w-12 group-hover:bg-blue-500 transition-all duration-500" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 group-hover:text-black transition-colors">
              Support Development
            </span>
          </a>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
