'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Mic, MicOff, Volume2, VolumeX, Send, Loader2 } from '@/components/icons'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  originalContent?: string  // Original language before translation
  language?: string
  timestamp: Date
  isVoice?: boolean
}

interface VoiceConversationProps {
  onSendMessage: (message: string, language: string, isVoice: boolean) => Promise<string>
  selectedLanguage: string
  profileId: string
}

const SUPPORTED_LANGUAGES = [
  { code: 'en-US', name: 'English', flag: '🇺🇸', ttsCode: 'en-US' },
  { code: 'hi-IN', name: 'Hindi', flag: '🇮🇳', ttsCode: 'hi-IN' },
  { code: 'mr-IN', name: 'Marathi', flag: '🇮🇳', ttsCode: 'mr-IN' },
  { code: 'gu-IN', name: 'Gujarati', flag: '🇮🇳', ttsCode: 'gu-IN' },
  { code: 'ta-IN', name: 'Tamil', flag: '🇮🇳', ttsCode: 'ta-IN' },
  { code: 'te-IN', name: 'Telugu', flag: '🇮🇳', ttsCode: 'te-IN' },
  { code: 'kn-IN', name: 'Kannada', flag: '🇮🇳', ttsCode: 'kn-IN' },
  { code: 'bn-IN', name: 'Bengali', flag: '🇮🇳', ttsCode: 'bn-IN' },
  { code: 'pa-IN', name: 'Punjabi', flag: '🇮🇳', ttsCode: 'pa-IN' },
  { code: 'es-ES', name: 'Spanish', flag: '🇪🇸', ttsCode: 'es-ES' },
  { code: 'fr-FR', name: 'French', flag: '🇫🇷', ttsCode: 'fr-FR' },
  { code: 'de-DE', name: 'German', flag: '🇩🇪', ttsCode: 'de-DE' },
  { code: 'zh-CN', name: 'Chinese', flag: '🇨🇳', ttsCode: 'zh-CN' },
  { code: 'ja-JP', name: 'Japanese', flag: '🇯🇵', ttsCode: 'ja-JP' },
  { code: 'ko-KR', name: 'Korean', flag: '🇰🇷', ttsCode: 'ko-KR' },
]

export function VoiceConversation({ onSendMessage, selectedLanguage: initialLanguage, profileId }: VoiceConversationProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [autoPlayVoice, setAutoPlayVoice] = useState(true)
  const [selectedLanguage, setSelectedLanguage] = useState(initialLanguage || 'en-US')

  const recognitionRef = useRef<any>(null)
  const synthRef = useRef<SpeechSynthesis | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize Speech Recognition
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = selectedLanguage

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        console.log('🎤 Voice input:', transcript)
        setInputText(transcript)
        setIsRecording(false)

        // Auto-submit after a brief delay to allow user to see the transcription
        setTimeout(() => {
          if (transcript.trim()) {
            handleSendMessage(transcript)
          }
        }, 500)
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsRecording(false)
      }

      recognitionRef.current.onend = () => {
        setIsRecording(false)
      }
    }

    // Initialize Speech Synthesis
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (synthRef.current) {
        synthRef.current.cancel()
      }
    }
  }, [selectedLanguage])

  useEffect(() => {
    // Update recognition language when selected language changes
    if (recognitionRef.current) {
      recognitionRef.current.lang = selectedLanguage
    }
  }, [selectedLanguage])

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startRecording = () => {
    if (recognitionRef.current && !isRecording) {
      try {
        recognitionRef.current.start()
        setIsRecording(true)
        console.log('🎤 Started recording in language:', selectedLanguage)
      } catch (error) {
        console.error('Failed to start recording:', error)
      }
    }
  }

  const stopRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop()
      setIsRecording(false)
    }
  }

  const speakText = (text: string, language: string) => {
    if (!synthRef.current || !autoPlayVoice) return

    // Cancel any ongoing speech
    synthRef.current.cancel()

    const utterance = new SpeechSynthesisUtterance(text)

    // Find appropriate voice for the language
    const voices = synthRef.current.getVoices()
    const langCode = language.split('-')[0] // Get base language code (e.g., 'hi' from 'hi-IN')
    const voice = voices.find(v => v.lang.startsWith(langCode) || v.lang === language)

    if (voice) {
      utterance.voice = voice
    }
    utterance.lang = language
    utterance.rate = 0.9
    utterance.pitch = 1

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = (error) => {
      console.error('Speech synthesis error:', error)
      setIsSpeaking(false)
    }

    synthRef.current.speak(utterance)
  }

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel()
      setIsSpeaking(false)
    }
  }

  const handleSendMessage = async (messageText?: string | React.MouseEvent) => {
    // If messageText is an event object (from button click), ignore it and use inputText
    const textToSend = (typeof messageText === 'string' ? messageText : inputText)
    if (!textToSend || !textToSend.trim() || isProcessing) return

    const wasVoice = isRecording || (typeof messageText === 'string' && !!messageText)  // If messageText is a string, it came from voice

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      language: selectedLanguage,
      timestamp: new Date(),
      isVoice: wasVoice
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsProcessing(true)

    try {
      // Send message to backend with language info
      const response = await onSendMessage(textToSend, selectedLanguage, wasVoice)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        language: selectedLanguage,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // Auto-play voice response if enabled
      if (autoPlayVoice) {
        speakText(response, selectedLanguage)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        language: 'en-US',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const currentLangInfo = SUPPORTED_LANGUAGES.find(l => l.code === selectedLanguage) || SUPPORTED_LANGUAGES[0]

  return (
    <div className="flex flex-col h-full">
      {/* Language Selector */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700">Language</label>
          <button
            onClick={() => setAutoPlayVoice(!autoPlayVoice)}
            className="flex items-center gap-2 text-xs text-gray-600 hover:text-gray-900"
          >
            {autoPlayVoice ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            Auto-play voice {autoPlayVoice ? 'ON' : 'OFF'}
          </button>
        </div>
        <select
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value)}
          className="w-full p-2 border rounded-md"
        >
          {SUPPORTED_LANGUAGES.map(lang => (
            <option key={lang.code} value={lang.code}>
              {lang.flag} {lang.name}
            </option>
          ))}
        </select>
        <p className="text-xs text-gray-500 mt-2">
          Speak or type in {currentLangInfo.name}. Responses will be in the same language.
        </p>
      </div>

      {/* Messages Container */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-12">
              <Mic className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-sm">Start a conversation by typing or using voice input</p>
              <p className="text-xs mt-2">Ask about your birth chart in any supported language</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-jio-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-xs opacity-70">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                  {message.isVoice && (
                    <span className="text-xs opacity-70">🎤</span>
                  )}
                  {message.role === 'assistant' && (
                    <button
                      onClick={() => speakText(message.content, message.language || selectedLanguage)}
                      className="text-xs opacity-70 hover:opacity-100"
                    >
                      <Volume2 className="w-3 h-3" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isProcessing && (
            <div className="flex justify-start">
              <div className="bg-gray-100 p-3 rounded-lg">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>
      </Card>

      {/* Input Area */}
      <div className="mt-4 flex gap-2">
        <div className="flex-1 relative">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Type or speak your question in ${currentLangInfo.name}...`}
            className="w-full p-3 pr-12 border rounded-lg resize-none focus:ring-2 focus:ring-jio-500 focus:border-transparent"
            rows={2}
            disabled={isProcessing || isRecording}
          />
          {isRecording && (
            <div className="absolute top-2 right-2 flex items-center gap-1 text-red-600 animate-pulse">
              <div className="w-2 h-2 bg-red-600 rounded-full animate-ping" />
              <span className="text-xs">Recording...</span>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2">
          <Button
            onClick={isRecording ? stopRecording : startRecording}
            variant={isRecording ? "destructive" : "outline"}
            size="icon"
            disabled={isProcessing}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </Button>

          <Button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isProcessing}
            size="icon"
          >
            <Send className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {isSpeaking && (
        <button
          onClick={stopSpeaking}
          className="mt-2 w-full p-2 bg-orange-100 text-orange-800 rounded-md text-sm hover:bg-orange-200 transition-colors"
        >
          🔊 Speaking... (Click to stop)
        </button>
      )}
    </div>
  )
}
