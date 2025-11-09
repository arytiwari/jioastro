'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog'
import { Hand, Sparkles, TrendingUp, Heart, Briefcase, AlertCircle, Star, ArrowLeft, Trash2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { toast } from 'sonner'

interface ReadingDisplayProps {
  readingId: string
  onBack: () => void
}

export default function ReadingDisplay({ readingId, onBack }: ReadingDisplayProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['palm-reading', readingId],
    queryFn: async () => {
      const response = await apiClient.getPalmReading(readingId)
      return response.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => {
      return apiClient.deletePalmReading(readingId)
    },
    onSuccess: () => {
      // Optimistically update the cache before refetch
      queryClient.setQueryData(['palm-readings'], (old: any) => {
        if (!old || !old.readings) return old

        const filteredReadings = old.readings.filter((r: any) => r.reading_id !== readingId)

        return {
          readings: filteredReadings,
          total_count: filteredReadings.length,
          stats: {
            ...old.stats,
            total_readings: filteredReadings.length,
          }
        }
      })

      // Then invalidate to refetch accurate stats
      queryClient.invalidateQueries(['palm-readings'])

      toast.success('Palm reading deleted successfully')
      setDeleteDialogOpen(false)
      onBack() // Navigate back to the list
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete reading')
      setDeleteDialogOpen(false)
    },
  })

  const confirmDelete = () => {
    if (!deleteMutation.isPending) {
      deleteMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-12">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Sparkles className="h-12 w-12 text-primary animate-pulse" />
            <p className="text-muted-foreground">Loading reading...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <Button onClick={onBack} variant="outline" size="sm">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Readings
        </Button>
        <Card>
          <CardContent className="p-12">
            <div className="text-center space-y-4">
              <AlertCircle className="h-12 w-12 mx-auto text-destructive" />
              <div>
                <h3 className="text-lg font-semibold mb-1">Failed to load reading</h3>
                <p className="text-sm text-muted-foreground">
                  {error?.message || 'Please try again later'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const { reading, interpretation } = data

  return (
    <div className="space-y-6">
      {/* Back and Delete Buttons */}
      <div className="flex items-center justify-between">
        <Button onClick={onBack} variant="outline" size="sm">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Readings
        </Button>
        <Button
          onClick={() => setDeleteDialogOpen(true)}
          variant="destructive"
          size="sm"
        >
          <Trash2 className="mr-2 h-4 w-4" />
          Delete Reading
        </Button>
      </div>

      {/* Header with Image */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2">
                <Hand className="h-5 w-5" />
                {reading.hand_type === 'left' ? 'Left' : 'Right'} Hand Reading
              </CardTitle>
              <CardDescription>
                Analyzed {formatDistanceToNow(new Date(reading.created_at), { addSuffix: true })}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={reading.hand_shape ? 'default' : 'secondary'}>
                {reading.hand_shape ? `${reading.hand_shape} hand` : 'Analyzing...'}
              </Badge>
              <Badge variant="outline">
                {(reading.overall_confidence * 100).toFixed(0)}% Confidence
              </Badge>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Interpretation Summary */}
      {interpretation && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg leading-relaxed">{interpretation.summary}</p>
          </CardContent>
        </Card>
      )}

      {/* Main Tabs */}
      <Tabs defaultValue="analysis" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="personality">Personality</TabsTrigger>
          <TabsTrigger value="events">Life Events</TabsTrigger>
          <TabsTrigger value="details">Details</TabsTrigger>
        </TabsList>

        {/* Detailed Analysis Tab */}
        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Detailed Analysis</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none dark:prose-invert">
              {interpretation ? (
                <div
                  className="whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{ __html: interpretation.detailed_analysis.replace(/\n/g, '<br />') }}
                />
              ) : (
                <p className="text-muted-foreground">Analysis in progress...</p>
              )}
            </CardContent>
          </Card>

          {/* Recommendations */}
          {interpretation?.recommendations && interpretation.recommendations.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="h-5 w-5 text-yellow-500" />
                  Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {interpretation.recommendations.map((rec: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-primary mt-0.5">•</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Personality Tab */}
        <TabsContent value="personality" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Personality Traits</CardTitle>
              <CardDescription>
                Based on your hand shape and palm features
              </CardDescription>
            </CardHeader>
            <CardContent>
              {interpretation?.personality_traits && interpretation.personality_traits.length > 0 ? (
                <div className="grid gap-3">
                  {interpretation.personality_traits.map((trait: string, index: number) => (
                    <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                      <Heart className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                      <span>{trait}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No personality traits detected yet.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Life Events Tab */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Life Events Predictions</CardTitle>
              <CardDescription>
                Predicted timeline based on palm line analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {interpretation?.life_events && interpretation.life_events.length > 0 ? (
                <div className="space-y-4">
                  {interpretation.life_events.map((event: any, index: number) => (
                    <div key={index} className="border-l-2 border-primary pl-4 py-2">
                      <div className="flex items-start justify-between mb-1">
                        <Badge variant="outline">{event.event_type || 'General'}</Badge>
                        {event.age_range && (
                          <span className="text-sm text-muted-foreground">Age {event.age_range}</span>
                        )}
                      </div>
                      <p className="text-sm mt-2">{event.description}</p>
                      {event.confidence && (
                        <div className="mt-2 flex items-center gap-2">
                          <TrendingUp className="h-3 w-3 text-muted-foreground" />
                          <span className="text-xs text-muted-foreground">
                            {(event.confidence * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No life events predicted yet.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Details Tab */}
        <TabsContent value="details" className="space-y-4">
          {/* Detected Lines */}
          <Card>
            <CardHeader>
              <CardTitle>Detected Palm Lines</CardTitle>
            </CardHeader>
            <CardContent>
              {reading.lines_detected && reading.lines_detected.length > 0 ? (
                <div className="space-y-3">
                  {reading.lines_detected.map((line: any, index: number) => (
                    <div key={index} className="p-3 rounded-lg bg-muted/50">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold capitalize">{line.line_type}</span>
                        <Badge variant="outline">{(line.confidence * 100).toFixed(0)}%</Badge>
                      </div>
                      {line.characteristics && (
                        <div className="text-sm text-muted-foreground">
                          {Object.entries(line.characteristics).map(([key, value]: [string, any]) => (
                            <span key={key} className="inline-block mr-3">
                              {key}: <span className="font-medium">{value}</span>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No palm lines detected yet.</p>
              )}
            </CardContent>
          </Card>

          {/* Detected Mounts */}
          <Card>
            <CardHeader>
              <CardTitle>Detected Palm Mounts</CardTitle>
            </CardHeader>
            <CardContent>
              {reading.mounts_detected && reading.mounts_detected.length > 0 ? (
                <div className="grid grid-cols-2 gap-3">
                  {reading.mounts_detected.map((mount: any, index: number) => (
                    <div key={index} className="p-3 rounded-lg bg-muted/50">
                      <div className="font-semibold mb-1">{mount.mount_name}</div>
                      <div className="text-sm text-muted-foreground capitalize">
                        {mount.prominence}
                      </div>
                      <Badge variant="outline" className="mt-2 text-xs">
                        {(mount.confidence * 100).toFixed(0)}% confidence
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No palm mounts detected yet.</p>
              )}
            </CardContent>
          </Card>

          {/* RAG Sources */}
          {interpretation?.rag_sources && interpretation.rag_sources.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Knowledge Sources</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {interpretation.rag_sources.map((source: string, index: number) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {source}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader onClose={() => setDeleteDialogOpen(false)}>
            <DialogTitle>Delete Palm Reading?</DialogTitle>
            <DialogDescription>
              This will permanently delete this palm reading, interpretation, and all associated images.
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleteMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
