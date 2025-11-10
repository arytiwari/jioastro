'use client'

import { useQuery } from '@/lib/query'
import Link from 'next/link'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Calendar, MapPin, Star, Edit } from '@/components/icons'
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
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-9 w-64 mb-2" />
            <Skeleton className="h-5 w-80" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32 mb-2" />
                <Skeleton className="h-4 w-48" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-10 w-full mt-4" />
              </CardContent>
            </Card>
          ))}
        </div>
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
            <Card key={profile.id} className="h-full">
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
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    <span>{profile.city?.display_name || profile.birth_city || 'Unknown'}</span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {profile.birth_lat.toFixed(2)}°, {profile.birth_lon.toFixed(2)}°
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-2">
                  <Link href={`/dashboard/chart/${profile.id}`} className="w-full">
                    <Button variant="default" size="sm" className="w-full">
                      View Chart
                    </Button>
                  </Link>
                  <Link href={`/dashboard/profiles/${profile.id}/edit`} className="w-full">
                    <Button variant="outline" size="sm" className="w-full">
                      <Edit className="w-3 h-3 mr-1" />
                      Edit
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
