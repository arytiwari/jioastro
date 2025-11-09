"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Settings, Clock, Users, BookmarkPlus, Play, Trash2, Download } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { useToast } from "@/hooks/use-toast"

interface ExpertSettings {
  id: string
  user_id: string
  preferred_ayanamsa: string
  preferred_house_system: string
  show_seconds: boolean
  show_retrograde_symbols: boolean
  show_dignity_symbols: boolean
  decimal_precision: number
  use_true_node: boolean
  include_uranus: boolean
  include_neptune: boolean
  include_pluto: boolean
  default_vargas: string[]
  enable_rectification_tools: boolean
  enable_bulk_analysis: boolean
  enable_custom_exports: boolean
}

interface RectificationSession {
  id: string
  original_name: string
  original_date: string
  original_time: string
  status: string
  tested_times_count: number
  best_match_time?: string
  best_match_score?: number
  created_at: string
}

interface BulkJob {
  id: string
  job_name: string
  analysis_type: string
  total_profiles: number
  status: string
  processed_count: number
  failed_count: number
  created_at: string
}

interface Preset {
  id: string
  preset_name: string
  preset_description?: string
  is_public: boolean
  ayanamsa: string
  house_system: string
  usage_count: number
  created_at: string
}

export default function ExpertConsolePage() {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('settings')

  // Settings state
  const [settings, setSettings] = useState<ExpertSettings | null>(null)
  const [loadingSettings, setLoadingSettings] = useState(true)

  // Rectification state
  const [rectificationSessions, setRectificationSessions] = useState<RectificationSession[]>([])
  const [loadingRectification, setLoadingRectification] = useState(false)

  // Bulk jobs state
  const [bulkJobs, setBulkJobs] = useState<BulkJob[]>([])
  const [loadingBulkJobs, setLoadingBulkJobs] = useState(false)

  // Presets state
  const [presets, setPresets] = useState<Preset[]>([])
  const [loadingPresets, setLoadingPresets] = useState(false)

  // Load settings on mount
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoadingSettings(true)
      const response = await apiClient.get('/expert/settings')
      setSettings(response.data)
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to load settings",
        variant: "destructive"
      })
    } finally {
      setLoadingSettings(false)
    }
  }

  const updateSettings = async (updates: Partial<ExpertSettings>) => {
    try {
      const response = await apiClient.patch('/expert/settings', updates)
      setSettings(response.data)
      toast({
        title: "Success",
        description: "Settings updated successfully"
      })
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to update settings",
        variant: "destructive"
      })
    }
  }

  const loadRectificationSessions = async () => {
    try {
      setLoadingRectification(true)
      const response = await apiClient.get('/expert/rectification')
      setRectificationSessions(response.data.sessions || [])
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load rectification sessions",
        variant: "destructive"
      })
    } finally {
      setLoadingRectification(false)
    }
  }

  const loadBulkJobs = async () => {
    try {
      setLoadingBulkJobs(true)
      const response = await apiClient.get('/expert/bulk-jobs')
      setBulkJobs(response.data.jobs || [])
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load bulk jobs",
        variant: "destructive"
      })
    } finally {
      setLoadingBulkJobs(false)
    }
  }

  const loadPresets = async () => {
    try {
      setLoadingPresets(true)
      const response = await apiClient.get('/expert/presets')
      setPresets(response.data.presets || [])
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to load presets",
        variant: "destructive"
      })
    } finally {
      setLoadingPresets(false)
    }
  }

  // Load data when switching tabs
  useEffect(() => {
    if (activeTab === 'rectification' && rectificationSessions.length === 0) {
      loadRectificationSessions()
    } else if (activeTab === 'bulk' && bulkJobs.length === 0) {
      loadBulkJobs()
    } else if (activeTab === 'presets' && presets.length === 0) {
      loadPresets()
    }
  }, [activeTab])

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Expert Console</h1>
        <p className="text-muted-foreground">
          Professional astrologer tools: custom settings, rectification, bulk analysis, and presets
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Settings
          </TabsTrigger>
          <TabsTrigger value="rectification" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Rectification
          </TabsTrigger>
          <TabsTrigger value="bulk" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            Bulk Analysis
          </TabsTrigger>
          <TabsTrigger value="presets" className="flex items-center gap-2">
            <BookmarkPlus className="h-4 w-4" />
            Presets
          </TabsTrigger>
        </TabsList>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Calculation Preferences</CardTitle>
              <CardDescription>
                Configure your preferred ayanamsa and house system
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingSettings ? (
                <div className="text-center py-8">Loading settings...</div>
              ) : settings ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="ayanamsa">Preferred Ayanamsa</Label>
                      <Select
                        value={settings.preferred_ayanamsa}
                        onValueChange={(value) => updateSettings({ preferred_ayanamsa: value })}
                      >
                        <SelectTrigger id="ayanamsa">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="lahiri">Lahiri (Chitrapaksha)</SelectItem>
                          <SelectItem value="raman">Raman</SelectItem>
                          <SelectItem value="krishnamurti">Krishnamurti (KP)</SelectItem>
                          <SelectItem value="yukteshwar">Sri Yukteshwar</SelectItem>
                          <SelectItem value="jn_bhasin">JN Bhasin</SelectItem>
                          <SelectItem value="true_citra">True Chitrapaksha</SelectItem>
                          <SelectItem value="true_revati">True Revati</SelectItem>
                          <SelectItem value="true_pushya">True Pushya</SelectItem>
                          <SelectItem value="galactic_center">Galactic Center</SelectItem>
                          <SelectItem value="none">Tropical (No Ayanamsa)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="house-system">House System</Label>
                      <Select
                        value={settings.preferred_house_system}
                        onValueChange={(value) => updateSettings({ preferred_house_system: value })}
                      >
                        <SelectTrigger id="house-system">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="placidus">Placidus</SelectItem>
                          <SelectItem value="koch">Koch</SelectItem>
                          <SelectItem value="equal">Equal House</SelectItem>
                          <SelectItem value="whole_sign">Whole Sign</SelectItem>
                          <SelectItem value="porphyry">Porphyry</SelectItem>
                          <SelectItem value="regiomontanus">Regiomontanus</SelectItem>
                          <SelectItem value="campanus">Campanus</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-sm font-medium mb-3">Display Options</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label htmlFor="show-seconds" className="cursor-pointer">Show Seconds</Label>
                        <Switch
                          id="show-seconds"
                          checked={settings.show_seconds}
                          onCheckedChange={(checked) => updateSettings({ show_seconds: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="show-retrograde" className="cursor-pointer">Show Retrograde Symbols</Label>
                        <Switch
                          id="show-retrograde"
                          checked={settings.show_retrograde_symbols}
                          onCheckedChange={(checked) => updateSettings({ show_retrograde_symbols: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="show-dignity" className="cursor-pointer">Show Dignity Symbols</Label>
                        <Switch
                          id="show-dignity"
                          checked={settings.show_dignity_symbols}
                          onCheckedChange={(checked) => updateSettings({ show_dignity_symbols: checked })}
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-sm font-medium mb-3">Advanced Options</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label htmlFor="true-node" className="cursor-pointer">Use True Node (vs Mean Node)</Label>
                        <Switch
                          id="true-node"
                          checked={settings.use_true_node}
                          onCheckedChange={(checked) => updateSettings({ use_true_node: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="uranus" className="cursor-pointer">Include Uranus</Label>
                        <Switch
                          id="uranus"
                          checked={settings.include_uranus}
                          onCheckedChange={(checked) => updateSettings({ include_uranus: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="neptune" className="cursor-pointer">Include Neptune</Label>
                        <Switch
                          id="neptune"
                          checked={settings.include_neptune}
                          onCheckedChange={(checked) => updateSettings({ include_neptune: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="pluto" className="cursor-pointer">Include Pluto</Label>
                        <Switch
                          id="pluto"
                          checked={settings.include_pluto}
                          onCheckedChange={(checked) => updateSettings({ include_pluto: checked })}
                        />
                      </div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h3 className="text-sm font-medium mb-3">Professional Features</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label htmlFor="rectification" className="cursor-pointer">Enable Rectification Tools</Label>
                        <Switch
                          id="rectification"
                          checked={settings.enable_rectification_tools}
                          onCheckedChange={(checked) => updateSettings({ enable_rectification_tools: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="bulk-analysis" className="cursor-pointer">Enable Bulk Analysis</Label>
                        <Switch
                          id="bulk-analysis"
                          checked={settings.enable_bulk_analysis}
                          onCheckedChange={(checked) => updateSettings({ enable_bulk_analysis: checked })}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label htmlFor="custom-exports" className="cursor-pointer">Enable Custom Exports</Label>
                        <Switch
                          id="custom-exports"
                          checked={settings.enable_custom_exports}
                          onCheckedChange={(checked) => updateSettings({ enable_custom_exports: checked })}
                        />
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">Failed to load settings</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rectification Tab */}
        <TabsContent value="rectification" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Birth Time Rectification</CardTitle>
              <CardDescription>
                Refine birth time using life events and dasha analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">Rectification Sessions</h3>
                <p className="text-muted-foreground mb-4">
                  {loadingRectification
                    ? "Loading sessions..."
                    : rectificationSessions.length === 0
                    ? "No rectification sessions yet"
                    : `${rectificationSessions.length} session(s) found`}
                </p>
                <Button>
                  <Clock className="h-4 w-4 mr-2" />
                  Create New Session
                </Button>
              </div>

              {rectificationSessions.length > 0 && (
                <div className="mt-6 space-y-4">
                  {rectificationSessions.map((session) => (
                    <Card key={session.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold">{session.original_name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {session.original_date} at {session.original_time}
                            </p>
                          </div>
                          <Badge variant={
                            session.status === 'completed' ? 'default' :
                            session.status === 'running' ? 'secondary' :
                            session.status === 'failed' ? 'destructive' : 'outline'
                          }>
                            {session.status}
                          </Badge>
                        </div>
                        {session.best_match_time && (
                          <div className="mt-4 p-3 bg-muted rounded-lg">
                            <p className="text-sm font-medium">Best Match: {session.best_match_time}</p>
                            <p className="text-sm text-muted-foreground">
                              Score: {session.best_match_score?.toFixed(2)}% confidence
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Bulk Analysis Tab */}
        <TabsContent value="bulk" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Bulk Analysis Jobs</CardTitle>
              <CardDescription>
                Process multiple charts in batches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">Bulk Processing</h3>
                <p className="text-muted-foreground mb-4">
                  {loadingBulkJobs
                    ? "Loading jobs..."
                    : bulkJobs.length === 0
                    ? "No bulk jobs yet"
                    : `${bulkJobs.length} job(s) found`}
                </p>
                <Button>
                  <Users className="h-4 w-4 mr-2" />
                  Create New Job
                </Button>
              </div>

              {bulkJobs.length > 0 && (
                <div className="mt-6 space-y-4">
                  {bulkJobs.map((job) => (
                    <Card key={job.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h4 className="font-semibold">{job.job_name}</h4>
                            <p className="text-sm text-muted-foreground">{job.analysis_type}</p>
                          </div>
                          <Badge variant={
                            job.status === 'completed' ? 'default' :
                            job.status === 'processing' ? 'secondary' :
                            job.status === 'failed' ? 'destructive' : 'outline'
                          }>
                            {job.status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>{job.total_profiles} profiles</span>
                          <span>•</span>
                          <span>{job.processed_count} processed</span>
                          {job.failed_count > 0 && (
                            <>
                              <span>•</span>
                              <span className="text-destructive">{job.failed_count} failed</span>
                            </>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Presets Tab */}
        <TabsContent value="presets" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Calculation Presets</CardTitle>
              <CardDescription>
                Save and reuse calculation configurations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BookmarkPlus className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">Saved Presets</h3>
                <p className="text-muted-foreground mb-4">
                  {loadingPresets
                    ? "Loading presets..."
                    : presets.length === 0
                    ? "No presets saved yet"
                    : `${presets.length} preset(s) available`}
                </p>
                <Button>
                  <BookmarkPlus className="h-4 w-4 mr-2" />
                  Create New Preset
                </Button>
              </div>

              {presets.length > 0 && (
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {presets.map((preset) => (
                    <Card key={preset.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold">{preset.preset_name}</h4>
                          {preset.is_public && <Badge variant="secondary">Public</Badge>}
                        </div>
                        {preset.preset_description && (
                          <p className="text-sm text-muted-foreground mb-3">
                            {preset.preset_description}
                          </p>
                        )}
                        <div className="text-sm space-y-1">
                          <p><span className="font-medium">Ayanamsa:</span> {preset.ayanamsa}</p>
                          <p><span className="font-medium">House System:</span> {preset.house_system}</p>
                          <p className="text-muted-foreground">Used {preset.usage_count} times</p>
                        </div>
                        <div className="flex gap-2 mt-4">
                          <Button size="sm" variant="outline" className="flex-1">
                            Apply
                          </Button>
                          <Button size="sm" variant="ghost">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
