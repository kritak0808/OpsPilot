'use client'

import * as React from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Terminal as TermIcon, Play, AlertTriangle, CheckCircle2, 
  Clock, ArrowLeft, Download, Copy, PlayCircle, Loader2
} from 'lucide-react'

interface LogMessage {
  stage: string
  message: string
  timestamp: string
}

export default function PipelineRunConsolePage() {
  const { runId } = useParams() as { runId: string }
  const { token } = useAuth()
  const router = useRouter()

  const [status, setStatus] = React.useState('pending')
  const [stages, setStages] = React.useState<Record<string, string>>({
    build: 'pending',
    test: 'pending',
    deploy: 'pending',
  })
  const [logs, setLogs] = React.useState<LogMessage[]>([])
  const [error, setError] = React.useState('')
  const [autoScroll, setAutoScroll] = React.useState(true)
  const logEndRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (!runId) return

    // Establish dynamic WebSocket connection to stream logs in real-time
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const wsBaseUrl = baseUrl.replace(/^http/, 'ws')
    const wsUrl = `${wsBaseUrl}/api/v1/pipelines/ws/runs/${runId}`
    const socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      setStatus('running')
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'stage_update') {
        setStages((prev) => ({ ...prev, [data.stage]: data.status }))
      } else if (data.type === 'console_log') {
        setLogs((prev) => [
          ...prev,
          { stage: data.stage, message: data.message, timestamp: data.timestamp },
        ])
      } else if (data.type === 'pipeline_complete') {
        setStatus(data.status)
        socket.close()
      }
    }

    socket.onerror = () => {
      setError('Real-time telemetry stream failed.')
      setStatus('failed')
    }

    socket.onclose = () => {
      // Stream finished
    }

    return () => {
      socket.close()
    }
  }, [runId])

  React.useEffect(() => {
    if (autoScroll) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  const getStatusColor = (val: string) => {
    switch (val) {
      case 'success':
        return 'text-success'
      case 'failed':
        return 'text-error'
      case 'running':
        return 'text-primary'
      default:
        return 'text-muted-foreground/60'
    }
  }

  const getStatusBg = (val: string) => {
    switch (val) {
      case 'success':
        return 'bg-success/10 border-success/20'
      case 'failed':
        return 'bg-error/10 border-error/20'
      case 'running':
        return 'bg-primary/10 border-primary/20'
      default:
        return 'bg-muted/10 border-border/40'
    }
  }

  const handleCopyLogs = () => {
    const text = logs.map(l => `[${l.stage.toUpperCase()}] ${l.message}`).join('\n')
    navigator.clipboard.writeText(text)
    alert('Logs copied to clipboard')
  }

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="pipelines">
        <div className="p-8 space-y-6 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
          
          {/* Header */}
          <div className="flex justify-between items-center border-b border-border pb-4 shrink-0">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => router.push('/pipelines')}
                className="p-1.5 border border-border bg-card rounded-md hover:bg-muted/30"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              <div>
                <h1 className="text-base font-semibold flex items-center gap-2">
                  Pipeline Run Telemetry Console
                </h1>
                <p className="text-[10px] text-muted-foreground font-mono">Run: {runId}</p>
              </div>
            </div>
            <div className="flex gap-2.5">
              <span className={`px-3 py-1 rounded border text-[10px] font-bold uppercase tracking-wider ${getStatusBg(status)} ${getStatusColor(status)}`}>
                {status}
              </span>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-error/15 border border-error/20 text-error text-xs rounded shrink-0 select-none">
              {error}
            </div>
          )}

          {/* Interactive Connected Pipeline Stages Diagram */}
          <div className="grid grid-cols-3 gap-4 shrink-0 select-none">
            {Object.entries(stages).map(([stageName, stageStatus], idx) => {
              const isRunning = stageStatus === 'running'
              const isSuccess = stageStatus === 'success'
              const isFailed = stageStatus === 'failed'
              return (
                <div 
                  key={stageName}
                  className={`p-4 border rounded-xl flex items-center gap-3 transition-colors ${getStatusBg(stageStatus)}`}
                >
                  <div className="h-8 w-8 rounded-lg bg-card border border-border flex items-center justify-center font-bold text-xs shrink-0 shadow-sm">
                    {idx + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xs font-semibold capitalize truncate">{stageName} Stage</h3>
                    <p className={`text-[10px] font-bold uppercase mt-0.5 ${getStatusColor(stageStatus)}`}>
                      {stageStatus}
                    </p>
                  </div>
                  {isRunning && <Loader2 className="h-4.5 w-4.5 text-primary animate-spin shrink-0" />}
                  {isSuccess && <CheckCircle2 className="h-4.5 w-4.5 text-success shrink-0" />}
                  {isFailed && <AlertTriangle className="h-4.5 w-4.5 text-error shrink-0" />}
                </div>
              )
            })}
          </div>

          {/* Premium Console output Terminal */}
          <div className="flex-1 min-h-0 border border-border bg-[#09090b] rounded-xl flex flex-col shadow-inner overflow-hidden">
            
            {/* Terminal Tab Bar */}
            <div className="px-4 py-2 bg-card/65 border-b border-border flex justify-between items-center shrink-0 select-none">
              <div className="flex items-center gap-2">
                <TermIcon className="h-4 w-4 text-primary" />
                <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">NOC Terminal Console</span>
              </div>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setAutoScroll(!autoScroll)}
                  className={`px-2 py-1 rounded text-[9px] font-bold border transition-colors ${
                    autoScroll ? 'border-primary/20 bg-primary/10 text-primary' : 'border-border text-muted-foreground'
                  }`}
                >
                  Auto-Scroll: {autoScroll ? 'ON' : 'OFF'}
                </button>
                <button 
                  onClick={handleCopyLogs}
                  className="p-1 border border-border bg-background hover:bg-muted/50 rounded-md text-foreground/50 hover:text-foreground"
                  title="Copy logs"
                >
                  <Copy className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            {/* Terminal Body */}
            <div className="flex-1 overflow-y-auto p-5 font-mono text-[10px] text-zinc-400 leading-relaxed scrollbar-thin select-text">
              <div className="text-zinc-600 border-b border-border/30 pb-2 mb-3">
                --- PIPELINE LOG STREAM SYSTEM INITIALIZED ---
              </div>
              {logs.map((log, idx) => (
                <div key={idx} className="flex gap-4 hover:bg-white/2 p-0.5 rounded">
                  <span className="text-primary font-semibold select-none">[{log.stage.toUpperCase()}]</span>
                  <span className="flex-1 break-all">{log.message}</span>
                </div>
              ))}
              {logs.length === 0 && status === 'pending' && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  <span>Enqueuing workspace builder pods...</span>
                </div>
              )}
              <div ref={logEndRef} />
            </div>

          </div>

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
