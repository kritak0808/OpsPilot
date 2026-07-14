'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { 
  Play, Edit3, Plus, GitBranch, Terminal, RefreshCw, 
  Layers, FolderOpen, AlertCircle
} from 'lucide-react'

interface Project {
  id: string
  name: string
}

interface Pipeline {
  id: string
  name: string
  slug: string
  description?: string
}

export default function PipelinesPage() {
  const [projects, setProjects] = React.useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = React.useState<string>('')
  const [pipelines, setPipelines] = React.useState<Pipeline[]>([])
  
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchData = React.useCallback(async () => {
    if (!token || !activeOrgId) return
    setIsLoading(true)
    try {
      const projRes = await fetch('/api/v1/projects', {
        headers: { Authorization: `Bearer ${token}`, 'X-Org-ID': activeOrgId },
      })
      if (!projRes.ok) throw new Error('Failed to load projects.')
      const projData = await projRes.json()
      setProjects(projData)
      if (projData.length > 0) {
        setSelectedProjectId(projData[0].id)
      } else {
        setIsLoading(false)
      }
    } catch (err: any) {
      setError(err.message)
      setIsLoading(false)
    }
  }, [token, activeOrgId])

  React.useEffect(() => {
    fetchData()
  }, [fetchData])

  const fetchPipelines = React.useCallback(async () => {
    if (!token || !selectedProjectId) return
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/pipelines', {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': selectedProjectId },
      })
      if (res.ok) {
        const data = await res.json()
        setPipelines(data)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, selectedProjectId])

  React.useEffect(() => {
    fetchPipelines()
  }, [fetchPipelines])

  const handleTriggerRun = async (pipelineId: string) => {
    try {
      const res = await fetch(`/api/v1/pipelines/${pipelineId}/run`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Trigger run failed.')
      const data = await res.json()
      router.push(`/pipelines/runs/${data.id}`)
    } catch (err: any) {
      setError(err.message)
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.06 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="pipelines">
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary">
                Enterprise CI/CD Pipelines
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Configure integrations, verify deployments status, and view run executions
              </p>
            </div>
            
            <button
              onClick={() => router.push(`/pipelines/create?project_id=${selectedProjectId}`)}
              disabled={!selectedProjectId}
              className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded-md shadow-md disabled:opacity-50"
            >
              <Plus className="h-3.5 w-3.5" />
              Build Pipeline
            </button>
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

          {/* Pipelines Grid */}
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2].map(n => (
                <div key={n} className="h-28 w-full border border-border bg-card/40 rounded-xl shimmer" />
              ))}
            </div>
          ) : pipelines.length > 0 ? (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {pipelines.map((pipe) => (
                <motion.div
                  key={pipe.id}
                  variants={itemVariants}
                  className="p-6 border border-border bg-card rounded-xl hover:border-primary/20 hover:shadow-lg transition-all flex justify-between items-start gap-4 relative overflow-hidden group"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-2">
                      <Layers className="h-4 w-4 text-primary" />
                      <h2 className="text-sm font-semibold text-foreground/90 truncate">{pipe.name}</h2>
                    </div>
                    <p className="text-[9px] text-muted-foreground font-mono bg-background px-2 py-0.5 rounded border border-border/30 w-max">
                      slug: {pipe.slug}
                    </p>
                    {pipe.description && (
                      <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                        {pipe.description}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex flex-col gap-2 shrink-0 w-28">
                    <button
                      onClick={() => handleTriggerRun(pipe.id)}
                      className="w-full py-1.5 bg-success hover:bg-success/90 text-white text-[10px] font-bold rounded-lg flex items-center justify-center gap-1 transition-colors"
                    >
                      <Play className="h-3 w-3" />
                      Run Cycle
                    </button>
                    <button
                      onClick={() => router.push(`/pipelines/create?project_id=${selectedProjectId}&pipeline_id=${pipe.id}`)}
                      className="w-full py-1.5 border border-border bg-background hover:bg-muted/40 text-foreground/70 hover:text-foreground text-[10px] font-semibold rounded-lg flex items-center justify-center gap-1 transition-all"
                    >
                      <Edit3 className="h-3 w-3" />
                      Edit Config
                    </button>
                  </div>

                  <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform pointer-events-none" />
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <div className="border border-dashed border-border p-12 text-center rounded-xl max-w-md mx-auto space-y-4">
              <AlertCircle className="h-10 w-10 text-primary mx-auto" />
              <div className="space-y-1">
                <p className="text-sm font-semibold">No active pipelines</p>
                <p className="text-xs text-muted-foreground">Register your first deployment flow configuration to start builds.</p>
              </div>
              <button
                onClick={() => router.push(`/pipelines/create?project_id=${selectedProjectId}`)}
                disabled={!selectedProjectId}
                className="px-4 py-2 bg-primary text-primary-foreground text-xs font-semibold rounded-lg disabled:opacity-50"
              >
                Create First Pipeline
              </button>
            </div>
          )}

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
