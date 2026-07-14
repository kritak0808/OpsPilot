'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Organization {
  id: string
  name: string
  slug: string
  billing_tier: string
}

export default function OrgSelectPage() {
  const [orgs, setOrgs] = React.useState<Organization[]>([])
  const [newOrgName, setNewOrgName] = React.useState('')
  const [newOrgSlug, setNewOrgSlug] = React.useState('')
  const [error, setError] = React.useState('')
  const [isLoadingOrgs, setIsLoadingOrgs] = React.useState(true)
  const [isCreating, setIsCreating] = React.useState(false)
  const { token, setOrg } = useAuth()
  const router = useRouter()

  const fetchOrgs = React.useCallback(async () => {
    if (!token) return
    try {
      const res = await fetch('/api/v1/organizations', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Failed to retrieve organizations.')
      const data = await res.json()
      setOrgs(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoadingOrgs(false)
    }
  }, [token])

  React.useEffect(() => {
    fetchOrgs()
  }, [fetchOrgs])

  const handleSelectOrg = (orgId: string) => {
    setOrg(orgId)
    router.replace('/')
  }

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsCreating(true)

    try {
      const res = await fetch('/api/v1/organizations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: newOrgName, slug: newOrgSlug }),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Organization creation failed.')
      }

      const createdOrg = await res.json()
      setOrgs((prev) => [...prev, createdOrg])
      setNewOrgName('')
      setNewOrgSlug('')
      handleSelectOrg(createdOrg.id)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen flex items-center justify-center bg-[#090b0f] text-[#f1f5f9] p-6">
        <div className="max-w-md w-full border border-[#1d232f] bg-[#11151c] p-8 rounded-md space-y-6 shadow-md">
          <div className="text-center">
            <h1 className="text-xl font-bold tracking-tight">Select Organization</h1>
            <p className="text-xs text-foreground/50 mt-1">
              Select an active tenant or create a new workspace.
            </p>
          </div>

          {error && (
            <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded">
              {error}
            </div>
          )}

          {isLoadingOrgs ? (
            <div className="py-4 text-center text-xs text-foreground/40">
              Loading available organizations...
            </div>
          ) : orgs.length > 0 ? (
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-foreground/70 uppercase">
                Your Organizations
              </label>
              <div className="space-y-1">
                {orgs.map((org) => (
                  <div
                    key={org.id}
                    onClick={() => handleSelectOrg(org.id)}
                    className="p-3 border border-[#1d232f] hover:border-primary bg-[#090b0f] hover:bg-primary/5 rounded cursor-pointer transition-all flex justify-between items-center text-sm"
                  >
                    <span className="font-semibold">{org.name}</span>
                    <span className="text-xs text-foreground/45">slug: {org.slug}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-3 bg-[#090b0f] border border-[#1d232f] text-center text-xs text-foreground/50 rounded">
              No organizations found. Create a new organization below.
            </div>
          )}

          <div className="border-t border-[#1d232f] pt-6 space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-foreground/80">
              Create New Organization
            </h2>
            <form onSubmit={handleCreateOrg} className="space-y-3">
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">
                  Org Name
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Corp"
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
                  value={newOrgName}
                  onChange={(e) => {
                    setNewOrgName(e.target.value)
                    setNewOrgSlug(e.target.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''))
                  }}
                />
              </div>
              <div className="space-y-1">
                <label className="block text-xs font-semibold text-foreground/70 uppercase">
                  Org Slug
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. acme-corp"
                  className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
                  value={newOrgSlug}
                  onChange={(e) => setNewOrgSlug(e.target.value)}
                />
              </div>
              <button
                type="submit"
                disabled={isCreating}
                className="w-full py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded transition-colors disabled:opacity-50"
              >
                {isCreating ? 'Creating Org...' : 'Create & Select Org'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}
