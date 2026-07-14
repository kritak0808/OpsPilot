'use client'

import * as React from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeft, Compass, CheckCircle2, AlertTriangle, Cpu, 
  Layers, Database, Terminal, RefreshCw, RefreshCw as LoopIcon
} from 'lucide-react'

interface Node {
  id: string
  name: string
  cpu_capacity: string
  memory_capacity: string
  status: string
}

interface Namespace {
  id: string
  name: string
  status: string
}

interface Pod {
  name: string
  status: string
  node_name?: string
  restart_count: number
  cpu: string
  memory: string
}

interface Deployment {
  id: string
  name: string
  replicas: number
  available_replicas: number
}

export default function ClusterExplorerPage() {
  const { id } = useParams() as { id: string }
  const { token } = useAuth()
  const router = useRouter()

  const [clusterName, setClusterName] = React.useState('')
  const [nodes, setNodes] = React.useState<Node[]>([])
  const [namespaces, setNamespaces] = React.useState<Namespace[]>([])
  const [pods, setPods] = React.useState<Pod[]>([])
  const [deploys, setDeploys] = React.useState<Deployment[]>([])

  const [activeTab, setActiveTab] = React.useState<'nodes' | 'namespaces' | 'deployments' | 'pods'>('nodes')
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)

  const fetchData = React.useCallback(async () => {
    if (!token || !id) return
    setIsLoading(true)
    try {
      // Get Cluster Name
      const clsRes = await fetch(`/api/v1/clusters/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (clsRes.ok) {
        const clsData = await clsRes.json()
        setClusterName(clsData.name)
      }

      // Nodes
      const nodesRes = await fetch(`/api/v1/clusters/${id}/nodes`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (nodesRes.ok) setNodes(await nodesRes.json())

      // Namespaces
      const nsRes = await fetch(`/api/v1/clusters/${id}/namespaces`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (nsRes.ok) setNamespaces(await nsRes.json())

      // Pods
      const podsRes = await fetch(`/api/v1/clusters/${id}/pods`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (podsRes.ok) setPods(await podsRes.json())

      // Deployments
      const deploysRes = await fetch(`/api/v1/clusters/${id}/deployments`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (deploysRes.ok) setDeploys(await deploysRes.json())
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, id])

  React.useEffect(() => {
    fetchData()
  }, [fetchData])

  const getStatusColor = (val: string) => {
    switch (val.toLowerCase()) {
      case 'running':
      case 'ready':
      case 'active':
        return 'text-success'
      case 'failed':
      case 'crashloopbackoff':
        return 'text-error'
      default:
        return 'text-warning'
    }
  }

  const getStatusBg = (val: string) => {
    switch (val.toLowerCase()) {
      case 'running':
      case 'ready':
      case 'active':
        return 'bg-success/10 border-success/20'
      case 'failed':
      case 'crashloopbackoff':
        return 'bg-error/10 border-error/20'
      default:
        return 'bg-warning/10 border-warning/20'
    }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="clusters">
        <div className="p-8 space-y-8 max-w-5xl mx-auto h-[calc(100vh-4rem)] flex flex-col">
          
          {/* Header */}
          <div className="flex justify-between items-center border-b border-border pb-4 shrink-0">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => router.push('/clusters')}
                className="p-1.5 border border-border bg-card rounded-md hover:bg-muted/30"
              >
                <ArrowLeft className="h-4 w-4" />
              </button>
              <div>
                <h1 className="text-base font-semibold flex items-center gap-2">
                  <Compass className="h-4.5 w-4.5 text-primary animate-pulse" />
                  {clusterName || 'K8s Cluster Workspace'}
                </h1>
                <p className="text-[10px] text-muted-foreground font-mono">Topology ID: {id}</p>
              </div>
            </div>
            <button
              onClick={fetchData}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80 disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              Sync Topology
            </button>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded-md shrink-0">
              {error}
            </div>
          )}

          {/* Premium Sliding Tabs */}
          <div className="border-b border-border flex gap-6 text-sm font-semibold shrink-0 select-none">
            {(['nodes', 'namespaces', 'deployments', 'pods'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 relative text-[10px] font-bold uppercase tracking-widest transition-colors ${
                  activeTab === tab ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {tab}
                {activeTab === tab && (
                  <motion.div 
                    layoutId="activeClusterTab"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
              </button>
            ))}
          </div>

          {/* Dynamic Tab Contents Area */}
          <div className="flex-1 overflow-y-auto min-h-0 pt-2">
            
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map(n => (
                  <div key={n} className="h-20 w-full border border-border bg-card/30 rounded-xl shimmer" />
                ))}
              </div>
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.15 }}
                  className="h-full"
                >
                  
                  {/* Nodes Tab */}
                  {activeTab === 'nodes' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-8">
                      {nodes.map((node) => (
                        <div 
                          key={node.id} 
                          className="p-5 border border-border bg-card rounded-xl space-y-4 hover:shadow-lg transition-shadow relative overflow-hidden group"
                        >
                          <div className="flex justify-between items-center select-none">
                            <div className="flex items-center gap-2">
                              <Cpu className="h-4 w-4 text-primary" />
                              <h3 className="font-bold text-xs text-foreground/90 truncate">{node.name}</h3>
                            </div>
                            <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider flex items-center gap-1 ${getStatusBg(node.status)} ${getStatusColor(node.status)}`}>
                              {node.status}
                            </span>
                          </div>
                          
                          <div className="text-[11px] text-muted-foreground space-y-2">
                            <div className="space-y-1">
                              <div className="flex justify-between">
                                <span>CPU Capacity:</span>
                                <span className="font-semibold text-foreground/90">{node.cpu_capacity} cores</span>
                              </div>
                              <div className="h-1 bg-muted rounded-full overflow-hidden">
                                <div className="h-full bg-primary w-2/5 rounded-full" />
                              </div>
                            </div>
                            <div className="space-y-1">
                              <div className="flex justify-between">
                                <span>Memory Capacity:</span>
                                <span className="font-semibold text-foreground/90">{node.memory_capacity}</span>
                              </div>
                              <div className="h-1 bg-muted rounded-full overflow-hidden">
                                <div className="h-full bg-accent w-3/5 rounded-full" />
                              </div>
                            </div>
                          </div>
                          
                          <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform pointer-events-none" />
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Namespaces Tab */}
                  {activeTab === 'namespaces' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 pb-8 select-none">
                      {namespaces.map((ns) => (
                        <div key={ns.id} className="p-4 border border-border bg-card rounded-xl flex justify-between items-center hover:border-primary/25 transition-colors">
                          <div className="flex items-center gap-2">
                            <Layers className="h-4 w-4 text-primary" />
                            <span className="font-bold text-xs text-foreground/90">{ns.name}</span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider ${getStatusBg(ns.status)} ${getStatusColor(ns.status)}`}>
                            {ns.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Deployments Tab */}
                  {activeTab === 'deployments' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-8">
                      {deploys.map((dep) => {
                        const progress = dep.replicas > 0 ? (dep.available_replicas / dep.replicas) * 100 : 0
                        return (
                          <div key={dep.id} className="p-5 border border-border bg-card rounded-xl space-y-4 hover:shadow-lg transition-shadow relative overflow-hidden group">
                            <div className="flex justify-between items-center select-none">
                              <h3 className="font-bold text-xs text-foreground/90 truncate">{dep.name}</h3>
                              <span className="text-[10px] font-bold text-primary bg-primary/5 border border-primary/15 px-2 py-0.5 rounded">
                                {dep.available_replicas} / {dep.replicas} Replicas
                              </span>
                            </div>
                            <div className="space-y-1">
                              <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                                <motion.div 
                                  initial={{ width: 0 }}
                                  animate={{ width: `${progress}%` }}
                                  transition={{ duration: 0.5, ease: 'easeOut' }}
                                  className="bg-primary h-full rounded-full" 
                                />
                              </div>
                              <span className="text-[9px] text-muted-foreground block">{Math.round(progress)}% load target met</span>
                            </div>
                            <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform pointer-events-none" />
                          </div>
                        )
                      })}
                    </div>
                  )}

                  {/* Pods Tab */}
                  {activeTab === 'pods' && (
                    <div className="grid grid-cols-1 gap-4 pb-8">
                      {pods.map((pod, idx) => {
                        const isFailed = pod.status.toLowerCase().includes('fail') || pod.status.toLowerCase().includes('backoff')
                        return (
                          <div key={idx} className="p-4 border border-border bg-card rounded-xl flex flex-col md:flex-row justify-between gap-4">
                            <div className="space-y-1.5 flex-1 min-w-0">
                              <div className="flex gap-2 items-center">
                                <Database className="h-4 w-4 text-primary shrink-0" />
                                <h4 className="font-semibold text-xs text-foreground/90 truncate">{pod.name}</h4>
                              </div>
                              <p className="text-[9px] text-muted-foreground font-mono">
                                Assigned Node: <span className="text-foreground/70">{pod.node_name || 'Unassigned'}</span>
                              </p>
                              <div className="flex flex-wrap gap-4 text-[10px] text-muted-foreground pt-1 select-none">
                                <p className="flex items-center gap-1"><Cpu className="h-3 w-3 text-muted-foreground/60" /> CPU: <span className="font-bold text-foreground/80">{pod.cpu}</span></p>
                                <p className="flex items-center gap-1"><Terminal className="h-3 w-3 text-muted-foreground/60" /> RAM: <span className="font-bold text-foreground/80">{pod.memory}</span></p>
                              </div>
                            </div>
                            <div className="flex md:flex-col justify-between md:justify-center items-end shrink-0 select-none">
                              <span className={`px-2 py-0.5 rounded text-[8px] font-bold uppercase tracking-wider ${getStatusBg(pod.status)} ${getStatusColor(pod.status)}`}>
                                {pod.status}
                              </span>
                              <p className="text-[9px] text-muted-foreground mt-1">Restarts: {pod.restart_count}</p>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}

                </motion.div>
              </AnimatePresence>
            )}

          </div>

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
