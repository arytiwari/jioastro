'use client'

import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { HelpCircle } from '@/components/icons'

// Vedic Astrology Terms Dictionary
const ASTRO_TERMS: Record<string, string> = {
  // Chart Types
  'D1': 'Rashi Chart - The main birth chart showing planetary positions in zodiac signs and houses',
  'D9': 'Navamsa Chart - Divisional chart for marriage, dharma, and soul purpose. Shows deeper karmic patterns',
  'Navamsa': 'D9 chart representing marriage compatibility and spiritual evolution',

  // Basic Concepts
  'Lagna': 'Ascendant - The rising sign at time of birth. Represents your outward personality and physical body',
  'Ascendant': 'Rising sign at birth time. First house cusp representing self, personality, and physical appearance',
  'Rashi': 'Zodiac sign. One of 12 divisions of the celestial sphere',

  // Planets
  'Sun': 'Surya - Represents soul, father, authority, vitality, and government',
  'Moon': 'Chandra - Represents mind, mother, emotions, and mental stability',
  'Mercury': 'Budha - Represents intelligence, communication, business, and analytical skills',
  'Venus': 'Shukra - Represents love, beauty, luxury, arts, and relationships',
  'Mars': 'Mangal - Represents energy, courage, siblings, property, and aggression',
  'Jupiter': 'Guru - Represents wisdom, knowledge, children, wealth, and spirituality',
  'Saturn': 'Shani - Represents discipline, karma, delays, longevity, and hard work',
  'Rahu': 'North Node - Represents desires, materialism, foreign connections, and sudden events',
  'Ketu': 'South Node - Represents spirituality, moksha, past life, and detachment',

  // Dashas
  'Dasha': 'Planetary period - A time period ruled by a specific planet affecting life events',
  'Vimshottari Dasha': '120-year cycle system showing planetary periods and their sub-periods',
  'Mahadasha': 'Major planetary period lasting from 6 to 20 years depending on the planet',
  'Antardasha': 'Sub-period within a Mahadasha, ruled by another planet',

  // Yogas
  'Yoga': 'Planetary combination creating specific effects. Can be auspicious or inauspicious',
  'Raj Yoga': 'Royal combination - Brings success, power, authority, and high status',
  'Dhana Yoga': 'Wealth combination - Creates prosperity and financial abundance',
  'Gaja Kesari': 'Elephant-Lion Yoga - Moon-Jupiter combination bringing wisdom and respect',

  // Doshas
  'Dosha': 'Astrological affliction caused by planetary positions creating challenges',
  'Manglik': 'Mars affliction affecting marriage. Causes in 7th house or aspecting it',
  'Kaal Sarpa': 'Rahu-Ketu axis affliction. All planets between nodes creating restrictions',
  'Pitra Dosha': 'Ancestral affliction - Issues from past generations needing remedies',
  'Sade Sati': '7.5 year Saturn transit over natal Moon. Brings challenges and karmic lessons',

  // Houses
  '1st House': 'Lagna Bhava - Self, personality, physical body, overall life path',
  '2nd House': 'Dhana Bhava - Wealth, family, speech, food, early childhood',
  '4th House': 'Sukha Bhava - Mother, home, property, vehicles, inner peace',
  '5th House': 'Putra Bhava - Children, education, creativity, past life merit',
  '7th House': 'Kalatra Bhava - Marriage, partnerships, business, spouse',
  '9th House': 'Dharma Bhava - Father, luck, religion, higher education, long journeys',
  '10th House': 'Karma Bhava - Career, profession, reputation, authority',
  '11th House': 'Labha Bhava - Gains, income, friends, fulfillment of desires',

  // Transit Terms
  'Transit': 'Gochar - Current movement of planets affecting your natal chart',
  'Gochar': 'Planetary transits - Current positions of planets relative to birth chart',
  'Retrograde': 'Vakri - Planet appearing to move backward. Intensifies its effects',

  // Strength
  'Shadbala': 'Six-fold strength calculation measuring planetary power and effectiveness',
  'Exalted': 'Uchcha - Planet in its most powerful sign giving best results',
  'Debilitated': 'Neecha - Planet in its weakest sign giving challenging results',
  'Own Sign': 'Swa-Rashi - Planet in the sign it rules, comfortable and stable',

  // Numerology
  'Life Path': 'Your life\'s purpose and main lessons calculated from birth date',
  'Expression Number': 'Natural talents and abilities from your full name',
  'Soul Urge': 'Inner desires and motivations from vowels in your name',
  'Psychic Number': 'Moolank - Your inner self from birth day (Vedic numerology)',
  'Destiny Number': 'Bhagyank - How others see you from full birth date (Vedic numerology)',
}

interface AstroTermProps {
  term: string
  children?: React.ReactNode
  className?: string
}

export function AstroTerm({ term, children, className }: AstroTermProps) {
  const definition = ASTRO_TERMS[term]

  if (!definition) {
    return <span className={className}>{children || term}</span>
  }

  return (
    <TooltipProvider>
      <Tooltip delayDuration={200}>
        <TooltipTrigger asChild>
          <span className={`inline-flex items-center gap-1 cursor-help border-b border-dotted border-gray-400 ${className || ''}`}>
            {children || term}
            <HelpCircle className="w-3 h-3 text-gray-500" />
          </span>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs">
          <p className="text-sm">{definition}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

// Convenience component for inline terms without children
export function Term({ term }: { term: string }) {
  return <AstroTerm term={term} />
}
