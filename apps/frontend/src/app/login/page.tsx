'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuth } from '@/providers/auth-provider'
import { Sparkles, Mail, Lock, LogIn } from 'lucide-react'

export default function LoginPage() {
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [error, setError] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.message || 'Authentication credentials rejected.')
      }

      const data = await response.json()
      
      // Load user profile details
      const userRes = await fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${data.access_token}` },
      })
      const userData = await userRes.json()

      login(data.access_token, data.refresh_token, userData)
      router.replace('/org-select')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#090b0f] gradient-mesh text-[#f1f5f9] p-6 relative overflow-hidden">
      
      {/* Background radial overlays */}
      <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-primary/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-accent/10 blur-[120px] pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="max-w-md w-full border border-border/80 bg-card/60 backdrop-blur-xl p-8 rounded-xl space-y-6 shadow-2xl relative z-10"
      >
        <div className="text-center space-y-2">
          <div className="h-11 w-11 rounded-lg bg-primary flex items-center justify-center text-white font-bold mx-auto mb-4 border border-primary-foreground/10 shadow-lg">
            OP
          </div>
          <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-foreground to-primary">
            Sign in to OpsPilot
          </h1>
          <p className="text-xs text-muted-foreground">
            Provide your credentials to access the Operations Center.
          </p>
        </div>

        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded-md"
          >
            {error}
          </motion.div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="block text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4.5 w-4.5 text-muted-foreground/60" />
              <input
                type="email"
                required
                className="w-full bg-background border border-border pl-10 pr-3 py-2 text-sm rounded outline-none focus:border-primary transition-colors text-foreground"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="operator@opspilot.ai"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 h-4.5 w-4.5 text-muted-foreground/60" />
              <input
                type="password"
                required
                className="w-full bg-background border border-border pl-10 pr-3 py-2 text-sm rounded outline-none focus:border-primary transition-colors text-foreground"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded-md transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-primary/20 disabled:opacity-50 mt-6"
          >
            {isSubmitting ? 'Authenticating...' : (
              <>
                <LogIn className="h-4 w-4" />
                Sign In
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            Don&apos;t have an account?{' '}
            <span
              onClick={() => router.push('/register')}
              className="text-primary hover:underline cursor-pointer font-bold transition-all"
            >
              Sign Up
            </span>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
