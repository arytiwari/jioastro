'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Sparkles, Briefcase, Heart, Activity, TrendingUp, Home, BookOpen } from '@/components/icons'

const CATEGORIES = [
  { id: 'career', label: 'Career & Work', icon: Briefcase, color: 'text-blue-600' },
  { id: 'relationship', label: 'Love & Relationships', icon: Heart, color: 'text-pink-600' },
  { id: 'health', label: 'Health & Wellness', icon: Activity, color: 'text-green-600' },
  { id: 'finance', label: 'Finance & Wealth', icon: TrendingUp, color: 'text-yellow-600' },
  { id: 'family', label: 'Family & Home', icon: Home, color: 'text-jio-600' },
  { id: 'spiritual', label: 'Spiritual Growth', icon: BookOpen, color: 'text-indigo-600' },
]

export default function AskQuestionPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [question, setQuestion] = useState('')
  const [category, setCategory] = useState('')
  const [selectedProfile, setSelectedProfile] = useState('')

  // Fetch profiles
  const { data: profiles, isLoading: profilesLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Create query mutation
  const createQueryMutation = useMutation({
    mutationFn: async (data: { profile_id: string; question: string; category?: string }) => {
      const response = await apiClient.createQuery(data)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['queries'])
      queryClient.invalidateQueries(['recent-queries'])
      // Redirect to history page to see the response
      router.push(`/dashboard/history`)
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedProfile) {
      alert('Please select a birth profile')
      return
    }

    if (!question.trim()) {
      alert('Please enter a question')
      return
    }

    createQueryMutation.mutate({
      profile_id: selectedProfile,
      question: question.trim(),
      category: category || undefined,
    })
  }

  const handleQuickQuestion = (quickQ: string, cat: string) => {
    setQuestion(quickQ)
    setCategory(cat)
  }

  if (profilesLoading) {
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    )
  }

  if (!profiles || profiles.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <Sparkles className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Profiles Yet</h3>
          <p className="text-gray-600 mb-6">
            You need to create a birth profile before asking questions
          </p>
          <Button onClick={() => router.push('/dashboard/profiles/new')}>
            Create Your First Profile
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Ask a Question</h1>
        <p className="text-gray-600 mt-2">
          Get personalized AI-powered insights based on your birth chart
        </p>
      </div>

      {/* Quick Category Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Choose a Topic</CardTitle>
          <CardDescription>Select a category or scroll down to ask a custom question</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {CATEGORIES.map((cat) => {
              const Icon = cat.icon
              return (
                <button
                  key={cat.id}
                  onClick={() => setCategory(cat.id)}
                  className={`p-4 border rounded-lg text-left hover:border-jio-300 hover:bg-jio-50 transition-colors ${
                    category === cat.id ? 'border-jio-500 bg-jio-50' : ''
                  }`}
                >
                  <Icon className={`w-5 h-5 ${cat.color} mb-2`} />
                  <p className="text-sm font-semibold">{cat.label}</p>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Question Form */}
      <Card>
        <CardHeader>
          <CardTitle>Your Question</CardTitle>
          <CardDescription>Be specific for better insights (10 queries per day limit)</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {createQueryMutation.error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
                {(createQueryMutation.error as any)?.response?.data?.detail || 'Failed to submit question'}
              </div>
            )}

            {/* Profile Selection */}
            <div className="space-y-2">
              <Label htmlFor="profile">Birth Profile</Label>
              <Select value={selectedProfile} onValueChange={setSelectedProfile} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select a profile" />
                </SelectTrigger>
                <SelectContent>
                  {profiles.map((profile: any) => (
                    <SelectItem key={profile.id} value={profile.id}>
                      {profile.name} {profile.is_primary && '(Primary)'}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Question Input */}
            <div className="space-y-2">
              <Label htmlFor="question">Your Question</Label>
              <Textarea
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Example: What career path is most suitable for me based on my chart?"
                rows={5}
                required
                disabled={createQueryMutation.isPending}
              />
              <p className="text-xs text-gray-500">
                Minimum 10 characters, maximum 1000 characters
              </p>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={createQueryMutation.isPending || !selectedProfile || question.length < 10}
            >
              {createQueryMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Getting your insights...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 mr-2" />
                  Get AI Insights
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Sample Questions */}
      {category && (
        <Card className="bg-gradient-to-r from-jio-50 to-blue-50">
          <CardHeader>
            <CardTitle>Sample Questions for {CATEGORIES.find(c => c.id === category)?.label}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {category === 'career' && (
                <>
                  <button
                    onClick={() => handleQuickQuestion('What career path is most suitable for me based on my planetary positions?', 'career')}
                    className="text-left text-sm text-jio-700 hover:underline block"
                  >
                    • What career path is most suitable for me?
                  </button>
                  <button
                    onClick={() => handleQuickQuestion('When is the best time for a career change or job switch?', 'career')}
                    className="text-left text-sm text-jio-700 hover:underline block"
                  >
                    • When is the best time for a career change?
                  </button>
                </>
              )}
              {category === 'relationship' && (
                <>
                  <button
                    onClick={() => handleQuickQuestion('What does my chart reveal about my romantic relationships and marriage prospects?', 'relationship')}
                    className="text-left text-sm text-jio-700 hover:underline block"
                  >
                    • What does my chart reveal about marriage prospects?
                  </button>
                  <button
                    onClick={() => handleQuickQuestion('How can I improve my relationships based on my birth chart?', 'relationship')}
                    className="text-left text-sm text-jio-700 hover:underline block"
                  >
                    • How can I improve my relationships?
                  </button>
                </>
              )}
              {category === 'health' && (
                <>
                  <button
                    onClick={() => handleQuickQuestion('What health areas should I pay special attention to based on my chart?', 'health')}
                    className="text-left text-sm text-jio-700 hover:underline block"
                  >
                    • What health areas should I focus on?
                  </button>
                </>
              )}
              {/* Add more categories as needed */}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-gray-700">
          <strong>Note:</strong> AI interpretations are based on your birth chart but should be used as guidance, not absolute predictions. For serious life decisions, consult with a qualified astrologer.
        </p>
      </div>
    </div>
  )
}
