'use client'

import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Trophy, Medal, Crown, Users, TrendingUp, Loader2 } from 'lucide-react'

interface LeaderboardEntry {
  user_id: string
  current_streak?: number
  longest_streak?: number
  total_games_played?: number
  total_games_won?: number
  total_score?: number
  rank?: number
}

export default function LeaderboardPage() {
  const [activeTab, setActiveTab] = useState('all_time')
  const [globalLeaderboard, setGlobalLeaderboard] = useState<LeaderboardEntry[]>([])
  const [friendsLeaderboard, setFriendsLeaderboard] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [userRank, setUserRank] = useState<number | null>(null)

  useEffect(() => {
    loadLeaderboards()
  }, [activeTab])

  const loadLeaderboards = async () => {
    setLoading(true)
    try {
      // Load global leaderboard
      const globalResponse = await apiClient.getAstroWordleLeaderboard(activeTab, 100)
      if (globalResponse && globalResponse.data) {
        setGlobalLeaderboard(globalResponse.data.entries || [])
        setUserRank(globalResponse.data.user_rank)
      }

      // Load friends leaderboard
      const friendsResponse = await apiClient.getAstroWordleFriendsLeaderboard()
      if (friendsResponse && friendsResponse.data) {
        setFriendsLeaderboard(friendsResponse.data.entries || [])
      }
    } catch (error) {
      console.error('Error loading leaderboards:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="h-5 w-5 text-yellow-500" />
      case 2:
        return <Medal className="h-5 w-5 text-gray-400" />
      case 3:
        return <Medal className="h-5 w-5 text-orange-600" />
      default:
        return <span className="text-sm text-muted-foreground">#{rank}</span>
    }
  }

  const getRankBadgeColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 2:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
      case 3:
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
      default:
        return 'bg-muted'
    }
  }

  const LeaderboardTable = ({ entries, showScore = false }: { entries: LeaderboardEntry[], showScore?: boolean }) => {
    if (entries.length === 0) {
      return (
        <div className="text-center py-8 text-muted-foreground">
          <Users className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>No entries yet. Be the first!</p>
        </div>
      )
    }

    return (
      <div className="space-y-2">
        {entries.map((entry, idx) => {
          const rank = entry.rank || idx + 1
          const isTopThree = rank <= 3

          return (
            <div
              key={entry.user_id}
              className={`flex items-center gap-4 p-4 rounded-lg border transition-colors ${
                isTopThree ? getRankBadgeColor(rank) + ' border-2' : 'bg-card hover:bg-accent'
              }`}
            >
              {/* Rank */}
              <div className="flex items-center justify-center w-12">
                {getRankIcon(rank)}
              </div>

              {/* User Info */}
              <div className="flex-1 min-w-0">
                <p className="font-semibold truncate">
                  User {entry.user_id.substring(0, 8)}
                </p>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  {showScore ? (
                    <>
                      <span>{entry.total_score || 0} pts</span>
                      <span>•</span>
                      <span>{entry.total_games_won || 0} wins</span>
                    </>
                  ) : (
                    <>
                      <span>{entry.total_games_won || 0} wins</span>
                      <span>•</span>
                      <span>{entry.total_games_played || 0} played</span>
                    </>
                  )}
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center gap-6">
                {entry.current_streak !== undefined && (
                  <div className="text-center">
                    <div className="text-lg font-bold">{entry.current_streak}</div>
                    <p className="text-xs text-muted-foreground">Streak</p>
                  </div>
                )}
                {entry.longest_streak !== undefined && (
                  <div className="text-center">
                    <div className="text-lg font-bold text-primary">{entry.longest_streak}</div>
                    <p className="text-xs text-muted-foreground">Best</p>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Trophy className="h-8 w-8 text-yellow-500" />
            Leaderboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Top AstroWordle players
          </p>
        </div>
        {userRank && (
          <Badge variant="outline" className="text-lg px-4 py-2">
            Your Rank: #{userRank}
          </Badge>
        )}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all_time">All Time</TabsTrigger>
          <TabsTrigger value="monthly">Monthly</TabsTrigger>
          <TabsTrigger value="weekly">Weekly</TabsTrigger>
          <TabsTrigger value="daily">Daily</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-6">
          {/* Global Leaderboard */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Global Rankings
              </CardTitle>
              <CardDescription>
                Top 100 players {activeTab.replace('_', ' ')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <LeaderboardTable entries={globalLeaderboard} showScore={activeTab !== 'all_time'} />
              )}
            </CardContent>
          </Card>

          {/* Friends Leaderboard */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Friends Rankings
              </CardTitle>
              <CardDescription>
                Compare with your friends
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <LeaderboardTable entries={friendsLeaderboard} />
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
