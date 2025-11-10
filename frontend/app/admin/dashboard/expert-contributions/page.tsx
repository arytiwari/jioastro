'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  ArrowLeft,
  Plus,
  Search,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  CheckCircle,
  XCircle,
  Clock,
  Code,
  TrendingUp,
} from '@/components/icons'

interface Contribution {
  id: number
  expert_id: string
  contribution_type: 'additive' | 'incremental' | 'update'
  category: 'yoga' | 'dasha' | 'transit' | 'house' | 'planet' | 'aspect' | 'varga' | 'remedy'
  subcategory?: string
  title: string
  description: string
  rule_definition?: string
  example_charts?: string
  expected_impact?: string
  algorithm_changes?: string
  affected_modules?: string[]
  classical_reference?: string
  modern_reference?: string
  status: 'pending' | 'under_review' | 'approved' | 'implemented' | 'rejected'
  priority: 'low' | 'normal' | 'high' | 'critical'
  confidence_level?: number
  upvotes: number
  downvotes: number
  net_votes: number
  comment_count: number
  created_at: string
  updated_at: string
  reviewed_by?: string
  reviewed_at?: string
  review_notes?: string
}

interface Stats {
  total_contributions: number
  pending_contributions: number
  under_review_contributions: number
  approved_contributions: number
  implemented_contributions: number
  rejected_contributions: number
  total_upvotes: number
  total_downvotes: number
  avg_accuracy_improvement: number
  total_validated_impacts: number
}

export default function ExpertContributionsPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'list' | 'create' | 'stats'>('list')
  const [contributions, setContributions] = useState<Contribution[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedContribution, setSelectedContribution] = useState<Contribution | null>(null)

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')

  // Form data
  const [formData, setFormData] = useState({
    contribution_type: 'additive' as const,
    category: 'yoga' as const,
    subcategory: '',
    title: '',
    description: '',
    rule_definition: '',
    example_charts: '',
    expected_impact: '',
    algorithm_changes: '',
    classical_reference: '',
    modern_reference: '',
    priority: 'normal' as const,
    confidence_level: 7,
  })

  // Load data on mount
  useEffect(() => {
    loadContributions()
    loadStats()
  }, [statusFilter, categoryFilter])

  const loadContributions = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (categoryFilter !== 'all') params.append('category', categoryFilter)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/expert-knowledge/contributions?${params}`
      )
      const data = await response.json()
      setContributions(data.contributions || [])
    } catch (error) {
      console.error('Failed to load contributions:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/expert-knowledge/stats`
      )
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/expert-knowledge/contributions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      )

      if (!response.ok) throw new Error('Failed to create contribution')

      alert('Contribution created successfully!')
      setActiveTab('list')
      loadContributions()
      loadStats()
      resetForm()
    } catch (error) {
      console.error('Error creating contribution:', error)
      alert('Failed to create contribution')
    }
  }

  const handleApprove = async (id: number) => {
    if (!confirm('Are you sure you want to approve this contribution?')) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/expert-knowledge/contributions/${id}/approve`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            review_notes: 'Approved by admin',
            approved: true,
          }),
        }
      )

      if (!response.ok) throw new Error('Failed to approve')

      alert('Contribution approved!')
      loadContributions()
      loadStats()
    } catch (error) {
      console.error('Error approving contribution:', error)
      alert('Failed to approve contribution')
    }
  }

  const handleReject = async (id: number) => {
    const reason = prompt('Please provide a reason for rejection:')
    if (!reason) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/expert-knowledge/contributions/${id}/reject`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            review_notes: reason,
            approved: false,
          }),
        }
      )

      if (!response.ok) throw new Error('Failed to reject')

      alert('Contribution rejected')
      loadContributions()
      loadStats()
    } catch (error) {
      console.error('Error rejecting contribution:', error)
      alert('Failed to reject contribution')
    }
  }

  const resetForm = () => {
    setFormData({
      contribution_type: 'additive',
      category: 'yoga',
      subcategory: '',
      title: '',
      description: '',
      rule_definition: '',
      example_charts: '',
      expected_impact: '',
      algorithm_changes: '',
      classical_reference: '',
      modern_reference: '',
      priority: 'normal',
      confidence_level: 7,
    })
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'secondary',
      under_review: 'outline',
      approved: 'default',
      implemented: 'default',
      rejected: 'destructive',
    }

    const icons: Record<string, any> = {
      pending: Clock,
      under_review: Search,
      approved: CheckCircle,
      implemented: Code,
      rejected: XCircle,
    }

    const Icon = icons[status] || Clock

    return (
      <Badge variant={variants[status] || 'default'}>
        <Icon className="w-3 h-3 mr-1" />
        {status.replace('_', ' ')}
      </Badge>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Back Button */}
      <Button
        variant="outline"
        onClick={() => router.push('/admin/dashboard')}
        className="mb-4"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Dashboard
      </Button>

      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Expert Knowledge Management</h1>
          <p className="text-muted-foreground">
            Manage expert contributions to improve JioAstro's predictions
          </p>
        </div>
        <Button onClick={() => setActiveTab('create')}>
          <Plus className="w-4 h-4 mr-2" />
          New Contribution
        </Button>
      </div>

      {/* Statistics Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_contributions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pending_contributions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Under Review
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.under_review_contributions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Approved
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.approved_contributions}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Implemented
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.implemented_contributions}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
        <TabsList>
          <TabsTrigger value="list">Contributions</TabsTrigger>
          <TabsTrigger value="create">Create New</TabsTrigger>
          <TabsTrigger value="stats">Statistics</TabsTrigger>
        </TabsList>

        {/* List Tab */}
        <TabsContent value="list" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label>Status Filter</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Statuses</SelectItem>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="under_review">Under Review</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="implemented">Implemented</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Category Filter</Label>
                  <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="yoga">Yoga</SelectItem>
                      <SelectItem value="dasha">Dasha</SelectItem>
                      <SelectItem value="transit">Transit</SelectItem>
                      <SelectItem value="house">House</SelectItem>
                      <SelectItem value="planet">Planet</SelectItem>
                      <SelectItem value="aspect">Aspect</SelectItem>
                      <SelectItem value="varga">Varga</SelectItem>
                      <SelectItem value="remedy">Remedy</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Search</Label>
                  <Input
                    placeholder="Search by title..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contributions List */}
          <Card>
            <CardHeader>
              <CardTitle>Contributions ({contributions.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">Loading...</div>
              ) : contributions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No contributions found
                </div>
              ) : (
                <div className="space-y-4">
                  {contributions
                    .filter((c) =>
                      c.title.toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .map((contribution) => (
                      <Card key={contribution.id} className="hover:bg-accent transition-colors">
                        <CardContent className="pt-6">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h3 className="text-lg font-semibold">{contribution.title}</h3>
                                {getStatusBadge(contribution.status)}
                                <Badge variant="outline">{contribution.category}</Badge>
                                <Badge variant="outline">{contribution.contribution_type}</Badge>
                              </div>

                              <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                                {contribution.description}
                              </p>

                              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <ThumbsUp className="w-4 h-4" />
                                  {contribution.upvotes}
                                </div>
                                <div className="flex items-center gap-1">
                                  <ThumbsDown className="w-4 h-4" />
                                  {contribution.downvotes}
                                </div>
                                <div className="flex items-center gap-1">
                                  <MessageSquare className="w-4 h-4" />
                                  {contribution.comment_count}
                                </div>
                                {contribution.confidence_level && (
                                  <div className="flex items-center gap-1">
                                    <TrendingUp className="w-4 h-4" />
                                    Confidence: {contribution.confidence_level}/10
                                  </div>
                                )}
                              </div>
                            </div>

                            {contribution.status === 'pending' && (
                              <div className="flex gap-2 ml-4">
                                <Button
                                  size="sm"
                                  variant="default"
                                  onClick={() => handleApprove(contribution.id)}
                                >
                                  <CheckCircle className="w-4 h-4 mr-1" />
                                  Approve
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleReject(contribution.id)}
                                >
                                  <XCircle className="w-4 h-4 mr-1" />
                                  Reject
                                </Button>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Create Tab */}
        <TabsContent value="create">
          <Card>
            <CardHeader>
              <CardTitle>Create New Contribution</CardTitle>
              <CardDescription>
                Submit a new expert knowledge contribution to improve JioAstro's predictions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Basic Information</h3>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="contribution_type">Type *</Label>
                      <Select
                        value={formData.contribution_type}
                        onValueChange={(value: any) =>
                          setFormData({ ...formData, contribution_type: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="additive">Additive (New Knowledge)</SelectItem>
                          <SelectItem value="incremental">Incremental (Refinement)</SelectItem>
                          <SelectItem value="update">Update (Correction)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="category">Category *</Label>
                      <Select
                        value={formData.category}
                        onValueChange={(value: any) =>
                          setFormData({ ...formData, category: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="yoga">Yoga</SelectItem>
                          <SelectItem value="dasha">Dasha</SelectItem>
                          <SelectItem value="transit">Transit</SelectItem>
                          <SelectItem value="house">House</SelectItem>
                          <SelectItem value="planet">Planet</SelectItem>
                          <SelectItem value="aspect">Aspect</SelectItem>
                          <SelectItem value="varga">Varga</SelectItem>
                          <SelectItem value="remedy">Remedy</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="subcategory">Subcategory</Label>
                      <Input
                        id="subcategory"
                        value={formData.subcategory}
                        onChange={(e) =>
                          setFormData({ ...formData, subcategory: e.target.value })
                        }
                        placeholder="e.g., raj_yoga"
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="title">Title *</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Brief title for your contribution"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description *</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) =>
                        setFormData({ ...formData, description: e.target.value })
                      }
                      placeholder="Detailed description of the contribution"
                      rows={4}
                      required
                    />
                  </div>
                </div>

                {/* Technical Details */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Technical Details</h3>

                  <div>
                    <Label htmlFor="rule_definition">Rule Definition</Label>
                    <Textarea
                      id="rule_definition"
                      value={formData.rule_definition}
                      onChange={(e) =>
                        setFormData({ ...formData, rule_definition: e.target.value })
                      }
                      placeholder="Formal rule description"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="example_charts">Example Charts</Label>
                    <Textarea
                      id="example_charts"
                      value={formData.example_charts}
                      onChange={(e) =>
                        setFormData({ ...formData, example_charts: e.target.value })
                      }
                      placeholder="Birth chart examples demonstrating the rule"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="expected_impact">Expected Impact</Label>
                    <Textarea
                      id="expected_impact"
                      value={formData.expected_impact}
                      onChange={(e) =>
                        setFormData({ ...formData, expected_impact: e.target.value })
                      }
                      placeholder="How this should affect predictions"
                      rows={2}
                    />
                  </div>

                  <div>
                    <Label htmlFor="algorithm_changes">Algorithm Changes</Label>
                    <Textarea
                      id="algorithm_changes"
                      value={formData.algorithm_changes}
                      onChange={(e) =>
                        setFormData({ ...formData, algorithm_changes: e.target.value })
                      }
                      placeholder="Pseudo-code or description of code changes"
                      rows={4}
                    />
                  </div>
                </div>

                {/* References */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">References</h3>

                  <div>
                    <Label htmlFor="classical_reference">Classical Reference</Label>
                    <Input
                      id="classical_reference"
                      value={formData.classical_reference}
                      onChange={(e) =>
                        setFormData({ ...formData, classical_reference: e.target.value })
                      }
                      placeholder="e.g., Brihat Parashara Hora Shastra, Chapter 41"
                    />
                  </div>

                  <div>
                    <Label htmlFor="modern_reference">Modern Reference</Label>
                    <Input
                      id="modern_reference"
                      value={formData.modern_reference}
                      onChange={(e) =>
                        setFormData({ ...formData, modern_reference: e.target.value })
                      }
                      placeholder="Modern work reference"
                    />
                  </div>
                </div>

                {/* Metadata */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Metadata</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="priority">Priority</Label>
                      <Select
                        value={formData.priority}
                        onValueChange={(value: any) =>
                          setFormData({ ...formData, priority: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="normal">Normal</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="critical">Critical</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label htmlFor="confidence_level">
                        Confidence Level (1-10): {formData.confidence_level}
                      </Label>
                      <Input
                        id="confidence_level"
                        type="range"
                        min="1"
                        max="10"
                        value={formData.confidence_level}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            confidence_level: parseInt(e.target.value),
                          })
                        }
                      />
                    </div>
                  </div>
                </div>

                {/* Submit */}
                <div className="flex gap-2">
                  <Button type="submit">Create Contribution</Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      resetForm()
                      setActiveTab('list')
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Stats Tab */}
        <TabsContent value="stats">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Statistics</CardTitle>
              <CardDescription>
                Comprehensive metrics about expert contributions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Contribution Status</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Total:</span>
                        <span className="font-bold">{stats.total_contributions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Pending:</span>
                        <span className="font-bold">{stats.pending_contributions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Under Review:</span>
                        <span className="font-bold">{stats.under_review_contributions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Approved:</span>
                        <span className="font-bold">{stats.approved_contributions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Implemented:</span>
                        <span className="font-bold">{stats.implemented_contributions}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Rejected:</span>
                        <span className="font-bold">{stats.rejected_contributions}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-4">Community Engagement</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Total Upvotes:</span>
                        <span className="font-bold">{stats.total_upvotes}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Total Downvotes:</span>
                        <span className="font-bold">{stats.total_downvotes}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Validated Impacts:</span>
                        <span className="font-bold">{stats.total_validated_impacts}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Avg. Accuracy Improvement:</span>
                        <span className="font-bold">
                          {stats.avg_accuracy_improvement.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
