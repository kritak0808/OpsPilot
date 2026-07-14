'use client'

import * as React from 'react'

if (typeof window !== 'undefined' && !(window as any).__fetch_patched) {
  (window as any).__fetch_patched = true
  const originalFetch = window.fetch
  window.fetch = async (input, init) => {
    if (typeof input === 'string' && input.startsWith('/api/')) {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      input = `${baseUrl}${input}`
    }
    return originalFetch(input, init)
  }
}

interface UserProfile {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

interface AuthContextType {
  user: UserProfile | null
  token: string | null
  activeOrgId: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (token: string, refreshToken: string, user: UserProfile) => void
  logout: () => void
  setOrg: (orgId: string) => void
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = React.useState<UserProfile | null>(null)
  const [token, setToken] = React.useState<string | null>(null)
  const [activeOrgId, setActiveOrgId] = React.useState<string | null>(null)
  const [isLoading, setIsLoading] = React.useState<boolean>(true)

  React.useEffect(() => {
    // Load local auth credentials if present on startup
    const storedUser = localStorage.getItem('opspilot_user')
    const storedToken = localStorage.getItem('opspilot_token')
    const storedOrg = localStorage.getItem('opspilot_org')

    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser))
      setToken(storedToken)
      if (storedOrg) setActiveOrgId(storedOrg)
    }
    setIsLoading(false)
  }, [])

  const login = (accessToken: string, refreshToken: string, userProfile: UserProfile) => {
    setToken(accessToken)
    setUser(userProfile)
    localStorage.setItem('opspilot_token', accessToken)
    localStorage.setItem('opspilot_refresh', refreshToken)
    localStorage.setItem('opspilot_user', JSON.stringify(userProfile))
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    setActiveOrgId(null)
    localStorage.removeItem('opspilot_token')
    localStorage.removeItem('opspilot_refresh')
    localStorage.removeItem('opspilot_user')
    localStorage.removeItem('opspilot_org')
  }

  const setOrg = (orgId: string) => {
    setActiveOrgId(orgId)
    localStorage.setItem('opspilot_org', orgId)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        activeOrgId,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
        setOrg,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = React.useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
