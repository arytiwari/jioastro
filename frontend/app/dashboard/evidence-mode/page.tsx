'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Shield, BookOpen, Search, FileText, CheckCircle, XCircle } from '@/components/icons'
import { apiClient } from '@/lib/api'

interface Source {
  id: string
  title: string
  author: string
  source_type: string
  publication_year?: number
  verified: boolean
  verification_level: string
  citation_count: number
  tags: string[]
  description?: string
}

export default function EvidenceModePage() {
  const [sources, setSources] = useState<Source[]>([])
  const [filteredSources, setFilteredSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterVerified, setFilterVerified] = useState<string>('all')

  useEffect(() => {
    fetchSources()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [sources, searchQuery, filterType, filterVerified])

  const fetchSources = async () => {
    setLoading(true)
    try {
      const response = await apiClient.post('/api/v2/evidence-mode/sources/search', {
        query: '',
        source_type: null,
        verified_only: false,
        page: 1,
        page_size: 50
      })
      setSources(response.data.sources || [])
    } catch (error) {
      console.error('Error fetching sources:', error)
      // Set demo data for demonstration
      setDemoData()
    } finally {
      setLoading(false)
    }
  }

  const setDemoData = () => {
    const demoSources: Source[] = [
      {
        id: '1',
        title: 'Brihat Parashara Hora Shastra',
        author: 'Maharishi Parashara',
        source_type: 'classical_text',
        verified: true,
        verification_level: 'high',
        citation_count: 245,
        tags: ['Vedic Astrology', 'Horoscopy', 'Classical'],
        description: 'The foundational text of Vedic astrology, containing comprehensive knowledge on birth chart interpretation.'
      },
      {
        id: '2',
        title: 'Jataka Parijata',
        author: 'Vaidyanatha Dikshita',
        source_type: 'classical_text',
        publication_year: 1426,
        verified: true,
        verification_level: 'high',
        citation_count: 178,
        tags: ['Vedic Astrology', 'Predictive', 'Classical'],
        description: 'A comprehensive work on predictive astrology and horoscope interpretation.'
      },
      {
        id: '3',
        title: 'Saravali',
        author: 'Kalyana Varma',
        source_type: 'classical_text',
        verified: true,
        verification_level: 'high',
        citation_count: 156,
        tags: ['Vedic Astrology', 'Principles', 'Classical'],
        description: 'An ancient treatise covering fundamental principles of astrology.'
      },
      {
        id: '4',
        title: 'Phaladeepika',
        author: 'Mantreswara',
        source_type: 'classical_text',
        publication_year: 1490,
        verified: true,
        verification_level: 'high',
        citation_count: 142,
        tags: ['Vedic Astrology', 'Predictive', 'Classical'],
        description: 'A classical work focusing on the predictive aspects of Vedic astrology.'
      },
      {
        id: '5',
        title: 'Hora Sara',
        author: 'Prithuyasas',
        source_type: 'classical_text',
        verified: true,
        verification_level: 'medium',
        citation_count: 89,
        tags: ['Vedic Astrology', 'Horoscopy'],
        description: 'An important classical text on horoscope analysis.'
      },
      {
        id: '6',
        title: 'Modern Research on Vedic Astrology',
        author: 'Dr. K.S. Charak',
        source_type: 'research_paper',
        publication_year: 2003,
        verified: true,
        verification_level: 'medium',
        citation_count: 34,
        tags: ['Research', 'Modern', 'Validation'],
        description: 'Contemporary research validating classical astrological principles.'
      }
    ]
    setSources(demoSources)
  }

  const applyFilters = () => {
    let filtered = [...sources]

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(source =>
        source.title.toLowerCase().includes(query) ||
        source.author.toLowerCase().includes(query) ||
        source.tags.some(tag => tag.toLowerCase().includes(query))
      )
    }

    // Type filter
    if (filterType !== 'all') {
      filtered = filtered.filter(source => source.source_type === filterType)
    }

    // Verified filter
    if (filterVerified === 'verified') {
      filtered = filtered.filter(source => source.verified)
    } else if (filterVerified === 'unverified') {
      filtered = filtered.filter(source => !source.verified)
    }

    setFilteredSources(filtered)
  }

  const getSourceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'classical_text': 'Classical Text',
      'research_paper': 'Research Paper',
      'commentary': 'Commentary',
      'modern_study': 'Modern Study',
      'conference_paper': 'Conference Paper',
      'journal': 'Journal Article',
      'expert_opinion': 'Expert Opinion',
      'case_study': 'Case Study'
    }
    return labels[type] || type
  }

  const getVerificationColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-green-700 bg-green-100'
      case 'medium': return 'text-blue-700 bg-blue-100'
      case 'low': return 'text-yellow-700 bg-yellow-100'
      default: return 'text-gray-700 bg-gray-100'
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-green-100 rounded-lg">
            <Shield className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Evidence Mode</h1>
            <p className="text-gray-600">Citation-backed trust system</p>
          </div>
        </div>
        <p className="text-gray-700 mt-2">
          Explore classical texts and research that back our astrological insights
        </p>
      </div>

      {/* Info Banner */}
      <Card className="mb-6 border-green-200 bg-green-50">
        <CardContent className="py-4">
          <div className="flex items-start gap-3">
            <BookOpen className="w-5 h-5 text-green-600 mt-0.5" />
            <div>
              <p className="font-semibold text-green-900">Trust Through Transparency</p>
              <p className="text-sm text-green-700">
                Every insight is backed by classical texts and verified sources. Browse our evidence library below.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search and Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Search Sources</CardTitle>
          <CardDescription>Find classical texts and research papers</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by title, author, or tags..."
                className="w-full pl-10 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Source Type</label>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="all">All Types</option>
                  <option value="classical_text">Classical Texts</option>
                  <option value="research_paper">Research Papers</option>
                  <option value="commentary">Commentaries</option>
                  <option value="modern_study">Modern Studies</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Verification Status</label>
                <select
                  value={filterVerified}
                  onChange={(e) => setFilterVerified(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="all">All Sources</option>
                  <option value="verified">Verified Only</option>
                  <option value="unverified">Unverified</option>
                </select>
              </div>
            </div>

            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                Showing {filteredSources.length} of {sources.length} sources
              </span>
              {(searchQuery || filterType !== 'all' || filterVerified !== 'all') && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSearchQuery('')
                    setFilterType('all')
                    setFilterVerified('all')
                  }}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sources List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading sources...</p>
        </div>
      ) : filteredSources.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Search className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600">No sources found matching your criteria</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredSources.map((source) => (
            <Card key={source.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <BookOpen className="w-5 h-5 text-green-600" />
                      {source.title}
                      {source.verified && (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      )}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      by {source.author}
                      {source.publication_year && ` • ${source.publication_year}`}
                    </CardDescription>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span className={`text-xs px-2 py-1 rounded ${getVerificationColor(source.verification_level)}`}>
                      {source.verification_level} confidence
                    </span>
                    <span className="text-xs text-gray-600">
                      {source.citation_count} citations
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {source.description && (
                  <p className="text-sm text-gray-700 mb-3">{source.description}</p>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-2">
                    <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                      {getSourceTypeLabel(source.source_type)}
                    </span>
                    {source.tags.slice(0, 3).map((tag, index) => (
                      <span key={index} className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <Button variant="outline" size="sm">
                    <FileText className="w-4 h-4 mr-1" />
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Stats Summary */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Evidence Library Statistics</CardTitle>
          <CardDescription>Our commitment to accuracy</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-900">{sources.length}</p>
              <p className="text-sm text-green-700">Total Sources</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-900">
                {sources.filter(s => s.verified).length}
              </p>
              <p className="text-sm text-blue-700">Verified</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-900">
                {sources.reduce((sum, s) => sum + s.citation_count, 0)}
              </p>
              <p className="text-sm text-purple-700">Total Citations</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-900">
                {sources.filter(s => s.source_type === 'classical_text').length}
              </p>
              <p className="text-sm text-orange-700">Classical Texts</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
