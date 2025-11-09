'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Sparkles, Star, Calendar, History, User, BookOpen } from 'lucide-react'

export default function TarotPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('daily')
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(null)
  const [selectedSpreadId, setSelectedSpreadId] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [selectedReading, setSelectedReading] = useState<string | null>(null)

  // Fetch user profiles for holistic analysis
  const { data: profilesData } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Fetch tarot spreads
  const { data: spreadsData } = useQuery({
    queryKey: ['tarot-spreads'],
    queryFn: async () => {
      const response = await apiClient.getTarotSpreads()
      return response.data
    },
  })

  // Fetch user's readings
  const { data: readingsData, isLoading: isLoadingReadings } = useQuery({
    queryKey: ['tarot-readings'],
    queryFn: async () => {
      const response = await apiClient.getTarotReadings({ limit: 20 })
      return response.data
    },
  })

  // Daily card mutation
  const dailyCardMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.drawDailyCard()
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['tarot-readings'])
    },
  })

  // Create reading mutation
  const createReadingMutation = useMutation({
    mutationFn: async (data: {
      spread_id?: string
      spread_name: string
      reading_type: string
      question?: string
      profile_id?: string
      num_cards?: number
    }) => {
      const response = await apiClient.createTarotReading(data)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['tarot-readings'])
      setSelectedReading(data.id)
      setActiveTab('readings')
    },
  })

  const handleDrawDailyCard = () => {
    dailyCardMutation.mutate()
  }

  const handleCreateReading = () => {
    if (!selectedSpreadId) return

    const spread = spreadsData?.spreads?.find((s: any) => s.id === selectedSpreadId)
    if (!spread) return

    createReadingMutation.mutate({
      spread_id: selectedSpreadId,
      spread_name: spread.name,
      reading_type: spread.name.toLowerCase().replace(/\s+/g, '_'),
      question: question || undefined,
      profile_id: selectedProfileId || undefined,
      num_cards: spread.num_cards,
    })
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Sparkles className="h-8 w-8 text-purple-600" />
          <h1 className="text-4xl font-bold">Tarot Reading</h1>
        </div>
        <p className="text-muted-foreground text-lg">
          Unlock insights with AI-powered tarot readings and ancient wisdom
        </p>
      </div>

      {/* Profile Selector for Holistic Analysis */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <User className="h-5 w-5" />
            Holistic Analysis (Optional)
          </CardTitle>
          <CardDescription>
            Link to your birth profile for cross-domain insights combining Astrology, Numerology, and Tarot
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="profile-select">Select Birth Profile</Label>
            <Select
              value={selectedProfileId || 'none'}
              onValueChange={(value) => setSelectedProfileId(value === 'none' ? null : value)}
            >
              <SelectTrigger id="profile-select">
                <SelectValue placeholder="No profile (basic reading only)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">No profile (basic reading only)</SelectItem>
                {profilesData?.map((profile: any) => (
                  <SelectItem key={profile.id} value={profile.id}>
                    {profile.name} - {new Date(profile.birth_date).toLocaleDateString()}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedProfileId && (
              <p className="text-sm text-purple-600">
                ✨ Holistic analysis enabled - your reading will include astrological and numerological correlations
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto">
          <TabsTrigger value="daily" className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span className="hidden sm:inline">Daily Card</span>
          </TabsTrigger>
          <TabsTrigger value="reading" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            <span className="hidden sm:inline">New Reading</span>
          </TabsTrigger>
          <TabsTrigger value="readings" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            <span className="hidden sm:inline">History</span>
            {readingsData?.total_count > 0 && (
              <Badge variant="secondary" className="ml-1">
                {readingsData.total_count}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Daily Card Tab */}
        <TabsContent value="daily" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Daily Card</CardTitle>
              <CardDescription>
                Draw a single card to provide guidance and insight for the day ahead
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center space-y-4">
                {dailyCardMutation.isPending ? (
                  <div className="flex flex-col items-center py-12 space-y-4">
                    <Sparkles className="h-12 w-12 text-purple-600 animate-pulse" />
                    <p className="text-muted-foreground">Drawing your daily card...</p>
                  </div>
                ) : dailyCardMutation.data ? (
                  <div className="w-full max-w-md space-y-4">
                    <div className="text-center p-6 border-2 border-purple-200 rounded-lg bg-purple-50">
                      <h3 className="text-2xl font-bold mb-2">
                        {dailyCardMutation.data.card.name}
                      </h3>
                      <Badge variant={dailyCardMutation.data.is_reversed ? 'destructive' : 'default'}>
                        {dailyCardMutation.data.is_reversed ? 'Reversed' : 'Upright'}
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-4">
                        {dailyCardMutation.data.guidance}
                      </p>
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-semibold">Keywords:</h4>
                      <div className="flex flex-wrap gap-2">
                        {dailyCardMutation.data.keywords?.map((keyword: string, idx: number) => (
                          <Badge key={idx} variant="outline">{keyword}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <Button
                    onClick={handleDrawDailyCard}
                    size="lg"
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    <Sparkles className="h-5 w-5 mr-2" />
                    Draw Daily Card
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* New Reading Tab */}
        <TabsContent value="reading" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Create New Reading</CardTitle>
              <CardDescription>
                Choose a spread and ask your question to receive guidance
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="spread-select">Select Spread</Label>
                <Select value={selectedSpreadId || ''} onValueChange={setSelectedSpreadId}>
                  <SelectTrigger id="spread-select">
                    <SelectValue placeholder="Choose a tarot spread" />
                  </SelectTrigger>
                  <SelectContent>
                    {spreadsData?.spreads?.map((spread: any) => (
                      <SelectItem key={spread.id} value={spread.id}>
                        {spread.name} ({spread.num_cards} cards) - {spread.difficulty_level}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedSpreadId && spreadsData?.spreads && (
                  <p className="text-sm text-muted-foreground">
                    {spreadsData.spreads.find((s: any) => s.id === selectedSpreadId)?.description}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="question">Your Question (Optional)</Label>
                <Textarea
                  id="question"
                  placeholder="What would you like guidance on?"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  rows={3}
                />
              </div>

              <Button
                onClick={handleCreateReading}
                disabled={!selectedSpreadId || createReadingMutation.isPending}
                className="w-full bg-purple-600 hover:bg-purple-700"
                size="lg"
              >
                {createReadingMutation.isPending ? (
                  <>
                    <Sparkles className="h-5 w-5 mr-2 animate-pulse" />
                    Drawing Cards...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Draw Cards
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Readings History Tab */}
        <TabsContent value="readings" className="space-y-6">
          {selectedReading ? (
            <div>
              <Button
                variant="outline"
                onClick={() => setSelectedReading(null)}
                className="mb-4"
              >
                ← Back to Readings List
              </Button>
              <ReadingDetail readingId={selectedReading} />
            </div>
          ) : (
            <ReadingsList
              readings={readingsData?.readings || []}
              isLoading={isLoadingReadings}
              onReadingClick={setSelectedReading}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Simple ReadingsList component
function ReadingsList({
  readings,
  isLoading,
  onReadingClick
}: {
  readings: any[]
  isLoading: boolean
  onReadingClick: (id: string) => void
}) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Sparkles className="h-12 w-12 mx-auto text-purple-600 animate-pulse mb-4" />
          <p className="text-muted-foreground">Loading your readings...</p>
        </CardContent>
      </Card>
    )
  }

  if (!readings || readings.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No readings yet. Draw your first card!</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {readings.map((reading: any) => (
        <Card
          key={reading.id}
          className="cursor-pointer hover:border-purple-300 transition-colors"
          onClick={() => onReadingClick(reading.id)}
        >
          <CardHeader>
            <CardTitle className="text-lg flex items-center justify-between">
              {reading.spread_name}
              {reading.is_favorite && <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />}
            </CardTitle>
            <CardDescription>
              {reading.question || 'General guidance'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{reading.num_cards} cards</span>
              <span>{new Date(reading.created_at).toLocaleDateString()}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// Simple ReadingDetail component
function ReadingDetail({ readingId }: { readingId: string }) {
  const { data: reading, isLoading } = useQuery({
    queryKey: ['tarot-reading', readingId],
    queryFn: async () => {
      const response = await apiClient.getTarotReading(readingId)
      return response.data
    },
  })

  if (isLoading || !reading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Sparkles className="h-12 w-12 mx-auto text-purple-600 animate-pulse mb-4" />
          <p className="text-muted-foreground">Loading reading...</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{reading.spread_name}</CardTitle>
          {reading.question && (
            <CardDescription className="text-base">
              Question: {reading.question}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Cards Drawn */}
          <div>
            <h3 className="font-semibold mb-4">Cards Drawn:</h3>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {reading.cards_drawn?.map((card: any, idx: number) => (
                <div key={idx} className="border rounded-lg p-4">
                  <p className="text-sm font-medium text-purple-600">{card.position_name}</p>
                  <p className="text-lg font-bold mt-1">{card.card_name}</p>
                  <Badge variant={card.is_reversed ? 'destructive' : 'default'} className="mt-2">
                    {card.is_reversed ? 'Reversed' : 'Upright'}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Interpretation */}
          {reading.interpretation && (
            <div>
              <h3 className="font-semibold mb-2">Interpretation:</h3>
              <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                {reading.interpretation}
              </div>
            </div>
          )}

          {/* Holistic Correlations */}
          {reading.astrology_correlations && (
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-purple-600" />
                Astrological Insights
              </h3>
              <p className="text-sm">{reading.astrology_correlations.correlation_notes}</p>
            </div>
          )}

          {reading.numerology_correlations && (
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-purple-600" />
                Numerological Insights
              </h3>
              <p className="text-sm">{reading.numerology_correlations.correlation_notes}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
