'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { 
  Sparkles, ShieldAlert, Cpu, Award, DollarSign, 
  ArrowUpRight, Play, Eye, Activity, RefreshCw
} from 'lucide-react'

interface Recommendation {
  category: string
  impact: string
  confidence: number
  description: string
  actions: string[]
}

export default function AIAdvisorPage() {
  const [recs, setRecs] = React.useState<Recommendation[]>([])
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  const { token } = useAuth()
  const router = useRouter()

  const fetchRecommendations = React.useCallback(async () => {
    if (!token) return
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/ai/recommend', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to load recommendations.')
      const data = await res.json()
      setRecs(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token])

  React.useEffect(() => {
    fetchRecommendations()
  }, [fetchRecommendations])

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  }

  const cardVariants = {
    hidden: { opacity: 0, y: 15 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="ai">
        <div className="p-8 space-y-8 max-w-5xl mx-auto">
          
          {/* Header Panel */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary">
                AI Advisor Proactive Reviews
              </h1>
              <p className="text-xs text-muted-foreground mt-1">
                Security and resource allocation recommendations compiled by operations agents
              </p>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => fetchRecommendations()}
                disabled={isLoading}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-border bg-card hover:bg-muted/30 text-xs font-semibold rounded-md text-foreground/80 disabled:opacity-50"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                Scan System
              </button>
              <button
                onClick={() => router.push('/ai')}
                className="flex items-center gap-1.5 px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded-md shadow-md shadow-primary/10"
              >
                Operations Workspace
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded-md">
              {error}
            </div>
          )}

          {/* Recommendations Content */}
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(n => (
                <div key={n} className="h-32 w-full border border-border bg-card/40 rounded-xl shimmer" />
              ))}
            </div>
          ) : recs.length > 0 ? (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="show"
              className="space-y-6"
            >
              {recs.map((rec, idx) => {
                const isHighImpact = rec.impact.toLowerCase() === 'high'
                const isSecurity = rec.category.toLowerCase().includes('security')
                
                return (
                  <motion.div
                    key={idx}
                    variants={cardVariants}
                    className="p-6 border border-border bg-card rounded-xl hover:border-primary/25 hover:shadow-xl transition-all relative overflow-hidden group flex flex-col md:flex-row justify-between gap-6"
                  >
                    {/* Details Column */}
                    <div className="space-y-4 flex-1">
                      
                      {/* Tags row */}
                      <div className="flex flex-wrap gap-2.5 items-center select-none">
                        <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${
                          isSecurity ? 'bg-error/10 text-error' : 'bg-primary/10 text-primary'
                        }`}>
                          {rec.category}
                        </span>
                        <span className={`px-2.5 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider ${
                          isHighImpact ? 'bg-error/10 text-error' : 'bg-warning/10 text-warning'
                        }`}>
                          Impact: {rec.impact}
                        </span>
                        <span className="text-[10px] text-muted-foreground">• Confidence: {rec.confidence}%</span>
                      </div>

                      {/* Description */}
                      <div className="space-y-2">
                        <h3 className="text-sm font-semibold text-foreground/90">
                          {isSecurity ? 'Security Vulnerability Remediation' : 'Operational Cost Efficiency Review'}
                        </h3>
                        <p className="text-xs text-muted-foreground leading-relaxed">
                          {rec.description}
                        </p>
                      </div>

                      {/* Suggested actions list */}
                      <div className="space-y-2 pt-2">
                        <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest block">Proposed Mitigation Actions</span>
                        <div className="flex flex-wrap gap-2">
                          {rec.actions.map((act, aIdx) => (
                            <span key={aIdx} className="px-2.5 py-1 bg-background border border-border rounded text-[10px] text-foreground/80 font-medium">
                              {act}
                            </span>
                          ))}
                        </div>
                      </div>

                    </div>

                    {/* Gauges & Actions column */}
                    <div className="flex flex-col justify-between items-end shrink-0 w-full md:w-36 gap-4">
                      
                      {/* Radial Progress meter */}
                      <div className="flex items-center gap-3 bg-muted/20 p-2.5 rounded-lg border border-border/40 select-none">
                        <div className="text-right">
                          <p className="text-[9px] font-bold text-muted-foreground uppercase">Confidence</p>
                          <p className="text-xs font-bold text-foreground/90">{rec.confidence}%</p>
                        </div>
                        <div className="h-9 w-9 rounded-full border-2 border-primary/20 border-t-primary flex items-center justify-center font-bold text-[10px]">
                          {rec.confidence}
                        </div>
                      </div>

                      {/* Execute CTA */}
                      <button
                        onClick={() => alert(`Initiating agent orchestration sequence: '${rec.actions[0] || 'Apply recommendation'}'`)}
                        className="w-full py-2 bg-primary hover:bg-primary/95 text-primary-foreground text-xs font-bold rounded-lg flex items-center justify-center gap-1 shadow-md shadow-primary/10 hover:shadow-primary/20 transition-all"
                      >
                        <Play className="h-3 w-3" />
                        Execute Plan
                      </button>
                    </div>

                    <div className="absolute right-0 bottom-0 h-16 w-16 bg-gradient-to-br from-transparent to-primary/5 rounded-tl-full translate-x-4 translate-y-4 group-hover:scale-110 transition-transform pointer-events-none" />
                  </motion.div>
                )
              })}
            </motion.div>
          ) : (
            <div className="border border-dashed border-border p-12 text-center rounded-xl max-w-md mx-auto space-y-4">
              <Award className="h-10 w-10 text-primary mx-auto" />
              <div className="space-y-1">
                <p className="text-sm font-semibold">No new recommendations</p>
                <p className="text-xs text-muted-foreground">The platform node and Kubernetes clusters are fully optimized.</p>
              </div>
              <button
                onClick={() => fetchRecommendations()}
                className="px-4 py-2 bg-primary text-primary-foreground text-xs font-semibold rounded-lg"
              >
                Re-Scan Infrastructure
              </button>
            </div>
          )}

        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
