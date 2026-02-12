import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Clock, FileText, Trash2, Loader2 } from 'lucide-react'
import { listSessions, deleteSession } from '../services/api'
import type { SessionListItem } from '../types/models'

export function RecentProjects() {
    const navigate = useNavigate()
    const [sessions, setSessions] = useState<SessionListItem[]>([])
    const [isLoading, setIsLoading] = useState(true)
    const [deletingId, setDeletingId] = useState<string | null>(null)

    useEffect(() => {
        loadSessions()
    }, [])

    const loadSessions = async () => {
        try {
            const data = await listSessions()
            setSessions(data)
        } catch (error) {
            console.error('Failed to load sessions:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleDelete = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation()
        if (!confirm('Delete this project? This cannot be undone.')) return

        setDeletingId(sessionId)
        try {
            await deleteSession(sessionId)
            setSessions(sessions.filter(s => s.sessionId !== sessionId))
        } catch (error) {
            console.error('Failed to delete session:', error)
            alert('Failed to delete project')
        } finally {
            setDeletingId(null)
        }
    }

    const handleOpenSession = (sessionId: string) => {
        navigate(`/workflow?session=${sessionId}`)
    }

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr)
        const now = new Date()
        const diffMs = now.getTime() - date.getTime()
        const diffMins = Math.floor(diffMs / 60000)
        const diffHours = Math.floor(diffMs / 3600000)
        const diffDays = Math.floor(diffMs / 86400000)

        if (diffMins < 60) return `${diffMins}m ago`
        if (diffHours < 24) return `${diffHours}h ago`
        if (diffDays < 7) return `${diffDays}d ago`
        return date.toLocaleDateString()
    }

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 size={24} className="text-white/20 animate-spin" />
            </div>
        )
    }

    if (sessions.length === 0) {
        return null
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
            className="w-full max-w-4xl mx-auto mt-16"
        >
            <div className="mb-6 flex items-center gap-3">
                <Clock size={16} className="text-white/30" />
                <h2 className="text-[10px] font-black text-white/40 uppercase tracking-[0.3em]">
                    Recent Projects
                </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AnimatePresence mode="popLayout">
                    {sessions.slice(0, 6).map((session, idx) => (
                        <motion.button
                            key={session.sessionId}
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ duration: 0.3, delay: idx * 0.05 }}
                            onClick={() => handleOpenSession(session.sessionId)}
                            className="group relative bg-white/[0.02] backdrop-blur-xl border border-white/5 rounded-2xl p-6 text-left hover:bg-white/[0.04] hover:border-white/10 transition-all duration-500 overflow-hidden"
                        >
                            {/* Hover gradient */}
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/0 to-purple-500/0 group-hover:from-blue-500/5 group-hover:to-purple-500/5 transition-all duration-700 pointer-events-none" />

                            <div className="relative z-10">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-blue-500/10 group-hover:border-blue-500/20 transition-all duration-500">
                                            <FileText size={18} className="text-white/40 group-hover:text-blue-400 transition-colors duration-500" />
                                        </div>
                                        <div>
                                            <h3 className="text-sm font-black text-white/90 truncate max-w-[200px] group-hover:text-white transition-colors">
                                                {session.scriptName}
                                            </h3>
                                            <p className="text-[10px] font-bold text-white/30 uppercase tracking-wider mt-0.5">
                                                {session.beatCount} beats
                                            </p>
                                        </div>
                                    </div>

                                    <button
                                        onClick={(e) => handleDelete(session.sessionId, e)}
                                        disabled={deletingId === session.sessionId}
                                        className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 p-2 hover:bg-red-500/10 rounded-lg"
                                    >
                                        {deletingId === session.sessionId ? (
                                            <Loader2 size={14} className="text-red-400 animate-spin" />
                                        ) : (
                                            <Trash2 size={14} className="text-white/30 hover:text-red-400 transition-colors" />
                                        )}
                                    </button>
                                </div>

                                <div className="flex items-center gap-2 text-[9px] font-black text-white/20 uppercase tracking-[0.2em]">
                                    <Clock size={10} />
                                    {formatDate(session.updatedAt)}
                                </div>
                            </div>
                        </motion.button>
                    ))}
                </AnimatePresence>
            </div>
        </motion.div>
    )
}
