'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Repository {
  id: string
  name: string
  full_name: string
  clone_url: string
  default_branch: string
  webhook_id?: string
}

export default function RepositoriesPage() {
  const [repos, setRepos] = React.useState<Repository[]>([])
  const [error, setError] = React.useState('')
  const [isLoading, setIsLoading] = React.useState(true)
  
  const [syncStatus, setSyncStatus] = React.useState<Record<string, string>>({})
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const fetchRepos = React.useCallback(async () => {
    if (!token || !activeOrgId) return
    try {
      const res = await fetch('/api/v1/repositories', {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-Org-ID': activeOrgId,
        },
      })
      if (!res.ok) throw new Error('Failed to load repositories.')
      const data = await res.json()
      setRepos(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [token, activeOrgId])

  React.useEffect(() => {
    fetchRepos()
  }, [fetchRepos])

  const handleSyncRepo = async (repoId: string) => {
    setSyncStatus((prev) => ({ ...prev, [repoId]: 'Syncing...' }))
    try {
      const res = await fetch(`/api/v1/repositories/${repoId}/sync`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Sync request failed.')
      const data = await res.json()
      setSyncStatus((prev) => ({
        ...prev,
        [repoId]: `Done: ${data.recent_commits_count} commits, ${data.branches.length} branches`,
      }))
    } catch (err: any) {
      setSyncStatus((prev) => ({ ...prev, [repoId]: `Error: ${err.message}` }))
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-8">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Connected Repositories</h1>
            <p className="text-sm text-foreground/50">Manage source code connections, webhook triggers, and commit logs.</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
            >
              Dashboard
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

        {isLoading ? (
          <div className="text-sm text-foreground/50 py-8">Loading repositories...</div>
        ) : repos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {repos.map((repo) => (
              <div
                key={repo.id}
                className="p-6 border border-[#1d232f] bg-[#11151c] rounded-md space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    <h2 className="text-lg font-bold">{repo.name}</h2>
                    <span className="text-xs bg-[#090b0f] border border-[#1d232f] px-2 py-0.5 rounded text-foreground/60">
                      GitHub
                    </span>
                  </div>
                  <p className="text-xs text-foreground/50 italic">{repo.full_name}</p>
                  <p className="text-sm text-foreground/75">
                    Clone: <span className="font-mono text-xs">{repo.clone_url}</span>
                  </p>
                  <div className="flex gap-4 text-xs text-foreground/60 pt-1">
                    <p>Default Branch: <span className="font-semibold text-foreground/80">{repo.default_branch}</span></p>
                    <p>
                      Webhook:{' '}
                      <span className={repo.webhook_id ? 'text-success font-semibold' : 'text-warning font-semibold'}>
                        {repo.webhook_id ? 'Active' : 'Unregistered'}
                      </span>
                    </p>
                  </div>
                </div>

                <div className="pt-4 border-t border-[#1d232f] flex justify-between items-center gap-4">
                  <span className="text-xs text-foreground/60 font-mono">
                    {syncStatus[repo.id] || 'Last synced: Just now'}
                  </span>
                  <button
                    onClick={() => handleSyncRepo(repo.id)}
                    className="px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded"
                  >
                    Sync Metadata
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="border border-dashed border-[#1d232f] p-12 text-center rounded max-w-md mx-auto space-y-4">
            <p className="text-sm text-foreground/50">No source code repositories connected to this organization.</p>
            <button
              onClick={() => router.push('/repositories/connect')}
              className="px-4 py-2 bg-primary hover:bg-primary/95 text-white text-xs font-semibold rounded"
            >
              Link GitHub Codebase
            </button>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
