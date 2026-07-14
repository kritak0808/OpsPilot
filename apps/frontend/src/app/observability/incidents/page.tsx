'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Incident {
  id: string
  title: string
  severity: string
  status: string
  description?: string
  created_at: string
}

export default function IncidentsDashboardPage() {
  const [incidents, setIncidents] = React.useState<Incident[]>([])
  const [title, setTitle] = React.useState('')
  const [severity, setSeverity] = React.useState('P0')
  const [desc, setDesc] = React.useState('')
  
  const [projectId, setProjectId] = React.useState('')
  const [error, setError] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchIncidents = React.useCallback(async () => {
    if (!token || !projectId) return
    try {
      const res = await fetch('/api/v1/incidents', {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
      })
      if (!res.ok) throw new Error('Failed to query incidents.')
      const data = await res.json()
      setIncidents(data)
    } catch (err: any) {
      setError(err.message)
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
    fetchIncidents()
  }, [fetchIncidents])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const res = await fetch('/api/v1/incidents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
        body: JSON.stringify({ title, severity, description: desc }),
      })

      if (!res.ok) throw new Error('Incident triage launch failed.')
      
      setTitle('')
      setDesc('')
      fetchIncidents()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResolve = async (id: string) => {
    try {
      const res = await fetch(`/api/v1/incidents/${id}?status_val=resolved`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to resolve.')
      fetchIncidents()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const getSevColor = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'P0':
        return 'text-error font-extrabold'
      case 'P1':
        return 'text-warning font-bold'
      default:
        return 'text-foreground/60'
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-8">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Incident Management (SRE)</h1>
            <p className="text-sm text-foreground/50">Triage active service outages, alerts, and log events.</p>
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

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* File new incident form */}
          <div className="md:col-span-1 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 h-fit">
            <h2 className="text-sm font-bold uppercase tracking-wider">File Incident</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Incident Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Gateway memory leak"
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Severity</label>
                <select
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none text-[#f1f5f9]"
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                >
                  <option value="P0">P0 (Blocker outage)</option>
                  <option value="P1">P1 (Critical degradation)</option>
                  <option value="P2">P2 (Minor bug)</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Outage Description</label>
                <textarea
                  placeholder="Details..."
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary h-20 text-[#f1f5f9]"
                  value={desc}
                  onChange={(e) => setDesc(e.target.value)}
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting || !projectId}
                className="w-full py-2 bg-error hover:bg-error/95 text-white font-semibold text-sm rounded transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Filing Outage...' : 'File Triage Outage'}
              </button>
            </form>
          </div>

          {/* Active incidents list */}
          <div className="md:col-span-2 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-foreground/75">Active Outages Triage</h2>
            
            <div className="space-y-4 pt-2">
              {incidents.length > 0 ? (
                incidents.map((inc) => (
                  <div key={inc.id} className="p-4 border border-[#1d232f] bg-[#090b0f] rounded-md flex justify-between items-center text-sm">
                    <div className="space-y-1">
                      <div className="flex items-center gap-3">
                        <h3 className="font-bold">{inc.title}</h3>
                        <span className={`text-xs ${getSevColor(inc.severity)}`}>{inc.severity}</span>
                      </div>
                      {inc.description && <p className="text-xs text-foreground/50">{inc.description}</p>}
                      <p className="text-[10px] text-foreground/40 font-mono">Opened: {inc.created_at.split('T')[0]}</p>
                    </div>

                    <div className="flex gap-3">
                      <span className="text-xs bg-error/15 text-error px-2 py-0.5 rounded font-semibold uppercase self-center h-fit">
                        {inc.status}
                      </span>
                      {inc.status !== 'resolved' && (
                        <button
                          onClick={() => handleResolve(inc.id)}
                          className="px-3 py-1 bg-success hover:bg-success/90 text-white text-xs font-semibold rounded"
                        >
                          Resolve
                        </button>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-foreground/40 py-8">No active outages currently registered.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
