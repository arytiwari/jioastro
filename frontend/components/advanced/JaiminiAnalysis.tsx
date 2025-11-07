"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Loader2, AlertCircle, Star, Target, Home } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { getSession } from '@/lib/supabase'
import axios from 'axios'

interface JaiminiAnalysisProps {
  profileId: string
}

interface CharaKaraka {
  planet: string
  longitude: number
  sign: string
  house: number
  code: string
  role: string
  signification: string
}

interface Karakamsha {
  sign: string
  house_in_d9: number
  lord: string
}

interface ArudhaPada {
  sign: string
  house: number
  lord: string
  code: string
  name: string
  meaning: string
}

interface JaiminiData {
  chara_karakas: Record<string, CharaKaraka>
  atmakaraka: CharaKaraka
  karakamsha?: Karakamsha
  arudha_padas: Record<string, ArudhaPada>
  chara_dasha?: any
}

export default function JaiminiAnalysis({ profileId }: JaiminiAnalysisProps) {
  const [data, setData] = useState<JaiminiData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (profileId) {
      fetchJaiminiData()
    }
  }, [profileId])

  const fetchJaiminiData = async () => {
    try {
      setLoading(true)
      setError(null)

      const session = getSession()
      if (!session) return

      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/enhancements/jaimini/analyze/${profileId}`,
        {
          headers: {
            Authorization: `Bearer ${session.access_token}`
          }
        }
      )

      setData(response.data.analysis)
    } catch (err: any) {
      console.error('Error fetching Jaimini data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load Jaimini analysis')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!data) return null

  const karakaOrder = ['AK', 'AmK', 'BK', 'MK', 'PK', 'GK', 'DK']

  return (
    <div className="space-y-6">
      {/* Atmakaraka Highlight */}
      <Card className="border-primary">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Star className="h-5 w-5 text-primary" />
            <CardTitle>Atmakaraka (Soul Significator)</CardTitle>
          </div>
          <CardDescription>The planet with the highest degree - your soul's journey</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="p-4 bg-primary/10 rounded-lg">
              <div className="text-3xl font-bold text-primary">{data.atmakaraka?.planet || 'N/A'}</div>
              <div className="text-sm text-muted-foreground mt-1">
                {data.atmakaraka?.longitude ? `${data.atmakaraka.longitude.toFixed(2)}°` : 'N/A'}
              </div>
            </div>
            <div className="flex-1">
              <div className="font-medium">
                {data.atmakaraka?.sign || 'N/A'}
                {data.atmakaraka?.house && ` • House ${data.atmakaraka.house}`}
              </div>
              <div className="text-sm text-muted-foreground mt-1">{data.atmakaraka?.signification || 'N/A'}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* All Chara Karakas */}
      <Card>
        <CardHeader>
          <CardTitle>Chara Karakas (7 Significators)</CardTitle>
          <CardDescription>Planets become significators based on their degrees</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {karakaOrder.map((code) => {
              const karaka = data.chara_karakas[code]
              if (!karaka) return null

              return (
                <div key={code} className="flex items-start gap-3 p-3 border rounded-lg">
                  <div className="p-2 bg-secondary rounded">
                    <Badge variant="outline">{code}</Badge>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{karaka.planet}</div>
                    <div className="text-sm text-muted-foreground">{karaka.role}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {karaka.sign} • House {karaka.house} • {karaka.longitude.toFixed(2)}°
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Karakamsha */}
      {data.karakamsha && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              <CardTitle>Karakamsha</CardTitle>
            </div>
            <CardDescription>Navamsa position of Atmakaraka - reveals spiritual path</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <div className="p-4 bg-secondary rounded-lg">
                <div className="text-2xl font-bold">{data.karakamsha.sign}</div>
                <div className="text-sm text-muted-foreground mt-1">House {data.karakamsha.house_in_d9} in D9</div>
              </div>
              <div>
                <div className="text-sm"><span className="font-medium">Lord:</span> {data.karakamsha.lord}</div>
                <div className="text-sm text-muted-foreground mt-2">
                  Indicates your spiritual inclinations and deep motivations
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Arudha Padas */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Home className="h-5 w-5" />
            <CardTitle>Arudha Padas (Illusion Points)</CardTitle>
          </div>
          <CardDescription>How various life areas appear to others</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(data.arudha_padas).map(([key, pada]) => (
              <div key={key} className="p-3 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="secondary">{pada.code}</Badge>
                  <span className="text-sm font-medium">{pada.sign}</span>
                </div>
                <div className="text-sm font-medium">{pada.name}</div>
                <div className="text-xs text-muted-foreground mt-1">{pada.meaning}</div>
                <div className="text-xs text-muted-foreground mt-1">House {pada.house} • Lord: {pada.lord}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Chara Dasha */}
      {data.chara_dasha && data.chara_dasha.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Chara Dasha (Sign-Based Periods)</CardTitle>
            <CardDescription>Major life periods based on sign sequences</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.chara_dasha.slice(0, 5).map((dasha: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{dasha.sign}</div>
                    <div className="text-sm text-muted-foreground">
                      {new Date(dasha.start_date).toLocaleDateString()} - {new Date(dasha.end_date).toLocaleDateString()}
                    </div>
                  </div>
                  <Badge>{dasha.duration_years} years</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Interpretation Notes */}
      <Card className="bg-muted/50">
        <CardHeader>
          <CardTitle className="text-lg">Understanding Jaimini System</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><strong>Chara Karakas:</strong> Unlike fixed karakas, these change based on planetary degrees in your chart.</p>
          <p><strong>Atmakaraka:</strong> The planet with highest degree represents your soul's primary lessons and journey.</p>
          <p><strong>Arudha Padas:</strong> Show how different life areas appear externally vs. internal reality.</p>
          <p><strong>Karakamsha:</strong> Reveals your spiritual path and deep-seated motivations from past lives.</p>
        </CardContent>
      </Card>
    </div>
  )
}
