'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Project {
  id: string
  name: string
  slug: string
  description?: string
}

export default function ProjectsPage() {
  const [projects, setProjects] = React.useState<Project[]>([])
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchProjects = React.useCallback(async () => {
    if (!token || !activeOrgId) return
    try {
      const res = await fetch('/api/v1/projects', {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Org-ID': activeOrgId,
        },
      })
      if (!res.ok) throw new Error('Failed to load projects.')
      const data = await res.json()
      setProjects(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, activeOrgId])

  React.useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-8">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Projects Dashboard</h1>
            <p className="text-sm text-foreground/50">Manage your organization operations, pipeline runs, and resources.</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
            >
              Dashboard
            </button>
            <button
              onClick={() => router.push('/projects/create')}
              className="px-4 py-2 bg-primary hover:bg-primary/95 text-white text-sm font-semibold rounded"
            >
              New Project
            </button>
          </div>
        </header>

        {error && (
          <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded max-w-md">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-sm text-foreground/50 py-8">Loading projects...</div>
        ) : projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => router.push(`/projects/${project.id}`)}
                className="p-6 border border-[#1d232f] bg-[#11151c] hover:border-primary/50 hover:bg-[#11151c]/70 rounded-md cursor-pointer transition-all space-y-3"
              >
                <div className="flex justify-between items-start">
                  <h2 className="text-lg font-bold">{project.name}</h2>
                  <span className="text-xs bg-[#090b0f] px-2 py-0.5 rounded text-foreground/60">
                    {project.slug}
                  </span>
                </div>
                {project.description && (
                  <p className="text-sm text-foreground/60 line-clamp-2">{project.description}</p>
                )}
                <div className="pt-2 text-xs text-primary font-medium hover:underline flex items-center gap-1">
                  Manage applications &rarr;
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="border border-dashed border-[#1d232f] p-12 text-center rounded max-w-md mx-auto space-y-4">
            <p className="text-sm text-foreground/50">No projects found in this organization.</p>
            <button
              onClick={() => router.push('/projects/create')}
              className="px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded"
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
