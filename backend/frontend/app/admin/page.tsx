'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { BookOpen, Users, Database, TrendingUp, RefreshCw, CheckCircle, XCircle, Clock } from '@/components/icons'

export default function AdminDashboard() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState<any>(null)
  const [knowledge, setKnowledge] = useState<any[]>([])
  const [credentials, setCredentials] = useState({ username: '', password: '' })
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
      })

      if (!response.ok) {
        throw new Error('Invalid credentials')
      }

      const data = await response.json()
      localStorage.setItem('admin_token', data.access_token)
      setIsAuthenticated(true)
      await loadDashboardData(data.access_token)
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const loadDashboardData = async (token: string) => {
    setLoading(true)
    try {
      const statsResponse = await fetch('http://localhost:8000/api/v1/knowledge/stats')
      if (statsResponse.ok) {
        setStats(await statsResponse.json())
      }

      const kbResponse = await fetch('http://localhost:8000/api/v1/admin/knowledge?limit=100', {
        headers: { 'Authorization': \`Bearer \${token}\` }
      })
      if (kbResponse.ok) {
        const kbData = await kbResponse.json()
        setKnowledge(kbData.documents || [])
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleProcessDocument = async (documentId: string) => {
    const token = localStorage.getItem('admin_token')
    if (!token) return

    try {
      const response = await fetch(\`http://localhost:8000/api/v1/admin/knowledge/\${documentId}/process\`, {
        method: 'POST',
        headers: { 'Authorization': \`Bearer \${token}\` }
      })

      if (response.ok) {
        alert('Processing started! Check backend logs for progress.')
        await loadDashboardData(token)
      } else {
        alert('Failed to start processing')
      }
    } catch (err) {
      alert('Error starting processing')
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      setIsAuthenticated(true)
      loadDashboardData(token)
    }
  }, [])

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Admin Login</CardTitle>
            <CardDescription>Enter credentials to access admin dashboard</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">{error}</div>
              )}
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" value={credentials.username} onChange={(e) => setCredentials({ ...credentials, username: e.target.value })} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" value={credentials.password} onChange={(e) => setCredentials({ ...credentials, password: e.target.value })} required />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>{loading ? 'Logging in...' : 'Login'}</Button>
            </form>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-gray-600 mt-2">Manage knowledge base and monitor system</p>
          </div>
          <Button variant="outline" onClick={() => { localStorage.removeItem('admin_token'); setIsAuthenticated(false) }}>Logout</Button>
        </div>

        {loading && !stats ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}><CardHeader><Skeleton className="h-4 w-24 mb-2" /><Skeleton className="h-8 w-16" /></CardHeader></Card>
            ))}
          </div>
        ) : stats ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Rules</CardTitle>
                <BookOpen className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_rules || 0}</div>
                <p className="text-xs text-gray-600">{stats.rules_with_embeddings || 0} with embeddings</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Symbolic Keys</CardTitle>
                <Database className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_symbolic_keys || 0}</div>
                <p className="text-xs text-gray-600">Indexing patterns</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Coverage</CardTitle>
                <TrendingUp className="h-4 w-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.coverage_percentage || 0}%</div>
                <p className="text-xs text-gray-600">Embedding coverage</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Domains</CardTitle>
                <Users className="h-4 h-4 text-gray-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.rules_by_domain ? Object.keys(stats.rules_by_domain).length : 0}</div>
                <p className="text-xs text-gray-600">Knowledge categories</p>
              </CardContent>
            </Card>
          </div>
        ) : null}

        {stats?.rules_by_domain && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Rules by Domain</CardTitle>
              <CardDescription>Distribution across life areas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(stats.rules_by_domain).map(([domain, count]: [string, any]) => (
                  <div key={domain} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-24 text-sm font-medium capitalize">{domain}</div>
                      <div className="flex-1 bg-gray-200 rounded-full h-2 w-64">
                        <div className="bg-jio-600 h-2 rounded-full" style={{ width: \`\${(count / stats.total_rules) * 100}%\` }} />
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">{count} rules</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Knowledge Base Documents</CardTitle>
                <CardDescription>Manage and process texts</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={() => { const token = localStorage.getItem('admin_token'); if (token) loadDashboardData(token) }}>
                <RefreshCw className="w-4 h-4 mr-2" />Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {loading && knowledge.length === 0 ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="space-y-2 flex-1">
                      <Skeleton className="h-5 w-48" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                    <Skeleton className="h-10 w-24" />
                  </div>
                ))}
              </div>
            ) : knowledge.length > 0 ? (
              <div className="space-y-3">
                {knowledge.map((doc: any) => (
                  <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{doc.title}</h3>
                        {doc.is_indexed === 'true' && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-800">
                            <CheckCircle className="w-3 h-3" />Indexed
                          </span>
                        )}
                        {doc.is_indexed === 'processing' && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-blue-100 text-blue-800">
                            <Clock className="w-3 h-3" />Processing
                          </span>
                        )}
                        {doc.is_indexed === 'false' && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-800">
                            <XCircle className="w-3 h-3" />Not Indexed
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{doc.description || \`Added \${new Date(doc.created_at).toLocaleDateString()}\`}</p>
                    </div>
                    {doc.is_indexed !== 'processing' && (
                      <Button variant="outline" size="sm" onClick={() => handleProcessDocument(doc.id)}>
                        {doc.is_indexed === 'true' ? 'Reprocess' : 'Process'}
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-600">No documents found</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
