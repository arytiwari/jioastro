"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Play, Clock, Star, Sparkles, Flame, Heart, Circle } from "lucide-react"
import api from "@/lib/api"

interface RitualStep {
  step_number: number
  title: string
  description: string
  duration_seconds: number
}

interface Ritual {
  id: string
  name: string
  category: string
  deity: string | null
  duration_minutes: number
  difficulty: string
  description: string | null
  required_items: string[]
  audio_enabled: boolean
  benefits: string[]
  best_time_of_day: string | null
  step_count: number
}

const CATEGORY_ICONS = {
  daily: <Circle className="h-4 w-4" />,
  special: <Star className="h-4 w-4" />,
  remedial: <Flame className="h-4 w-4" />,
  festival: <Sparkles className="h-4 w-4" />,
  meditation: <Heart className="h-4 w-4" />,
}

const DIFFICULTY_COLORS = {
  beginner: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  intermediate: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
  advanced: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
}

export default function RitualsPage() {
  const router = useRouter()
  const [rituals, setRituals] = useState<Ritual[]>([])
  const [filteredRituals, setFilteredRituals] = useState<Ritual[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("all")
  const [selectedDeity, setSelectedDeity] = useState<string>("all")

  // Fetch all rituals on mount
  useEffect(() => {
    fetchRituals()
  }, [])

  // Filter rituals when filters change
  useEffect(() => {
    filterRituals()
  }, [searchQuery, selectedCategory, selectedDifficulty, selectedDeity, rituals])

  const fetchRituals = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await api.get("/rituals", {
        params: { limit: 100 }
      })
      setRituals(response.data.rituals || [])
    } catch (err: any) {
      console.error("Failed to fetch rituals:", err)
      setError(err.response?.data?.detail || "Failed to load rituals")
    } finally {
      setLoading(false)
    }
  }

  const filterRituals = () => {
    let filtered = [...rituals]

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(query) ||
        r.description?.toLowerCase().includes(query) ||
        r.deity?.toLowerCase().includes(query)
      )
    }

    // Category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter(r => r.category === selectedCategory)
    }

    // Difficulty filter
    if (selectedDifficulty !== "all") {
      filtered = filtered.filter(r => r.difficulty === selectedDifficulty)
    }

    // Deity filter
    if (selectedDeity !== "all") {
      filtered = filtered.filter(r => r.deity === selectedDeity)
    }

    setFilteredRituals(filtered)
  }

  const getUniqueDeities = () => {
    const deities = new Set<string>()
    rituals.forEach(r => {
      if (r.deity) deities.add(r.deity)
    })
    return Array.from(deities).sort()
  }

  const getCategoryCount = (category: string) => {
    return rituals.filter(r => r.category === category).length
  }

  const startRitual = (ritualId: string) => {
    router.push(`/dashboard/rituals/${ritualId}/player`)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading sacred rituals...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
          </CardContent>
          <CardFooter>
            <Button onClick={fetchRituals}>Retry</Button>
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Guided Rituals</h1>
        <p className="text-muted-foreground">
          Step-by-step voice-guided Vedic rituals for spiritual practice
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search rituals by name, deity, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
            <SelectTrigger>
              <SelectValue placeholder="Difficulty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Difficulties</SelectItem>
              <SelectItem value="beginner">Beginner</SelectItem>
              <SelectItem value="intermediate">Intermediate</SelectItem>
              <SelectItem value="advanced">Advanced</SelectItem>
            </SelectContent>
          </Select>

          <Select value={selectedDeity} onValueChange={setSelectedDeity}>
            <SelectTrigger>
              <SelectValue placeholder="Deity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Deities</SelectItem>
              {getUniqueDeities().map(deity => (
                <SelectItem key={deity} value={deity}>{deity}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            onClick={() => {
              setSearchQuery("")
              setSelectedCategory("all")
              setSelectedDifficulty("all")
              setSelectedDeity("all")
            }}
          >
            Clear Filters
          </Button>
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-8">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="all">
            All ({rituals.length})
          </TabsTrigger>
          <TabsTrigger value="daily">
            Daily ({getCategoryCount("daily")})
          </TabsTrigger>
          <TabsTrigger value="special">
            Special ({getCategoryCount("special")})
          </TabsTrigger>
          <TabsTrigger value="remedial">
            Remedial ({getCategoryCount("remedial")})
          </TabsTrigger>
          <TabsTrigger value="festival">
            Festival ({getCategoryCount("festival")})
          </TabsTrigger>
          <TabsTrigger value="meditation">
            Meditation ({getCategoryCount("meditation")})
          </TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Results Count */}
      <div className="mb-4">
        <p className="text-sm text-muted-foreground">
          Showing {filteredRituals.length} ritual{filteredRituals.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Ritual Cards Grid */}
      {filteredRituals.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">No rituals found matching your filters</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRituals.map((ritual) => (
            <Card key={ritual.id} className="flex flex-col hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {CATEGORY_ICONS[ritual.category as keyof typeof CATEGORY_ICONS]}
                    <span className="text-xs text-muted-foreground capitalize">
                      {ritual.category}
                    </span>
                  </div>
                  {ritual.audio_enabled && (
                    <Badge variant="secondary" className="text-xs">
                      🎙️ Voice
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-xl line-clamp-2">{ritual.name}</CardTitle>
                {ritual.deity && (
                  <CardDescription className="font-medium">
                    Deity: {ritual.deity}
                  </CardDescription>
                )}
              </CardHeader>

              <CardContent className="flex-grow space-y-4">
                {/* Description */}
                {ritual.description && (
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {ritual.description}
                  </p>
                )}

                {/* Difficulty & Duration */}
                <div className="flex items-center gap-4 text-sm">
                  <Badge className={DIFFICULTY_COLORS[ritual.difficulty as keyof typeof DIFFICULTY_COLORS]}>
                    {ritual.difficulty}
                  </Badge>
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>{ritual.duration_minutes} min</span>
                  </div>
                  <div className="text-muted-foreground">
                    {ritual.step_count} steps
                  </div>
                </div>

                {/* Best Time */}
                {ritual.best_time_of_day && (
                  <p className="text-xs text-muted-foreground">
                    ⏰ Best: {ritual.best_time_of_day}
                  </p>
                )}

                {/* Benefits */}
                {ritual.benefits && ritual.benefits.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold mb-1">Benefits:</p>
                    <ul className="text-xs text-muted-foreground space-y-0.5">
                      {ritual.benefits.slice(0, 3).map((benefit, idx) => (
                        <li key={idx} className="line-clamp-1">• {benefit}</li>
                      ))}
                      {ritual.benefits.length > 3 && (
                        <li>• +{ritual.benefits.length - 3} more...</li>
                      )}
                    </ul>
                  </div>
                )}

                {/* Required Items Preview */}
                {ritual.required_items && ritual.required_items.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold mb-1">Required Items:</p>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {ritual.required_items.slice(0, 4).join(", ")}
                      {ritual.required_items.length > 4 && ` +${ritual.required_items.length - 4} more`}
                    </p>
                  </div>
                )}
              </CardContent>

              <CardFooter className="pt-0">
                <Button
                  onClick={() => startRitual(ritual.id)}
                  className="w-full gap-2"
                >
                  <Play className="h-4 w-4" />
                  Start Ritual
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
