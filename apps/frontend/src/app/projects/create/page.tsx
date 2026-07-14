'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

export default function CreateProjectPage() {
  const [name, setName] = React.useState('')
  const [slug, setSlug] = React.useState('')
  const [desc, setDesc] = React.useState('')
  const [error, setError] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const res = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Org-ID': activeOrgId || '',
        },
        body: JSON.stringify({ name, slug, description: desc }),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Failed to create project.')
      }

      router.push('/projects')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex items-center justify-center bg-[#090b0f] text-[#f1f5f9] p-6">
        <div className="max-w-md w-full border border-[#1d232f] bg-[#11151c] p-8 rounded-md space-y-6 shadow-md">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Create New Project</h1>
            <p className="text-xs text-foreground/50 mt-1">
              Initialize a project space to group deployment applications.
            </p>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-foreground/70 uppercase">Project Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Core API Service"
                className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  setSlug(e.target.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''))
                }}
              />
            </div>
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-foreground/70 uppercase">Project Slug</label>
              <input
                type="text"
                required
                placeholder="e.g. core-api-service"
                className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="block text-xs font-semibold text-foreground/70 uppercase">Description</label>
              <textarea
                placeholder="Scope details..."
                className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary h-24"
                value={desc}
                onChange={(e) => setDesc(e.target.value)}
              />
            </div>
            <div className="flex gap-4 pt-2">
              <button
                type="button"
                onClick={() => router.back()}
                className="w-1/2 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10 text-center"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-1/2 py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Creating...' : 'Create'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </ProtectedRoute>
  )
}
