'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, User, MessageSquare, Star } from 'lucide-react'

export default function DashboardPage() {
  const { data: profiles, isLoading: profilesLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  const { data: queries, isLoading: queriesLoading } = useQuery({
    queryKey: ['recent-queries'],
    queryFn: async () => {
      const response = await apiClient.getQueries(5, 0)
      return response.data
    },
  })

  const { data: feedbackStats } = useQuery({
    queryKey: ['feedback-stats'],
    queryFn: async () => {
      const response = await apiClient.getFeedbackStats()
      return response.data
    },
  })

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome to Your Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Explore your astrological insights and ask questions about your life path
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Birth Profiles</CardTitle>
            <User className="w-4 h-4 text-jio-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{profiles?.length || 0}</div>
            <p className="text-xs text-gray-600 mt-1">
              {profiles?.length === 0 ? 'Create your first profile' : 'Active profiles'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Questions Asked</CardTitle>
            <MessageSquare className="w-4 h-4 text-jio-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{queries?.length || 0}</div>
            <p className="text-xs text-gray-600 mt-1">AI-powered insights</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            <Star className="w-4 h-4 text-jio-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {feedbackStats?.average_rating
                ? `${feedbackStats.average_rating} ⭐`
                : 'N/A'}
            </div>
            <p className="text-xs text-gray-600 mt-1">Your feedback</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profiles Section */}
        <Card>
          <CardHeader>
            <CardTitle>Birth Profiles</CardTitle>
            <CardDescription>Manage your birth charts and astrological data</CardDescription>
          </CardHeader>
          <CardContent>
            {profilesLoading ? (
              <div className="text-center py-8">
                <div className="w-6 h-6 border-3 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            ) : profiles && profiles.length > 0 ? (
              <div className="space-y-3">
                {profiles.slice(0, 3).map((profile: any) => (
                  <div key={profile.id} className="p-3 border rounded-lg hover:border-jio-300 transition-colors">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="font-semibold">{profile.name}</p>
                        <p className="text-xs text-gray-600">
                          {new Date(profile.birth_date).toLocaleDateString()}
                        </p>
                      </div>
                      {profile.is_primary && (
                        <span className="text-xs bg-jio-100 text-jio-700 px-2 py-1 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Link href={`/dashboard/chart/${profile.id}`} className="flex-1">
                        <Button variant="default" size="sm" className="w-full">
                          Enhanced Chart
                        </Button>
                      </Link>
                      <Link href={`/dashboard/profiles/${profile.id}`} className="flex-1">
                        <Button variant="outline" size="sm" className="w-full">
                          Basic Profile
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
                {profiles.length > 3 && (
                  <Link href="/dashboard/profiles">
                    <Button variant="ghost" className="w-full text-sm">
                      View all {profiles.length} profiles →
                    </Button>
                  </Link>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">No profiles yet</p>
                <Link href="/dashboard/profiles/new">
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Your First Profile
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Questions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Questions</CardTitle>
            <CardDescription>Your latest astrological insights</CardDescription>
          </CardHeader>
          <CardContent>
            {queriesLoading ? (
              <div className="text-center py-8">
                <div className="w-6 h-6 border-3 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              </div>
            ) : queries && queries.length > 0 ? (
              <div className="space-y-3">
                {queries.slice(0, 3).map((item: any, index: number) => {
                  const query = item?.query ?? item

                  if (!query) {
                    return null
                  }

                  const createdAt = query.created_at ?? item?.created_at
                  const key = query.id ?? item?.id ?? `query-${index}`

                  return (
                    <div key={key} className="p-3 border rounded-lg">
                      <p className="text-sm font-medium line-clamp-2">
                        {query.question ?? 'Question unavailable'}
                      </p>
                      {createdAt && (
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(createdAt).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  )
                })}
                <Link href="/dashboard/history">
                  <Button variant="ghost" className="w-full text-sm">
                    View all history →
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">No questions yet</p>
                <Link href="/dashboard/ask">
                  <Button>
                    <MessageSquare className="w-4 h-4 mr-2" />
                    Ask Your First Question
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Getting Started Guide (shown if no profiles) */}
      {!profilesLoading && (!profiles || profiles.length === 0) && (
        <Card className="bg-gradient-to-r from-jio-50 to-blue-50 border-jio-200">
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>Follow these steps to begin your astrological journey</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-4">
              <li className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-jio-600 text-white flex items-center justify-center text-sm font-bold">
                  1
                </div>
                <div>
                  <p className="font-semibold">Create Your Birth Profile</p>
                  <p className="text-sm text-gray-600">
                    Enter your birth date, time, and location to generate your Vedic birth chart
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-jio-600 text-white flex items-center justify-center text-sm font-bold">
                  2
                </div>
                <div>
                  <p className="font-semibold">View Your Charts</p>
                  <p className="text-sm text-gray-600">
                    Choose <strong>Enhanced Chart</strong> for North/South/Western styles with yogas and dasha timeline, or <strong>Basic Profile</strong> for standard view
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-jio-600 text-white flex items-center justify-center text-sm font-bold">
                  3
                </div>
                <div>
                  <p className="font-semibold">Ask Questions</p>
                  <p className="text-sm text-gray-600">
                    Get AI-powered insights about career, relationships, health, and more
                  </p>
                </div>
              </li>
            </ol>
            <div className="mt-6">
              <Link href="/dashboard/profiles/new">
                <Button size="lg" className="w-full md:w-auto">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Profile
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
