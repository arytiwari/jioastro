# Decision Copilot & Prashna Completion Plan

**Date**: 2025-11-09
**Goal**: Complete Decision Copilot (Muhurta) and Prashna to 100%
**Status**: Ready to implement

---

## Current Status Assessment

### ✅ Already Implemented

#### Decision Copilot (Muhurta) - ~80% Complete
**Backend (`app/api/v1/endpoints/muhurta.py`)**:
- ✅ 7 API endpoints (5 authenticated + 2 public)
- ✅ Panchang calculations (Tithi, Nakshatra, Yoga, Karana, Vara)
- ✅ Hora calculations with daily table
- ✅ Activity-based Muhurta finder (5 types: marriage, business, travel, property, surgery)
- ✅ Best time today finder
- ✅ Swiss Ephemeris integration
- ✅ Location-based calculations
- ✅ Sunrise/sunset timing

**Frontend (`app/dashboard/muhurta/page.tsx`)**:
- ✅ Page exists (~30KB, complete UI)
- ✅ Panchang display
- ✅ Hora table
- ✅ Activity selection
- ✅ Date range selection

**Service (`app/services/muhurta_service.py`)**:
- ✅ Complete Panchang calculation
- ✅ Hora sequence calculation
- ✅ Activity-specific Muhurta algorithms
- ✅ Inauspicious time detection (Rahukaal, etc.)

#### Prashna (Horary) - ~70% Complete
**Backend (`app/api/v1/endpoints/prashna.py`)**:
- ✅ 5 API endpoints (analyze, save, list, get, delete)
- ✅ Supabase integration for storage
- ✅ Chart calculation for question moment
- ✅ RLS policies
- ✅ User authentication

**Frontend (`app/dashboard/prashna/page.tsx`)**:
- ✅ Page exists (~22KB, complete UI)
- ✅ Question input form
- ✅ 11 question types supported
- ✅ Location & timezone handling
- ✅ Saved questions list
- ✅ Analysis display

**Service (`app/services/prashna_service.py`)**:
- ✅ Chart calculation for question moment
- ✅ Ascendant analysis
- ✅ Moon analysis (crucial in Prashna)
- ✅ House-based question analysis
- ✅ Karaka (significator) planet analysis
- ✅ Yogas detection
- ✅ Planetary strength calculation
- ✅ **Rule-based answer derivation (scoring system)**

---

## ❌ Missing Components

### Decision Copilot (Muhurta) - 20% Remaining

1. **AI-Powered Decision Guidance** ❌
   - Current: Rule-based Muhurta scoring
   - Needed: GPT-4 powered personalized recommendations
   - Features:
     - Analyze user's natal chart + Muhurta chart
     - Provide detailed pros/cons for specific timing
     - Compare multiple time options
     - Explain WHY a time is good/bad
     - Personalized to user's chart (dasha, transits, strengths)

2. **Chart-Based Timing Optimization** ❌
   - Current: Only Panchang-based selection
   - Needed: Integrate with user's birth chart
   - Features:
     - Avoid user's personal inauspicious times (8th lord transit, etc.)
     - Leverage user's beneficial dashas/transits
     - House-lord analysis for activity
     - D10 (career chart) integration for business timing
     - D7 (children chart) for child-related timing

3. **Frontend Integration** ❌
   - Needed:
     - Chart selection (which chart to use for timing)
     - AI recommendation display
     - Comparison table (multiple time options)
     - Personalization settings

### Prashna - 30% Remaining

1. **AI-Powered Answer Generation** ❌
   - Current: Rule-based scoring (0-100) + generic recommendations
   - Needed: GPT-4 powered detailed analysis
   - Features:
     - Natural language answer (Yes/No/Maybe + explanation)
     - Detailed reasoning based on chart factors
     - Timing prediction (when will it happen?)
     - Obstacles and opportunities
     - Remedies specific to question
     - Confidence level explanation

2. **Enhanced Analysis** ❌
   - Current: Basic house/planet analysis
   - Needed:
     - Aspect analysis (planets aspecting relevant houses)
     - Divisional chart integration (D9 for relationships, D10 for career)
     - Transit influence on question
     - Multi-factor synthesis (not just scoring)

3. **Frontend Enhancement** ❌
   - Needed:
     - Better answer display (formatted, readable)
     - Confidence meter visualization
     - Timing prediction timeline
     - Remedies section
     - Question history with filters

---

## Implementation Plan

### Phase 1: Prashna AI Enhancement (3-4 hours)

#### Step 1.1: Create AI Answer Service
**File**: `backend/app/services/prashna_ai_service.py` (NEW)

```python
class PrashnaAIService:
    """AI-powered Prashna answer generation using GPT-4"""

    def __init__(self, ai_service):
        self.ai_service = ai_service

    async def generate_detailed_answer(
        self,
        question: str,
        question_type: str,
        prashna_chart: Dict,
        user_birth_chart: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI-powered answer

        Returns:
        - answer: Yes/No/Maybe/Uncertain
        - explanation: Detailed reasoning (500-800 words)
        - timing: When it will manifest
        - obstacles: Challenges to overcome
        - opportunities: Favorable factors
        - remedies: Specific actions to take
        - confidence: 0-100 score with explanation
        """
```

**Prompt Template**:
```
You are a master Vedic astrologer analyzing a Prashna (horary) chart.

QUESTION: {question}
TYPE: {question_type}

PRASHNA CHART DATA:
- Query Time: {datetime}
- Ascendant: {lagna_sign} {lagna_degree}° - Lord {lagna_lord} in {lord_house} house
- Moon: {moon_sign} {moon_degree}° in {moon_nakshatra} nakshatra - {moon_strength}
- Relevant House ({question_house}): Lord {house_lord} in {lord_position}
- Karaka Planet ({karaka}): {karaka_sign} {karaka_house} house - {karaka_strength}

PLANETARY POSITIONS:
{planet_details}

YOGAS PRESENT:
{yogas}

ANSWER STRUCTURE (REQUIRED):

1. **Direct Answer**: [Yes / No / Maybe / Uncertain]

2. **Explanation** (500-800 words):
   - Analyze Lagna and its lord
   - Analyze Moon (most important in Prashna)
   - Analyze relevant house for question type
   - Analyze Karaka planet
   - Consider yogas and aspects
   - Synthesize all factors

3. **Timing Prediction**:
   - Most likely timeframe (days/weeks/months)
   - Astrological basis for timing
   - Key dates to watch

4. **Obstacles**:
   - Challenges indicated by chart
   - Planets/houses causing delays
   - What to avoid

5. **Opportunities**:
   - Favorable factors
   - Supportive planets/houses
   - Best approach

6. **Remedies**:
   - 3-5 specific Vedic remedies
   - Planet-specific (if needed)
   - Simple daily practices

7. **Confidence**: [0-100]%
   - Explain confidence level
   - Factors increasing certainty
   - Factors creating doubt

Use traditional Vedic Prashna principles. Be specific, practical, and compassionate.
```

#### Step 1.2: Update Prashna Service
**File**: `backend/app/services/prashna_service.py` (MODIFY)

Add method:
```python
async def analyze_prashna_with_ai(
    self,
    question: str,
    question_type: str,
    query_datetime: datetime,
    latitude: float,
    longitude: float,
    timezone_str: str,
    user_birth_chart_id: Optional[str] = None  # For personalization
) -> Dict[str, Any]:
    """
    Enhanced Prashna analysis with AI-powered answer

    Combines:
    1. Traditional calculations (existing code)
    2. AI-powered detailed answer (new)
    3. Optional birth chart comparison (new)
    """

    # Get traditional analysis (existing code)
    traditional_analysis = self.analyze_prashna(...)

    # Get AI-powered answer
    from app.services.prashna_ai_service import prashna_ai_service
    ai_answer = await prashna_ai_service.generate_detailed_answer(
        question=question,
        question_type=question_type,
        prashna_chart=traditional_analysis
    )

    # Merge results
    return {
        **traditional_analysis,
        "ai_answer": ai_answer,
        "has_ai_analysis": True
    }
```

#### Step 1.3: Update Prashna Endpoint
**File**: `backend/app/api/v1/endpoints/prashna.py` (MODIFY)

Change `/analyze` endpoint to use AI:
```python
@router.post("/analyze", response_model=schemas.PrashnaChartResponse)
async def analyze_prashna(
    request: schemas.PrashnaRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a horary (Prashna) question with AI-powered answer.
    """
    analysis = await prashna_service.analyze_prashna_with_ai(
        question=request.question,
        question_type=request.question_type,
        query_datetime=request.datetime,
        latitude=request.latitude,
        longitude=request.longitude,
        timezone_str=request.timezone
    )
    return analysis
```

#### Step 1.4: Update Prashna Schemas
**File**: `backend/app/schemas/prashna.py` (MODIFY)

Add AI answer schema:
```python
class AIAnswer(BaseModel):
    """AI-generated detailed answer"""
    answer: str  # "Yes", "No", "Maybe", "Uncertain"
    explanation: str  # 500-800 words
    timing: Dict[str, Any]
    obstacles: List[str]
    opportunities: List[str]
    remedies: List[Dict[str, str]]
    confidence: int  # 0-100
    confidence_explanation: str

class PrashnaChartResponse(BaseModel):
    """Enhanced with AI answer"""
    # ... existing fields ...
    ai_answer: Optional[AIAnswer] = None
    has_ai_analysis: bool = False
```

#### Step 1.5: Update Prashna Frontend
**File**: `frontend/app/dashboard/prashna/page.tsx` (MODIFY)

Add AI answer display component:
```typescript
{analysis?.ai_answer && (
  <Card className="mt-6">
    <CardHeader>
      <CardTitle>AI Analysis</CardTitle>
      <CardDescription>Detailed astrological answer</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="space-y-6">
        {/* Direct Answer */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-bold text-lg">Answer: {analysis.ai_answer.answer}</h3>
          <div className="mt-2 flex items-center">
            <span className="text-sm">Confidence:</span>
            <div className="ml-2 flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{width: `${analysis.ai_answer.confidence}%`}}
              />
            </div>
            <span className="ml-2 text-sm font-semibold">{analysis.ai_answer.confidence}%</span>
          </div>
        </div>

        {/* Explanation */}
        <div>
          <h4 className="font-semibold mb-2">Detailed Explanation</h4>
          <p className="text-gray-700 whitespace-pre-wrap">{analysis.ai_answer.explanation}</p>
        </div>

        {/* Timing */}
        <div>
          <h4 className="font-semibold mb-2">⏰ Timing Prediction</h4>
          <div className="bg-yellow-50 p-3 rounded">
            <p>{analysis.ai_answer.timing.timeframe}</p>
            <p className="text-sm text-gray-600 mt-1">{analysis.ai_answer.timing.basis}</p>
          </div>
        </div>

        {/* Obstacles */}
        {analysis.ai_answer.obstacles.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2">⚠️ Obstacles to Watch</h4>
            <ul className="list-disc pl-5 space-y-1">
              {analysis.ai_answer.obstacles.map((obstacle, i) => (
                <li key={i} className="text-gray-700">{obstacle}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Opportunities */}
        {analysis.ai_answer.opportunities.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2">✨ Opportunities</h4>
            <ul className="list-disc pl-5 space-y-1">
              {analysis.ai_answer.opportunities.map((opp, i) => (
                <li key={i} className="text-green-700">{opp}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Remedies */}
        {analysis.ai_answer.remedies.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2">🙏 Remedies</h4>
            <div className="space-y-2">
              {analysis.ai_answer.remedies.map((remedy, i) => (
                <div key={i} className="bg-purple-50 p-3 rounded">
                  <p className="font-medium">{remedy.title}</p>
                  <p className="text-sm text-gray-600">{remedy.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </CardContent>
  </Card>
)}
```

---

### Phase 2: Muhurta AI Enhancement (3-4 hours)

#### Step 2.1: Create Muhurta AI Service
**File**: `backend/app/services/muhurta_ai_service.py` (NEW)

```python
class MuhurtaAIService:
    """AI-powered Decision Copilot for Muhurta"""

    async def generate_decision_guidance(
        self,
        activity_type: str,
        muhurta_options: List[Dict],  # Multiple time options
        user_birth_chart: Optional[Dict] = None,
        user_current_dasha: Optional[Dict] = None,
        user_transits: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized decision guidance

        For each time option, provides:
        - Overall rating (1-10)
        - Detailed pros/cons
        - Personalization factors (if birth chart provided)
        - Best time recommendation
        - Comparison table
        """
```

**Prompt Template**:
```
You are a master Vedic astrologer helping someone choose the best time for: {activity_type}

CANDIDATE TIMES:
{muhurta_options_formatted}

USER'S BIRTH CHART:
{birth_chart_summary}

CURRENT DASHA:
{dasha_period}

CURRENT TRANSITS:
{transit_summary}

TASK:
1. Evaluate each time option (1-10 rating)
2. List pros and cons for each
3. Explain personalization factors (how it relates to user's chart)
4. Recommend the BEST time with clear reasoning
5. Provide a comparison table

Be specific, practical, and consider both traditional Muhurta rules AND personal chart factors.
```

#### Step 2.2: Add Chart Integration to Muhurta Service
**File**: `backend/app/services/muhurta_service.py` (MODIFY)

```python
async def find_muhurta_with_chart_optimization(
    self,
    activity_type: str,
    start_date: datetime,
    end_date: datetime,
    latitude: float,
    longitude: float,
    user_chart_id: Optional[str] = None,  # NEW
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Find Muhurta with personal chart optimization

    Steps:
    1. Get top times using traditional Muhurta rules
    2. If user chart provided:
       - Filter out times during user's 8th lord transit
       - Boost times during beneficial dasha
       - Consider D10 for career, D7 for children, etc.
    3. Get AI-powered comparison and recommendation
    """
```

#### Step 2.3: Update Muhurta Endpoint
**File**: `backend/app/api/v1/endpoints/muhurta.py` (MODIFY)

Add new endpoint:
```python
@router.post("/decision-copilot", response_model=schemas.DecisionCopilotResponse)
async def get_decision_guidance(
    request: schemas.DecisionCopilotRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    AI-powered Decision Copilot for choosing best time.

    Combines:
    - Traditional Muhurta calculation
    - User's personal chart (if provided)
    - Current dashas and transits
    - AI-powered comparison and recommendation
    """
    result = await muhurta_service.find_muhurta_with_chart_optimization(
        activity_type=request.activity_type,
        start_date=request.start_date,
        end_date=request.end_date,
        latitude=request.latitude,
        longitude=request.longitude,
        user_chart_id=request.chart_id,
        max_results=request.max_results
    )

    return result
```

#### Step 2.4: Update Muhurta Frontend
**File**: `frontend/app/dashboard/muhurta/page.tsx` (MODIFY)

Add Decision Copilot section:
```typescript
<Tabs defaultValue="panchang">
  <TabsList>
    <TabsTrigger value="panchang">Panchang</TabsTrigger>
    <TabsTrigger value="hora">Hora</TabsTrigger>
    <TabsTrigger value="muhurta">Find Muhurta</TabsTrigger>
    <TabsTrigger value="copilot">🤖 Decision Copilot</TabsTrigger>  {/* NEW */}
  </TabsList>

  <TabsContent value="copilot">
    {/* Chart selector */}
    <Select value={selectedChartId} onValueChange={setSelectedChartId}>
      <SelectTrigger>
        <SelectValue placeholder="Select your birth chart (optional)" />
      </SelectTrigger>
      <SelectContent>
        {userCharts.map(chart => (
          <SelectItem key={chart.id} value={chart.id}>
            {chart.name} - {chart.date_of_birth}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>

    {/* Activity + Date range (reuse existing UI) */}

    {/* AI Comparison Results */}
    {copilotResult && (
      <div className="space-y-6">
        {/* Recommended Time (highlighted) */}
        <Card className="border-2 border-green-500">
          <CardHeader className="bg-green-50">
            <CardTitle>✨ Recommended Time</CardTitle>
            <CardDescription>{copilotResult.best_time.datetime}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span>Overall Rating:</span>
                <div className="flex items-center">
                  {[...Array(10)].map((_, i) => (
                    <Star key={i} className={i < copilotResult.best_time.rating ? "fill-yellow-400" : "fill-gray-200"} size={16} />
                  ))}
                  <span className="ml-2 font-bold">{copilotResult.best_time.rating}/10</span>
                </div>
              </div>
              <p className="text-sm">{copilotResult.best_time.reasoning}</p>
            </div>
          </CardContent>
        </Card>

        {/* Comparison Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Options Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Pros</TableHead>
                  <TableHead>Cons</TableHead>
                  <TableHead>Personal Factors</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {copilotResult.comparison.map((option, i) => (
                  <TableRow key={i}>
                    <TableCell>{option.datetime}</TableCell>
                    <TableCell>{option.rating}/10</TableCell>
                    <TableCell>
                      <ul className="text-sm list-disc pl-4">
                        {option.pros.slice(0, 2).map((pro, j) => (
                          <li key={j}>{pro}</li>
                        ))}
                      </ul>
                    </TableCell>
                    <TableCell>
                      <ul className="text-sm list-disc pl-4">
                        {option.cons.slice(0, 2).map((con, j) => (
                          <li key={j}>{con}</li>
                        ))}
                      </ul>
                    </TableCell>
                    <TableCell className="text-sm text-gray-600">
                      {option.personalization_note}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    )}
  </TabsContent>
</Tabs>
```

---

## Testing Checklist

### Prashna Testing
- [ ] Analyze a career question
- [ ] Analyze a relationship question
- [ ] Verify AI answer is detailed (500+ words)
- [ ] Check timing prediction makes sense
- [ ] Verify remedies are specific
- [ ] Save and retrieve Prashna
- [ ] Delete Prashna
- [ ] Test with different question types

### Muhurta Testing
- [ ] Get Panchang for today
- [ ] Get Hora for current time
- [ ] Find marriage Muhurta (30-day range)
- [ ] Find business start Muhurta
- [ ] Test Decision Copilot WITHOUT birth chart
- [ ] Test Decision Copilot WITH birth chart
- [ ] Verify AI recommendations are personalized
- [ ] Check comparison table accuracy

---

## Documentation

### API Documentation Updates
- Add `/prashna/analyze` - Enhanced with AI answer
- Add `/muhurta/decision-copilot` - NEW endpoint
- Update Swagger UI with new schemas

### User Guide
- How to ask good Prashna questions
- Understanding AI answer confidence levels
- How to use Decision Copilot
- Interpreting personalized recommendations

---

## Success Metrics

### Prashna Complete (100%) When:
- ✅ AI-powered detailed answers (500+ words)
- ✅ Timing predictions with astrological basis
- ✅ Specific remedies for each question
- ✅ Confidence levels with explanation
- ✅ Frontend displays all AI answer components
- ✅ Save/load functionality works
- ✅ All 11 question types supported

### Muhurta Complete (100%) When:
- ✅ AI-powered Decision Copilot active
- ✅ Chart-based personalization working
- ✅ Multiple time options comparison
- ✅ Detailed pros/cons for each option
- ✅ Best time recommendation with reasoning
- ✅ Frontend displays comparison table
- ✅ All 5 activity types supported

---

## Estimated Timeline

**Total: 6-8 hours**

- Prashna AI Enhancement: 3-4 hours
  - AI service creation: 1 hour
  - Service integration: 1 hour
  - Frontend updates: 1 hour
  - Testing: 0.5-1 hour

- Muhurta AI Enhancement: 3-4 hours
  - AI service creation: 1 hour
  - Chart integration: 1 hour
  - Frontend Decision Copilot tab: 1 hour
  - Testing: 0.5-1 hour

---

## Next Steps

1. ✅ Complete this plan
2. Implement Prashna AI service
3. Update Prashna endpoint and frontend
4. Test Prashna end-to-end
5. Implement Muhurta AI service
6. Update Muhurta endpoint and frontend
7. Test Muhurta end-to-end
8. Create documentation
9. Mark features as 100% complete!

---

**Status**: Ready to implement
**Owner**: Claude Code
**Priority**: HIGH (Magical 12 completion)
