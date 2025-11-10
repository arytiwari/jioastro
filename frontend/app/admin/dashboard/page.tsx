'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

interface Document {
  id: string
  title: string
  description?: string
  document_type: string
  file_size?: number
  original_filename?: string
  is_indexed: string | boolean  // Handle both string and boolean from backend
  created_at: string
  tags?: string[]
  doc_metadata?: {
    text_length?: number
    num_chunks?: number
    num_embeddings?: number
    processing_time_seconds?: number
    processed_at?: string
    error?: string
  }
}

// Helper function to normalize is_indexed value to string
function normalizeIndexedStatus(value: string | boolean): 'false' | 'processing' | 'true' | 'failed' {
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false'
  }
  return value as 'false' | 'processing' | 'true' | 'failed'
}

interface UserProfile {
  id: string
  name: string
  birth_date: string
  birth_city?: string
  created_at: string
}

export default function AdminDashboardPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [adminUsername, setAdminUsername] = useState('')
  const [activeTab, setActiveTab] = useState<'knowledge' | 'users' | 'cities'>('knowledge')

  // Knowledge Bank State
  const [documents, setDocuments] = useState<Document[]>([])
  const [loadingDocuments, setLoadingDocuments] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileTitle, setFileTitle] = useState('')
  const [fileDescription, setFileDescription] = useState('')
  const [fileType, setFileType] = useState('text')
  const [fileTags, setFileTags] = useState('')
  const [uploadingFile, setUploadingFile] = useState(false)

  // User Management State
  const [users, setUsers] = useState<UserProfile[]>([])
  const [loadingUsers, setLoadingUsers] = useState(false)
  const [usersError, setUsersError] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    const username = localStorage.getItem('admin_username')

    if (!token || !username) {
      router.push('/admin/login')
      return
    }

    setIsAuthenticated(true)
    setAdminUsername(username)
  }, [router])

  useEffect(() => {
    if (isAuthenticated && activeTab === 'knowledge') {
      loadDocuments()
    }
  }, [isAuthenticated, activeTab])

  // Smart polling: only refresh when there are processing documents
  useEffect(() => {
    if (!isAuthenticated || activeTab !== 'knowledge') return

    // Check if any documents are currently processing
    const hasProcessingDocs = documents.some(doc => {
      const status = normalizeIndexedStatus(doc.is_indexed)
      return status === 'processing' || status === 'false'
    })

    if (!hasProcessingDocs) return // No need to poll

    // Poll every 5 seconds only when documents are processing
    const pollInterval = setInterval(() => {
      loadDocuments(true) // Pass true to indicate this is a background refresh
    }, 5000) // Increased to 5 seconds to reduce refresh frequency

    return () => clearInterval(pollInterval)
  }, [isAuthenticated, activeTab, documents])

  useEffect(() => {
    if (isAuthenticated && activeTab === 'users') {
      loadUsers()
    }
  }, [isAuthenticated, activeTab])

  const getAuthHeaders = () => {
    const token = localStorage.getItem('admin_token')
    return {
      'Authorization': `Bearer ${token}`,
    }
  }

  const loadDocuments = async (isBackgroundRefresh = false) => {
    // Only show loading spinner during initial load, not during background polling
    if (!isBackgroundRefresh) {
      setLoadingDocuments(true)
    }
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge?limit=100`,
        { headers: getAuthHeaders() }
      )

      if (!response.ok) throw new Error('Failed to load documents')

      const data = await response.json()
      if (!isBackgroundRefresh) {
        console.log('📄 Documents loaded:', data.documents)
      }
      setDocuments(data.documents || [])
    } catch (err) {
      console.error('Error loading documents:', err)
      if (!isBackgroundRefresh) {
        alert('Failed to load documents')
      }
    } finally {
      if (!isBackgroundRefresh) {
        setLoadingDocuments(false)
      }
    }
  }

  const loadUsers = async () => {
    setLoadingUsers(true)
    setUsersError(null)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/users?limit=100`,
        { headers: getAuthHeaders() }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        console.error('Failed to load users:', response.status, errorData)
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      console.log('👥 Users loaded:', data)
      setUsers(data || [])
      setUsersError(null)
    } catch (err: any) {
      console.error('Error loading users:', err)
      setUsersError(err.message || 'Failed to load users')
      setUsers([])
    } finally {
      setLoadingUsers(false)
    }
  }

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!selectedFile || !fileTitle) {
      alert('Please select a file and provide a title')
      return
    }

    setUploadingFile(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('title', fileTitle)
      if (fileDescription) formData.append('description', fileDescription)
      formData.append('document_type', fileType)
      if (fileTags) formData.append('tags', fileTags)

      const token = localStorage.getItem('admin_token')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge/upload`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const uploadedDoc = await response.json()

      // Reset form - clear file input properly
      setSelectedFile(null)
      setFileTitle('')
      setFileDescription('')
      setFileTags('')
      setFileType('text')

      // Clear file input element
      const fileInput = document.getElementById('file') as HTMLInputElement
      if (fileInput) fileInput.value = ''

      // Reload documents to show the new upload
      loadDocuments()
    } catch (err: any) {
      console.error('Upload error:', err)
      alert(`Upload failed: ${err.message}`)
    } finally {
      setUploadingFile(false)
    }
  }

  const handleProcessDocument = async (docId: string, title: string) => {
    if (!confirm(`Process "${title}"? This will extract rules and generate embeddings.`)) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge/${docId}/process`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Processing failed')
      }

      const result = await response.json()
      alert(result.message || 'Processing started successfully')
      loadDocuments() // Refresh to show updated status
    } catch (err: any) {
      console.error('Process error:', err)
      alert(`Failed to process document: ${err.message}`)
    }
  }

  const handleDeleteDocument = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/knowledge/${docId}`,
        {
          method: 'DELETE',
          headers: getAuthHeaders(),
        }
      )

      if (!response.ok) throw new Error('Delete failed')

      alert('Document deleted successfully')
      loadDocuments()
    } catch (err) {
      console.error('Delete error:', err)
      alert('Failed to delete document')
    }
  }

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user profile?')) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/admin/users/${userId}`,
        {
          method: 'DELETE',
          headers: getAuthHeaders(),
        }
      )

      if (!response.ok) throw new Error('Delete failed')

      alert('User deleted successfully')
      loadUsers()
    } catch (err) {
      console.error('Delete error:', err)
      alert('Failed to delete user')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_id')
    localStorage.removeItem('admin_username')
    router.push('/admin/login')
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Welcome back, {adminUsername}</p>
            </div>
            <div className="flex items-center gap-3">
              <Button onClick={() => router.push('/admin/dashboard/knowledge')} variant="default">
                📊 View Knowledge Base
              </Button>
              <Button onClick={handleLogout} variant="outline">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('knowledge')}
              className={`${
                activeTab === 'knowledge'
                  ? 'border-jio-600 text-jio-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Knowledge Bank
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`${
                activeTab === 'users'
                  ? 'border-jio-600 text-jio-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              User Management
            </button>
            <button
              onClick={() => router.push('/admin/dashboard/cities')}
              className={`${
                activeTab === 'cities'
                  ? 'border-jio-600 text-jio-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              City Management
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'knowledge' && (
          <div className="space-y-6">
            {/* Upload Form */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Knowledge Document</CardTitle>
                <CardDescription>
                  Upload text, PDF, Word documents, or images to enrich the AI knowledge base
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleFileUpload} className="space-y-4">
                  <div>
                    <Label htmlFor="file">File</Label>
                    <Input
                      id="file"
                      type="file"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      accept=".txt,.pdf,.doc,.docx,.jpg,.jpeg,.png"
                      required
                    />
                    <p className="text-sm text-gray-500 mt-1">Max size: 50MB</p>
                  </div>

                  <div>
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={fileTitle}
                      onChange={(e) => setFileTitle(e.target.value)}
                      placeholder="Document title"
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="description">Description (Optional)</Label>
                    <Textarea
                      id="description"
                      value={fileDescription}
                      onChange={(e) => setFileDescription(e.target.value)}
                      placeholder="Brief description of the document"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="type">Document Type</Label>
                    <Select value={fileType} onValueChange={setFileType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="text">Text</SelectItem>
                        <SelectItem value="pdf">PDF</SelectItem>
                        <SelectItem value="word">Word Document</SelectItem>
                        <SelectItem value="image">Image</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="tags">Tags (Optional)</Label>
                    <Input
                      id="tags"
                      value={fileTags}
                      onChange={(e) => setFileTags(e.target.value)}
                      placeholder="planets, houses, yogas (comma-separated)"
                    />
                  </div>

                  <Button type="submit" disabled={uploadingFile}>
                    {uploadingFile ? 'Uploading...' : 'Upload Document'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Documents List */}
            <Card>
              <CardHeader>
                <CardTitle>Uploaded Documents</CardTitle>
                <CardDescription>
                  Document status updates automatically every 5 seconds (only when processing)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loadingDocuments ? (
                  <div className="text-center py-8">
                    <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  </div>
                ) : documents.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No documents uploaded yet</p>
                ) : (
                  <div className="space-y-4">
                    {documents.map((doc) => (
                      <div
                        key={doc.id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium">{doc.title}</h3>
                            {/* Status Badge */}
                            {normalizeIndexedStatus(doc.is_indexed) === 'false' && (
                              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                                ⏳ Pending
                              </span>
                            )}
                            {normalizeIndexedStatus(doc.is_indexed) === 'processing' && (
                              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded flex items-center gap-1">
                                <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                                🔄 Processing
                              </span>
                            )}
                            {normalizeIndexedStatus(doc.is_indexed) === 'true' && (
                              <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded flex items-center gap-1">
                                <span className="text-green-600">✓</span>
                                ✅ Ready for Inference
                              </span>
                            )}
                            {normalizeIndexedStatus(doc.is_indexed) === 'failed' && (
                              <span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded">
                                ❌ Failed
                              </span>
                            )}
                          </div>
                          {doc.description && (
                            <p className="text-sm text-gray-600 mt-1">{doc.description}</p>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <span className="capitalize">{doc.document_type}</span>
                            {doc.file_size && (
                              <span>{(doc.file_size / 1024).toFixed(2)} KB</span>
                            )}
                            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                          </div>
                          {/* Show processing info if available */}
                          {normalizeIndexedStatus(doc.is_indexed) === 'true' && doc.doc_metadata && (
                            <div className="mt-2 text-xs text-gray-500">
                              Processed: {doc.doc_metadata.num_chunks || 0} chunks, {doc.doc_metadata.num_embeddings || 0} embeddings
                              {doc.doc_metadata.processing_time_seconds && (
                                <span> ({doc.doc_metadata.processing_time_seconds.toFixed(1)}s)</span>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          {/* Show Process button for pending or failed documents */}
                          {(normalizeIndexedStatus(doc.is_indexed) === 'false' ||
                            normalizeIndexedStatus(doc.is_indexed) === 'failed') && (
                            <Button
                              onClick={() => handleProcessDocument(doc.id, doc.title)}
                              variant="default"
                              size="sm"
                            >
                              Process
                            </Button>
                          )}
                          <Button
                            onClick={() => handleDeleteDocument(doc.id)}
                            variant="destructive"
                            size="sm"
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>User Profiles</CardTitle>
                  <Button onClick={loadUsers} variant="outline" size="sm">
                    Refresh
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loadingUsers ? (
                  <div className="text-center py-8">
                    <div className="w-8 h-8 border-4 border-jio-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  </div>
                ) : usersError ? (
                  <div className="text-center py-8">
                    <p className="text-red-600 mb-2">❌ {usersError}</p>
                    <Button onClick={loadUsers} variant="outline" size="sm">
                      Try Again
                    </Button>
                  </div>
                ) : users.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No users found</p>
                ) : (
                  <div className="space-y-4">
                    {users.map((user) => (
                      <div
                        key={user.id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                      >
                        <div className="flex-1">
                          <h3 className="font-medium">{user.name}</h3>
                          <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            <span>Born: {new Date(user.birth_date).toLocaleDateString()}</span>
                            {user.birth_city && <span>{user.birth_city}</span>}
                            <span>
                              Joined: {new Date(user.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        <Button
                          onClick={() => handleDeleteUser(user.id)}
                          variant="destructive"
                          size="sm"
                        >
                          Delete
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  )
}
