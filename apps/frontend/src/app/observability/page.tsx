'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { motion } from 'framer-motion'
import { 
  Activity, Terminal, Compass, ShieldAlert, FolderOpen,
  ArrowUpRight, RefreshCw, Layers, CheckCircle2
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

interface Project {
  id: string
  name: string
}

export default function ObservabilityDashboard() {
  const [projects, setProjects] = React.useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = React.useState('')
  const [cpuUsage, setCpuUsage] = React.useState<any[]>([])
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchProjects = React.useCallback(async () => {
    if (!token || !activeOrgId) return
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/projects', {
        headers: { Authorization: `Bearer ${token}`, 'X-Org-ID': activeOrgId },
      })
      if (!res.ok) throw new Error('Failed to query projects.')
      const data = await res.json()
      setProjects(data)
      if (data.length > 0) {
        setSelectedProjectId(data[0].id)
      } else {
        setIsLoading(false)
      }
    } catch (err: any) {
      setError(err.message)
      setIsLoading(false)
    }
  }, [token, activeOrgId])

  React.useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  const fetchMetrics = React.useCallback(async () => {
    if (!token || !selectedProjectId) return
    setIsLoading(true)
    try {
      const res = await fetch(`/api/v1/metrics?metric_name=cpu_usage`, {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': selectedProjectId },
      })
      if (res.ok) {
        const data = await res.json()
        const points = (data.points || []).map((pt: any, idx: number) => ({
          name: pt.timestamp ? new Date(pt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : `${idx}:00`,
          value: pt.value
        }))
        setCpuUsage(points)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, selectedProjectId])

  React.useEffect(() => {
    fetchMetrics()
  }, [fetchMetrics])

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="observability">
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary">
                Observability APM Explorer
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Analyze live time-series capacity metrics, monitor SLO compliance levels, and search Loki traces
              </p>
            </div>
            
            <div className="flex gap-2.5">
              <button
                onClick={() => router.push('/observability/logs')}
                className="flex items-center gap-1 px-3 py-1.5 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80"
              >
                Logs
              </button>
              <button
                onClick={() => router.push('/observability/traces')}
                className="flex items-center gap-1 px-3 py-1.5 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80"
              >
                Traces
              </button>
              <button
                onClick={() => router.push('/observability/incidents')}
                className="flex items-center gap-1 px-4 py-2 bg-error hover:bg-error/90 text-white text-xs font-semibold rounded-md shadow-md shadow-error/10"
              >
                Incidents Dashboard
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded-md">
              {error}
            </div>
          )}

          {/* Scope Select Panel */}
          <div className="flex items-center gap-3 bg-card/40 p-4 border border-border rounded-lg select-none">
            <FolderOpen className="h-4 w-4 text-primary" />
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Scope Project:</label>
            <select
              className="bg-background border border-border px-3 py-1.5 text-xs rounded-md outline-none text-foreground cursor-pointer focus:border-primary transition-colors"
              value={selectedProjectId}
              onChange={(e) => setSelectedProjectId(e.target.value)}
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* CPU utilization Recharts AreaChart */}
            <div className="md:col-span-2 border border-border bg-card p-6 rounded-xl space-y-4 flex flex-col h-80">
              <div className="flex justify-between items-center select-none">
                <h2 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-primary" />
                  CPU Core Utilization (%)
                </h2>
                <button 
                  onClick={fetchMetrics} 
                  disabled={isLoading}
                  className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              <div className="flex-1 min-h-0">
                {isLoading ? (
                  <div className="w-full h-full bg-muted/20 animate-pulse rounded-md" />
                ) : cpuUsage.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={cpuUsage} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="obsCpu" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.2}/>
                          <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="name" stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} />
                      <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} />
                      <Tooltip contentStyle={{ background: '#111113', borderColor: '#232326', fontSize: 11 }} />
                      <Area type="monotone" dataKey="value" stroke="#7C3AED" strokeWidth={1.5} fillOpacity={1} fill="url(#obsCpu)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full border border-dashed border-border flex items-center justify-center text-xs text-muted-foreground rounded-lg">
                    No metric data points registered for this time frame.
                  </div>
                )}
              </div>
            </div>

            {/* SLO status compliance metrics */}
            <div className="md:col-span-1 border border-border bg-card p-6 rounded-xl space-y-6 h-80 flex flex-col justify-between select-none">
              <div>
                <h2 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-success" />
                  SLO Compliance Targets
                </h2>
                <p className="text-[10px] text-muted-foreground mt-0.5">30-day compliance rolling averages</p>
              </div>

              <div className="space-y-4 flex-1 pt-4">
                {[
                  { name: 'Gateway Availability', met: '99.98%', target: '99.90%', ok: true },
                  { name: 'API Latency P99', met: '180ms', target: '250ms', ok: true },
                  { name: 'Database Queries P95', met: '32ms', target: '50ms', ok: true }
                ].map((slo, idx) => (
                  <div key={idx} className="border-b border-border/60 pb-3 space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-foreground/90">{slo.name}</span>
                      <span className="text-success font-bold font-mono">{slo.met}</span>
                    </div>
                    <div className="flex justify-between text-[9px] text-muted-foreground">
                      <span>Target: {slo.target}</span>
                      <span className="text-success uppercase font-extrabold">Active</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
