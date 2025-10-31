'use client'

import { useState } from 'react'
import { useMutation, useQueryClient } from '@/lib/query'
import { apiClient } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Star } from 'lucide-react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface FeedbackButtonProps {
  responseId: string
}

export function FeedbackButton({ responseId }: FeedbackButtonProps) {
  const queryClient = useQueryClient()
  const [showFeedback, setShowFeedback] = useState(false)
  const [rating, setRating] = useState(0)
  const [hoveredRating, setHoveredRating] = useState(0)
  const [comment, setComment] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const feedbackMutation = useMutation({
    mutationFn: async (data: { response_id: string; rating: number; comment?: string }) => {
      const response = await apiClient.createFeedback(data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['feedback-stats'])
      setSubmitted(true)
      setTimeout(() => {
        setShowFeedback(false)
        setSubmitted(false)
      }, 2000)
    },
  })

  const handleSubmit = () => {
    if (rating === 0) {
      alert('Please select a rating')
      return
    }

    feedbackMutation.mutate({
      response_id: responseId,
      rating,
      comment: comment.trim() || undefined,
    })
  }

  if (submitted) {
    return (
      <div className="text-green-600 text-sm font-semibold">
        ✓ Thank you for your feedback!
      </div>
    )
  }

  if (!showFeedback) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={() => setShowFeedback(true)}
      >
        <Star className="w-4 h-4 mr-2" />
        Rate this interpretation
      </Button>
    )
  }

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-white">
      <div>
        <Label>Rate this interpretation</Label>
        <div className="flex items-center gap-2 mt-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoveredRating(star)}
              onMouseLeave={() => setHoveredRating(0)}
              className="focus:outline-none"
            >
              <Star
                className={`w-8 h-8 transition-colors ${
                  star <= (hoveredRating || rating)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
          {rating > 0 && (
            <span className="text-sm text-gray-600 ml-2">
              {rating} star{rating !== 1 && 's'}
            </span>
          )}
        </div>
      </div>

      <div>
        <Label htmlFor="comment">Comments (optional)</Label>
        <Textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="What did you think of this interpretation?"
          rows={3}
          className="mt-2"
        />
      </div>

      <div className="flex gap-2">
        <Button
          onClick={handleSubmit}
          disabled={rating === 0 || feedbackMutation.isPending}
          size="sm"
        >
          {feedbackMutation.isPending ? 'Submitting...' : 'Submit Feedback'}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            setShowFeedback(false)
            setRating(0)
            setComment('')
          }}
        >
          Cancel
        </Button>
      </div>
    </div>
  )
}
