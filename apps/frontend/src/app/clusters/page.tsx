'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { motion } from 'framer-motion'
import { 
  Cloud, CheckCircle2, AlertTriangle, ArrowRight, 
  Plus, RefreshCw, Layers, Compass
} from 'lucide-react'

interface Cluster {
  id: string
  name: string
  slug: string
  is_healthy: boolean
}

export default function ClustersPage() {
  const [clusters, setClusters] = React.useState<Cluster[]>([])
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  const { token } = useAuth()
  const router = useRouter()

  const fetchClusters = React.useCallback(async () => {
    if (!token) return
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/clusters', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load clusters.')
      const data = await res.json()
      setClusters(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token])

  React.useEffect(() => {
    fetchClusters()
  }, [fetchClusters])

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
      <DashboardLayout activeTab="clusters">
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
          
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary">
                Kubernetes Explorer
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Monitor live cluster topologies, resource capacities, and pod health status
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => fetchClusters()}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80 disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                Sync Statuses
              </button>
              <button
                onClick={() => router.push('/clusters/import')}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded-md shadow-md shadow-primary/10"
              >
                <Plus className="h-3.5 w-3.5" />
                Import Cluster
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded-md">
              {error}
            </div>
          )}

          {/* Clusters Grid */}
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2].map(n => (
                <div key={n} className="h-36 w-full border border-border bg-card/40 rounded-xl shimmer" />
              ))}
            </div>
          ) : clusters.length > 0 ? (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {clusters.map((cluster) => (
                <motion.div
                  key={cluster.id}
                  variants={itemVariants}
                  onClick={() => router.push(`/clusters/${cluster.id}`)}
                  className="p-6 border border-border bg-card rounded-xl hover:border-primary/25 hover:shadow-lg transition-all flex flex-col justify-between h-40 cursor-pointer relative overflow-hidden group"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-2.5">
                        <Compass className="h-5 w-5 text-primary" />
                        <h2 className="text-sm font-semibold text-foreground/90 truncate">{cluster.name}</h2>
                      </div>
                      
                      <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider flex items-center gap-1 ${
                        cluster.is_healthy ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                      }`}>
                        {cluster.is_healthy ? (
                          <>
                            <CheckCircle2 className="h-2.5 w-2.5" />
                            Healthy
                          </>
                        ) : (
                          <>
                            <AlertTriangle className="h-2.5 w-2.5" />
                            Degraded
                          </>
                        )}
                      </span>
                    </div>
                    
                    <p className="text-[10px] text-muted-foreground font-mono">
                      slug: {cluster.slug}
                    </p>
                  </div>

                  <div className="flex justify-between items-center text-xs pt-4 border-t border-border/50">
                    <span className="text-muted-foreground">Nodes: 3 Online</span>
                    <span className="text-primary group-hover:translate-x-1 transition-transform flex items-center gap-1 font-bold">
                      Explore Cluster <ArrowRight className="h-3.5 w-3.5" />
                    </span>
                  </div>

                  <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform pointer-events-none" />
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <div className="border border-dashed border-border p-12 text-center rounded-xl max-w-md mx-auto space-y-4">
              <Cloud className="h-10 w-10 text-primary mx-auto" />
              <div className="space-y-1">
                <p className="text-sm font-semibold">No Kubernetes clusters linked</p>
                <p className="text-xs text-muted-foreground">Import your kubeconfig to start monitoring pods capacities and namespaces details.</p>
              </div>
              <button
                onClick={() => router.push('/clusters/import')}
                className="px-4 py-2 bg-primary text-primary-foreground text-xs font-semibold rounded-lg"
              >
                Import Kubeconfig
              </button>
            </div>
          )}

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
