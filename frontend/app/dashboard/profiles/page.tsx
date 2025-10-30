'use client'

import { useQuery } from '@/lib/query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Calendar, MapPin, Star } from 'lucide-react'
import { formatDate, formatTime } from '@/lib/utils'

export default function ProfilesPage() {
  const { data: profiles, isLoading } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Loading profiles...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Birth Profiles</h1>
          <p className="text-gray-600 mt-2">Manage your astrological birth data</p>
        </div>
        <Link href="/dashboard/profiles/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Profile
          </Button>
        </Link>
      </div>

      {!profiles || profiles.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <div className="mb-4">
              <Star className="w-12 h-12 text-gray-400 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Profiles Yet</h3>
            <p className="text-gray-600 mb-6">
              Create your first birth profile to generate your Vedic birth chart
            </p>
            <Link href="/dashboard/profiles/new">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Your First Profile
              </Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {profiles.map((profile: any) => (
            <Link key={profile.id} href={`/dashboard/profiles/${profile.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-xl">{profile.name}</CardTitle>
                    {profile.is_primary && (
                      <span className="text-xs bg-jio-100 text-jio-700 px-2 py-1 rounded font-semibold">
                        Primary
                      </span>
                    )}
                  </div>
                  <CardDescription className="flex items-center gap-1 mt-2">
                    <Calendar className="w-3 h-3" />
                    {formatDate(profile.birth_date)} at {formatTime(profile.birth_time)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    {profile.birth_city && (
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        <span>{profile.birth_city}</span>
                      </div>
                    )}
                    <div className="text-xs text-gray-500">
                      {profile.birth_lat.toFixed(2)}°, {profile.birth_lon.toFixed(2)}°
                    </div>
                  </div>
                  <div className="mt-4 space-y-2">
                    <Link href={`/dashboard/chart/${profile.id}`} onClick={(e) => e.stopPropagation()}>
                      <Button variant="default" className="w-full">
                        View Enhanced Chart
                      </Button>
                    </Link>
                    <Link href={`/dashboard/profiles/${profile.id}`} onClick={(e) => e.stopPropagation()}>
                      <Button variant="outline" className="w-full text-xs">
                        View Standard Chart
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
