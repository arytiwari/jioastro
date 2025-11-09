'use client'

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Upload, X, Check, Image as ImageIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ImageUploadProps {
  onImageUploaded: (imageData: string, handType: 'left' | 'right', viewType: string) => void
  isLoading?: boolean
}

export default function ImageUpload({ onImageUploaded, isLoading }: ImageUploadProps) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [handType, setHandType] = useState<'left' | 'right'>('left')
  const [viewType, setViewType] = useState<string>('front')
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const imageData = e.target?.result as string
        setSelectedImage(imageData)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleClear = () => {
    setSelectedImage(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleConfirm = () => {
    if (selectedImage) {
      onImageUploaded(selectedImage, handType, viewType)
      handleClear()
    }
  }

  return (
    <div className="space-y-6">
      {/* Hand and View Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="upload-hand-type">Hand</Label>
          <Select value={handType} onValueChange={(value: any) => setHandType(value)}>
            <SelectTrigger id="upload-hand-type">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="left">Left Hand</SelectItem>
              <SelectItem value="right">Right Hand</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="upload-view-type">View Type</Label>
          <Select value={viewType} onValueChange={setViewType}>
            <SelectTrigger id="upload-view-type">
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

      {/* Upload Area */}
      <Card
        className={cn(
          'relative overflow-hidden transition-colors cursor-pointer',
          isDragging && 'border-primary bg-primary/5',
          selectedImage && 'border-2 border-primary'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !selectedImage && fileInputRef.current?.click()}
      >
        <div className="aspect-video w-full">
          {selectedImage ? (
            <div className="relative w-full h-full">
              <img
                src={selectedImage}
                alt="Selected palm"
                className="w-full h-full object-contain bg-black"
              />
              <Button
                size="icon"
                variant="destructive"
                className="absolute top-2 right-2"
                onClick={(e) => {
                  e.stopPropagation()
                  handleClear()
                }}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center space-y-4">
              <div className="rounded-full bg-primary/10 p-6">
                {isDragging ? (
                  <Upload className="h-12 w-12 text-primary animate-bounce" />
                ) : (
                  <ImageIcon className="h-12 w-12 text-muted-foreground" />
                )}
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">
                  {isDragging ? 'Drop image here' : 'Upload Palm Image'}
                </h3>
                <p className="text-sm text-muted-foreground">
                  Click to browse or drag and drop your image
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports: JPG, PNG, WEBP (max 10MB)
                </p>
              </div>
            </div>
          )}
        </div>
      </Card>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleInputChange}
        className="hidden"
      />

      {/* Action Buttons */}
      {selectedImage && (
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handleConfirm}
            className="flex-1"
            size="lg"
            disabled={isLoading}
          >
            <Check className="mr-2 h-4 w-4" />
            {isLoading ? 'Uploading...' : 'Confirm & Analyze'}
          </Button>
          <Button onClick={handleClear} variant="outline" size="lg" disabled={isLoading}>
            <X className="mr-2 h-4 w-4" />
            Clear
          </Button>
        </div>
      )}

      {/* Helper Text */}
      <div className="text-sm text-muted-foreground text-center">
        {!selectedImage && 'Select a clear, well-lit photo of your palm'}
        {selectedImage && 'Review the image and click confirm to proceed with analysis'}
      </div>
    </div>
  )
}
