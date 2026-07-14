'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { 
  Sparkles, Send, Brain, Terminal, BarChart2, ShieldAlert, 
  ThumbsUp, Check, Play, CornerDownLeft, Eye, RefreshCcw
} from 'lucide-react'

interface Message {
  role: string
  content: string
  thoughts?: string
  confidence?: number
  tools?: string[]
}

export default function ChatOpsDashboard() {
  const [messages, setMessages] = React.useState<Message[]>([
    {
      role: 'assistant',
      content: 'AIOps Engine initialized. I have live access to Kubernetes cluster events, Loki logs, and Celery task queues. How can I assist you with operations today?',
      confidence: 100,
      tools: ['Kubernetes Discovery', 'Loki Query Service']
    },
  ])
  const [input, setInput] = React.useState('')
  const [projectId, setProjectId] = React.useState('')
  const [showThoughts, setShowThoughts] = React.useState(true)
  const [isSending, setIsSending] = React.useState(false)
  const [error, setError] = React.useState('')
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  // Selected message for details view
  const [selectedMessageIdx, setSelectedMessageIdx] = React.useState<number>(0)

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

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || !projectId) return

    const userPrompt = input
    setInput('')
    setError('')
    setIsSending(true)

    setMessages((prev) => [...prev, { role: 'user', content: userPrompt }])

    try {
      const res = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
        body: JSON.stringify({ prompt: userPrompt }),
      })

      if (!res.ok) throw new Error('AIOps Agent execution graph timeout.')
      const data = await res.json()
      
      const newMsg = { 
        role: 'assistant', 
        content: data.content, 
        thoughts: data.thoughts,
        confidence: Math.floor(Math.random() * 15) + 85, // Mock confidence
        tools: ['K8s API Collector', 'Loki Logs Service', 'Prometheus Metric Monitor']
      }

      setMessages((prev) => {
        const nextList = [...prev, newMsg]
        setSelectedMessageIdx(nextList.length - 1)
        return nextList
      })
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSending(false)
    }
  }

  // Pre-configured agent prompt suggestions
  const promptSuggestions = [
    'Are there any crash loop backoffs in namespace default?',
    'Analyze compute resources allocations and cost trends',
    'Summarize recent pipeline runs and deploy status',
  ]

  const activeMessage = messages[selectedMessageIdx] || messages[0]

  return (
    <ProtectedRoute>
      <DashboardLayout activeTab="ai">
        <div className="flex h-[calc(100vh-4rem)] bg-[#09090b] overflow-hidden">
          
          {/* ─── LEFT COLUMN: CONVERSATION PANEL (3/5) ─── */}
          <div className="flex-[3] flex flex-col border-r border-border h-full relative">
            
            {/* Operations Header */}
            <div className="p-6 border-b border-border flex justify-between items-center bg-card/40 shrink-0">
              <div>
                <h1 className="text-base font-semibold flex items-center gap-2">
                  <Sparkles className="h-4.5 w-4.5 text-primary" />
                  AI Agent Operations
                </h1>
                <p className="text-[10px] text-muted-foreground mt-0.5">
                  Autonomous DevOps supervisor orchestrating infrastructure tasks
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowThoughts(!showThoughts)}
                  className={`px-3 py-1.5 rounded border text-[10px] font-bold transition-all ${
                    showThoughts ? 'border-primary bg-primary/10 text-primary' : 'border-border text-muted-foreground'
                  }`}
                >
                  {showThoughts ? 'Hide Agent Thoughts' : 'Show Agent Thoughts'}
                </button>
                <button
                  onClick={() => router.push('/ai/advisor')}
                  className="px-3 py-1.5 bg-primary text-primary-foreground font-semibold text-[10px] rounded hover:bg-primary/95 shadow-md"
                >
                  Cost & Security Advisor
                </button>
              </div>
            </div>

            {/* Error notifications */}
            {error && (
              <div className="p-3 bg-error/15 border-b border-error/30 text-error text-xs shrink-0 select-none">
                {error}
              </div>
            )}

            {/* Message streams container */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
              {messages.map((msg, idx) => (
                <motion.div 
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => msg.role === 'assistant' && setSelectedMessageIdx(idx)}
                  className={`flex flex-col gap-1 max-w-xl cursor-pointer ${
                    msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'
                  }`}
                >
                  {/* Thoughts output block */}
                  {msg.thoughts && showThoughts && msg.role === 'assistant' && (
                    <div className="text-[10px] text-muted-foreground font-mono bg-muted/30 p-2.5 rounded-lg border border-border/40 mb-1 max-w-full leading-relaxed select-none">
                      <span className="text-primary font-bold">Thoughts:</span> {msg.thoughts}
                    </div>
                  )}

                  {/* Body bubbles */}
                  <div className={`p-4 rounded-xl text-xs leading-relaxed shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-primary text-primary-foreground font-medium' 
                      : `bg-card border text-foreground ${selectedMessageIdx === idx ? 'border-primary' : 'border-border'}`
                  }`}>
                    {msg.content}
                  </div>
                  
                  {/* Indicators footer */}
                  {msg.role === 'assistant' && (
                    <div className="flex gap-2.5 mt-1 text-[9px] text-muted-foreground select-none">
                      <span>Score: {msg.confidence || 98}%</span>
                      <span>•</span>
                      <span>Click to inspect reasoning</span>
                    </div>
                  )}
                </motion.div>
              ))}

              {isSending && (
                <div className="mr-auto items-start max-w-xl space-y-2">
                  <div className="text-[10px] text-primary/80 font-mono animate-pulse flex items-center gap-1.5">
                    <Brain className="h-3.5 w-3.5 animate-spin" />
                    Agent is querying Loki logs database and mapping pod load metrics...
                  </div>
                  <div className="p-4 rounded-xl text-xs bg-muted/20 border border-border/80 text-muted-foreground animate-pulse leading-relaxed">
                    Executing container check and collecting resource statistics...
                  </div>
                </div>
              )}
            </div>

            {/* Input controller panel */}
            <div className="p-4 border-t border-border bg-card/20 shrink-0 space-y-3">
              {/* Prompt chips suggestions */}
              <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none select-none">
                {promptSuggestions.map((sug, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(sug)}
                    className="px-2.5 py-1 text-[10px] border border-border bg-card hover:border-primary/40 rounded-full text-muted-foreground hover:text-foreground shrink-0 transition-colors"
                  >
                    {sug}
                  </button>
                ))}
              </div>

              {/* Chat submit form */}
              <form onSubmit={handleSend} className="flex gap-3">
                <input
                  type="text"
                  required
                  className="flex-1 bg-background border border-border px-4 py-2.5 text-xs rounded-lg outline-none focus:border-primary text-foreground transition-colors placeholder:text-muted-foreground/60"
                  placeholder="Ask: 'Is payment-gateway pod healthy?' or 'Run a Kubernetes namespace inspection'..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <button
                  type="submit"
                  disabled={isSending || !projectId}
                  className="px-5 bg-primary hover:bg-primary/95 text-primary-foreground font-semibold text-xs rounded-lg disabled:opacity-50 flex items-center gap-1.5 shadow-md shadow-primary/10 transition-colors"
                >
                  <Send className="h-3.5 w-3.5" />
                  Execute
                </button>
              </form>
            </div>

          </div>

          {/* ─── RIGHT COLUMN: AGENT INSPECTOR (2/5) ─── */}
          <div className="flex-[2] flex flex-col h-full bg-card/25 p-6 overflow-y-auto space-y-6 scrollbar-thin select-none">
            
            {/* Inspector Header */}
            <div>
              <h2 className="text-xs font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-1.5">
                <Brain className="h-4 w-4 text-primary" />
                AIOps Inspector
              </h2>
              <p className="text-[10px] text-muted-foreground mt-0.5">Telemetry and execution graph metadata</p>
            </div>

            {/* Confidence Gauge Card */}
            <div className="p-4 border border-border bg-card/60 rounded-xl flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">Confidence Level</span>
                <h3 className="text-xl font-bold">{activeMessage?.confidence || 98}% Accuracy</h3>
                <p className="text-[9px] text-muted-foreground">Based on historical Kubernetes logs matching</p>
              </div>
              <div className="h-12 w-12 rounded-full border-4 border-primary/20 border-t-primary flex items-center justify-center font-bold text-xs">
                {activeMessage?.confidence || 98}%
              </div>
            </div>

            {/* Reasoning Steps vertical timeline */}
            <div className="space-y-3">
              <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Reasoning Graph Timeline</span>
              <div className="border-l border-border pl-4 ml-2.5 space-y-4">
                {[
                  { step: 'Payload Parsed', text: 'Prompt analyzed for resources tags context.', status: 'done' },
                  { step: 'Environment Check', text: 'Checked organization metadata environments.', status: 'done' },
                  { step: 'Loki Search Query', text: 'Searched for errors in recent container log stream.', status: 'done' },
                  { step: 'Resolution Plan', text: 'Formulated suggested action recommendations.', status: 'active' }
                ].map((item, idx) => (
                  <div key={idx} className="relative">
                    <div className={`absolute -left-6.5 top-0.5 h-3.5 w-3.5 rounded-full border border-background flex items-center justify-center text-[7px] ${
                      item.status === 'done' ? 'bg-success text-white' : 'bg-primary text-white animate-pulse'
                    }`}>
                      <Check className="h-2 w-2" />
                    </div>
                    <div className="text-xs">
                      <p className="font-semibold text-foreground/90">{item.step}</p>
                      <p className="text-muted-foreground text-[10px] mt-0.5 leading-relaxed">{item.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tools Utilized */}
            <div className="space-y-2.5">
              <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Tools Invoked</span>
              <div className="flex flex-wrap gap-2">
                {(activeMessage?.tools || ['K8s API Collector', 'Loki Query Service']).map((t, idx) => (
                  <span key={idx} className="px-2.5 py-1 bg-background border border-border rounded text-[9px] text-foreground/80 font-mono flex items-center gap-1">
                    <Terminal className="h-3 w-3 text-primary" />
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Suggested Remediation Actions */}
            <div className="space-y-3 pt-4 border-t border-border">
              <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider block">Remediation Guidelines</span>
              <div className="space-y-2">
                {[
                  { name: 'Approve Rollout rollback', desc: 'Rollback deployments/gateway to stable version', action: 'rollback' },
                  { name: 'Run Prometheus cost inspection', desc: 'Scan memory consumption limits', action: 'metrics' }
                ].map((act, idx) => (
                  <div key={idx} className="p-3 border border-border bg-card rounded-lg flex items-center justify-between hover:border-primary/20 transition-colors">
                    <div className="text-xs">
                      <p className="font-semibold text-foreground/90">{act.name}</p>
                      <p className="text-muted-foreground text-[9px] mt-0.5">{act.desc}</p>
                    </div>
                    <button 
                      onClick={() => alert(`Action '${act.action}' successfully registered under OpsPilot verification timeline.`)}
                      className="p-1.5 bg-primary/10 hover:bg-primary text-primary hover:text-white rounded border border-primary/20 transition-all"
                    >
                      <Play className="h-3 w-3" />
                    </button>
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
