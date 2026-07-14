'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

interface Team {
  id: string
  name: string
  slug: string
  description?: string
}

interface ApiKey {
  id: string
  name: string
  scope: string
  created_at: string
  expires_at?: string
}

interface Secret {
  key: string
  version: number
  updated_at: string
  kms_encrypted: boolean
}

interface FeatureFlag {
  id: string
  key: string
  description?: string
  is_enabled: boolean
}

interface AuditLog {
  id: string
  action: string
  details: string
  created_at: string
}

export default function SettingsPage() {
  const { user, token, activeOrgId, logout } = useAuth()
  const router = useRouter()

  const [activeTab, setActiveTab] = React.useState<'profile' | 'api-keys' | 'secrets' | 'feature-flags' | 'audit' | 'usage'>('profile')
  const [projectId, setProjectId] = React.useState('')

  // 1. Profile / Teams states
  const [fullName, setFullName] = React.useState(user?.full_name || '')
  const [inviteEmail, setInviteEmail] = React.useState('')
  const [inviteRole, setInviteRole] = React.useState('Viewer')
  const [teamName, setTeamName] = React.useState('')
  const [teamSlug, setTeamSlug] = React.useState('')
  const [teamDesc, setTeamDesc] = React.useState('')
  const [teams, setTeams] = React.useState<Team[]>([])
  const [profileMsg, setProfileMsg] = React.useState('')
  const [inviteMsg, setInviteMsg] = React.useState('')
  const [teamMsg, setTeamMsg] = React.useState('')

  // 2. Governance states
  const [apiKeys, setApiKeys] = React.useState<ApiKey[]>([])
  const [keyName, setKeyName] = React.useState('')
  const [keyScope, setKeyScope] = React.useState('read')
  const [newKeyGenerated, setNewKeyGenerated] = React.useState('')
  const [secretsList, setSecretsList] = React.useState<Secret[]>([])
  const [flags, setFlags] = React.useState<FeatureFlag[]>([])
  const [flagKey, setFlagKey] = React.useState('')
  const [flagDesc, setFlagDesc] = React.useState('')
  const [auditLogs, setAuditLogs] = React.useState<AuditLog[]>([])
  const [usage, setUsage] = React.useState<any>(null)

  // Fetch projects context
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

  // Profile / Teams Handlers
  const fetchTeams = React.useCallback(async () => {
    if (!token || !activeOrgId) return
    try {
      const res = await fetch('/api/v1/teams', {
        headers: { Authorization: `Bearer ${token}`, 'X-Org-ID': activeOrgId },
      })
      if (res.ok) setTeams(await res.json())
    } catch (err) {
      // fail silently
    }
  }, [token, activeOrgId])

  React.useEffect(() => {
    fetchTeams()
  }, [fetchTeams])

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setProfileMsg('')
    try {
      const res = await fetch(`/api/v1/users/${user?.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ full_name: fullName }),
      })
      if (!res.ok) throw new Error('Failed to update profile.')
      setProfileMsg('Profile successfully updated.')
    } catch (err: any) {
      setProfileMsg(`Error: ${err.message}`)
    }
  }

  const handleInviteMember = async (e: React.FormEvent) => {
    e.preventDefault()
    setInviteMsg('')
    try {
      const res = await fetch(`/api/v1/organizations/${activeOrgId}/members`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Org-ID': activeOrgId || '',
        },
        body: JSON.stringify({ email: inviteEmail, role_name: inviteRole }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Invite execution failed.')
      }
      setInviteMsg('Member successfully added to organization.')
      setInviteEmail('')
    } catch (err: any) {
      setInviteMsg(`Error: ${err.message}`)
    }
  }

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault()
    setTeamMsg('')
    try {
      const res = await fetch('/api/v1/teams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Org-ID': activeOrgId || '',
        },
        body: JSON.stringify({ name: teamName, slug: teamSlug, description: teamDesc }),
      })
      if (!res.ok) throw new Error('Failed to create team.')
      const data = await res.json()
      setTeams((prev) => [...prev, data])
      setTeamMsg('Team successfully configured.')
      setTeamName('')
      setTeamSlug('')
      setTeamDesc('')
    } catch (err: any) {
      setTeamMsg(`Error: ${err.message}`)
    }
  }

  // Governance tab loaders
  const loadGovernanceData = React.useCallback(async () => {
    if (!token || !projectId) return
    try {
      // Load API Keys
      const keysRes = await fetch('/api/v1/api-keys', {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': projectId },
      })
      if (keysRes.ok) setApiKeys(await keysRes.json())

      // Secrets
      const secRes = await fetch('/api/v1/secrets', {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': projectId },
      })
      if (secRes.ok) setSecretsList(await secRes.json())

      // Flags
      const flagRes = await fetch('/api/v1/feature-flags', {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': projectId },
      })
      if (flagRes.ok) setFlags(await flagRes.json())

      // Audits
      const auditRes = await fetch('/api/v1/audit', {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': projectId },
      })
      if (auditRes.ok) setAuditLogs(await auditRes.json())

      // Usage
      const usageRes = await fetch('/api/v1/usage', {
        headers: { Authorization: `Bearer ${token}`, 'X-Project-ID': projectId },
      })
      if (usageRes.ok) setUsage(await usageRes.json())
    } catch (err) {
      // Fail-safe
    }
  }, [token, projectId])

  React.useEffect(() => {
    loadGovernanceData()
  }, [loadGovernanceData])

  const handleGenerateKey = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!keyName) return
    try {
      const res = await fetch('/api/v1/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
        body: JSON.stringify({ name: keyName, scope: keyScope, expires_days: 30 }),
      })
      if (!res.ok) throw new Error('API key generation failed.')
      const data = await res.json()
      setNewKeyGenerated(data.key_preview)
      setKeyName('')
      loadGovernanceData()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleCreateFlag = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!flagKey) return
    try {
      const res = await fetch('/api/v1/feature-flags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId,
        },
        body: JSON.stringify({ key: flagKey, description: flagDesc, is_enabled: false }),
      })
      if (!res.ok) throw new Error('Failed to create feature flag.')
      setFlagKey('')
      setFlagDesc('')
      loadGovernanceData()
    } catch (err: any) {
      alert(err.message)
    }
  }

  const handleRevokeKey = async (id: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) return
    try {
      const res = await fetch(`/api/v1/api-keys/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Revocation failed.')
      loadGovernanceData()
    } catch (err: any) {
      alert(err.message)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-8">
        <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Governance Settings</h1>
            <p className="text-sm text-foreground/50">Manage teams configuration, API keys, vault secrets, feature toggles, and audit trails.</p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
            >
              Dashboard
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 bg-error hover:bg-error/95 text-white text-sm font-semibold rounded"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Governance Navigation Tabs */}
        <div className="border-b border-[#1d232f] flex gap-6 text-sm font-semibold">
          {(['profile', 'api-keys', 'secrets', 'feature-flags', 'audit', 'usage'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 uppercase tracking-wider text-xs transition-all ${
                activeTab === tab
                  ? 'border-b-2 border-primary text-foreground'
                  : 'text-foreground/50 hover:text-foreground/80'
              }`}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>

        {/* Profile and Teams Panel */}
        {activeTab === 'profile' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fadeIn">
            {/* User Profile Form */}
            <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
              <h2 className="text-lg font-bold">User Profile Settings</h2>
              {profileMsg && <div className="text-xs text-primary">{profileMsg}</div>}
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Full Name</label>
                  <input
                    type="text"
                    required
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded"
                >
                  Save Changes
                </button>
              </form>
            </div>

            {/* Member Invitation Form */}
            <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
              <h2 className="text-lg font-bold">Invite Organization Members</h2>
              {inviteMsg && <div className="text-xs text-primary">{inviteMsg}</div>}
              <form onSubmit={handleInviteMember} className="space-y-4">
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Email Address</label>
                  <input
                    type="email"
                    required
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Assign Role</label>
                  <select
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                  >
                    <option value="OrgOwner">OrgOwner</option>
                    <option value="Admin">Admin</option>
                    <option value="DevOpsEngineer">DevOpsEngineer</option>
                    <option value="Developer">Developer</option>
                    <option value="Viewer">Viewer</option>
                  </select>
                </div>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded"
                >
                  Send Invite
                </button>
              </form>
            </div>

            {/* Teams Config Panel */}
            <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 md:col-span-2">
              <h2 className="text-lg font-bold">Manage Organization Teams</h2>
              {teamMsg && <div className="text-xs text-primary">{teamMsg}</div>}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <form onSubmit={handleCreateTeam} className="space-y-3 md:col-span-1 border-r border-[#1d232f] pr-6">
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-foreground/70 uppercase">Team Name</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. SRE Platform"
                      className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                      value={teamName}
                      onChange={(e) => {
                        setTeamName(e.target.value)
                        setTeamSlug(e.target.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''))
                      }}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-foreground/70 uppercase">Team Slug</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. sre-platform"
                      className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                      value={teamSlug}
                      onChange={(e) => setTeamSlug(e.target.value)}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-foreground/70 uppercase">Description</label>
                    <textarea
                      placeholder="Brief scope..."
                      className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary h-20 text-[#f1f5f9]"
                      value={teamDesc}
                      onChange={(e) => setTeamDesc(e.target.value)}
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded"
                  >
                    Create Team
                  </button>
                </form>

                <div className="md:col-span-2 space-y-4">
                  <h3 className="text-sm font-semibold uppercase text-foreground/70">Configured Teams</h3>
                  {teams.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {teams.map((team) => (
                        <div key={team.id} className="p-4 border border-[#1d232f] bg-[#090b0f] rounded space-y-1">
                          <h4 className="font-bold text-sm text-foreground">{team.name}</h4>
                          <p className="text-xs text-foreground/50">slug: {team.slug}</p>
                          {team.description && <p className="text-xs text-foreground/60 italic pt-1">{team.description}</p>}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-8 border border-dashed border-[#1d232f] text-center text-xs text-foreground/40 rounded">
                      No teams configured yet.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* API Keys Tab */}
        {activeTab === 'api-keys' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 h-fit">
              <h2 className="text-sm font-bold uppercase tracking-wider">Generate API Key</h2>
              <form onSubmit={handleGenerateKey} className="space-y-4">
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Key Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Jenkins Integration"
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                    value={keyName}
                    onChange={(e) => setKeyName(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Scope permissions</label>
                  <select
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                    value={keyScope}
                    onChange={(e) => setKeyScope(e.target.value)}
                  >
                    <option value="read">Read Only</option>
                    <option value="write">Write/Trigger</option>
                    <option value="admin">Full Admin</option>
                  </select>
                </div>
                <button
                  type="submit"
                  className="w-full py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded"
                >
                  Generate Cryptographic Key
                </button>
              </form>

              {newKeyGenerated && (
                <div className="mt-4 p-3 bg-success/15 border border-success/30 rounded text-xs">
                  <p className="font-bold text-success">Copy this key value now (shown only once):</p>
                  <p className="font-mono bg-[#090b0f] p-2 mt-2 rounded select-all break-all">{newKeyGenerated}</p>
                </div>
              )}
            </div>

            <div className="md:col-span-2 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider">Active API Keys</h2>
              <div className="space-y-3 pt-2">
                {apiKeys.map((key) => (
                  <div key={key.id} className="p-4 border border-[#1d232f] bg-[#090b0f] rounded flex justify-between items-center text-sm">
                    <div>
                      <h3 className="font-bold">{key.name}</h3>
                      <p className="text-xs text-foreground/50">scope: <span className="font-mono text-primary font-semibold">{key.scope}</span></p>
                    </div>
                    <button
                      onClick={() => handleRevokeKey(key.id)}
                      className="px-3 py-1 bg-error/10 hover:bg-error/20 border border-error/20 text-error text-xs font-semibold rounded"
                    >
                      Revoke
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Secrets Tab */}
        {activeTab === 'secrets' && (
          <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider">Vault KMS Environment Secrets</h2>
            <div className="space-y-4 pt-2">
              {secretsList.map((sec) => (
                <div key={sec.key} className="p-4 border border-[#1d232f] bg-[#090b0f] rounded flex justify-between items-center text-sm">
                  <div>
                    <h3 className="font-mono font-bold text-primary">{sec.key}</h3>
                    <p className="text-[10px] text-foreground/50 pt-1">Version: {sec.version}</p>
                  </div>
                  <span className="text-xs text-success font-semibold">KMS Encrypted</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Feature Flags Tab */}
        {activeTab === 'feature-flags' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 h-fit">
              <h2 className="text-sm font-bold uppercase tracking-wider">Create Feature Toggle</h2>
              <form onSubmit={handleCreateFlag} className="space-y-4">
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Flag Key</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. enable-new-checkout"
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary text-[#f1f5f9]"
                    value={flagKey}
                    onChange={(e) => setFlagKey(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="block text-xs font-semibold text-foreground/70 uppercase">Description</label>
                  <textarea
                    placeholder="Scope limits..."
                    className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary h-20 text-[#f1f5f9]"
                    value={flagDesc}
                    onChange={(e) => setFlagDesc(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded"
                >
                  Configure Flag
                </button>
              </form>
            </div>

            <div className="md:col-span-2 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider">Registered Flags</h2>
              <div className="space-y-3 pt-2">
                {flags.map((flg) => (
                  <div key={flg.id} className="p-4 border border-[#1d232f] bg-[#090b0f] rounded flex justify-between items-center text-sm">
                    <div>
                      <h3 className="font-mono font-bold">{flg.key}</h3>
                      {flg.description && <p className="text-xs text-foreground/50 mt-1">{flg.description}</p>}
                    </div>
                    <span className={`text-xs px-2.5 py-0.5 rounded font-bold uppercase ${
                      flg.is_enabled ? 'bg-success/15 text-success' : 'bg-foreground/10 text-foreground/50'
                    }`}>
                      {flg.is_enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Audit Tab */}
        {activeTab === 'audit' && (
          <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-wider">Audit Trail Logger</h2>
            <div className="space-y-3 pt-2">
              {auditLogs.length > 0 ? (
                auditLogs.map((log) => (
                  <div key={log.id} className="p-4 border border-[#1d232f] bg-[#090b0f] rounded flex justify-between items-center text-xs">
                    <div>
                      <span className="text-primary font-bold">[{log.action.toUpperCase()}]</span>
                      <span className="text-foreground/80 pl-3">{log.details}</span>
                    </div>
                    <span className="text-foreground/40 font-mono">{log.created_at.split('T')[0]}</span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-foreground/40 py-8 text-center">No audit trail records found.</p>
              )}
            </div>
          </div>
        )}

        {/* Usage Analytics Tab */}
        {activeTab === 'usage' && usage && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-2">
              <h3 className="text-xs font-bold text-foreground/60 uppercase">API Calls Count</h3>
              <p className="text-2xl font-extrabold font-mono text-primary">{usage.api_calls_count}</p>
            </div>
            <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-2">
              <h3 className="text-xs font-bold text-foreground/60 uppercase">Pipeline Runs Executed</h3>
              <p className="text-2xl font-extrabold font-mono text-success">{usage.pipeline_runs_count}</p>
            </div>
            <div className="border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-2">
              <h3 className="text-xs font-bold text-foreground/60 uppercase">Active Core Users</h3>
              <p className="text-2xl font-extrabold font-mono text-foreground">{usage.active_users_count}</p>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
