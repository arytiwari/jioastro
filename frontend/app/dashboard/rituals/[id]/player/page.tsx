"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import {
  ArrowLeft,
  ArrowRight,
  Pause,
  Play,
  Volume2,
  VolumeX,
  CheckCircle2,
  Clock,
  Lightbulb,
  Package,
  X
} from "lucide-react"
import api from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface RitualStep {
  step_number: number
  title: string
  description: string
  mantra?: string
  mantra_transliteration?: string
  mantra_translation?: string
  duration_seconds: number
  visual_aid_url?: string
  audio_instruction_url?: string
  required_items?: string[]
  tips?: string[]
}

interface Ritual {
  id: string
  name: string
  category: string
  deity: string | null
  duration_minutes: number
  difficulty: string
  description: string | null
  required_items: string[]
  steps: RitualStep[]
  audio_enabled: boolean
  benefits: string[]
  best_time_of_day: string | null
}

export default function RitualPlayerPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const ritualId = params.id as string

  const [ritual, setRitual] = useState<Ritual | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [isPaused, setIsPaused] = useState(false)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const speechSynthesisRef = useRef<SpeechSynthesisUtterance | null>(null)

  const currentStep = ritual?.steps[currentStepIndex]
  const totalSteps = ritual?.steps.length || 0
  const progressPercentage = ((currentStepIndex + 1) / totalSteps) * 100

  useEffect(() => {
    if (ritualId) {
      fetchRitualAndStartSession()
    }

    return () => {
      // Cleanup
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (speechSynthesisRef.current) {
        window.speechSynthesis.cancel()
      }
    }
  }, [ritualId])

  useEffect(() => {
    if (!isPaused && currentStep) {
      startTimer()
    } else {
      stopTimer()
    }

    return () => stopTimer()
  }, [isPaused, currentStepIndex])

  const fetchRitualAndStartSession = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch ritual details
      const ritualResponse = await api.get(`/rituals/${ritualId}`)
      setRitual(ritualResponse.data)

      // Start a new session
      const sessionResponse = await api.post(`/rituals/${ritualId}/start`, {
        ritual_template_id: ritualId,
        notes: null
      })
      setSessionId(sessionResponse.data.id)

      // Speak introduction
      if (voiceEnabled && ritualResponse.data) {
        speakText(`Welcome to ${ritualResponse.data.name}. Let's begin.`)
      }

    } catch (err: any) {
      console.error("Failed to load ritual:", err)
      setError(err.response?.data?.detail || "Failed to load ritual")
    } finally {
      setLoading(false)
    }
  }

  const startTimer = () => {
    stopTimer()
    timerRef.current = setInterval(() => {
      setElapsedTime(prev => prev + 1)
    }, 1000)
  }

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const speakText = (text: string) => {
    if (!voiceEnabled || !window.speechSynthesis) return

    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.volume = 1

    speechSynthesisRef.current = utterance
    window.speechSynthesis.speak(utterance)
  }

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled)
    if (voiceEnabled) {
      window.speechSynthesis.cancel()
    }
  }

  const togglePause = async () => {
    const newPausedState = !isPaused
    setIsPaused(newPausedState)

    try {
      if (newPausedState && sessionId) {
        await api.post(`/rituals/sessions/${sessionId}/pause`)
      } else if (!newPausedState && sessionId) {
        await api.post(`/rituals/sessions/${sessionId}/resume`)
      }
    } catch (err) {
      console.error("Failed to update session status:", err)
    }

    if (!newPausedState) {
      speakText(`Resuming ${currentStep?.title}`)
    }
  }

  const goToNextStep = async () => {
    if (currentStepIndex < totalSteps - 1) {
      const nextIndex = currentStepIndex + 1
      setCurrentStepIndex(nextIndex)
      setElapsedTime(0)

      // Update progress in backend
      if (sessionId) {
        try {
          await api.put(`/rituals/sessions/${sessionId}/progress`, {
            current_step: nextIndex + 1
          })
        } catch (err) {
          console.error("Failed to update progress:", err)
        }
      }

      // Speak next step
      if (voiceEnabled && ritual?.steps[nextIndex]) {
        speakText(`Step ${nextIndex + 1}: ${ritual.steps[nextIndex].title}`)
      }
    }
  }

  const goToPreviousStep = () => {
    if (currentStepIndex > 0) {
      const prevIndex = currentStepIndex - 1
      setCurrentStepIndex(prevIndex)
      setElapsedTime(0)

      // Speak previous step
      if (voiceEnabled && ritual?.steps[prevIndex]) {
        speakText(`Going back to step ${prevIndex + 1}: ${ritual.steps[prevIndex].title}`)
      }
    }
  }

  const speakMantra = () => {
    if (currentStep?.mantra) {
      const mantraText = currentStep.mantra_transliteration || currentStep.mantra
      speakText(mantraText)
    }
  }

  const completeRitual = async () => {
    if (!sessionId) return

    try {
      await api.post(`/rituals/sessions/${sessionId}/complete`, {
        rating: null,
        notes: null
      })

      toast({
        title: "Ritual Completed! 🙏",
        description: `You have successfully completed ${ritual?.name}`,
      })

      speakText(`Congratulations! You have completed the ritual. Om Shanti.`)

      // Navigate back to ritual library after a delay
      setTimeout(() => {
        router.push("/dashboard/rituals")
      }, 3000)

    } catch (err) {
      console.error("Failed to complete ritual:", err)
      toast({
        title: "Error",
        description: "Failed to mark ritual as complete",
        variant: "destructive"
      })
    }
  }

  const abandonRitual = async () => {
    if (!sessionId) {
      router.push("/dashboard/rituals")
      return
    }

    try {
      await api.post(`/rituals/sessions/${sessionId}/abandon`)
      router.push("/dashboard/rituals")
    } catch (err) {
      console.error("Failed to abandon ritual:", err)
      router.push("/dashboard/rituals")
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Preparing ritual...</p>
        </div>
      </div>
    )
  }

  if (error || !ritual || !currentStep) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error || "Ritual not found"}</p>
          </CardContent>
          <CardFooter>
            <Button onClick={() => router.push("/dashboard/rituals")}>
              Back to Rituals
            </Button>
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      <div className="container mx-auto py-4 px-4 max-w-4xl">
        {/* Header with Exit Button */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={abandonRitual}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{ritual.name}</h1>
              {ritual.deity && (
                <p className="text-sm text-muted-foreground">Deity: {ritual.deity}</p>
              )}
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={toggleVoice}>
            {voiceEnabled ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
          </Button>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2 text-sm">
            <span className="font-medium">
              Step {currentStepIndex + 1} of {totalSteps}
            </span>
            <span className="text-muted-foreground">
              {Math.round(progressPercentage)}% Complete
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>

        {/* Main Step Card */}
        <Card className="mb-6">
          <CardHeader className="pb-4">
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-3xl mb-2">
                  {currentStepIndex + 1}. {currentStep.title}
                </CardTitle>
                <CardDescription className="flex items-center gap-2 text-base">
                  <Clock className="h-4 w-4" />
                  Duration: {Math.floor(currentStep.duration_seconds / 60)}m {currentStep.duration_seconds % 60}s
                  {elapsedTime > 0 && (
                    <span className="ml-2">• Elapsed: {formatTime(elapsedTime)}</span>
                  )}
                </CardDescription>
              </div>
              {isPaused && (
                <Badge variant="secondary">Paused</Badge>
              )}
            </div>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Description */}
            <div>
              <h3 className="font-semibold mb-2">Instructions</h3>
              <p className="text-lg leading-relaxed">{currentStep.description}</p>
            </div>

            {/* Mantra Section */}
            {currentStep.mantra && (
              <>
                <Separator />
                <div className="bg-amber-50 dark:bg-amber-950 p-6 rounded-lg space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg">Sacred Mantra</h3>
                    {voiceEnabled && (
                      <Button variant="outline" size="sm" onClick={speakMantra}>
                        <Volume2 className="h-4 w-4 mr-2" />
                        Hear Pronunciation
                      </Button>
                    )}
                  </div>

                  {/* Sanskrit */}
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">Sanskrit:</p>
                    <p className="text-2xl font-medium text-amber-900 dark:text-amber-100">
                      {currentStep.mantra}
                    </p>
                  </div>

                  {/* Transliteration */}
                  {currentStep.mantra_transliteration && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Pronunciation:</p>
                      <p className="text-lg italic">{currentStep.mantra_transliteration}</p>
                    </div>
                  )}

                  {/* Translation */}
                  {currentStep.mantra_translation && (
                    <div>
                      <p className="text-sm text-muted-foreground mb-1">Meaning:</p>
                      <p className="text-base">{currentStep.mantra_translation}</p>
                    </div>
                  )}
                </div>
              </>
            )}

            {/* Required Items */}
            {currentStep.required_items && currentStep.required_items.length > 0 && (
              <>
                <Separator />
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Package className="h-4 w-4" />
                    <h3 className="font-semibold">Required Items</h3>
                  </div>
                  <ul className="grid grid-cols-2 gap-2">
                    {currentStep.required_items.map((item, idx) => (
                      <li key={idx} className="text-sm flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}

            {/* Tips */}
            {currentStep.tips && currentStep.tips.length > 0 && (
              <>
                <Separator />
                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Lightbulb className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                    <h3 className="font-semibold">Tips</h3>
                  </div>
                  <ul className="space-y-1">
                    {currentStep.tips.map((tip, idx) => (
                      <li key={idx} className="text-sm">• {tip}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Navigation Controls */}
        <div className="flex items-center justify-between gap-4">
          <Button
            variant="outline"
            onClick={goToPreviousStep}
            disabled={currentStepIndex === 0}
            size="lg"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Previous
          </Button>

          <Button
            variant={isPaused ? "default" : "secondary"}
            onClick={togglePause}
            size="lg"
            className="min-w-32"
          >
            {isPaused ? (
              <>
                <Play className="h-5 w-5 mr-2" />
                Resume
              </>
            ) : (
              <>
                <Pause className="h-5 w-5 mr-2" />
                Pause
              </>
            )}
          </Button>

          {currentStepIndex === totalSteps - 1 ? (
            <Button
              variant="default"
              onClick={completeRitual}
              size="lg"
              className="bg-green-600 hover:bg-green-700"
            >
              <CheckCircle2 className="h-5 w-5 mr-2" />
              Complete
            </Button>
          ) : (
            <Button
              variant="outline"
              onClick={goToNextStep}
              size="lg"
            >
              Next
              <ArrowRight className="h-5 w-5 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
