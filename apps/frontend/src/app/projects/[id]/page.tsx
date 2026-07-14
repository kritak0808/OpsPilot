'use client'

import * as React from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Project {
  id: string
  name: string
  slug: string
  description?: string
}

interface Application {
  id: string
  name: string
  slug: string
  description?: string
}

export default function ProjectDetailsPage() {
  const { id } = useParams() as { id: string }
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const [project, setProject] = React.useState<Project | null>(null)
  const [apps, setApps] = React.useState<Application[]>([])
  const [newAppName, setNewAppName] = React.useState('')
  const [newAppSlug, setNewAppSlug] = React.useState('')
  const [newAppDesc, setNewAppDesc] = React.useState('')
  
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  const [isCreatingApp, setIsCreatingApp] = React.useState(false)

  const fetchData = React.useCallback(async () => {
    if (!token || !id) return
    try {
      // Get Project details
      const projRes = await fetch(`/api/v1/projects/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!projRes.ok) throw new Error('Failed to load project details.')
      const projData = await projRes.json()
      setProject(projData)

      // Get applications
      const appsRes = await fetch(`/api/v1/projects/${id}/applications`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (appsRes.ok) {
        const appsData = await appsRes.json()
        setApps(appsData)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, id])

  React.useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleCreateApp = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsCreatingApp(true)

    try {
      const res = await fetch(`/api/v1/projects/${id}/applications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newAppName, slug: newAppSlug, description: newAppDesc }),
      })

      if (!res.ok) throw new Error('Failed to create application.')
      const data = await res.json()
      setApps((prev) => [...prev, data])
      setNewAppName('')
      setNewAppSlug('')
      setNewAppDesc('')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsCreatingApp(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#090b0f] text-[#f1f5f9]">
        <p className="text-sm text-foreground/50 animate-pulse">Loading project data...</p>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#090b0f] text-[#f1f5f9]">
        <p className="text-sm text-error">Project not found or access denied.</p>
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-8">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{project.name}</h1>
            <p className="text-sm text-foreground/50">{project.description || 'No description provided.'}</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/projects')}
              className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
            >
              All Projects
            </button>
            <button
              onClick={() => router.push('/repositories/connect')}
              className="px-4 py-2 bg-primary hover:bg-primary/95 text-white text-sm font-semibold rounded"
            >
              Connect Codebase
            </button>
          </div>
        </header>

        {error && (
          <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded max-w-md">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Applications list */}
          <div className="md:col-span-2 space-y-4">
            <h2 className="text-lg font-bold">Applications</h2>
            {apps.length > 0 ? (
              <div className="grid grid-cols-1 gap-4">
                {apps.map((app) => (
                  <div
                    key={app.id}
                    className="p-5 border border-[#1d232f] bg-[#11151c] rounded flex justify-between items-center"
                  >
                    <div>
                      <h3 className="font-bold text-base">{app.name}</h3>
                      <p className="text-xs text-foreground/50 mt-1">slug: {app.slug}</p>
                      {app.description && <p className="text-sm text-foreground/60 mt-2">{app.description}</p>}
                    </div>
                    <button
                      onClick={() => router.push(`/repositories/connect?app_id=${app.id}`)}
                      className="px-3 py-1.5 border border-[#1d232f] bg-[#090b0f] hover:bg-border/15 text-xs rounded font-semibold"
                    >
                      Connect Repo
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="border border-dashed border-[#1d232f] p-8 text-center text-sm text-foreground/45 rounded">
                No deployment applications registered in this project.
              </div>
            )}
          </div>

          {/* Create App Form */}
          <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 h-fit">
            <h2 className="text-lg font-bold">Register Application</h2>
            <form onSubmit={handleCreateApp} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Application Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Frontend SSR"
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
                  value={newAppName}
                  onChange={(e) => {
                    setNewAppName(e.target.value)
                    setNewAppSlug(e.target.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''))
                  }}
                />
              </div>
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Application Slug</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. frontend-ssr"
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
                  value={newAppSlug}
                  onChange={(e) => setNewAppSlug(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Description</label>
                <textarea
                  placeholder="App description..."
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary h-20"
                  value={newAppDesc}
                  onChange={(e) => setNewAppDesc(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={isCreatingApp}
                className="w-full py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded transition-colors disabled:opacity-50"
              >
                {isCreatingApp ? 'Registering...' : 'Register Application'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
