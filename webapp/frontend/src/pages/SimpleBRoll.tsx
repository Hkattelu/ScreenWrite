import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { searchSimpleBRoll, downloadSimpleBRoll, type AssetCandidate } from '../services/api'

export function SimpleBRoll() {
    const navigate = useNavigate()
    const [query, setQuery] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [candidates, setCandidates] = useState<AssetCandidate[]>([])
    const [selectedCandidate, setSelectedCandidate] = useState<AssetCandidate | null>(null)
    const [startTime, setStartTime] = useState(0)
    const [segmentDuration, setSegmentDuration] = useState(5)
    const [isDownloading, setIsDownloading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // History state
    const [history, setHistory] = useState<AssetCandidate[]>([])

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = Math.floor(seconds % 60)
        const ms = Math.floor((seconds % 1) * 10)
        return `${mins}:${secs.toString().padStart(2, '0')}.${ms}`
    }

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim()) return

        setIsLoading(true)
        setError(null)
        setCandidates([])

        try {
            const results = await searchSimpleBRoll(query)
            setCandidates(results)
            if (results.length === 0) {
                setError('No videos found for this query.')
            }
        } catch (err: any) {
            setError(err.message || 'Search failed. Is the backend running?')
        } finally {
            setIsLoading(false)
        }
    }

    const handleDownload = async () => {
        if (!selectedCandidate) return

        setIsDownloading(true)
        setError(null)

        try {
            const blob = await downloadSimpleBRoll(selectedCandidate, startTime, segmentDuration)

            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `broll_${selectedCandidate.title.replace(/\s+/g, '_')}_${Math.floor(startTime)}s.mp4`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)

            // Add to history if not duplicate by ID
            setHistory(prev => {
                const exists = prev.some(h => h.id === selectedCandidate.id)
                return exists ? prev : [selectedCandidate, ...prev].slice(0, 10)
            })

            // Close modal on success
            setSelectedCandidate(null)
        } catch (err) {
            setError('Download failed. Please try again.')
        } finally {
            setIsDownloading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white p-6 md:p-12 selection:bg-blue-500/30">
            {/* Background Decor */}
            <div className="fixed inset-0 pointer-events-none opacity-20">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-600 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600 rounded-full blur-[120px]" />
            </div>

            <div className="max-w-7xl mx-auto relative z-10 grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-12">
                <div className="flex flex-col">
                    {/* Header */}
                    <header className="flex items-center justify-between mb-12">
                        <button
                            onClick={() => navigate('/')}
                            className="group flex items-center gap-2 text-white/40 hover:text-white transition-colors"
                        >
                            <svg className="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                            <span className="text-sm font-bold uppercase tracking-widest">Back</span>
                        </button>

                        <div className="flex flex-col items-end">
                            <span className="text-[10px] font-black uppercase tracking-[0.4em] text-blue-500 mb-1 font-mono">LIGHTWEIGHT_MODE</span>
                            <h1 className="text-2xl font-medium tracking-tight italic">Simple B-Roll</h1>
                        </div>
                    </header>

                    {/* Search Bar */}
                    <section className="mb-12">
                        <form onSubmit={handleSearch} className="relative max-w-2xl group">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Search for footage..."
                                className="w-full bg-white/[0.03] border border-white/10 rounded-2xl px-8 py-5 text-xl outline-none focus:border-blue-500/50 focus:bg-white/[0.05] transition-all placeholder:text-white/10"
                            />
                            <div className="absolute right-3 top-3 bottom-3 flex gap-2">
                                {query && (
                                    <button
                                        type="button"
                                        onClick={() => setQuery('')}
                                        className="px-4 text-white/20 hover:text-white transition-colors capitalize text-xs font-bold"
                                    >
                                        Clear
                                    </button>
                                )}
                                <button
                                    type="submit"
                                    disabled={isLoading || !query.trim()}
                                    className="px-6 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 rounded-xl font-bold transition-all active:scale-95 flex items-center gap-2"
                                >
                                    {isLoading ? (
                                        <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                    ) : (
                                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                        </svg>
                                    )}
                                    <span>Search</span>
                                </button>
                            </div>
                        </form>
                    </section>

                    {/* Error State */}
                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="mb-8 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-center text-sm font-medium"
                            >
                                {error}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Results Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
                        <AnimatePresence mode="popLayout">
                            {candidates.map((candidate, idx) => (
                                <motion.div
                                    key={candidate.id + idx}
                                    layout
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                    whileHover={{ y: -8 }}
                                    onClick={() => {
                                        setSelectedCandidate(candidate)
                                        setStartTime(0)
                                        setSegmentDuration(Math.min(5, candidate.duration))
                                    }}
                                    className="group relative bg-white/[0.02] border border-white/5 rounded-2xl overflow-hidden cursor-pointer hover:border-blue-500/30 transition-all duration-300 flex flex-col"
                                >
                                    <div className="aspect-video relative overflow-hidden bg-black/40">
                                        <img
                                            src={candidate.thumbnail_url}
                                            alt={candidate.title}
                                            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                            loading="lazy"
                                        />
                                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
                                            <div className="px-5 py-2.5 bg-white text-black text-[10px] font-black uppercase rounded-full tracking-widest shadow-xl scale-90 group-hover:scale-100 transition-transform">
                                                Configure Clip
                                            </div>
                                        </div>
                                        <div className="absolute bottom-3 right-3 px-2 py-1 bg-black/60 backdrop-blur-md rounded-lg text-[10px] font-bold border border-white/5">
                                            {Math.floor(candidate.duration / 60)}:{(Math.floor(candidate.duration) % 60).toString().padStart(2, '0')}
                                        </div>
                                    </div>
                                    <div className="p-5 flex items-center justify-between flex-grow">
                                        <h3 className="text-sm font-medium line-clamp-2 pr-4 text-white/70 group-hover:text-white transition-colors">
                                            {candidate.title}
                                        </h3>
                                        <span className="text-[9px] font-black uppercase tracking-[0.2em] text-white/10 group-hover:text-blue-500/50 transition-colors whitespace-nowrap">
                                            {candidate.source}
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Sidebar: History */}
                <div className="hidden lg:block relative">
                    <div className="sticky top-12 space-y-6">
                        <div className="flex items-center gap-2 text-white/40">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-xs font-black uppercase tracking-widest">Session History</span>
                        </div>

                        <div className="space-y-4">
                            <AnimatePresence initial={false}>
                                {history.length === 0 ? (
                                    <div className="p-8 border border-dashed border-white/5 rounded-2xl text-center">
                                        <p className="text-xs text-white/20">No clips downloaded yet</p>
                                    </div>
                                ) : (
                                    history.map((item, idx) => (
                                        <motion.div
                                            key={`${item.id}-${idx}`}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            className="group flex gap-3 p-3 bg-white/[0.02] hover:bg-white/[0.05] border border-white/5 rounded-xl transition-colors cursor-pointer"
                                            onClick={() => {
                                                setSelectedCandidate(item)
                                                setStartTime(0)
                                                setSegmentDuration(Math.min(5, item.duration))
                                            }}
                                        >
                                            <div className="w-16 h-12 rounded-lg bg-black/40 overflow-hidden shrink-0">
                                                <img src={item.thumbnail_url} className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity" />
                                            </div>
                                            <div className="flex-grow min-w-0">
                                                <p className="text-xs font-medium text-white/60 group-hover:text-white truncate transition-colors">{item.title}</p>
                                                <p className="text-[10px] text-white/20 uppercase tracking-widest mt-1">Redownload</p>
                                            </div>
                                        </motion.div>
                                    ))
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>

                {/* Selection Modal */}
                <AnimatePresence>
                    {selectedCandidate && (
                        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                onClick={() => setSelectedCandidate(null)}
                                className="absolute inset-0 bg-black/90 backdrop-blur-md"
                            />

                            <motion.div
                                initial={{ opacity: 0, scale: 0.95, y: 40 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95, y: 40 }}
                                className="relative w-full max-w-4xl bg-[#0d0d0d] border border-white/10 rounded-[40px] overflow-hidden shadow-[0_32px_128px_-32px_rgba(0,0,0,1)] grid grid-cols-1 md:grid-cols-[1.5fr_1fr]"
                            >
                                {/* Visual Preview */}
                                <div className="bg-black relative group h-full min-h-[300px] md:min-h-full">
                                    {selectedCandidate.source === 'youtube' ? (
                                        <iframe
                                            className="w-full h-full absolute inset-0"
                                            src={`https://www.youtube.com/embed/${selectedCandidate.id}?start=${Math.floor(startTime)}&autoplay=0&controls=1&modestbranding=1&rel=0`}
                                            title="YouTube Preview"
                                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                            allowFullScreen
                                        />
                                    ) : (
                                        <>
                                            <img
                                                src={selectedCandidate.thumbnail_url}
                                                alt={selectedCandidate.title}
                                                className="w-full h-full object-cover opacity-60 group-hover:opacity-40 transition-opacity"
                                            />
                                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                                <div className="px-4 py-2 bg-black/50 backdrop-blur rounded-full text-xs font-medium text-white/60">
                                                    Preview Unavailable for Stock
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>

                                {/* Controls */}
                                <div className="p-8 md:p-10 flex flex-col h-full bg-[#0d0d0d]">
                                    <div className="flex justify-between items-start mb-8">
                                        <div className="space-y-1">
                                            <h2 className="text-xl font-medium tracking-tight line-clamp-2">{selectedCandidate.title}</h2>
                                            <p className="text-[10px] text-white/20 uppercase tracking-[0.3em] font-black">{selectedCandidate.source}</p>
                                        </div>
                                        <button
                                            onClick={() => setSelectedCandidate(null)}
                                            className="p-2 -mr-2 hover:bg-white/5 rounded-full transition-colors shrink-0"
                                        >
                                            <svg className="w-6 h-6 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </button>
                                    </div>

                                    <div className="space-y-8 flex-grow">
                                        {/* Start Time Control */}
                                        <div className="space-y-3">
                                            <div className="flex justify-between text-[10px] font-black uppercase tracking-[0.2em] text-white/20">
                                                <span>Start Time</span>
                                                <span className="text-blue-500 font-mono tracking-normal text-sm">{formatTime(startTime)}</span>
                                            </div>
                                            <div className="relative h-12 bg-white/[0.02] rounded-xl overflow-hidden border border-white/5 group-hover:border-white/10 transition-colors">
                                                <motion.div
                                                    className="absolute top-0 bottom-0 bg-blue-500/10 border-r border-blue-500/50"
                                                    style={{
                                                        width: `${(startTime / selectedCandidate.duration) * 100}%`
                                                    }}
                                                />
                                                {/* Playhead Indicator */}
                                                <div
                                                    className="absolute top-0 bottom-0 border-l border-white/50 w-px z-20 pointer-events-none"
                                                    style={{ left: `${(startTime / selectedCandidate.duration) * 100}%` }}
                                                />
                                                <input
                                                    type="range"
                                                    min="0"
                                                    max={Math.max(0, selectedCandidate.duration - segmentDuration)}
                                                    step="0.1"
                                                    value={startTime}
                                                    onChange={(e) => setStartTime(parseFloat(e.target.value))}
                                                    className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-30"
                                                />
                                            </div>
                                            <p className="text-[10px] text-white/30">Drag to scrub through the video timeline.</p>
                                        </div>

                                        {/* Duration Control & Presets */}
                                        <div className="space-y-4">
                                            <div className="flex justify-between text-[10px] font-black uppercase tracking-[0.2em] text-white/20">
                                                <span>Duration</span>
                                                <span className="text-blue-500 font-mono tracking-normal text-sm">{segmentDuration.toFixed(1)}s</span>
                                            </div>

                                            {/* Presets */}
                                            <div className="flex gap-2">
                                                {[3, 5, 10, 15, 30].map(sec => (
                                                    <button
                                                        key={sec}
                                                        onClick={() => setSegmentDuration(Math.min(sec, selectedCandidate.duration))}
                                                        className={`
                              flex-1 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider border transition-all
                              ${segmentDuration === sec
                                                                ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                                                                : 'bg-white/5 border-transparent text-white/40 hover:bg-white/10 hover:text-white'}
                            `}
                                                    >
                                                        {sec}s
                                                    </button>
                                                ))}
                                            </div>

                                            <input
                                                type="range"
                                                min="1"
                                                max={Math.min(60, selectedCandidate.duration)}
                                                step="0.5"
                                                value={segmentDuration}
                                                onChange={(e) => setSegmentDuration(parseFloat(e.target.value))}
                                                className="w-full h-1.5 bg-white/[0.03] rounded-full appearance-none accent-blue-500 cursor-pointer"
                                            />
                                        </div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex gap-3 pt-8 mt-auto border-t border-white/5">
                                        <button
                                            onClick={() => setSelectedCandidate(null)}
                                            className="px-6 py-4 rounded-2xl text-xs font-bold uppercase tracking-wider text-white/30 hover:text-white hover:bg-white/5 transition-colors"
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            onClick={handleDownload}
                                            disabled={isDownloading}
                                            className="flex-grow py-4 bg-blue-600 hover:bg-blue-500 active:scale-95 disabled:opacity-50 disabled:active:scale-100 rounded-2xl text-xs font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-3 shadow-xl shadow-blue-600/10"
                                        >
                                            {isDownloading ? (
                                                <>
                                                    <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                                    <span>Processing...</span>
                                                </>
                                            ) : (
                                                <>
                                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                                    </svg>
                                                    <span>Downlaod Clip</span>
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    )
}
