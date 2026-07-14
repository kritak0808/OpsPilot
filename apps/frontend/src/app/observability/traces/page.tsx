'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Span {
  span_id: string
  name: string
  duration_ms: number
  parent_span_id: string | null
}

export default function TraceExplorerPage() {
  const [spans, setSpans] = React.useState<Span[]>([])
  const [projectId, setProjectId] = React.useState('')
  const [traceId, setTraceId] = React.useState('')
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(false)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchTraces = React.useCallback(async () => {
    if (!token || !projectId) return
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/traces', {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
      })
      if (!res.ok) throw new Error('Trace analysis fetch failed.')
      const data = await res.json()
      setSpans(data.spans || [])
      setTraceId(data.trace_id)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, projectId])

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

  React.useEffect(() => {
    fetchTraces()
  }, [fetchTraces])

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-6">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-xl font-bold tracking-tight">OpenTelemetry trace waterfall</h1>
            {traceId && <p className="text-xs text-foreground/50 mt-1">Trace ID: <span className="font-mono">{traceId}</span></p>}
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

        {isLoading ? (
          <div className="text-sm text-foreground/50 py-8">Analyzing transaction trace tree...</div>
        ) : (
          <div className="border border-[#1d232f] bg-[#11151c] rounded-md p-6 space-y-4">
            <h2 className="text-base font-bold uppercase tracking-wider text-foreground/75">Spans Waterfall</h2>
            
            <div className="space-y-4 pt-4">
              {spans.map((span) => (
                <div key={span.span_id} className="space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className={`font-mono ${span.parent_span_id ? 'pl-8 text-foreground/60' : 'font-semibold text-foreground/95'}`}>
                      {span.parent_span_id ? '└── ' : ''}{span.name}
                    </span>
                    <span className="font-mono text-primary font-bold">{span.duration_ms}ms</span>
                  </div>
                  <div className="w-full bg-[#090b0f] h-2 rounded overflow-hidden">
                    <div
                      className="bg-primary h-full rounded"
                      style={{
                        marginLeft: span.parent_span_id ? '20%' : '0%',
                        width: `${(span.duration_ms / 350) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
