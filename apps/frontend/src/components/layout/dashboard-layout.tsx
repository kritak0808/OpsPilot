'use client'

import * as React from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  LayoutDashboard, FolderKanban, GitBranch, PlayCircle, 
  Send, Compass, HelpCircle, Settings, Bell, Search, 
  ChevronLeft, ChevronRight, Moon, Sun, Monitor, LogOut,
  Sparkles, CheckCircle2, AlertTriangle, Info, Terminal, Maximize2
} from 'lucide-react'
import { useAuth } from '@/providers/auth-provider'

interface DashboardLayoutProps {
  children: React.ReactNode
  activeTab?: string
}

export function DashboardLayout({ children, activeTab }: DashboardLayoutProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, logout, activeOrgId, token } = useAuth()
  
  const [isCollapsed, setIsCollapsed] = React.useState(false)
  const [isSearchOpen, setIsSearchOpen] = React.useState(false)
  const [isNotificationOpen, setIsNotificationOpen] = React.useState(false)
  const [isAiOpen, setIsAiOpen] = React.useState(false)
  const [currentTheme, setCurrentTheme] = React.useState('dark')
  
  // AI assistant states
  const [aiInput, setAiInput] = React.useState('')
  const [aiMessages, setAiMessages] = React.useState<any[]>([
    { role: 'assistant', content: 'Hi! I am your OpsPilot AI assistant. I can inspect pods, trigger pipeline runs, or analyze costs. What would you like to do?' }
  ])
  const [isAiSending, setIsAiSending] = React.useState(false)

  // Notifications mock data
  const [notifications] = React.useState([
    { id: '1', type: 'success', text: 'Deployment rollout successful: gateway-v2', time: '5m ago' },
    { id: '2', type: 'error', text: 'Pod crash detected: payments-service-pod-01', time: '12m ago' },
    { id: '3', type: 'info', text: 'Pipeline run queued: billing-api-ci', time: '1h ago' }
  ])

  // Search results state
  const [searchQuery, setSearchQuery] = React.useState('')
  const searchItems = [
    { title: 'System Dashboard', url: '/' },
    { title: 'View Projects', url: '/projects' },
    { title: 'Link Git Repositories', url: '/repositories' },
    { title: 'CI/CD Pipelines', url: '/pipelines' },
    { title: 'Canary Deployments', url: '/deployments' },
    { title: 'Kubernetes Clusters Explorer', url: '/clusters' },
    { title: 'Observability telemetry', url: '/observability' },
    { title: 'Settings and variables', url: '/settings' },
    { title: 'AI Operations Center', url: '/ai' }
  ]
  const filteredSearch = searchItems.filter(item => 
    item.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  React.useEffect(() => {
    // Sync theme on mount
    const savedTheme = localStorage.getItem('opspilot_theme') || 'dark'
    applyTheme(savedTheme)
  }, [])

  const applyTheme = (themeName: string) => {
    setCurrentTheme(themeName)
    const root = window.document.documentElement
    root.classList.remove('dark', 'light')
    root.removeAttribute('data-theme')
    
    if (themeName === 'dark') {
      root.classList.add('dark')
    } else if (themeName === 'oled') {
      root.classList.add('dark')
      root.setAttribute('data-theme', 'oled')
    } else if (themeName === 'enterprise-blue') {
      root.classList.add('dark')
      root.setAttribute('data-theme', 'enterprise-blue')
    } else {
      root.classList.add('light')
    }
    localStorage.setItem('opspilot_theme', themeName)
  }

  // Keyboard shortcut for Command Palette (Ctrl+K or Cmd+K)
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setIsSearchOpen(prev => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const handleSendAi = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!aiInput.trim()) return

    const userPrompt = aiInput
    setAiInput('')
    setAiMessages(prev => [...prev, { role: 'user', content: userPrompt }])
    setIsAiSending(true)

    try {
      // Get a project ID first to act as scope if needed
      let projId = ''
      const projRes = await fetch('/api/v1/projects', {
        headers: { Authorization: `Bearer ${token}`, 'X-Org-ID': activeOrgId || '' },
      })
      if (projRes.ok) {
        const data = await projRes.json()
        if (data.length > 0) projId = data[0].id
      }

      const res = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projId,
        },
        body: JSON.stringify({ prompt: userPrompt }),
      })

      if (!res.ok) throw new Error('AI Orchestrator connection failed')
      const data = await res.json()
      setAiMessages(prev => [...prev, { role: 'assistant', content: data.content }])
    } catch (err: any) {
      setAiMessages(prev => [...prev, { role: 'assistant', content: `Error: ${err.message}. Please verify the AIOps engine status.` }])
    } finally {
      setIsAiSending(false)
    }
  }

  const menuItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Projects', icon: FolderKanban, path: '/projects' },
    { name: 'Codebases', icon: GitBranch, path: '/repositories' },
    { name: 'Pipelines', icon: PlayCircle, path: '/pipelines' },
    { name: 'Deployments', icon: Send, path: '/deployments' },
    { name: 'Clusters', icon: Compass, path: '/clusters' },
    { name: 'Observability', icon: HelpCircle, path: '/observability' },
    { name: 'AI Ops', icon: Sparkles, path: '/ai' },
    { name: 'Settings', icon: Settings, path: '/settings' },
  ]

  // Breadcrumbs parsing
  const pathParts = pathname.split('/').filter(p => p)
  const breadcrumbs = pathParts.map((part, index) => {
    const url = '/' + pathParts.slice(0, index + 1).join('/')
    const isLast = index === pathParts.length - 1
    return { name: part.charAt(0).toUpperCase() + part.slice(1), url, isLast }
  })

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground gradient-mesh font-sans">
      
      {/* ─── SIDEBAR NAVIGATION ─── */}
      <motion.aside 
        animate={{ width: isCollapsed ? 72 : 260 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className="flex flex-col h-full border-r border-border bg-card shrink-0 select-none overflow-hidden"
      >
        {/* Brand Header */}
        <div className="flex items-center h-16 px-4 border-b border-border gap-3 shrink-0">
          <div className="flex items-center justify-center h-9 w-9 rounded bg-primary text-primary-foreground font-bold shrink-0">
            OP
          </div>
          {!isCollapsed && (
            <motion.span 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-bold text-base tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground via-foreground/90 to-primary"
            >
              OpsPilot AI
            </motion.span>
          )}
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto overflow-x-hidden scrollbar-none">
          {!isCollapsed && (
            <span className="block px-3 py-2 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
              Core Operations
            </span>
          )}
          {menuItems.map((item) => {
            const isTabActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path))
            return (
              <div
                key={item.name}
                onClick={() => router.push(item.path)}
                className={`relative flex items-center h-10 px-3 rounded-md cursor-pointer transition-all ${
                  isTabActive 
                    ? 'text-primary-foreground bg-primary' 
                    : 'text-foreground/70 hover:text-foreground hover:bg-muted/40'
                }`}
              >
                <item.icon className="h-5 w-5 shrink-0" />
                {!isCollapsed && (
                  <motion.span 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="ml-3 text-sm font-medium"
                  >
                    {item.name}
                  </motion.span>
                )}
                {isTabActive && (
                  <motion.div 
                    layoutId="activeIndicator"
                    className="absolute left-0 w-1 h-6 bg-white rounded-r"
                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                  />
                )}
              </div>
            )
          })}
        </nav>

        {/* Collapsible toggle */}
        <div className="p-3 border-t border-border flex justify-between items-center shrink-0">
          {!isCollapsed && (
            <div className="flex items-center gap-2 pl-2">
              <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center font-bold text-xs text-primary">
                {user?.full_name ? user.full_name.charAt(0) : 'U'}
              </div>
              <div className="text-[10px] overflow-hidden w-28">
                <p className="font-semibold truncate">{user?.full_name || 'Operator'}</p>
                <p className="text-muted-foreground truncate">{user?.email || 'session'}</p>
              </div>
            </div>
          )}
          <button 
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded hover:bg-muted/50 text-foreground/50 hover:text-foreground"
          >
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>
      </motion.aside>

      {/* ─── MAIN WORKSPACE PANEL ─── */}
      <main className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative">
        
        {/* Top Header */}
        <header className="h-16 border-b border-border bg-card/65 backdrop-blur px-6 flex items-center justify-between shrink-0 z-30">
          
          {/* Breadcrumbs */}
          <div className="flex items-center gap-2 text-xs text-foreground/60 select-none">
            <span className="cursor-pointer hover:text-foreground" onClick={() => router.push('/')}>opspilot</span>
            {breadcrumbs.map((bc, idx) => (
              <React.Fragment key={idx}>
                <span>/</span>
                <span 
                  className={`cursor-pointer ${bc.isLast ? 'text-foreground font-semibold' : 'hover:text-foreground'}`}
                  onClick={() => !bc.isLast && router.push(bc.url)}
                >
                  {bc.name.toLowerCase()}
                </span>
              </React.Fragment>
            ))}
          </div>

          {/* Controls Panel */}
          <div className="flex items-center gap-3">
            
            {/* Global Search Bar */}
            <div 
              onClick={() => setIsSearchOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 rounded border border-border bg-background hover:border-muted-foreground/40 cursor-pointer w-48 transition-colors text-xs text-muted-foreground select-none"
            >
              <Search className="h-3 w-3 shrink-0" />
              <span className="flex-1">Search NOC...</span>
              <kbd className="text-[9px] border border-border px-1.5 py-0.5 rounded bg-muted/30">⌘K</kbd>
            </div>

            {/* Notification center */}
            <div className="relative">
              <button 
                onClick={() => setIsNotificationOpen(!isNotificationOpen)}
                className="p-2 border border-border bg-background rounded-md text-foreground/70 hover:text-foreground hover:bg-muted/30 relative"
              >
                <Bell className="h-4 w-4" />
                <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-error" />
              </button>
              <AnimatePresence>
                {isNotificationOpen && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsNotificationOpen(false)} />
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="absolute right-0 mt-2 w-80 rounded-md border border-border bg-card p-4 shadow-xl z-50 space-y-3"
                    >
                      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Notification Feed</h3>
                      <div className="space-y-2">
                        {notifications.map(n => (
                          <div key={n.id} className="flex gap-2.5 p-2 rounded hover:bg-muted/40 text-xs">
                            {n.type === 'success' && <CheckCircle2 className="h-4 w-4 text-success shrink-0" />}
                            {n.type === 'error' && <AlertTriangle className="h-4 w-4 text-error shrink-0" />}
                            {n.type === 'info' && <Info className="h-4 w-4 text-accent shrink-0" />}
                            <div className="flex-1">
                              <p className="text-foreground/90 font-medium">{n.text}</p>
                              <span className="text-[10px] text-muted-foreground">{n.time}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>

            {/* Theme switcher */}
            <div className="relative">
              <div className="flex border border-border bg-background p-0.5 rounded-md gap-0.5 select-none">
                <button 
                  onClick={() => applyTheme('dark')}
                  className={`p-1.5 rounded-md ${currentTheme === 'dark' ? 'bg-primary text-white' : 'text-foreground/50 hover:bg-muted/40'}`}
                  title="Dark Theme"
                >
                  <Moon className="h-3.5 w-3.5" />
                </button>
                <button 
                  onClick={() => applyTheme('light')}
                  className={`p-1.5 rounded-md ${currentTheme === 'light' ? 'bg-primary text-white' : 'text-foreground/50 hover:bg-muted/40'}`}
                  title="Light Theme"
                >
                  <Sun className="h-3.5 w-3.5" />
                </button>
                <button 
                  onClick={() => applyTheme('oled')}
                  className={`px-1.5 py-0.5 text-[9px] font-bold rounded-md ${currentTheme === 'oled' ? 'bg-primary text-white' : 'text-foreground/50 hover:bg-muted/40'}`}
                  title="OLED Theme"
                >
                  OLED
                </button>
                <button 
                  onClick={() => applyTheme('enterprise-blue')}
                  className={`px-1.5 py-0.5 text-[9px] font-bold rounded-md ${currentTheme === 'enterprise-blue' ? 'bg-primary text-white' : 'text-foreground/50 hover:bg-muted/40'}`}
                  title="Enterprise Blue"
                >
                  BLUE
                </button>
              </div>
            </div>

            {/* Logout */}
            <button 
              onClick={() => {
                logout()
                router.replace('/login')
              }}
              className="p-2 border border-border bg-background rounded-md text-foreground/50 hover:text-error hover:bg-error/5"
              title="Logout session"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>

        {/* Main page scroll canvas */}
        <div className="flex-1 overflow-y-auto min-h-0 relative">
          {children}
        </div>

        {/* Global AI Action Button */}
        <button 
          onClick={() => setIsAiOpen(true)}
          className="fixed bottom-6 right-6 h-12 w-12 rounded-full bg-primary text-primary-foreground shadow-2xl flex items-center justify-center hover:scale-105 hover:bg-primary/95 transition-transform z-40 border border-primary-foreground/10"
        >
          <Sparkles className="h-5 w-5 animate-pulse" />
        </button>

      </main>

      {/* ─── COMMAND PALETTE MODAL ─── */}
      <AnimatePresence>
        {isSearchOpen && (
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsSearchOpen(false)}
              className="fixed inset-0 bg-background/80 backdrop-blur-sm"
            />
            <motion.div 
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="relative max-w-xl w-full border border-border bg-card rounded-md shadow-2xl overflow-hidden"
            >
              <div className="flex items-center px-4 py-3 border-b border-border gap-3">
                <Search className="h-5 w-5 text-muted-foreground" />
                <input 
                  type="text"
                  autoFocus
                  placeholder="Type a page name or shortcut (e.g. settings)..."
                  className="flex-1 bg-transparent text-sm outline-none border-none"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <span className="text-[10px] text-muted-foreground border border-border px-1.5 py-0.5 rounded bg-muted/40">ESC</span>
              </div>
              <div className="p-2 max-h-72 overflow-y-auto">
                <h4 className="px-3 py-1.5 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Navigation Shortcuts</h4>
                {filteredSearch.map((item, idx) => (
                  <div 
                    key={idx}
                    onClick={() => {
                      setIsSearchOpen(false)
                      router.push(item.url)
                    }}
                    className="flex justify-between items-center px-3 py-2 rounded hover:bg-muted/50 cursor-pointer text-xs transition-colors"
                  >
                    <span>{item.title}</span>
                    <span className="text-[10px] text-muted-foreground">{item.url}</span>
                  </div>
                ))}
                {filteredSearch.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-6">No matching pages found.</p>
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ─── FLOATING AI ASSISTANT DRAWER ─── */}
      <AnimatePresence>
        {isAiOpen && (
          <div className="fixed inset-0 z-50 flex justify-end">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsAiOpen(false)}
              className="fixed inset-0 bg-background/50 backdrop-blur-xs"
            />
            <motion.div 
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 220 }}
              className="relative w-96 h-full border-l border-border bg-card flex flex-col shadow-2xl z-50"
            >
              <div className="h-16 px-4 border-b border-border flex items-center justify-between bg-muted/20">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  <span className="font-bold text-sm">OpsPilot AI Co-Pilot</span>
                </div>
                <button 
                  onClick={() => setIsAiOpen(false)}
                  className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground"
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>

              {/* Chat history */}
              <div className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-thin">
                {aiMessages.map((msg, idx) => (
                  <div key={idx} className={`flex flex-col gap-1 max-w-[85%] ${msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}>
                    <div className={`p-3 rounded-md text-xs leading-relaxed ${
                      msg.role === 'user' ? 'bg-primary text-white' : 'bg-muted/50 border border-border'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                ))}
                {isAiSending && (
                  <div className="mr-auto items-start max-w-[85%] space-y-1 animate-pulse">
                    <div className="p-3 rounded-md text-xs bg-muted/30 border border-border text-muted-foreground">
                      Co-pilot is investigating cluster telemetry and routing...
                    </div>
                  </div>
                )}
              </div>

              {/* Chat input */}
              <form onSubmit={handleSendAi} className="p-4 border-t border-border flex gap-2">
                <input 
                  type="text"
                  required
                  placeholder="Ask co-pilot: 'Trigger pipeline', 'Check deployments'..."
                  className="flex-1 bg-background border border-border px-3 py-2 text-xs rounded outline-none focus:border-primary"
                  value={aiInput}
                  onChange={(e) => setAiInput(e.target.value)}
                />
                <button 
                  type="submit"
                  disabled={isAiSending}
                  className="px-3 py-2 bg-primary hover:bg-primary/95 text-white rounded text-xs font-semibold shrink-0 disabled:opacity-50"
                >
                  Ask
                </button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  )
}
