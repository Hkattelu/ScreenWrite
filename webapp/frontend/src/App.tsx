/**
 * Main App component with routing
 */

import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom'
import { Home } from './pages/Home'
import { Workflow } from './pages/Workflow'
import { SyntaxGuide } from './pages/SyntaxGuide'
import { Film } from 'lucide-react'
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
        
        {/* Floating Support Button */}
        <div className="fixed bottom-8 right-8 z-50 group">
          <a 
            href="https://ko-fi.com/glowstringman" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center gap-3 pl-3 pr-5 py-2 bg-[oklch(85%_0.15_85)] hover:bg-[oklch(88%_0.17_88)] text-black rounded-full shadow-lg shadow-[oklch(85%_0.15_85/0.2)] hover:shadow-[oklch(85%_0.15_85/0.4)] active:scale-95 transition-all duration-300 ring-1 ring-black/5"
          >
            <div className="relative flex items-center justify-center w-9 h-9 bg-white rounded-full shadow-inner group-hover:scale-110 transition-transform duration-500 ease-out-back">
              <svg 
                viewBox="0 0 24 24" 
                fill="currentColor" 
                className="w-5 h-5 text-[oklch(65%_0.2_30)] group-hover:animate-pulse"
              >
                <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
              </svg>
              {/* Little sparkle */}
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full animate-ping opacity-0 group-hover:opacity-100" />
            </div>
            <div className="flex flex-col -gap-1">
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-black/40 leading-none">Support</span>
              <span className="text-sm font-black uppercase tracking-tight leading-none">Project</span>
            </div>
          </a>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
