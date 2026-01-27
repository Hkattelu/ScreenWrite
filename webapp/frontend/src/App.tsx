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
        
        {/* Cinematic Support Credit */}
        <div className="fixed bottom-10 left-10 z-50 group">
          <a 
            href="https://ko-fi.com/glowstringman" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex flex-col gap-0 active:scale-95 transition-transform duration-200"
          >
            <div className="bg-black text-white px-4 py-1.5 flex items-center gap-3 rounded-t-sm">
              <Film size={12} className="text-blue-500 fill-blue-500" />
              <span className="text-[10px] font-black uppercase tracking-[0.3em]">Executive Producer</span>
            </div>
            <div className="bg-white border-x border-b border-black px-4 py-2 flex items-center justify-between group-hover:bg-gray-50 transition-colors rounded-b-sm">
              <span className="text-xs font-bold text-black tracking-tight" style={{ fontFamily: "'Charter', serif" }}>
                GlowStringman
              </span>
              <div className="flex items-center gap-1.5 ml-8">
                <span className="text-[9px] font-black uppercase tracking-widest text-gray-400">Support</span>
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
              </div>
            </div>
          </a>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
