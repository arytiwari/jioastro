'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Camera, RotateCcw, Hand, Check, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface CameraCaptureProps {
  onImageCaptured: (imageData: string, handType: 'left' | 'right', viewType: string) => void
  isLoading?: boolean
}

export default function CameraCapture({ onImageCaptured, isLoading }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [handType, setHandType] = useState<'left' | 'right'>('left')
  const [viewType, setViewType] = useState<string>('front')
  const [cameraError, setCameraError] = useState<string | null>(null)

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop())
      }
    }
  }, [stream])

  // Set stream when video element is ready
  useEffect(() => {
    if (stream && videoRef.current && isCameraActive && !capturedImage) {
      // Check if video already has the stream
      if (videoRef.current.srcObject === stream) {
        console.log('🎥 Video already has stream, ensuring it plays')
        if (videoRef.current.paused) {
          videoRef.current.play().catch(err => {
            console.error('❌ Error playing video:', err)
          })
        }
        return
      }

      console.log('🎥 Setting stream to video element in useEffect')
      console.log('Video ref:', videoRef.current)
      videoRef.current.srcObject = stream

      videoRef.current.onloadedmetadata = () => {
        console.log('Video metadata loaded!')
        console.log('Video dimensions:', videoRef.current?.videoWidth, 'x', videoRef.current?.videoHeight)
        console.log('Video readyState:', videoRef.current?.readyState)
        console.log('Attempting to play...')

        videoRef.current?.play()
          .then(() => {
            console.log('✅ Video playing successfully!')
            console.log('Video element:', {
              paused: videoRef.current?.paused,
              muted: videoRef.current?.muted,
              width: videoRef.current?.offsetWidth,
              height: videoRef.current?.offsetHeight,
              display: window.getComputedStyle(videoRef.current!).display,
              visibility: window.getComputedStyle(videoRef.current!).visibility,
              opacity: window.getComputedStyle(videoRef.current!).opacity
            })
          })
          .catch((err) => {
            console.error('❌ Error playing video:', err)
            setCameraError('Failed to play video stream.')
          })
      }
    }
  }, [stream, isCameraActive, capturedImage])

  const startCamera = async () => {
    try {
      setCameraError(null)
      console.log('📹 Starting camera...')

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user', // Use front camera by default (more compatible)
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
      })

      console.log('✅ Media stream obtained:', mediaStream)
      console.log('Stream tracks:', mediaStream.getTracks())
      console.log('Video track settings:', mediaStream.getVideoTracks()[0]?.getSettings())

      // Set state - this will trigger useEffect to set up video element
      setIsCameraActive(true)
      setStream(mediaStream)

      console.log('Camera state updated - useEffect will handle video setup')
    } catch (error) {
      console.error('❌ Error accessing camera:', error)
      setCameraError(`Failed to access camera: ${error instanceof Error ? error.message : 'Unknown error'}. Please check permissions and try again.`)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
    }
    setIsCameraActive(false)
  }

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')

      if (ctx) {
        // Get video dimensions
        const videoWidth = video.videoWidth
        const videoHeight = video.videoHeight

        // Define crop area to match guide overlay (portrait ratio ~2:3)
        // The guide is roughly 40% of video width and 60% of video height
        const cropWidth = Math.floor(videoWidth * 0.4)
        const cropHeight = Math.floor(videoHeight * 0.6)

        // Center the crop area
        const cropX = Math.floor((videoWidth - cropWidth) / 2)
        const cropY = Math.floor((videoHeight - cropHeight) / 2)

        console.log('📸 Capturing with crop:', {
          videoSize: `${videoWidth}x${videoHeight}`,
          cropArea: `${cropWidth}x${cropHeight}`,
          cropPosition: `${cropX},${cropY}`
        })

        // Set canvas to crop dimensions
        canvas.width = cropWidth
        canvas.height = cropHeight

        // Flip horizontally (mirror effect) and draw cropped area
        ctx.translate(cropWidth, 0)
        ctx.scale(-1, 1)

        // Draw the cropped portion of the video
        ctx.drawImage(
          video,
          cropX, cropY, cropWidth, cropHeight,  // Source rectangle from video
          0, 0, cropWidth, cropHeight            // Destination rectangle on canvas
        )

        // Reset transformations
        ctx.setTransform(1, 0, 0, 1, 0, 0)

        // Convert to base64
        const imageData = canvas.toDataURL('image/jpeg', 0.9)
        setCapturedImage(imageData)

        console.log('✅ Image captured and cropped to guide area')
      }
    }
  }

  const retakeImage = () => {
    setCapturedImage(null)
  }

  const confirmAndUpload = () => {
    if (capturedImage) {
      onImageCaptured(capturedImage, handType, viewType)
      setCapturedImage(null)
      stopCamera()
    }
  }

  return (
    <div className="space-y-6">
      {/* Hand and View Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="hand-type">Hand</Label>
          <Select value={handType} onValueChange={(value: any) => setHandType(value)}>
            <SelectTrigger id="hand-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="left">Left Hand</SelectItem>
              <SelectItem value="right">Right Hand</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="view-type">View Type</Label>
          <Select value={viewType} onValueChange={setViewType}>
            <SelectTrigger id="view-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="front">Front (Palm)</SelectItem>
              <SelectItem value="back">Back of Hand</SelectItem>
              <SelectItem value="zoomed">Zoomed Lines</SelectItem>
              <SelectItem value="thumb_edge">Thumb Edge</SelectItem>
              <SelectItem value="side">Side View</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Camera View / Preview */}
      <Card className="relative overflow-hidden bg-black">
        <div className="w-full min-h-[400px] md:min-h-[500px] flex items-center justify-center">
          {capturedImage ? (
            // Show captured image
            <img src={capturedImage} alt="Captured palm" className="w-full h-full object-contain max-h-[600px]" />
          ) : isCameraActive ? (
            // Show live camera feed with guide overlay
            <div className="relative w-full min-h-[400px] md:min-h-[500px]">
              <video
                ref={videoRef}
                className="w-full h-auto bg-black"
                autoPlay
                playsInline
                muted
                style={{ transform: 'scaleX(-1)', minHeight: '400px' }}
              />
              {/* Hand positioning guide overlay */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="border-2 border-dashed border-white/60 rounded-lg w-48 h-72 md:w-64 md:h-96 flex items-center justify-center backdrop-blur-[1px]">
                  <Hand className="h-24 w-24 md:h-32 md:w-32 text-white/40" />
                </div>
              </div>
            </div>
          ) : (
            // Placeholder when camera is off
            <div className="flex items-center justify-center h-full min-h-[400px] bg-muted w-full">
              <div className="text-center space-y-4">
                <Camera className="h-16 w-16 mx-auto text-muted-foreground" />
                <p className="text-muted-foreground">Click "Start Camera" to begin</p>
              </div>
            </div>
          )}
        </div>
        <canvas ref={canvasRef} className="hidden" />
      </Card>

      {/* Error Message */}
      {cameraError && (
        <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-md">
          <AlertCircle className="h-4 w-4" />
          <p className="text-sm">{cameraError}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        {!isCameraActive && !capturedImage && (
          <Button onClick={startCamera} className="flex-1" size="lg">
            <Camera className="mr-2 h-4 w-4" />
            Start Camera
          </Button>
        )}

        {isCameraActive && !capturedImage && (
          <>
            <Button onClick={captureImage} className="flex-1" size="lg">
              <Camera className="mr-2 h-4 w-4" />
              Capture Image
            </Button>
            <Button onClick={stopCamera} variant="outline" size="lg">
              Cancel
            </Button>
          </>
        )}

        {capturedImage && (
          <>
            <Button
              onClick={confirmAndUpload}
              className="flex-1"
              size="lg"
              disabled={isLoading}
            >
              <Check className="mr-2 h-4 w-4" />
              {isLoading ? 'Uploading...' : 'Confirm & Analyze'}
            </Button>
            <Button onClick={retakeImage} variant="outline" size="lg" disabled={isLoading}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Retake
            </Button>
          </>
        )}
      </div>

      {/* Helper Text */}
      <div className="text-sm text-muted-foreground text-center">
        {!isCameraActive &&
          !capturedImage &&
          'Position your palm flat in front of the camera with good lighting'}
        {isCameraActive &&
          !capturedImage &&
          'Align your palm with the guide overlay and click capture'}
        {capturedImage && 'Review the image and click confirm to proceed with analysis'}
      </div>
    </div>
  )
}
