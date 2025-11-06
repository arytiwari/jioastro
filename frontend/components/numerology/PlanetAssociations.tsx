import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Sun, Moon, Sparkles, Gem } from '@/components/icons'
import { cn } from '@/lib/utils'

interface PlanetData {
  number: number
  planet: string
  favorable_dates?: number[]
  favorable_colors?: string[]
  favorable_gems?: string[]
  favorable_days?: string[]
  meaning?: string
}

interface PlanetAssociationsProps {
  psychicNumber?: PlanetData
  destinyNumber?: PlanetData
}

const planetIcons: { [key: string]: React.ReactNode } = {
  Sun: <Sun className="w-6 h-6" />,
  Moon: <Moon className="w-6 h-6" />,
  Jupiter: <Sparkles className="w-6 h-6" />,
  Rahu: <Moon className="w-6 h-6" />,
  Mercury: <Sparkles className="w-6 h-6" />,
  Venus: <Sparkles className="w-6 h-6" />,
  Ketu: <Sparkles className="w-6 h-6" />,
  Saturn: <Moon className="w-6 h-6" />,
  Mars: <Sparkles className="w-6 h-6" />,
}

const planetColors: { [key: string]: string } = {
  Sun: 'orange',
  Moon: 'blue',
  Jupiter: 'yellow',
  Rahu: 'gray',
  Mercury: 'green',
  Venus: 'pink',
  Ketu: 'purple',
  Saturn: 'black',
  Mars: 'red',
}

function PlanetCard({ data, title }: { data: PlanetData; title: string }) {
  const planet = data.planet
  const colorClass = planetColors[planet] || 'purple'

  const bgColorClass = cn({
    'bg-orange-100 text-orange-700': colorClass === 'orange',
    'bg-blue-100 text-blue-700': colorClass === 'blue',
    'bg-yellow-100 text-yellow-700': colorClass === 'yellow',
    'bg-gray-100 text-gray-700': colorClass === 'gray',
    'bg-green-100 text-green-700': colorClass === 'green',
    'bg-pink-100 text-pink-700': colorClass === 'pink',
    'bg-purple-100 text-purple-700': colorClass === 'purple',
    'bg-slate-100 text-slate-700': colorClass === 'black',
    'bg-red-100 text-red-700': colorClass === 'red',
  })

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{title}</CardTitle>
          <div className={cn('p-2 rounded-full', bgColorClass)}>
            {planetIcons[planet] || <Sparkles className="w-6 h-6" />}
          </div>
        </div>
        <CardDescription>Number {data.number}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="text-lg font-bold mb-2">{planet}</div>
          {data.meaning && <div className="text-sm text-gray-600">{data.meaning}</div>}
        </div>

        <div className="space-y-3">
          {data.favorable_dates && data.favorable_dates.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
                Favorable Dates
              </div>
              <div className="flex flex-wrap gap-2">
                {data.favorable_dates.map((date) => (
                  <span
                    key={date}
                    className={cn('px-2 py-1 rounded text-sm font-medium', bgColorClass)}
                  >
                    {date}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.favorable_days && data.favorable_days.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
                Favorable Days
              </div>
              <div className="flex flex-wrap gap-2">
                {data.favorable_days.map((day) => (
                  <span
                    key={day}
                    className="px-2 py-1 rounded text-xs bg-gray-100 text-gray-700"
                  >
                    {day}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.favorable_colors && data.favorable_colors.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-600 uppercase mb-1 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Favorable Colors
              </div>
              <div className="flex flex-wrap gap-2">
                {data.favorable_colors.map((color) => (
                  <span
                    key={color}
                    className="px-3 py-1 rounded text-xs bg-gray-100 text-gray-700 capitalize"
                  >
                    {color}
                  </span>
                ))}
              </div>
            </div>
          )}

          {data.favorable_gems && data.favorable_gems.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-600 uppercase mb-1 flex items-center gap-1">
                <Gem className="w-3 h-3" />
                Favorable Gems
              </div>
              <div className="flex flex-wrap gap-2">
                {data.favorable_gems.map((gem) => (
                  <span
                    key={gem}
                    className="px-3 py-1 rounded text-xs bg-gray-100 text-gray-700 capitalize"
                  >
                    {gem}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export function PlanetAssociations({ psychicNumber, destinyNumber }: PlanetAssociationsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {psychicNumber && <PlanetCard data={psychicNumber} title="Psychic Number (Moolank)" />}
      {destinyNumber && <PlanetCard data={destinyNumber} title="Destiny Number (Bhagyank)" />}
    </div>
  )
}
