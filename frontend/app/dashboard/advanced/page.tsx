"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Loader2, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getSession } from '@/lib/supabase'
import axios from 'axios'

// Import components
import JaiminiAnalysis from '@/components/advanced/JaiminiAnalysis'
import LalKitabAnalysis from '@/components/advanced/LalKitabAnalysis'
import AshtakavargaAnalysis from '@/components/advanced/AshtakavargaAnalysis'

interface Profile {
  id: string
  name: string
  date_of_birth: string
  birth_time: string
  birth_city: string
}

export default function AdvancedSystemsPage() {
  const router = useRouter()

  const [profiles, setProfiles] = useState<Profile[]>([])
  const [selectedProfile, setSelectedProfile] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('jaimini')

  // Fetch profiles on mount
  useEffect(() => {
    fetchProfiles()
  }, [])

  const fetchProfiles = async () => {
    try {
      setLoading(true)
      const session = getSession()

      if (!session) {
        router.push('/auth/login')
        return
      }

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/profiles`,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`
          }
        }
      )

      setProfiles(response.data || [])
      if (response.data && response.data.length > 0) {
        setSelectedProfile(response.data[0].id)
      }
    } catch (err: any) {
      console.error('Error fetching profiles:', err)
      setError(err.message || 'Failed to load profiles')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  if (profiles.length === 0) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>No Profiles Found</CardTitle>
            <CardDescription>
              Create a birth profile first to access advanced astrological systems.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => router.push('/dashboard/profiles')}>
              Create Profile
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Astrological Systems</h1>
          <p className="text-muted-foreground mt-2">
            Explore Jaimini, Lal Kitab, and Ashtakavarga systems for deeper insights
          </p>
        </div>

        {/* Profile Selector */}
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium">Select Profile:</label>
          <Select value={selectedProfile} onValueChange={setSelectedProfile}>
            <SelectTrigger className="w-64">
              <SelectValue>
                {selectedProfile && profiles.find(p => p.id === selectedProfile) ?
                  `${profiles.find(p => p.id === selectedProfile)!.name} (${profiles.find(p => p.id === selectedProfile)!.date_of_birth})` :
                  'Select a profile'}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {profiles.map((profile) => (
                <SelectItem key={profile.id} value={profile.id}>
                  {profile.name} ({profile.date_of_birth})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* System Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="jaimini">Jaimini System</TabsTrigger>
          <TabsTrigger value="lalkitab">Lal Kitab</TabsTrigger>
          <TabsTrigger value="ashtakavarga">Ashtakavarga</TabsTrigger>
        </TabsList>

        <TabsContent value="jaimini" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Jaimini Astrology</CardTitle>
              <CardDescription>
                Chara Karakas, Karakamsha, Arudha Padas, and Chara Dasha analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedProfile && <JaiminiAnalysis profileId={selectedProfile} />}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="lalkitab" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lal Kitab System</CardTitle>
              <CardDescription>
                Planetary Debts, Blind Planets, and Practical Remedies
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedProfile && <LalKitabAnalysis profileId={selectedProfile} />}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ashtakavarga" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ashtakavarga System</CardTitle>
              <CardDescription>
                Bhinna, Sarva Ashtakavarga, and Transit Analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedProfile && <AshtakavargaAnalysis profileId={selectedProfile} />}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Jaimini System</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Sign-based system focusing on Chara Karakas (significators) and Arudha Padas (illusion points) for timing events.
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Lal Kitab</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Unique system identifying karmic debts, blind planets, and providing simple practical remedies for common people.
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Ashtakavarga</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            Point-based system (bindus) for accurate transit predictions and evaluating planetary strength in each house.
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
