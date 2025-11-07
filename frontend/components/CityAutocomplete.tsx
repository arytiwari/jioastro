'use client'

import { useState, useEffect, useRef } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiClient } from '@/lib/api'

interface City {
  id: number
  name: string
  state: string
  latitude: number
  longitude: number
  display_name: string
}

interface CityAutocompleteProps {
  onCitySelect: (city: City) => void
  disabled?: boolean
  initialValue?: string
}

export function CityAutocomplete({ onCitySelect, disabled, initialValue = '' }: CityAutocompleteProps) {
  const [searchTerm, setSearchTerm] = useState(initialValue)
  const [cities, setCities] = useState<City[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedCity, setSelectedCity] = useState<City | null>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

  // Fetch cities based on search term
  useEffect(() => {
    const fetchCities = async () => {
      if (searchTerm.length < 2) {
        setCities([])
        return
      }

      // Don't search if the searchTerm matches the selected city
      if (selectedCity && searchTerm === selectedCity.display_name) {
        return
      }

      setLoading(true)
      try {
        const response = await apiClient.getCities(searchTerm, undefined, 50)
        setCities(response.data as City[])
        setIsOpen(true)
      } catch (error) {
        console.error('Failed to fetch cities:', error)
        setCities([])
      } finally {
        setLoading(false)
      }
    }

    // Debounce the search
    const timeoutId = setTimeout(() => {
      fetchCities()
    }, 300)

    return () => clearTimeout(timeoutId)
  }, [searchTerm, selectedCity])

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
    setSelectedCity(null)
  }

  const handleCityClick = (city: City) => {
    setSelectedCity(city)
    setSearchTerm(city.display_name)
    setIsOpen(false)
    onCitySelect(city)
  }

  return (
    <div className="space-y-2" ref={wrapperRef}>
      <Label htmlFor="city-search">Birth City</Label>
      <div className="relative">
        <Input
          id="city-search"
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder="Search for a city (e.g., Mumbai, Delhi)..."
          disabled={disabled}
          onFocus={() => {
            if (cities.length > 0) setIsOpen(true)
          }}
          className="w-full"
        />

        {loading && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-blue-600" />
          </div>
        )}

        {isOpen && cities.length > 0 && (
          <div className="absolute z-50 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg max-h-60 overflow-auto">
            {cities.map((city) => (
              <button
                key={city.id}
                type="button"
                onClick={() => handleCityClick(city)}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none transition-colors"
              >
                <div className="font-medium">{city.name}</div>
                <div className="text-sm text-gray-600">{city.state}</div>
              </button>
            ))}
          </div>
        )}

        {isOpen && searchTerm.length >= 2 && cities.length === 0 && !loading && (
          <div className="absolute z-50 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg p-4 text-center text-gray-500">
            No cities found. Try a different search term.
          </div>
        )}
      </div>

      {selectedCity && (
        <p className="text-xs text-gray-500">
          Selected: {selectedCity.display_name} (Lat: {selectedCity.latitude}, Lon: {selectedCity.longitude})
        </p>
      )}

      <p className="text-xs text-gray-500">
        Search for your birth city from 700+ Indian cities and towns
      </p>
    </div>
  )
}
