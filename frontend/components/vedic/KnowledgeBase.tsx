'use client'

import React, { useState } from 'react'

interface KnowledgeItem {
  name?: string
  description?: string
  nature?: string
  strength?: string
  house?: number
  signifies?: string
  planet?: string
  years?: number
  number?: number
  lord?: string
  symbol?: string
  note?: string
}

interface KnowledgeData {
  title: string
  description: string
  items: KnowledgeItem[]
}

const VEDIC_KNOWLEDGE: Record<string, KnowledgeData> = {
  planets: {
    title: 'Vedic Planets (Grahas)',
    description: 'The nine planets in Vedic astrology and their significations',
    items: [
      { name: 'Sun (Surya)', nature: 'Soul, authority, father, government', strength: 'Exalted in Aries, debilitated in Libra' },
      { name: 'Moon (Chandra)', nature: 'Mind, mother, emotions, public', strength: 'Exalted in Taurus, debilitated in Scorpio' },
      { name: 'Mars (Mangala)', nature: 'Energy, courage, siblings, property', strength: 'Exalted in Capricorn, debilitated in Cancer' },
      { name: 'Mercury (Budha)', nature: 'Intelligence, communication, business', strength: 'Exalted in Virgo, debilitated in Pisces' },
      { name: 'Jupiter (Guru)', nature: 'Wisdom, children, wealth, spirituality', strength: 'Exalted in Cancer, debilitated in Capricorn' },
      { name: 'Venus (Shukra)', nature: 'Love, marriage, luxury, arts', strength: 'Exalted in Pisces, debilitated in Virgo' },
      { name: 'Saturn (Shani)', nature: 'Discipline, karma, delays, longevity', strength: 'Exalted in Libra, debilitated in Aries' },
      { name: 'Rahu (North Node)', nature: 'Desires, illusions, foreign, technology', strength: 'Exalted in Taurus/Gemini' },
      { name: 'Ketu (South Node)', nature: 'Spirituality, detachment, past life', strength: 'Exalted in Scorpio/Sagittarius' }
    ]
  },
  houses: {
    title: 'Vedic Houses (Bhavas)',
    description: 'The twelve houses representing different life areas',
    items: [
      { house: 1, name: 'Tanu Bhava', signifies: 'Self, personality, physical body, appearance' },
      { house: 2, name: 'Dhana Bhava', signifies: 'Wealth, family, speech, food' },
      { house: 3, name: 'Sahaja Bhava', signifies: 'Siblings, courage, communication, short journeys' },
      { house: 4, name: 'Sukha Bhava', signifies: 'Mother, home, property, happiness, education' },
      { house: 5, name: 'Putra Bhava', signifies: 'Children, creativity, intelligence, romance' },
      { house: 6, name: 'Ripu Bhava', signifies: 'Enemies, diseases, debts, service' },
      { house: 7, name: 'Kalatra Bhava', signifies: 'Spouse, partnerships, marriage' },
      { house: 8, name: 'Ayu Bhava', signifies: 'Longevity, transformation, occult, inheritance' },
      { house: 9, name: 'Dharma Bhava', signifies: 'Father, fortune, religion, higher education' },
      { house: 10, name: 'Karma Bhava', signifies: 'Career, status, reputation, authority' },
      { house: 11, name: 'Labha Bhava', signifies: 'Gains, friends, aspirations, income' },
      { house: 12, name: 'Vyaya Bhava', signifies: 'Losses, expenses, foreign lands, spirituality' }
    ]
  },
  yogas: {
    title: 'Major Vedic Yogas',
    description: 'Important planetary combinations that influence life events',
    items: [
      { name: 'Raj Yoga', description: 'Combination of 9th and 10th lords brings power and success' },
      { name: 'Dhana Yoga', description: 'Wealth combinations from 2nd, 5th, 9th, 11th lords' },
      { name: 'Gaja Kesari Yoga', description: 'Jupiter in Kendra from Moon - wisdom and prosperity' },
      { name: 'Budhaditya Yoga', description: 'Sun-Mercury conjunction enhances intelligence' },
      { name: 'Chandra-Mangala Yoga', description: 'Moon-Mars combination for wealth' },
      { name: 'Pancha Mahapurusha Yoga', description: 'Five great yogas from Mars, Mercury, Jupiter, Venus, Saturn' },
      { name: 'Neecha Bhanga Raj Yoga', description: 'Cancellation of debilitation creates powerful yoga' }
    ]
  },
  nakshatras: {
    title: 'Nakshatras (Lunar Mansions)',
    description: '27 lunar mansions in Vedic astrology, each spanning 13°20\'',
    items: [
      { number: 1, name: 'Ashwini', lord: 'Ketu', symbol: 'Horse head' },
      { number: 2, name: 'Bharani', lord: 'Venus', symbol: 'Yoni' },
      { number: 3, name: 'Krittika', lord: 'Sun', symbol: 'Razor' },
      { number: 4, name: 'Rohini', lord: 'Moon', symbol: 'Chariot' },
      { number: 5, name: 'Mrigashira', lord: 'Mars', symbol: 'Deer head' },
      { number: 6, name: 'Ardra', lord: 'Rahu', symbol: 'Teardrop' },
      { number: 7, name: 'Punarvasu', lord: 'Jupiter', symbol: 'Bow and quiver' },
      { number: 8, name: 'Pushya', lord: 'Saturn', symbol: 'Cow udder' },
      { number: 9, name: 'Ashlesha', lord: 'Mercury', symbol: 'Serpent' },
      { note: 'Total 27 nakshatras, each spanning 13°20\' of the zodiac' }
    ]
  },
  dashas: {
    title: 'Vimshottari Dasha System',
    description: '120-year planetary period system based on Moon\'s nakshatra',
    items: [
      { planet: 'Ketu', years: 7, nature: 'Spiritual transformation' },
      { planet: 'Venus', years: 20, nature: 'Comfort, luxury, relationships' },
      { planet: 'Sun', years: 6, nature: 'Authority, recognition' },
      { planet: 'Moon', years: 10, nature: 'Emotional growth, public life' },
      { planet: 'Mars', years: 7, nature: 'Energy, conflicts, property' },
      { planet: 'Rahu', years: 18, nature: 'Desires, foreign connections' },
      { planet: 'Jupiter', years: 16, nature: 'Expansion, wisdom, children' },
      { planet: 'Saturn', years: 19, nature: 'Discipline, delays, karma' },
      { planet: 'Mercury', years: 17, nature: 'Learning, business, communication' }
    ]
  }
}

export function KnowledgeBase() {
  const [selectedTopic, setSelectedTopic] = useState<string>('planets')

  const topics = [
    { id: 'planets', icon: '🪐', label: 'Planets' },
    { id: 'houses', icon: '🏠', label: 'Houses' },
    { id: 'yogas', icon: '✨', label: 'Yogas' },
    { id: 'nakshatras', icon: '⭐', label: 'Nakshatras' },
    { id: 'dashas', icon: '⏰', label: 'Dashas' }
  ]

  const currentKnowledge = VEDIC_KNOWLEDGE[selectedTopic]

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      {/* Topic Selector */}
      <div className="flex flex-wrap justify-center gap-2 mb-6">
        {topics.map((topic) => (
          <button
            key={topic.id}
            onClick={() => setSelectedTopic(topic.id)}
            className={`px-4 py-2 rounded-lg border-2 transition-all ${
              selectedTopic === topic.id
                ? 'border-jio-600 bg-jio-50 text-jio-900 font-semibold shadow-md'
                : 'border-gray-300 bg-white text-gray-700 hover:border-jio-400 hover:bg-jio-50'
            }`}
          >
            <span className="text-xl mr-2">{topic.icon}</span>
            {topic.label}
          </button>
        ))}
      </div>

      {/* Knowledge Content */}
      <div className="space-y-4">
        <div className="border-b pb-3">
          <h2 className="text-2xl font-bold text-gray-900">{currentKnowledge.title}</h2>
          <p className="text-sm text-gray-600 mt-1">{currentKnowledge.description}</p>
        </div>

        <div className="space-y-3">
          {currentKnowledge.items.map((item, index) => {
            if (item.note) {
              return (
                <div key={index} className="text-sm text-gray-500 italic text-center p-3 bg-gray-50 rounded-lg">
                  {item.note}
                </div>
              )
            }

            return (
              <div
                key={index}
                className="p-4 rounded-lg border-2 border-gray-200 bg-gray-50 hover:border-jio-300 hover:bg-jio-50 transition-all"
              >
                <div className="space-y-2">
                  {/* Title/Name */}
                  {item.name && (
                    <h3 className="font-bold text-lg text-gray-900">{item.name}</h3>
                  )}

                  {/* House number */}
                  {item.house !== undefined && (
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-jio-600 text-white font-bold rounded-md text-sm">
                        House {item.house}
                      </span>
                      <span className="font-semibold text-gray-800">{item.name}</span>
                    </div>
                  )}

                  {/* Planet info for dashas */}
                  {item.planet && item.years && (
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-gray-900">{item.planet}</span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded">
                        {item.years} years
                      </span>
                    </div>
                  )}

                  {/* Nakshatra info */}
                  {item.number !== undefined && item.lord && (
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2 py-1 bg-amber-600 text-white font-bold rounded text-sm">
                        #{item.number}
                      </span>
                      <span className="font-bold text-gray-900">{item.name}</span>
                      <span className="text-sm text-gray-600">Lord: {item.lord}</span>
                      <span className="text-sm text-gray-500 italic">{item.symbol}</span>
                    </div>
                  )}

                  {/* Description/Nature */}
                  {item.description && (
                    <p className="text-sm text-gray-700">{item.description}</p>
                  )}
                  {item.nature && (
                    <p className="text-sm text-gray-700"><span className="font-semibold">Signifies:</span> {item.nature}</p>
                  )}
                  {item.signifies && (
                    <p className="text-sm text-gray-700">{item.signifies}</p>
                  )}

                  {/* Strength info */}
                  {item.strength && (
                    <p className="text-xs text-gray-600 mt-1"><span className="font-semibold">Strength:</span> {item.strength}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Attribution */}
      <div className="mt-6 pt-4 border-t text-center">
        <p className="text-xs text-gray-500">
          Based on classical Vedic astrology texts and principles
        </p>
      </div>
    </div>
  )
}
