'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { 
  Terminal, Shield, Cpu, Activity, AlertTriangle, 
  ArrowUpRight, Users, Play, Clock, Cloud, DollarSign, Sparkles, FolderKanban, Settings
} from 'lucide-react'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { useAuth } from '@/providers/auth-provider'
import { 
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts'

export default function HomePage() {
  const router = useRouter()
  const { token, activeOrgId, user } = useAuth()
  
  // Data states
  const [stats, setStats] = React.useState({
    projectsCount: 0,
    clustersCount: 0,
    pipelinesCount: 0,
    incidentsCount: 0
  })
  const [incidents, setIncidents] = React.useState<any[]>([])
  const [pipelines, setPipelines] = React.useState<any[]>([])
  const [isLoading, setIsLoading] = React.useState(true)

  // Recharts mock resources data
  const resourceData = [
    { name: '10:00', cpu: 28, mem: 45 },
    { name: '11:00', cpu: 32, mem: 46 },
    { name: '12:00', cpu: 45, mem: 55 },
    { name: '13:00', cpu: 38, mem: 52 },
    { name: '14:00', cpu: 58, mem: 62 },
    { name: '15:00', cpu: 42, mem: 59 },
    { name: '16:00', cpu: 31, mem: 58 },
  ]

  const costData = [
    { category: 'Compute', amount: 1450, color: '#7C3AED' },
    { category: 'Storage', amount: 820, color: '#3B82F6' },
    { category: 'Network', amount: 620, color: '#22C55E' },
    { category: 'DBs', amount: 480, color: '#F59E0B' },
  ]

  React.useEffect(() => {
    if (!token || !activeOrgId) return
    
    // Fetch overview details in parallel
    Promise.all([
      fetch('/api/v1/projects', { headers: { Authorization: `Bearer ${token}`, 'X-Org-ID': activeOrgId } }).then(r => r.json()),
      fetch('/api/v1/clusters', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch('/api/v1/incidents', { headers: { Authorization: `Bearer ${token}` } }).then(r => r.ok ? r.json() : []),
    ]).then(([projects, clusters, activeIncidents]) => {
      setStats({
        projectsCount: projects.length || 0,
        clustersCount: clusters.length || 0,
        pipelinesCount: 3, // Default mock count
        incidentsCount: activeIncidents.length || 0
      })
      setIncidents(activeIncidents.slice(0, 3))
      setIsLoading(false)
    }).catch(() => {
      setIsLoading(false)
    })
  }, [token, activeOrgId])

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="dashboard">
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
          
          {/* Welcome Dashboard Panel */}
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6"
          >
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary">
                System Command Center
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Active operations overview for {user?.full_name || 'Operator'} • Org context synchronized.
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => router.push('/ai')}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded-md border border-primary-foreground/10"
              >
                <Sparkles className="h-3.5 w-3.5" />
                Launch AIOps Agent
              </button>
              <button
                onClick={() => router.push('/clusters/import')}
                className="flex items-center gap-1.5 px-4 py-2 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80"
              >
                <Cloud className="h-3.5 w-3.5" />
                Connect Cluster
              </button>
            </div>
          </motion.div>

          {/* Quick Metrics Grid */}
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {[
              { title: 'Cluster Nodes', val: stats.clustersCount, icon: Cloud, desc: 'Active K8s topologies', color: 'text-primary' },
              { title: 'Project Scopes', val: stats.projectsCount, icon: FolderKanban, desc: 'Registered workspaces', color: 'text-accent' },
              { title: 'Active Outages', val: stats.incidentsCount, icon: AlertTriangle, desc: 'Unresolved incidents', color: stats.incidentsCount > 0 ? 'text-error' : 'text-success' },
              { title: 'Runner Load', val: '100% Health', icon: Shield, desc: 'Gateway online & secured', color: 'text-success' }
            ].map((metric, idx) => (
              <motion.div 
                key={idx}
                variants={itemVariants}
                className="p-5 border border-border bg-card rounded-md space-y-2 hover:shadow-lg hover:border-primary/20 transition-all flex flex-col justify-between h-32 relative overflow-hidden group"
              >
                <div className="flex justify-between items-center text-muted-foreground z-10">
                  <span className="text-[10px] font-bold uppercase tracking-wider">{metric.title}</span>
                  <metric.icon className={`h-4.5 w-4.5 ${metric.color}`} />
                </div>
                <div className="z-10">
                  <p className="text-2xl font-bold tracking-tight">{metric.val}</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5">{metric.desc}</p>
                </div>
                <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform" />
              </motion.div>
            ))}
          </motion.div>

          {/* Visual Analytics Graphs */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Resource utilization area chart */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="lg:col-span-2 p-6 border border-border bg-card rounded-md space-y-4 flex flex-col"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-sm font-semibold">Cluster Resource Utilization</h3>
                  <p className="text-[10px] text-muted-foreground">Historical memory and processor allocations</p>
                </div>
                <div className="flex gap-3 text-[10px] font-medium">
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#7C3AED]" /> CPU</span>
                  <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-[#3B82F6]" /> Memory</span>
                </div>
              </div>
              <div className="h-64 flex-1">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={resourceData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#7C3AED" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorMem" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ background: '#111113', borderColor: '#232326', fontSize: 11, borderRadius: 6 }} />
                    <Area type="monotone" dataKey="cpu" stroke="#7C3AED" strokeWidth={1.5} fillOpacity={1} fill="url(#colorCpu)" />
                    <Area type="monotone" dataKey="mem" stroke="#3B82F6" strokeWidth={1.5} fillOpacity={1} fill="url(#colorMem)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* Cloud resources cost breakdown bar chart */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="p-6 border border-border bg-card rounded-md space-y-4 flex flex-col justify-between"
            >
              <div>
                <h3 className="text-sm font-semibold">Cloud Spend Allocation</h3>
                <p className="text-[10px] text-muted-foreground">Monthly direct compute resource costs</p>
              </div>
              <div className="h-44">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={costData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="category" stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#71717a" fontSize={10} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: 'rgba(255,255,255,0.02)' }} contentStyle={{ background: '#111113', borderColor: '#232326', fontSize: 11 }} />
                    <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
                      {costData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="pt-2 border-t border-border flex justify-between items-center text-xs">
                <span className="text-muted-foreground">Total Budget Used:</span>
                <span className="font-bold flex items-center"><DollarSign className="h-3.5 w-3.5" />3,370</span>
              </div>
            </motion.div>

          </div>

          {/* Lower Grid: Incidents and Recent Activity */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Active alert incidents panel */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              className="p-6 border border-border bg-card rounded-md space-y-4"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-sm font-semibold">Active Operational Alarms</h3>
                  <p className="text-[10px] text-muted-foreground">Triggered alarms requiring operator mitigation</p>
                </div>
                <span 
                  onClick={() => router.push('/observability')}
                  className="text-[10px] text-primary hover:underline cursor-pointer font-bold flex items-center"
                >
                  Mitigation Panel <ArrowUpRight className="h-3.5 w-3.5" />
                </span>
              </div>

              <div className="space-y-3">
                {incidents.map((incident, idx) => (
                  <div key={incident.id || idx} className="p-3 border border-border bg-background rounded flex items-center justify-between hover:border-error/20 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-2 w-2 rounded-full bg-error animate-pulse" />
                      <div className="text-xs">
                        <p className="font-semibold text-foreground/90">{incident.title || 'Outage Incident'}</p>
                        <p className="text-muted-foreground text-[10px] mt-0.5">Severity: {incident.severity} • Status: {incident.status}</p>
                      </div>
                    </div>
                    <span className="text-[10px] text-muted-foreground">{incident.created_at ? new Date(incident.created_at).toLocaleTimeString() : 'Recent'}</span>
                  </div>
                ))}
                {incidents.length === 0 && (
                  <div className="text-center py-8 text-xs text-muted-foreground border border-dashed border-border rounded">
                    All components reporting healthy. No alarms active.
                  </div>
                )}
              </div>
            </motion.div>

            {/* Quick Actions & Gateway Terminal panel */}
            <motion.div 
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="p-6 border border-border bg-card rounded-md space-y-4 flex flex-col justify-between"
            >
              <div>
                <h3 className="text-sm font-semibold">NOC Quick Gateway</h3>
                <p className="text-[10px] text-muted-foreground">Access operations dashboards and logs</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'CI/CD Pipelines', url: '/pipelines', desc: 'Trigger build cycles', icon: Play },
                  { name: 'Kubernetes Map', url: '/clusters', desc: 'Explore namespaces', icon: Cloud },
                  { name: 'Metrics Analytics', url: '/observability', desc: 'Review Loki traces', icon: Activity },
                  { name: 'System Settings', url: '/settings', desc: 'Manage credentials', icon: Settings }
                ].map((act, idx) => (
                  <div 
                    key={idx}
                    onClick={() => router.push(act.url)}
                    className="p-4 border border-border bg-background hover:bg-muted/40 hover:border-primary/20 rounded cursor-pointer transition-all space-y-2 flex flex-col justify-between"
                  >
                    <act.icon className="h-4.5 w-4.5 text-primary" />
                    <div>
                      <h4 className="text-xs font-semibold">{act.name}</h4>
                      <p className="text-[9px] text-muted-foreground mt-0.5">{act.desc}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-3 border border-border bg-background rounded-md flex items-center justify-between text-xs text-muted-foreground select-none">
                <div className="flex items-center gap-2">
                  <Terminal className="h-3.5 w-3.5 text-primary" />
                  <span>Telemetry Listener: Active</span>
                </div>
                <span className="h-2 w-2 rounded-full bg-success" />
              </div>
            </motion.div>

          </div>

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
