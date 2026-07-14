'use client'

import * as React from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

function ConnectRepoContent() {
  const searchParams = useSearchParams()
  const appId = searchParams.get('app_id')

  const [tokenInput, setTokenInput] = React.useState('')
  const [repos, setRepos] = React.useState<any[]>([])
  const [selectedRepo, setSelectedRepo] = React.useState<any | null>(null)
  
  const [error, setError] = React.useState('')
  const [isLoadingRepos, setIsLoadingRepos] = React.useState(false)
  const [isConnecting, setIsConnecting] = React.useState(false)
  const { token, activeOrgId } = useAuth()
  const router = useRouter()

  const handleFetchRepos = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoadingRepos(true)
    setSelectedRepo(null)

    try {
      // Fetch user repos from mock GitHub API representation 
      const res = await fetch('https://api.github.com/user/repos?per_page=50', {
        headers: { Authorization: `Bearer ${tokenInput}` },
      })
      if (!res.ok) throw new Error('Failed to load repositories from GitHub. Verify Token scopes.')
      const data = await res.json()
      setRepos(data.map((r: any) => ({
        external_id: String(r.id),
        name: r.name,
        full_name: r.full_name,
        clone_url: r.clone_url,
      })))
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoadingRepos(false)
    }
  }

  const handleConnect = async () => {
    if (!selectedRepo) return
    setError('')
    setIsConnecting(true)

    try {
      // Generate standard provider UUID for GitProvider (fallback is handled at router)
      const providerId = '47474747-4747-4747-4747-474747474747'

      const res = await fetch('/api/v1/repositories/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Org-ID': activeOrgId || '',
        },
        body: JSON.stringify({
          git_provider_id: providerId,
          external_id: selectedRepo.external_id,
          name: selectedRepo.name,
          full_name: selectedRepo.full_name,
          clone_url: selectedRepo.clone_url,
          token: tokenInput,
        }),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Connection failed.')
      }

      router.push('/repositories')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsConnecting(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-8">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Connect Codebase</h1>
            <p className="text-sm text-foreground/50">Authenticate and sync code metadata to configure CI/CD automations.</p>
          </div>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
          >
            Go Back
          </button>
        </header>

        {error && (
          <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded max-w-md">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Step 1: Input GitHub Token */}
          <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
            <h2 className="text-lg font-bold">1. Provide GitHub OAuth Access Token</h2>
            <form onSubmit={handleFetchRepos} className="space-y-4">
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">Personal Access Token</label>
                <input
                  type="password"
                  required
                  placeholder="ghp_..."
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={isLoadingRepos}
                className="px-4 py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded transition-colors disabled:opacity-50"
              >
                {isLoadingRepos ? 'Fetching repositories...' : 'Load Repositories'}
              </button>
            </form>
          </div>

          {/* Step 2: Choose Repository & Connect */}
          <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <h2 className="text-lg font-bold">2. Select Target Repository</h2>
              {repos.length > 0 ? (
                <div className="max-h-60 overflow-y-auto space-y-1 border border-[#1d232f] p-2 bg-[#090b0f] rounded">
                  {repos.map((repo) => (
                    <div
                      key={repo.external_id}
                      onClick={() => setSelectedRepo(repo)}
                      className={`p-2 rounded text-xs cursor-pointer transition-all ${
                        selectedRepo?.external_id === repo.external_id
                          ? 'bg-primary/20 border border-primary text-foreground'
                          : 'hover:bg-border/10 text-foreground/70'
                      }`}
                    >
                      {repo.full_name}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-foreground/45 italic py-6 text-center">
                  Load your GitHub Token to see repositories list.
                </p>
              )}
            </div>

            {selectedRepo && (
              <div className="pt-4 border-t border-[#1d232f] space-y-3">
                <div className="text-xs text-foreground/60">
                  <p>Selected: <span className="font-bold text-foreground">{selectedRepo.full_name}</span></p>
                  <p className="mt-1">Clone URL: <span className="italic">{selectedRepo.clone_url}</span></p>
                </div>
                <button
                  onClick={handleConnect}
                  disabled={isConnecting}
                  className="w-full py-2 bg-success text-white font-semibold text-sm rounded hover:bg-success/90 transition-all disabled:opacity-50"
                >
                  {isConnecting ? 'Linking Codebase...' : 'Establish Integration Connection'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}

export default function ConnectRepoPage() {
  return (
    <React.Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-[#090b0f] text-[#f1f5f9]">
        <p className="text-sm text-foreground/50 animate-pulse">Loading connection wizard...</p>
      </div>
    }>
      <ConnectRepoContent />
    </React.Suspense>
  )
}
