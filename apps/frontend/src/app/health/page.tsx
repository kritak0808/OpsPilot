'use client'

import * as React from 'react'

export default function HealthPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background text-foreground p-6">
      <div className="max-w-md w-full border border-border bg-card p-8 rounded-md space-y-4 shadow-sm text-center">
        <div className="h-12 w-12 rounded bg-success/20 text-success flex items-center justify-center mx-auto text-xl font-bold">
          ✓
        </div>
        <h1 className="text-xl font-bold tracking-tight">Client Health Status</h1>
        <p className="text-sm text-foreground/60">
          The OpsPilot client-side web application interface is loaded and fully operational.
        </p>
        <div className="pt-4 border-t border-border flex justify-between text-xs text-foreground/50">
          <span>Version: 1.0.0</span>
          <span>Environment: Production</span>
        </div>
      </div>
    </div>
  )
}
