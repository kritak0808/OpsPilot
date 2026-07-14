'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Log {
  timestamp: string
  service: string
  level: string
  message: string
}

export default function LogsExplorerPage() {
  const [logs, setLogs] = React.useState<Log[]>([])
  const [query, setQuery] = React.useState('')
  const [projectId, setProjectId] = React.useState('')
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(false)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchLogs = React.useCallback(async () => {
    if (!token || !projectId) return
    setIsLoading(true)
    setError('')
    try {
      const res = await fetch(`/api/v1/logs?query=${encodeURIComponent(query)}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
      })
      if (!res.ok) throw new Error('Query logs execution failed.')
      const data = await res.json()
      setLogs(data.logs || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, projectId, query])

  // Get project ID first
  React.useEffect(() => {
    if (!token || !activeOrgId) return
    fetch('/api/v1/projects', {
      headers: { Authorization: `Bearer ${token}`, 'X-Org-ID': activeOrgId },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.length > 0) setProjectId(data[0].id)
      })
  }, [token, activeOrgId])

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'text-error font-bold'
      case 'WARN':
        return 'text-warning font-semibold'
      default:
        return 'text-foreground/50'
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-6">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Loki Logs Console</h1>
            <p className="text-xs text-foreground/50">Query and filter aggregated microservice container logs.</p>
          </div>
          <button
            onClick={() => router.push('/observability')}
            className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
          >
            Observability Panel
          </button>
        </header>

        {error && (
          <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded max-w-md">
            {error}
          </div>
        )}

        <div className="flex gap-4">
          <input
            type="text"
            className="flex-1 bg-[#11151c] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9] font-mono"
            placeholder='e.g. {container="api-gateway"} |= "error"'
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            onClick={fetchLogs}
            disabled={isLoading || !projectId}
            className="px-6 py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Querying...' : 'LogQL Search'}
          </button>
        </div>

        {/* Console log list window */}
        <div className="border border-[#1d232f] bg-[#090b0f] p-6 rounded-md h-[550px] overflow-y-auto font-mono text-xs text-[#a3b3c2] leading-relaxed scrollbar-thin space-y-2">
          {logs.length > 0 ? (
            logs.map((log, idx) => (
              <div key={idx} className="flex gap-4 border-b border-border/5 pb-1">
                <span className="text-foreground/40">{log.timestamp.split(' ')[1] || log.timestamp}</span>
                <span className="text-primary">{`[${log.service.toUpperCase()}]`}</span>
                <span className={getLevelColor(log.level)}>{`[${log.level}]`}</span>
                <span>{log.message}</span>
              </div>
            ))
          ) : (
            <p className="text-foreground/30 text-center py-20">Enter LogQL search statement to query logs stream.</p>
          )}
        </div>
      </div>
    </ProtectedRoute>
  )
}
