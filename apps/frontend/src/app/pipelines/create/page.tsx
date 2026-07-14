'use client'

import * as React from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuth } from '@/providers/auth-provider'
import { ProtectedRoute } from '@/components/auth/protected-route'

const DEFAULT_YAML = `stages:
  - name: build
    jobs:
      - name: compile
        runner_image: ubuntu-latest
        steps:
          - name: run-compile
            run: npm run build
  - name: test
    jobs:
      - name: unit-tests
        steps:
          - name: run-tests
            run: npm run test
`

function CreatePipelineContent() {
  const searchParams = useSearchParams()
  const projectId = searchParams.get('project_id')

  const [name, setName] = React.useState('')
  const [slug, setSlug] = React.useState('')
  const [desc, setDesc] = React.useState('')
  const [yamlConfig, setYamlConfig] = React.useState(DEFAULT_YAML)
  
  const [error, setError] = React.useState('')
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const { token } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const res = await fetch('/api/v1/pipelines', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Project-ID': projectId || '',
        },
        body: JSON.stringify({ name, slug, description: desc, yaml_config: yamlConfig }),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Pipeline creation failed.')
      }

      router.push('/pipelines')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#090b0f] text-[#f1f5f9] p-8 space-y-6">
      <header className="flex justify-between items-center border-b border-[#1d232f] pb-6">
        <div>
          <h1 className="text-xl font-bold tracking-tight">Configure Pipeline</h1>
          <p className="text-xs text-foreground/50">Edit your pipeline specifications and step workflows.</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 border border-[#1d232f] bg-[#11151c] text-sm font-semibold rounded hover:bg-border/10"
        >
          Cancel
        </button>
      </header>

      {error && (
        <div className="p-3 bg-error/10 border border-error/20 text-error text-xs rounded max-w-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Meta configurations */}
        <div className="md:col-span-1 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4 h-fit">
          <h2 className="text-base font-bold uppercase tracking-wider">Metadata</h2>
          
          <div className="space-y-1">
            <label className="block text-xs font-semibold text-foreground/70 uppercase">Pipeline Name</label>
            <input
              type="text"
              required
              placeholder="e.g. Production CI"
              className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                setSlug(e.target.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''))
              }}
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-foreground/70 uppercase">Pipeline Slug</label>
            <input
              type="text"
              required
              placeholder="e.g. production-ci"
              className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-foreground/70 uppercase">Description</label>
            <textarea
              placeholder="Scope details..."
              className="w-full bg-[#090b0f] border border-[#1d232f] px-3 py-2 text-sm rounded outline-none focus:border-primary h-20"
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2 bg-primary hover:bg-primary/95 text-white font-semibold text-sm rounded transition-all disabled:opacity-50"
          >
            {isSubmitting ? 'Saving Configuration...' : 'Register Pipeline Config'}
          </button>
        </div>

        {/* YAML workflow editor */}
        <div className="md:col-span-2 border border-[#1d232f] bg-[#11151c] p-6 rounded-md space-y-4">
          <h2 className="text-base font-bold uppercase tracking-wider">Workflow Configuration (YAML)</h2>
          <textarea
            required
            className="w-full bg-[#090b0f] border border-[#1d232f] p-4 text-sm font-mono rounded outline-none focus:border-primary h-96 text-[#f1f5f9] leading-relaxed resize-none"
            value={yamlConfig}
            onChange={(e) => setYamlConfig(e.target.value)}
          />
        </div>
      </form>
    </div>
  )
}

export default function CreatePipelinePage() {
  return (
    <ProtectedRoute>
      <React.Suspense fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#090b0f] text-[#f1f5f9]">
          <p className="text-sm text-foreground/50 animate-pulse">Loading editor canvas...</p>
        </div>
      }>
        <CreatePipelineContent />
      </React.Suspense>
    </ProtectedRoute>
  )
}
