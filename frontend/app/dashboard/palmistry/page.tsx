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
import { Camera, Upload, Hand, History, Sparkles, AlertCircle, User } from 'lucide-react'
import CameraCapture from '@/components/palmistry/CameraCapture'
import ImageUpload from '@/components/palmistry/ImageUpload'
import ReadingsList from '@/components/palmistry/ReadingsList'
import ReadingDisplay from '@/components/palmistry/ReadingDisplay'

export default function PalmistryPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('capture')
  const [selectedReading, setSelectedReading] = useState<string | null>(null)
  const [uploadedPhotoId, setUploadedPhotoId] = useState<string | null>(null)
  const [selectedProfileId, setSelectedProfileId] = useState<string | null>(null)

  // Fetch user profiles for holistic analysis
  const { data: profilesData } = useQuery({
    queryKey: ['profiles'],
    queryFn: async () => {
      const response = await apiClient.getProfiles()
      return response.data
    },
  })

  // Fetch palm readings
  const { data: readingsData, isLoading: isLoadingReadings } = useQuery({
    queryKey: ['palm-readings'],
    queryFn: async () => {
      const response = await apiClient.getPalmReadings({ limit: 20 })
      return response.data
    },
  })

  // Upload image mutation
  const uploadMutation = useMutation({
    mutationFn: async (data: {
      hand_type: 'left' | 'right'
      view_type: 'front' | 'back' | 'zoomed' | 'thumb_edge' | 'side'
      image: string
      capture_method: 'camera' | 'upload'
    }) => {
      const response = await apiClient.uploadPalmImage({
        ...data,
        profile_id: selectedProfileId || undefined,  // Pass selected profile for holistic analysis
        device_info: {
          device_type: /mobile/i.test(navigator.userAgent) ? 'mobile' : 'desktop',
          screen_width: window.screen.width,
          screen_height: window.screen.height,
          user_agent: navigator.userAgent,
        },
      })
      return response.data
    },
    onSuccess: (data: any) => {
      setUploadedPhotoId(data.photo_id)
      // Automatically analyze after upload
      analyzeMutation.mutate({
        photo_ids: [data.photo_id],
      })
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to upload image')
    },
  })

  // Analyze palm mutation
  const analyzeMutation = useMutation({
    mutationFn: async (data: {
      photo_ids: string[]
      reanalysis?: boolean
      priority?: 'high' | 'normal' | 'low'
    }) => {
      const response = await apiClient.analyzePalm(data)
      return response.data
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries(['palm-readings'])
      setSelectedReading(data.reading.reading_id)
      setActiveTab('readings')
    },
    onError: (error: any) => {
      alert(error?.message || 'Failed to analyze palm')
    },
  })

  const handleImageCaptured = (imageData: string, handType: 'left' | 'right', viewType: string) => {
    uploadMutation.mutate({
      hand_type: handType,
      view_type: viewType as any,
      image: imageData,
      capture_method: 'camera',
    })
  }

  const handleImageUploaded = (imageData: string, handType: 'left' | 'right', viewType: string) => {
    uploadMutation.mutate({
      hand_type: handType,
      view_type: viewType as any,
      image: imageData,
      capture_method: 'upload',
    })
  }

  const handleReadingSelected = (readingId: string) => {
    setSelectedReading(readingId)
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Hand className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold">Palmistry Intelligence</h1>
        </div>
        <p className="text-muted-foreground text-lg">
          AI-powered palm reading analysis with ancient wisdom and modern technology
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
            Link to your birth profile for cross-domain insights combining Astrology, Numerology, and Palmistry
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="profile-select">Select Birth Profile</Label>
            <Select value={selectedProfileId || 'none'} onValueChange={(value) => setSelectedProfileId(value === 'none' ? null : value)}>
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
              <p className="text-sm text-primary">
                ✨ Holistic analysis enabled - your reading will correlate palm features with astrological positions and numerological patterns
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 lg:w-auto">
          <TabsTrigger value="capture" className="flex items-center gap-2">
            <Camera className="h-4 w-4" />
            <span className="hidden sm:inline">Camera</span>
          </TabsTrigger>
          <TabsTrigger value="upload" className="flex items-center gap-2">
            <Upload className="h-4 w-4" />
            <span className="hidden sm:inline">Upload</span>
          </TabsTrigger>
          <TabsTrigger value="readings" className="flex items-center gap-2">
            <History className="h-4 w-4" />
            <span className="hidden sm:inline">Readings</span>
            {readingsData?.total_count > 0 && (
              <Badge variant="secondary" className="ml-1">
                {readingsData.total_count}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Camera Capture Tab */}
        <TabsContent value="capture" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Capture Palm Image</CardTitle>
              <CardDescription>
                Use your device camera to capture a clear image of your palm. Follow the on-screen guidance for best results.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {uploadMutation.isPending || analyzeMutation.isPending ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <Sparkles className="h-12 w-12 text-primary animate-pulse" />
                  <div className="text-center">
                    <h3 className="text-lg font-semibold">
                      {uploadMutation.isPending ? 'Uploading image...' : 'Analyzing your palm...'}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {uploadMutation.isPending
                        ? 'Validating image quality'
                        : 'AI is detecting lines, mounts, and patterns'}
                    </p>
                  </div>
                </div>
              ) : (
                <CameraCapture
                  onImageCaptured={handleImageCaptured}
                  isLoading={uploadMutation.isPending}
                />
              )}
            </CardContent>
          </Card>

          {/* Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Tips for Best Results</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>Ensure good lighting - natural daylight works best</p>
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>Keep your hand flat and fingers spread naturally</p>
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>Avoid shadows or glare on your palm</p>
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                <p>Capture images of both left and right hands for complete analysis</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload Palm Image</CardTitle>
              <CardDescription>
                Upload a photo of your palm from your device. Ensure the image is clear and well-lit.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {uploadMutation.isPending || analyzeMutation.isPending ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-4">
                  <Sparkles className="h-12 w-12 text-primary animate-pulse" />
                  <div className="text-center">
                    <h3 className="text-lg font-semibold">
                      {uploadMutation.isPending ? 'Uploading image...' : 'Analyzing your palm...'}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {uploadMutation.isPending
                        ? 'Validating image quality'
                        : 'AI is detecting lines, mounts, and patterns'}
                    </p>
                  </div>
                </div>
              ) : (
                <ImageUpload
                  onImageUploaded={handleImageUploaded}
                  isLoading={uploadMutation.isPending}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Readings History Tab */}
        <TabsContent value="readings" className="space-y-6">
          {selectedReading ? (
            <>
              <Button
                variant="outline"
                onClick={() => setSelectedReading(null)}
                className="mb-4"
              >
                ← Back to Readings List
              </Button>
              <ReadingDisplay
                readingId={selectedReading}
                onBack={() => setSelectedReading(null)}
              />
            </>
          ) : (
            <ReadingsList
              readings={readingsData?.readings || []}
              stats={readingsData?.stats}
              isLoading={isLoadingReadings}
              onReadingClick={handleReadingSelected}
            />
          )}
        </TabsContent>
      </Tabs>

      {/* Stats Footer */}
      {readingsData?.stats && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Your Palmistry Journey</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{readingsData.stats.total_readings}</p>
                <p className="text-xs text-muted-foreground">Total Readings</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">
                  {(readingsData.stats.avg_confidence * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-muted-foreground">Avg Confidence</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">
                  {readingsData.stats.hands_analyzed.left || 0}
                </p>
                <p className="text-xs text-muted-foreground">Left Hand</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">
                  {readingsData.stats.hands_analyzed.right || 0}
                </p>
                <p className="text-xs text-muted-foreground">Right Hand</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
