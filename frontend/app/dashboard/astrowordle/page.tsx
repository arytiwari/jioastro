'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  Brain,
  Flame,
  Trophy,
  Share2,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Sparkles
} from 'lucide-react'

interface Question {
  id: string
  question_text: string
  question_type: string
  difficulty: string
  hint?: string
  category?: string
  correct_answer?: string
  explanation?: string
}

interface Guess {
  guess: string
  is_correct: boolean
  feedback: string
  timestamp: string
}

interface Challenge {
  challenge_id: string
  challenge_number: number
  challenge_date: string
  question: Question
  user_attempt: any
  is_completed: boolean
  guesses_remaining: number
}

interface Stats {
  current_streak: number
  longest_streak: number
  total_games_played: number
  total_games_won: number
  win_percentage: number
  average_guesses: number
  wins_distribution: Record<number, number>
}

const FEEDBACK_COLORS = {
  correct: 'bg-green-500',
  very_close: 'bg-yellow-500',
  close: 'bg-orange-500',
  somewhat_close: 'bg-blue-500',
  wrong: 'bg-gray-300'
}

const FEEDBACK_EMOJIS = {
  correct: '🟢',
  very_close: '🟡',
  close: '🟠',
  somewhat_close: '🔵',
  wrong: '⬜'
}

export default function AstroWordlePage() {
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [guess, setGuess] = useState('')
  const [guesses, setGuesses] = useState<Guess[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [showResult, setShowResult] = useState(false)
  const [resultData, setResultData] = useState<any>(null)

  useEffect(() => {
    loadTodaysChallenge()
    loadStats()
  }, [])

  const loadTodaysChallenge = async () => {
    setLoading(true)
    try {
      const response = await apiClient.getAstroWordleToday()
      if (response && response.data && response.data.data) {
        const challengeData = response.data.data
        setChallenge(challengeData)
        if (challengeData.user_attempt && challengeData.user_attempt.guesses) {
          setGuesses(challengeData.user_attempt.guesses)
          if (challengeData.is_completed) {
            setShowResult(true)
            setResultData({
              is_correct: challengeData.user_attempt.is_correct,
              score: challengeData.user_attempt.score,
              num_guesses: challengeData.user_attempt.num_guesses
            })
          }
        }
      }
    } catch (error) {
      console.error('Error loading challenge:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await apiClient.getAstroWordleStats()
      if (response && response.data && response.data.data) {
        setStats(response.data.data)
      }
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const submitGuess = async () => {
    if (!guess.trim() || !challenge) return

    setSubmitting(true)
    try {
      const response = await apiClient.submitAstroWordleGuess(guess, challenge.challenge_id)

      if (response && response.data && response.data.data) {
        const guessData = response.data.data
        // Add new guess to list
        const newGuess: Guess = {
          guess: guess,
          is_correct: guessData.is_correct,
          feedback: guessData.feedback,
          timestamp: new Date().toISOString()
        }

        const updatedGuesses = [...guesses, newGuess]
        setGuesses(updatedGuesses)
        setGuess('')

        // Check if completed
        if (guessData.is_completed) {
          setShowResult(true)
          setResultData(guessData)
          // Reload stats
          loadStats()
        }
      }
    } catch (error) {
      console.error('Error submitting guess:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleShare = () => {
    if (!resultData || !challenge) return

    // Generate emoji grid
    const emojiGrid = guesses.map(g => FEEDBACK_EMOJIS[g.feedback as keyof typeof FEEDBACK_EMOJIS] || '⬜').join('')
    const result = resultData.is_correct ? `${guesses.length}/6` : 'X/6'

    const shareText = `AstroWordle #${challenge.challenge_number} ${result}

${emojiGrid}

Test your astrology knowledge!
jioastro.com/astrowordle`

    // Copy to clipboard
    if (navigator.clipboard) {
      navigator.clipboard.writeText(shareText)
      alert('Copied to clipboard! Share on social media.')
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (!challenge) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-muted-foreground">No challenge available today</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8 text-purple-500" />
            AstroWordle
          </h1>
          <p className="text-muted-foreground mt-1">
            Daily astrology quiz - Challenge #{challenge.challenge_number}
          </p>
        </div>
        <div className="flex items-center gap-4">
          {stats && (
            <>
              <div className="text-center">
                <div className="flex items-center gap-1">
                  <Flame className="h-4 w-4 text-orange-500" />
                  <span className="text-2xl font-bold">{stats.current_streak}</span>
                </div>
                <p className="text-xs text-muted-foreground">Streak</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.win_percentage}%</div>
                <p className="text-xs text-muted-foreground">Win Rate</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Question Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>{challenge?.question?.question_text || 'Loading question...'}</CardTitle>
            <Badge variant="outline">{challenge?.question?.difficulty || 'N/A'}</Badge>
          </div>
          <CardDescription>
            Category: {challenge?.question?.category || 'N/A'} • Type: {challenge?.question?.question_type || 'N/A'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Hint */}
          {challenge?.question?.hint && !showResult && (
            <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-md flex items-start gap-2">
              <AlertCircle className="h-4 w-4 text-blue-500 mt-0.5" />
              <p className="text-sm">{challenge?.question?.hint}</p>
            </div>
          )}

          {/* Guesses Display */}
          {guesses.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-semibold text-sm">Your Guesses:</h3>
              {guesses.map((g, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 p-3 rounded-md border"
                >
                  <div className="text-2xl">{FEEDBACK_EMOJIS[g.feedback as keyof typeof FEEDBACK_EMOJIS]}</div>
                  <div className="flex-1">
                    <p className="font-medium">{g.guess}</p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {g.feedback.replace('_', ' ')}
                    </p>
                  </div>
                  {g.is_correct && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                </div>
              ))}
            </div>
          )}

          {/* Input Area */}
          {!showResult && (
            <div className="space-y-3">
              <div className="flex gap-2">
                <Input
                  value={guess}
                  onChange={(e) => setGuess(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && submitGuess()}
                  placeholder="Enter your answer..."
                  disabled={submitting}
                  className="flex-1"
                />
                <Button
                  onClick={submitGuess}
                  disabled={!guess.trim() || submitting}
                >
                  {submitting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Submit'
                  )}
                </Button>
              </div>
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>Guesses: {guesses.length}/6</span>
                <span>{challenge.guesses_remaining} remaining</span>
              </div>
            </div>
          )}

          {/* Result Display */}
          {showResult && resultData && (
            <div className="space-y-4">
              <div className={`p-6 rounded-lg text-center ${resultData.is_correct ? 'bg-green-50 dark:bg-green-950' : 'bg-red-50 dark:bg-red-950'}`}>
                {resultData.is_correct ? (
                  <>
                    <Sparkles className="h-12 w-12 mx-auto mb-3 text-green-500" />
                    <h3 className="text-2xl font-bold mb-2">Correct!</h3>
                    <p className="text-lg mb-2">Score: {resultData.score}/100</p>
                    <p className="text-sm text-muted-foreground">
                      Solved in {resultData.num_guesses} guess{resultData.num_guesses !== 1 ? 'es' : ''}
                    </p>
                  </>
                ) : (
                  <>
                    <XCircle className="h-12 w-12 mx-auto mb-3 text-red-500" />
                    <h3 className="text-2xl font-bold mb-2">Better luck tomorrow!</h3>
                    <p className="text-sm text-muted-foreground">
                      The answer was: <strong>{challenge?.question?.correct_answer}</strong>
                    </p>
                  </>
                )}
              </div>

              {/* Explanation */}
              {challenge?.question?.explanation && (
                <div className="p-4 bg-muted rounded-md">
                  <h4 className="font-semibold mb-2">Explanation:</h4>
                  <p className="text-sm">{challenge?.question?.explanation}</p>
                </div>
              )}

              {/* Share Button */}
              <Button onClick={handleShare} className="w-full gap-2">
                <Share2 className="h-4 w-4" />
                Share Result
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats Summary */}
      {stats && stats.total_games_played > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5" />
              Your Statistics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.total_games_played}</div>
                <p className="text-xs text-muted-foreground">Games Played</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.total_games_won}</div>
                <p className="text-xs text-muted-foreground">Games Won</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.longest_streak}</div>
                <p className="text-xs text-muted-foreground">Best Streak</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.average_guesses}</div>
                <p className="text-xs text-muted-foreground">Avg Guesses</p>
              </div>
            </div>

            {/* Win Distribution */}
            <div className="mt-6 space-y-2">
              <h4 className="font-semibold text-sm">Guess Distribution:</h4>
              {Object.entries(stats.wins_distribution).map(([guesses, count]) => (
                <div key={guesses} className="flex items-center gap-2">
                  <span className="text-sm w-4">{guesses}</span>
                  <div className="flex-1">
                    <div
                      className="h-6 bg-primary rounded flex items-center justify-end pr-2"
                      style={{ width: `${(count / Math.max(...Object.values(stats.wins_distribution))) * 100}%` }}
                    >
                      <span className="text-xs text-white">{count}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
