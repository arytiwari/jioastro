'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Plus, Edit, Trash2, Search, MapPin } from '@/components/icons'
import { apiClient } from '@/lib/api'

interface City {
  id: number
  name: string
  state: string
  latitude: number
  longitude: number
  display_name: string
}

export default function AdminCitiesPage() {
  const [cities, setCities] = useState<City[]>([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [editingCity, setEditingCity] = useState<City | null>(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    state: '',
    latitude: '',
    longitude: '',
    display_name: ''
  })

  // Load cities on mount and when search term changes
  useEffect(() => {
    loadCities()
  }, [searchTerm])

  const loadCities = async () => {
    setLoading(true)
    try {
      const response = await apiClient.getCities(searchTerm || undefined, undefined, 100)
      setCities(response.data as City[])
    } catch (error) {
      console.error('Failed to load cities:', error)
      alert('Failed to load cities')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const cityData = {
      name: formData.name,
      state: formData.state,
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude),
      display_name: formData.display_name || `${formData.name}, ${formData.state}`
    }

    try {
      if (editingCity) {
        // Update existing city
        await apiClient.updateCity(editingCity.id, cityData)
        alert('City updated successfully!')
      } else {
        // Create new city
        await apiClient.createCity(cityData)
        alert('City created successfully!')
      }

      // Reset form and reload
      setFormData({ name: '', state: '', latitude: '', longitude: '', display_name: '' })
      setEditingCity(null)
      setShowAddForm(false)
      loadCities()
    } catch (error) {
      console.error('Error saving city:', error)
      alert('Failed to save city')
    }
  }

  const handleEdit = (city: City) => {
    setEditingCity(city)
    setFormData({
      name: city.name,
      state: city.state,
      latitude: city.latitude.toString(),
      longitude: city.longitude.toString(),
      display_name: city.display_name
    })
    setShowAddForm(true)
  }

  const handleDelete = async (city: City) => {
    if (!confirm(`Are you sure you want to delete "${city.display_name}"?`)) {
      return
    }

    try {
      await apiClient.deleteCity(city.id)
      alert('City deleted successfully!')
      loadCities()
    } catch (error) {
      console.error('Error deleting city:', error)
      alert('Failed to delete city')
    }
  }

  const handleCancel = () => {
    setFormData({ name: '', state: '', latitude: '', longitude: '', display_name: '' })
    setEditingCity(null)
    setShowAddForm(false)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">City Master Management</h1>
          <p className="text-muted-foreground">
            Add, edit, and manage cities with geographic coordinates
          </p>
        </div>
        <Button onClick={() => setShowAddForm(!showAddForm)}>
          <Plus className="w-4 h-4 mr-2" />
          Add New City
        </Button>
      </div>

      {/* Add/Edit Form */}
      {showAddForm && (
        <Card>
          <CardHeader>
            <CardTitle>{editingCity ? 'Edit City' : 'Add New City'}</CardTitle>
            <CardDescription>
              Enter city details with latitude and longitude coordinates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">City Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="e.g., New Delhi"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="state">State/Province *</Label>
                  <Input
                    id="state"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    placeholder="e.g., Delhi"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="latitude">Latitude *</Label>
                  <Input
                    id="latitude"
                    type="number"
                    step="any"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                    placeholder="e.g., 28.6139"
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="longitude">Longitude *</Label>
                  <Input
                    id="longitude"
                    type="number"
                    step="any"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                    placeholder="e.g., 77.2090"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="display_name">Display Name (Optional)</Label>
                <Input
                  id="display_name"
                  value={formData.display_name}
                  onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                  placeholder="Auto-generated if left empty"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Leave empty to auto-generate as "City, State"
                </p>
              </div>

              <div className="flex gap-2">
                <Button type="submit">
                  {editingCity ? 'Update City' : 'Create City'}
                </Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search cities by name or state..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" onClick={loadCities}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Cities List */}
      <Card>
        <CardHeader>
          <CardTitle>Cities ({cities.length})</CardTitle>
          <CardDescription>
            Manage your city master database
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : cities.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No cities found. Add your first city to get started.
            </div>
          ) : (
            <div className="space-y-2">
              {cities.map((city) => (
                <div
                  key={city.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <MapPin className="w-5 h-5 text-muted-foreground mt-0.5" />
                    <div>
                      <div className="font-semibold">{city.display_name}</div>
                      <div className="text-sm text-muted-foreground">
                        {city.name}, {city.state}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        Lat: {city.latitude.toFixed(4)}, Lon: {city.longitude.toFixed(4)}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(city)}
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(city)}
                      className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
