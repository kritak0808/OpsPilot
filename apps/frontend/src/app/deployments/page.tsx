'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, RefreshCw, Layers, CheckCircle2, ChevronRight, 
  Minus, Plus, ShieldAlert, Cpu, Database
} from 'lucide-react'

interface Deployment {
  id: string
  name: string
  replicas: number
  available_replicas: number
  cluster_name: string
}

export default function DeploymentsPage() {
  const [deployments, setDeployments] = React.useState<Deployment[]>([])
  const [scaleInput, setScaleInput] = React.useState<Record<string, number>>({})
  const [scaleMsg, setScaleMsg] = React.useState<Record<string, string>>({})
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchDeployments = React.useCallback(async () => {
    if (!token || !activeOrgId) return
    setIsLoading(true)
    try {
      // Query projects then clusters to list active deployments
      const clustersRes = await fetch('/api/v1/clusters', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!clustersRes.ok) throw new Error('Failed to query clusters.')
      const clusters = await clustersRes.json()
      
      let allDeploys: Deployment[] = []
      for (const cluster of clusters) {
        const depRes = await fetch(`/api/v1/clusters/${cluster.id}/deployments`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (depRes.ok) {
          const deps = await depRes.json()
          allDeploys = allDeploys.concat(deps.map((d: any) => ({
            ...d,
            cluster_name: cluster.name,
          })))
        }
      }
      setDeployments(allDeploys)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, activeOrgId])

  React.useEffect(() => {
    fetchDeployments()
  }, [fetchDeployments])

  const handleScale = async (id: string) => {
    const val = scaleInput[id]
    if (val === undefined) return
    
    setScaleMsg((prev) => ({ ...prev, [id]: 'Scaling...' }))
    try {
      const res = await fetch(`/api/v1/clusters/deployments/${id}/scale`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ replicas: val }),
      })
      if (!res.ok) throw new Error('Scale failed.')
      setScaleMsg((prev) => ({ ...prev, [id]: 'Config updated successfully.' }))
      
      // Update local state
      setDeployments((prev) =>
        prev.map((d) => (d.id === id ? { ...d, replicas: val } : d))
      )
    } catch (err: any) {
      setScaleMsg((prev) => ({ ...prev, [id]: `Error: ${err.message}` }))
    }
  }

  const handleRollback = async (id: string) => {
    if (!confirm('Are you sure you want to trigger a rollback to the previous version?')) return
    try {
      const res = await fetch(`/api/v1/clusters/deployments/${id}/rollback`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Rollback failed.')
      alert('Rollback successfully triggered.')
    } catch (err: any) {
      alert(`Rollback failed: ${err.message}`)
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="deployments">
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary">
                Active Deployments
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Manage scaling properties and trigger version rollbacks across cluster environments
              </p>
            </div>
            
            <button
              onClick={() => fetchDeployments()}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80 disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              Sync Statuses
            </button>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded-md">
              {error}
            </div>
          )}

          {/* Active Deployments List */}
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2].map(n => (
                <div key={n} className="h-32 w-full border border-border bg-card/40 rounded-xl shimmer" />
              ))}
            </div>
          ) : deployments.length > 0 ? (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="space-y-6"
            >
              {deployments.map((dep) => {
                const currentScale = scaleInput[dep.id] !== undefined ? scaleInput[dep.id] : dep.replicas
                const progressPercentage = dep.replicas > 0 ? (dep.available_replicas / dep.replicas) * 100 : 0
                const isHealthy = dep.available_replicas === dep.replicas && dep.replicas > 0
                
                return (
                  <motion.div
                    key={dep.id}
                    variants={itemVariants}
                    className="p-6 border border-border bg-card rounded-xl hover:border-primary/20 hover:shadow-lg transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden group"
                  >
                    
                    {/* Info */}
                    <div className="space-y-3 flex-1 min-w-0">
                      <div className="flex gap-2.5 items-center select-none">
                        <div className="h-2 w-2 rounded-full bg-success" />
                        <h2 className="text-sm font-bold text-foreground/90 truncate">{dep.name}</h2>
                        <span className="text-[9px] bg-background border border-border/80 px-2 py-0.5 rounded font-mono text-muted-foreground">
                          {dep.cluster_name}
                        </span>
                      </div>
                      
                      {/* Replica status text */}
                      <p className="text-[11px] text-muted-foreground">
                        Replicas: <span className="font-semibold text-foreground/90">{dep.available_replicas} online</span> of {dep.replicas} requested
                      </p>

                      {/* Replica visual progress bar */}
                      <div className="space-y-1">
                        <div className="h-1.5 w-full max-w-md bg-muted rounded-full overflow-hidden border border-border/20">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${progressPercentage}%` }}
                            transition={{ duration: 0.5, ease: 'easeOut' }}
                            className={`h-full rounded-full ${
                              isHealthy ? 'bg-success' : 'bg-primary'
                            }`}
                          />
                        </div>
                        <span className="text-[9px] text-muted-foreground">{Math.round(progressPercentage)}% capacity met</span>
                      </div>

                      {scaleMsg[dep.id] && (
                        <p className="text-[10px] text-primary animate-pulse">{scaleMsg[dep.id]}</p>
                      )}
                    </div>

                    {/* Scale controls & Rollback CTA */}
                    <div className="flex flex-wrap md:flex-nowrap items-center gap-4 shrink-0 w-full md:w-auto">
                      
                      {/* Scale interface */}
                      <div className="flex items-center gap-2 border border-border bg-background p-1.5 rounded-lg">
                        <button
                          onClick={() => setScaleInput(prev => ({ ...prev, [dep.id]: Math.max(0, currentScale - 1) }))}
                          className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground transition-colors"
                        >
                          <Minus className="h-3.5 w-3.5" />
                        </button>
                        <span className="w-8 text-center text-xs font-bold font-mono">{currentScale}</span>
                        <button
                          onClick={() => setScaleInput(prev => ({ ...prev, [dep.id]: Math.min(100, currentScale + 1) }))}
                          className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground transition-colors"
                        >
                          <Plus className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => handleScale(dep.id)}
                          className="ml-2 px-3 py-1 bg-primary text-primary-foreground text-[10px] font-bold rounded-md hover:bg-primary/95 transition-colors"
                        >
                          Apply
                        </button>
                      </div>

                      {/* Rollback Trigger */}
                      <button
                        onClick={() => handleRollback(dep.id)}
                        className="px-4 py-2 border border-error/20 bg-error/5 hover:bg-error hover:text-white text-error text-[10px] font-bold rounded-lg transition-all"
                      >
                        Rollback
                      </button>

                    </div>

                    <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform pointer-events-none" />
                  </motion.div>
                )
              })}
            </motion.div>
          ) : (
            <div className="border border-dashed border-border p-12 text-center rounded-xl max-w-md mx-auto space-y-4">
              <ShieldAlert className="h-10 w-10 text-primary mx-auto" />
              <div className="space-y-1">
                <p className="text-sm font-semibold">No active deployments</p>
                <p className="text-xs text-muted-foreground">Import and link a target Kubernetes cluster mapping to view active workloads.</p>
              </div>
              <button
                onClick={() => router.push('/clusters/import')}
                className="px-4 py-2 bg-primary text-primary-foreground text-xs font-semibold rounded-lg"
              >
                Link Target Cluster
              </button>
            </div>
          )}

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
