import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, TrendingUp, AlertTriangle } from '@/components/icons'
import { cn } from '@/lib/utils'

interface CycleData {
  number: number
  meaning?: string
  start_date?: string
  end_date?: string
}

interface PinnacleData extends CycleData {
  age_range?: string
}

interface ChallengeData extends CycleData {
  age_range?: string
}

interface CyclesTimelineProps {
  personalYear?: CycleData
  personalMonth?: CycleData
  personalDay?: CycleData
  pinnacles?: PinnacleData[]
  challenges?: ChallengeData[]
  universalYear?: CycleData
}

export function CyclesTimeline({
  personalYear,
  personalMonth,
  personalDay,
  pinnacles,
  challenges,
  universalYear,
}: CyclesTimelineProps) {
  return (
    <div className="space-y-6">
      {/* Current Cycles */}
      {(personalYear || personalMonth || personalDay) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Current Cycles
            </CardTitle>
            <CardDescription>Your active numerology cycles today</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {personalYear && (
                <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
                  <div className="flex items-center justify-center w-12 h-12 bg-purple-600 text-white rounded-full font-bold">
                    {personalYear.number}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">Personal Year</div>
                    <div className="text-xs text-gray-600 mt-1">{personalYear.meaning}</div>
                  </div>
                </div>
              )}
              {personalMonth && (
                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-full font-bold">
                    {personalMonth.number}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">Personal Month</div>
                    <div className="text-xs text-gray-600 mt-1">{personalMonth.meaning}</div>
                  </div>
                </div>
              )}
              {personalDay && (
                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-center w-12 h-12 bg-green-600 text-white rounded-full font-bold">
                    {personalDay.number}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-sm">Personal Day</div>
                    <div className="text-xs text-gray-600 mt-1">{personalDay.meaning}</div>
                  </div>
                </div>
              )}
            </div>

            {universalYear && (
              <div className="pt-4 border-t">
                <div className="text-sm text-gray-600">
                  <span className="font-semibold">Universal Year {universalYear.number}:</span>{' '}
                  {universalYear.meaning}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Pinnacles - Life Periods */}
      {pinnacles && pinnacles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Pinnacles - Life Achievement Periods
            </CardTitle>
            <CardDescription>Four major life periods showing opportunities and growth</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

              <div className="space-y-6">
                {pinnacles.map((pinnacle, idx) => (
                  <div key={idx} className="relative pl-14">
                    {/* Timeline dot */}
                    <div className="absolute left-4 top-2 w-4 h-4 bg-purple-600 rounded-full border-4 border-white shadow"></div>

                    <div className="bg-white border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-semibold">
                          Pinnacle {idx + 1}
                          {pinnacle.age_range && (
                            <span className="ml-2 text-sm text-gray-500">({pinnacle.age_range})</span>
                          )}
                        </div>
                        <div className="flex items-center justify-center w-10 h-10 bg-purple-100 text-purple-700 rounded-full font-bold">
                          {pinnacle.number}
                        </div>
                      </div>
                      {pinnacle.meaning && (
                        <div className="text-sm text-gray-600">{pinnacle.meaning}</div>
                      )}
                      {(pinnacle.start_date || pinnacle.end_date) && (
                        <div className="text-xs text-gray-500 mt-2">
                          {pinnacle.start_date} - {pinnacle.end_date}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Challenges - Life Lessons */}
      {challenges && challenges.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Challenges - Life Lessons
            </CardTitle>
            <CardDescription>Four life challenges showing areas requiring growth</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {challenges.map((challenge, idx) => (
                <div key={idx} className="border rounded-lg p-4 bg-orange-50">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-semibold">
                      Challenge {idx + 1}
                      {challenge.age_range && (
                        <span className="ml-2 text-sm text-gray-500">({challenge.age_range})</span>
                      )}
                    </div>
                    <div className="flex items-center justify-center w-10 h-10 bg-orange-200 text-orange-700 rounded-full font-bold">
                      {challenge.number}
                    </div>
                  </div>
                  {challenge.meaning && (
                    <div className="text-sm text-gray-600">{challenge.meaning}</div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
