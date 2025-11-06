'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Database, FileText, TrendingUp, AlertCircle, CheckCircle, Clock, BookOpen, Sparkles } from '@/components/icons'

interface KnowledgeOverview {
  summary: {
    total_documents: number
    indexed_documents: number
    processing_documents: number
    failed_documents: number
    total_rules: number
    total_embeddings: number
    total_text_chars: number
    total_text_mb: number
  }
  documents_by_type: Record<string, number>
  rules_by_domain: Record<string, number>
  recent_documents: Array<{
    id: string
    title: string
    type: string
    status: string
    uploaded_at: string
    embeddings: number
    text_chars: number
  }>
}

interface Rule {
  id: string
  rule_id: string
  domain: string
  condition: string
  effect: string
  anchor: string
  weight: number
  created_at: string
}

export default function AdminKnowledgePage() {
  const router = useRouter()
  const [adminUsername, setAdminUsername] = useState('')
  const [overview, setOverview] = useState<KnowledgeOverview | null>(null)
  const [rules, setRules] = useState<Rule[]>([])
  const [selectedDomain, setSelectedDomain] = useState<string>('all')
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'documents' | 'rules'>('overview')

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('admin_token')
    const username = localStorage.getItem('admin_username')

    if (!token || !username) {
      router.push('/admin/login')
      return
    }

    setAdminUsername(username)
    fetchOverview()
  }, [])

  useEffect(() => {
    if (activeTab === 'rules') {
      fetchRules()
    }
  }, [activeTab, selectedDomain])

  const fetchOverview = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge/stats/overview`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setOverview(data)
      }
    } catch (error) {
      console.error('Error fetching knowledge overview:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRules = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const url = selectedDomain === 'all'
        ? `${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge/rules/all?limit=100`
        : `${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge/rules/all?domain=${selectedDomain}&limit=100`

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setRules(data.rules || [])
      }
    } catch (error) {
      console.error('Error fetching rules:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_username')
    router.push('/admin/login')
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'true':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'processing':
        return <Clock className="w-4 h-4 text-blue-600 animate-spin" />
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />
      default:
        return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome back, {adminUsername}</p>
            </div>
            <div className="flex items-center gap-3">
              <Button onClick={() => router.push('/admin/dashboard')} variant="outline">
                ← Back to Dashboard
              </Button>
              <Button onClick={handleLogout} variant="outline">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold flex items-center gap-3">
              <Database className="w-8 h-8 text-blue-600" />
              Knowledge Base
            </h2>
            <p className="text-gray-600 mt-1">
              View all ingested knowledge, embeddings, and rules
            </p>
          </div>
          <Button onClick={fetchOverview} variant="outline">
            <TrendingUp className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        <Button
          variant={activeTab === 'overview' ? 'default' : 'outline'}
          onClick={() => setActiveTab('overview')}
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Overview
        </Button>
        <Button
          variant={activeTab === 'documents' ? 'default' : 'outline'}
          onClick={() => setActiveTab('documents')}
        >
          <FileText className="w-4 h-4 mr-2" />
          Documents
        </Button>
        <Button
          variant={activeTab === 'rules' ? 'default' : 'outline'}
          onClick={() => setActiveTab('rules')}
        >
          <BookOpen className="w-4 h-4 mr-2" />
          Rules
        </Button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && overview && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Total Documents</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{overview.summary.total_documents}</div>
                <p className="text-xs text-gray-500 mt-1">
                  {overview.summary.indexed_documents} indexed
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Total Rules</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">{overview.summary.total_rules}</div>
                <p className="text-xs text-gray-500 mt-1">
                  Across {Object.keys(overview.rules_by_domain).length} domains
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Embeddings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">{overview.summary.total_embeddings}</div>
                <p className="text-xs text-gray-500 mt-1">
                  Vector embeddings
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Content Size</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">{overview.summary.total_text_mb} MB</div>
                <p className="text-xs text-gray-500 mt-1">
                  {(overview.summary.total_text_chars / 1000).toFixed(0)}K chars
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Processing Status */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span>Indexed</span>
                  </div>
                  <span className="font-semibold">{overview.summary.indexed_documents}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-600" />
                    <span>Processing</span>
                  </div>
                  <span className="font-semibold">{overview.summary.processing_documents}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                    <span>Failed</span>
                  </div>
                  <span className="font-semibold">{overview.summary.failed_documents}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Rules by Domain */}
          <Card>
            <CardHeader>
              <CardTitle>Rules by Domain</CardTitle>
              <CardDescription>Distribution of knowledge rules across domains</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(overview.rules_by_domain).map(([domain, count]) => (
                  <div key={domain} className="p-3 border rounded-lg">
                    <div className="text-sm text-gray-600 capitalize">{domain}</div>
                    <div className="text-2xl font-bold mt-1">{count}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Documents Tab */}
      {activeTab === 'documents' && overview && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Documents</CardTitle>
              <CardDescription>Latest uploaded knowledge documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {overview.recent_documents.map((doc) => (
                  <div key={doc.id} className="p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(doc.status)}
                          <h3 className="font-semibold">{doc.title}</h3>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded">{doc.type}</span>
                        </div>
                        <div className="mt-2 text-sm text-gray-600 space-y-1">
                          <div>📊 {doc.embeddings} embeddings</div>
                          <div>📝 {(doc.text_chars / 1000).toFixed(1)}K characters</div>
                          <div>🕐 {formatDate(doc.uploaded_at)}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Rules Tab */}
      {activeTab === 'rules' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Knowledge Base Rules</CardTitle>
                  <CardDescription>Astrology rules extracted from documents</CardDescription>
                </div>
                <select
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  className="px-3 py-2 border rounded-md"
                >
                  <option value="all">All Domains</option>
                  {overview && Object.keys(overview.rules_by_domain).map(domain => (
                    <option key={domain} value={domain}>{domain}</option>
                  ))}
                </select>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {rules.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No rules found for selected domain
                  </div>
                ) : (
                  rules.map((rule) => (
                    <div key={rule.id} className="p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-start justify-between mb-2">
                        <div className="font-mono text-sm text-blue-600">{rule.rule_id}</div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded">
                            {rule.domain}
                          </span>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                            Weight: {rule.weight}
                          </span>
                        </div>
                      </div>
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-semibold text-gray-700">Condition:</span>
                          <p className="text-gray-600 mt-1">{rule.condition}</p>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Effect:</span>
                          <p className="text-gray-600 mt-1">{rule.effect}</p>
                        </div>
                        {rule.anchor && (
                          <div>
                            <span className="font-semibold text-gray-700">Source:</span>
                            <p className="text-gray-500 text-xs mt-1">{rule.anchor}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      </main>
    </div>
  )
}
