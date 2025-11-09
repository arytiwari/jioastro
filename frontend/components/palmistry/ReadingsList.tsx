'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogBody, DialogFooter } from '@/components/ui/dialog'
import { Hand, ChevronRight, Calendar, TrendingUp, Trash2 } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { toast } from 'sonner'

interface Reading {
  reading_id: string
  photo_id: string
  hand_type: 'left' | 'right'
  created_at: string
  overall_confidence: number
  has_interpretation: boolean
  thumbnail_url: string
}

interface Stats {
  total_readings: number
  avg_confidence: number
  latest_reading_date: string | null
  hands_analyzed: {
    left?: number
    right?: number
  }
}

interface ReadingsListProps {
  readings: Reading[]
  stats?: Stats
  isLoading: boolean
  onReadingClick: (readingId: string) => void
}

export default function ReadingsList({ readings, stats, isLoading, onReadingClick }: ReadingsListProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [readingToDelete, setReadingToDelete] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const deleteMutation = useMutation({
    mutationFn: async (readingId: string) => {
      return apiClient.deletePalmReading(readingId)
    },
    onSuccess: (_, deletedReadingId) => {
      // Optimistically update the cache before refetch
      queryClient.setQueryData(['palm-readings'], (old: any) => {
        if (!old || !old.readings) return old

        const filteredReadings = old.readings.filter((r: any) => r.reading_id !== deletedReadingId)

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
      setReadingToDelete(null)
    },
    onError: (error: any) => {
      toast.error(error.message || 'Failed to delete reading')
      setDeleteDialogOpen(false)
      setReadingToDelete(null)
    },
  })

  const handleDeleteClick = (e: React.MouseEvent, readingId: string) => {
    e.stopPropagation() // Prevent triggering the card click
    setReadingToDelete(readingId)
    setDeleteDialogOpen(true)
  }

  const confirmDelete = () => {
    if (readingToDelete && !deleteMutation.isPending) {
      deleteMutation.mutate(readingToDelete)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-20 h-20 bg-muted rounded-lg" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-1/3" />
                  <div className="h-3 bg-muted rounded w-1/2" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!readings || readings.length === 0) {
    return (
      <Card>
        <CardContent className="p-12">
          <div className="text-center space-y-4">
            <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Hand className="h-8 w-8 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-1">No Readings Yet</h3>
              <p className="text-sm text-muted-foreground">
                Capture or upload an image of your palm to get started
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Stats Summary */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{stats.total_readings}</p>
                <p className="text-xs text-muted-foreground mt-1">Total Readings</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">
                  {(stats.avg_confidence * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-muted-foreground mt-1">Avg Confidence</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">
                  {stats.hands_analyzed.left || 0}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Left Hand</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">
                  {stats.hands_analyzed.right || 0}
                </p>
                <p className="text-xs text-muted-foreground mt-1">Right Hand</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Readings List */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold">Your Readings</h3>
        {readings.map((reading) => (
          <Card
            key={reading.reading_id}
            className="cursor-pointer hover:border-primary transition-colors"
            onClick={() => onReadingClick(reading.reading_id)}
          >
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                {/* Thumbnail */}
                <div className="relative w-20 h-20 rounded-lg overflow-hidden bg-muted flex-shrink-0">
                  {reading.thumbnail_url ? (
                    <img
                      src={reading.thumbnail_url}
                      alt={`${reading.hand_type} palm`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Hand className="h-8 w-8 text-muted-foreground" />
                    </div>
                  )}
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant={reading.hand_type === 'left' ? 'default' : 'secondary'}>
                      {reading.hand_type === 'left' ? 'Left Hand' : 'Right Hand'}
                    </Badge>
                    {reading.has_interpretation && (
                      <Badge variant="outline" className="bg-green-500/10 text-green-700 border-green-200">
                        Analyzed
                      </Badge>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      <span>
                        {formatDistanceToNow(new Date(reading.created_at), { addSuffix: true })}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-3 w-3" />
                      <span>{(reading.overall_confidence * 100).toFixed(0)}% confidence</span>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => handleDeleteClick(e, reading.reading_id)}
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

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
