'use client'

import { useState, useEffect } from 'react'
import { KnowledgeBase } from '@/components/vedic/KnowledgeBase'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BookOpen, Search, TrendingUp, Sparkles } from '@/components/icons'
import { apiClient } from '@/lib/api'

interface Rule {
  rule_id: string
  condition: string
  effect: string
  domain: string
  weight: number
  bphs_anchor?: string
  commentary?: string
}

interface KnowledgeStats {
  total_rules: number
  domains: string[]
  avg_weight: number
}

export default function KnowledgeBasePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDomain, setSelectedDomain] = useState('')
  const [rules, setRules] = useState<Rule[]>([])
  const [stats, setStats] = useState<KnowledgeStats | null>(null)
  const [domains, setDomains] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [searchLoading, setSearchLoading] = useState(false)

  // Load stats and domains on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [statsRes, domainsRes] = await Promise.all([
          apiClient.getKnowledgeStats(),
          apiClient.getDomains()
        ])
        setStats(statsRes.data)
        setDomains(domainsRes.data || [])
      } catch (err) {
        console.error('Failed to load knowledge base data:', err)
      }
    }
    loadData()
  }, [])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearchLoading(true)
    try {
      const response = await apiClient.retrieveRules({
        query: searchQuery,
        domains: selectedDomain ? [selectedDomain] : undefined,
        top_k: 20
      })
      setRules(response.data.rules || [])
    } catch (err) {
      console.error('Failed to search rules:', err)
    } finally {
      setSearchLoading(false)
    }
  }

  const handleDomainFilter = async (domain: string) => {
    setSelectedDomain(domain)
    if (!domain) {
      setRules([])
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.getRulesByDomain(domain, 30, 0.3)
      setRules(response.data || [])
    } catch (err) {
      console.error('Failed to load domain rules:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="w-8 h-8 text-jio-600" />
          <h1 className="text-3xl font-bold text-gray-900">Vedic Astrology Knowledge Base</h1>
        </div>
        <p className="text-gray-600">
          Learn about fundamental concepts and explore 120+ BPHS rules
        </p>
      </div>

      {/* Introduction Card */}
      <Card className="bg-gradient-to-r from-jio-50 to-blue-50 border-jio-200">
        <CardHeader>
          <CardTitle className="text-jio-900">Welcome to Vedic Wisdom</CardTitle>
          <CardDescription className="text-jio-700">
            Explore the ancient science of Jyotish (Vedic Astrology)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 leading-relaxed">
            Vedic astrology, also known as Jyotish (the science of light), is an ancient system
            of astrology that originated in India over 5,000 years ago. It provides insights into
            your personality, relationships, career, health, and spiritual path based on the precise
            positions of planets at your birth.
          </p>
          {stats && (
            <div className="mt-4 p-3 bg-white rounded-lg border border-jio-200">
              <p className="text-xs font-semibold text-jio-700 mb-2">Knowledge Base Stats:</p>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <p className="text-2xl font-bold text-jio-900">{stats.total_rules}</p>
                  <p className="text-xs text-gray-600">BPHS Rules</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-jio-900">{domains.length}</p>
                  <p className="text-xs text-gray-600">Domains</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-jio-900">{(stats.avg_weight * 100).toFixed(0)}%</p>
                  <p className="text-xs text-gray-600">Avg Weight</p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="basics" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="basics">Basics</TabsTrigger>
          <TabsTrigger value="rules">BPHS Rules</TabsTrigger>
          <TabsTrigger value="search">Rule Search</TabsTrigger>
        </TabsList>

        {/* Basics Tab */}
        <TabsContent value="basics" className="space-y-6">
          <KnowledgeBase />

          {/* How to Use */}
          <Card>
            <CardHeader>
              <CardTitle>How to Use Your Chart</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-sm text-gray-700">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">1. Start with the Basics</h4>
                  <p>
                    Learn about the 9 planets (Grahas) and their significations. Each planet represents
                    different aspects of life and personality.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">2. Understand the Houses</h4>
                  <p>
                    The 12 houses (Bhavas) represent different life areas from self to spirituality.
                    Planets placed in different houses influence those life areas.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">3. Look for Yogas</h4>
                  <p>
                    Yogas are special planetary combinations that create specific results in life.
                    They can indicate talents, challenges, or opportunities.
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">4. Check Your Dasha</h4>
                  <p>
                    Your current Dasha (planetary period) shows which planet's energy is most active
                    in your life right now and influences current life events.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* BPHS Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-jio-600" />
                Brihat Parashara Hora Shastra Rules
              </CardTitle>
              <CardDescription>
                Browse rules by domain from the classical text
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700">Select Domain:</label>
                <Select value={selectedDomain} onValueChange={handleDomainFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a domain to view rules" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Domains</SelectItem>
                    {domains.map((domain) => (
                      <SelectItem key={domain} value={domain}>
                        {domain.charAt(0).toUpperCase() + domain.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {loading ? (
                <div className="text-center py-8">
                  <div className="w-6 h-6 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                  <p className="text-sm text-gray-600">Loading rules...</p>
                </div>
              ) : rules.length > 0 ? (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {rules.map((rule, index) => (
                    <Card key={index} className="border-l-4 border-blue-500">
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between mb-2">
                          <p className="text-xs font-mono text-gray-600">Rule #{rule.rule_id}</p>
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-800 rounded">
                              {rule.domain}
                            </span>
                            <span className="text-xs font-medium px-2 py-0.5 bg-gray-100 rounded">
                              {(rule.weight * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        <p className="text-sm font-semibold text-gray-900 mb-1">
                          <span className="text-gray-600">If:</span> {rule.condition}
                        </p>
                        <p className="text-sm text-gray-700 mb-2">
                          <span className="text-gray-600 font-semibold">Then:</span> {rule.effect}
                        </p>
                        {rule.bphs_anchor && (
                          <p className="text-xs text-gray-500">
                            <BookOpen className="w-3 h-3 inline mr-1" />
                            BPHS: {rule.bphs_anchor}
                          </p>
                        )}
                        {rule.commentary && (
                          <p className="text-xs text-gray-600 mt-2 italic">{rule.commentary}</p>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : selectedDomain ? (
                <p className="text-center text-gray-500 py-8">
                  Select a domain to view rules
                </p>
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rule Search Tab */}
        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5 text-jio-600" />
                Search BPHS Rules
              </CardTitle>
              <CardDescription>
                Search through 120+ rules using semantic search (powered by embeddings)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="e.g., What indicates wealth in a chart?"
                  value={searchQuery}
                  onChange={(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button onClick={handleSearch} disabled={searchLoading || !searchQuery.trim()}>
                  {searchLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                </Button>
              </div>

              {rules.length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-3">
                    Found {rules.length} relevant rules
                  </p>
                  <div className="space-y-3 max-h-[600px] overflow-y-auto">
                    {rules.map((rule, index) => (
                      <Card key={index} className="border-l-4 border-purple-500">
                        <CardContent className="pt-4">
                          <div className="flex items-start justify-between mb-2">
                            <p className="text-xs font-mono text-gray-600">Rule #{rule.rule_id}</p>
                            <div className="flex items-center gap-2">
                              <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-800 rounded">
                                {rule.domain}
                              </span>
                              <span className="text-xs font-medium px-2 py-0.5 bg-gray-100 rounded">
                                {(rule.weight * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                          <p className="text-sm font-semibold text-gray-900 mb-1">
                            <span className="text-gray-600">Condition:</span> {rule.condition}
                          </p>
                          <p className="text-sm text-gray-700 mb-2">
                            <span className="text-gray-600 font-semibold">Effect:</span> {rule.effect}
                          </p>
                          {rule.bphs_anchor && (
                            <p className="text-xs text-gray-500">
                              <BookOpen className="w-3 h-3 inline mr-1" />
                              BPHS: {rule.bphs_anchor}
                            </p>
                          )}
                          {rule.commentary && (
                            <p className="text-xs text-gray-600 mt-2 italic">{rule.commentary}</p>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Attribution */}
      <Card className="border-jio-200 bg-jio-50">
        <CardContent className="py-4">
          <p className="text-xs text-gray-600 text-center">
            Based on classical Vedic astrology texts including Brihat Parashara Hora Shastra.
            Calculations powered by Swiss Ephemeris and Kerykeion libraries.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
