# Guided Rituals (#7) - Implementation Plan

**Date**: 2025-01-09
**Status**: Planning
**Priority**: Magical 12 Feature #7

---

## 🎯 Feature Overview

**Guided Rituals** provides interactive, step-by-step instructions for performing Vedic rituals with voice guidance, visual aids, and progress tracking.

### Key Capabilities:
- 🎙️ **Voice Guidance**: Text-to-speech for each ritual step
- 📋 **Step-by-Step Instructions**: Clear, sequential guidance
- ⏱️ **Timing**: Duration estimates and notifications
- ✅ **Progress Tracking**: Save ritual completion status
- 📸 **Visual Aids**: Diagrams, images, and videos
- 🔔 **Reminders**: Notifications for ritual times
- 🌐 **Multi-Language**: Support for Sanskrit mantras with transliteration
- 📱 **AR (Future)**: Augmented reality overlays for advanced features

---

## 📊 System Architecture

### 1. Backend Components

#### A. Ritual Templates Database
**Table**: `ritual_templates`
```sql
- id (UUID)
- name (TEXT) - "Ganesh Puja", "Navagraha Puja"
- category (TEXT) - "daily", "special", "remedial", "festival"
- deity (TEXT) - "Ganesha", "Shiva", "Lakshmi"
- duration_minutes (INTEGER)
- difficulty (TEXT) - "beginner", "intermediate", "advanced"
- required_items (JSONB) - List of materials needed
- steps (JSONB) - Array of step objects
- audio_enabled (BOOLEAN)
- created_at, updated_at
```

**Step Object Structure**:
```json
{
  "step_number": 1,
  "title": "Purification (Achamana)",
  "description": "Sip water three times while chanting mantras",
  "mantra": "Om Keshavaya Namaha",
  "mantra_translation": "Salutations to Lord Keshava",
  "duration_seconds": 60,
  "visual_aid_url": "/images/rituals/achamana.jpg",
  "audio_instruction_url": "/audio/rituals/achamana_en.mp3",
  "required_items": ["water", "spoon"],
  "tips": ["Sit facing East", "Use clean water"]
}
```

#### B. User Ritual Progress
**Table**: `user_ritual_sessions`
```sql
- id (UUID)
- user_id (UUID)
- ritual_template_id (UUID)
- started_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- current_step (INTEGER)
- status (TEXT) - "in_progress", "completed", "paused", "abandoned"
- notes (TEXT)
```

#### C. Ritual Library Service
**File**: `backend/app/services/ritual_service.py`

**Methods**:
- `get_all_rituals()` - List all available rituals
- `get_ritual_by_id(ritual_id)` - Get specific ritual with all steps
- `get_rituals_by_category(category)` - Filter by category
- `get_rituals_by_deity(deity)` - Filter by deity
- `search_rituals(query)` - Search by name/description
- `start_ritual_session(user_id, ritual_id)` - Begin new session
- `update_progress(session_id, step_number)` - Mark step complete
- `complete_ritual(session_id)` - Mark ritual complete
- `get_user_ritual_history(user_id)` - Get past rituals

#### D. AI Enhancement Service (Optional)
**File**: `backend/app/services/ritual_ai_service.py`

**Methods**:
- `generate_personalized_ritual(user_chart, purpose)` - Create custom ritual
- `explain_ritual_significance(ritual_id, user_context)` - AI explanation
- `suggest_best_time(ritual_id, user_location)` - Muhurta for ritual

---

### 2. Frontend Components

#### A. Ritual Library Page
**Path**: `/dashboard/rituals/page.tsx`

**Features**:
- Grid view of all rituals with cards
- Filter by category, deity, difficulty
- Search functionality
- Quick info: duration, difficulty, required items
- Start ritual button

**UI Elements**:
- Category tabs: Daily | Special | Remedial | Festival
- Deity filter dropdown
- Difficulty badges
- Duration indicator
- Material checklist preview

#### B. Ritual Player Component
**Path**: `/dashboard/rituals/[id]/player/page.tsx`

**Features**:
- Large step display with number
- Title and description
- Mantra display with transliteration
- Audio playback controls
- Progress bar (X of Y steps)
- Previous/Next navigation
- Pause/Resume
- Exit with save progress
- Timer for each step
- Visual aids (images/diagrams)

**UI Layout**:
```
+----------------------------------+
|  [<] Ganesh Puja            [X]  |
|  Step 3 of 12 [========>    ]   |
+----------------------------------+
|                                  |
|  [Large Visual Aid Image]        |
|                                  |
+----------------------------------+
| 3. Offer Flowers                 |
| Place fresh flowers at the feet  |
| of Lord Ganesha while chanting:  |
|                                  |
| ॐ गं गणपतये नमः                  |
| Om Gam Ganapataye Namaha         |
| Salutations to Lord Ganesha      |
|                                  |
| Duration: 2 minutes              |
+----------------------------------+
| [🔊 Play Audio] [Pause] [Done]  |
| [← Previous]  [Skip]  [Next →]  |
+----------------------------------+
```

#### C. Voice Controls Component
**Component**: `RitualVoicePlayer.tsx`

**Features**:
- Text-to-speech for instructions
- Mantra pronunciation audio (pre-recorded)
- Play/Pause/Stop controls
- Speed adjustment (0.75x, 1x, 1.25x)
- Voice selection (male/female, language)
- Auto-advance option

**Browser API**: Web Speech API (speech synthesis)

#### D. AR Viewer Component (Future Phase)
**Component**: `RitualARView.tsx`

**Features** (Phase 2):
- Camera overlay with step indicators
- 3D placement guides for items
- Gesture recognition for step completion
- AR markers for ritual area setup

---

### 3. API Endpoints

#### Ritual Management
```
GET    /api/v1/rituals                 - List all rituals
GET    /api/v1/rituals/{id}            - Get ritual details
GET    /api/v1/rituals/category/{cat}  - Filter by category
GET    /api/v1/rituals/deity/{deity}   - Filter by deity
GET    /api/v1/rituals/search?q={query} - Search rituals
```

#### Session Management
```
POST   /api/v1/rituals/{id}/start      - Start ritual session
PUT    /api/v1/rituals/sessions/{id}/progress - Update progress
POST   /api/v1/rituals/sessions/{id}/complete - Complete ritual
GET    /api/v1/rituals/sessions/history - Get user's ritual history
DELETE /api/v1/rituals/sessions/{id}   - Cancel/delete session
```

#### AI Enhancements (Optional)
```
POST   /api/v1/rituals/personalize     - Generate custom ritual
POST   /api/v1/rituals/{id}/explain    - Get AI explanation
POST   /api/v1/rituals/{id}/timing     - Get best time for ritual
```

---

## 🎨 UI/UX Design

### Color Scheme
- **Primary**: Orange/Saffron (sacred color)
- **Secondary**: Gold/Yellow (purity)
- **Accent**: Deep red (energy)
- **Background**: Cream/Off-white
- **Text**: Dark brown/Black

### Icons
- 🕉️ Om symbol for spiritual rituals
- 🔔 Bell for puja rituals
- 🌸 Lotus for meditation
- 🔥 Fire for homa/havan
- 📿 Mala beads for japa

### Animations
- Fade in/out for step transitions
- Progress bar animation
- Completion celebration (confetti/flowers)
- Smooth audio waveform visualization

---

## 📱 Ritual Categories & Templates

### Daily Rituals
1. **Morning Prayers** (Pratha Smarana) - 5 min
2. **Ganesh Puja** - 15 min
3. **Surya Namaskar** (Sun Salutation) - 10 min
4. **Evening Aarti** - 10 min
5. **Bedtime Prayers** - 5 min

### Special Occasion Rituals
1. **Satyanarayan Puja** - 90 min
2. **Lakshmi Puja** (Diwali) - 45 min
3. **Durga Puja** - 60 min
4. **Griha Pravesh** (Housewarming) - 120 min

### Remedial Rituals
1. **Navagraha Puja** - 60 min
2. **Mangal Shanti Puja** - 45 min
3. **Kaal Sarpa Dosh Puja** - 90 min
4. **Rahu-Ketu Shanti** - 60 min

### Festival Rituals
1. **Diwali Lakshmi Puja** - 45 min
2. **Holi Holika Dahan** - 30 min
3. **Raksha Bandhan** - 15 min
4. **Janmashtami Puja** - 60 min

### Meditation & Japa
1. **Gayatri Mantra Japa** (108 times) - 20 min
2. **Om Meditation** - 15 min
3. **Maha Mrityunjaya Mantra** - 30 min
4. **Hanuman Chalisa** - 10 min

---

## 🔧 Technical Implementation

### Phase 1: Core Features (Week 1)
- ✅ Database schema and migrations
- ✅ Backend ritual service
- ✅ API endpoints (CRUD)
- ✅ Seed 10 ritual templates
- ✅ Frontend ritual library page
- ✅ Basic ritual player component

### Phase 2: Enhanced Features (Week 2)
- ✅ Voice synthesis integration
- ✅ Audio file storage (AWS S3/Supabase Storage)
- ✅ Progress tracking
- ✅ Session management
- ✅ Visual aids integration
- ✅ Timer and notifications

### Phase 3: AI & Personalization (Week 3)
- ✅ AI ritual explanation
- ✅ Personalized ritual generation
- ✅ Best time recommendation
- ✅ Chart-based customization

### Phase 4: AR & Advanced (Future)
- 🔮 AR camera integration
- 🔮 Gesture controls
- 🔮 3D item placement
- 🔮 Virtual ritual space

---

## 📦 Dependencies

### Backend
- `gtts` or `pyttsx3` - Text-to-speech (optional server-side)
- `pillow` - Image processing for visual aids
- `supabase-storage` - Audio/image file storage

### Frontend
- `react-speech-kit` - Web Speech API wrapper
- `react-player` - Audio playback
- `framer-motion` - Animations
- `@react-three/fiber` - AR/3D (Phase 4)

---

## 🎯 Success Metrics

### User Engagement
- Number of rituals started per user
- Completion rate (% of rituals finished)
- Average session duration
- Most popular rituals

### Feature Usage
- Voice guidance usage (% enabled)
- Audio playback usage
- Progress save/resume rate
- Repeat ritual rate

### Technical Performance
- API response time < 200ms
- Audio playback latency < 100ms
- Page load time < 2s
- Voice synthesis delay < 500ms

---

## 🚀 Launch Plan

### MVP (Minimum Viable Product)
**Features**:
- 10 pre-built ritual templates
- Step-by-step text instructions
- Basic progress tracking
- Simple UI with next/previous navigation

**Timeline**: 3-4 days

### V1 (Full Featured)
**Features**:
- 25+ ritual templates
- Voice guidance
- Audio mantras
- Visual aids
- Full session management
- Ritual history

**Timeline**: 7-10 days

### V2 (AI Enhanced)
**Features**:
- AI explanations
- Personalized rituals
- Muhurta integration
- Chart-based recommendations

**Timeline**: +5 days

---

## 📝 Sample Ritual Template

### Ganesh Puja (15 minutes)

**Required Items**:
- Ganesh idol/picture
- Flowers (red hibiscus preferred)
- Incense sticks
- Lamp (diya)
- Coconut
- Sweets (modak/ladoo)
- Water
- Bell

**Steps**:

1. **Preparation (1 min)**
   - Clean the puja area
   - Arrange all items
   - Sit comfortably facing East

2. **Purification (1 min)**
   - Sprinkle water around puja area
   - Chant: "Om Apavitra Pavitra Va..."

3. **Invocation (2 min)**
   - Ring bell
   - Light lamp and incense
   - Chant: "Om Gan Ganapataye Namaha" (108 times)

4. **Offering Flowers (2 min)**
   - Offer flowers at feet
   - Chant: "Om Gajananaya Namaha"

5. **Offering Sweets (1 min)**
   - Place sweets before deity
   - Chant: "Om Vakratundaya Namaha"

6. **Aarti (3 min)**
   - Circle lamp clockwise 7 times
   - Sing: "Jai Ganesh Jai Ganesh Jai Ganesh Deva..."

7. **Prayers (3 min)**
   - Recite Ganesh Stuti
   - Make personal prayers

8. **Circumambulation (1 min)**
   - Walk around deity 3 times (if possible)

9. **Prasad Distribution (1 min)**
   - Take and distribute blessed food

10. **Closing (30 sec)**
    - Thank Lord Ganesha
    - Chant: "Om Shanti Shanti Shanti"

---

## 🔐 Database Migrations

### Migration File: `create_ritual_tables.sql`

```sql
-- Ritual Templates
CREATE TABLE ritual_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    deity TEXT,
    duration_minutes INTEGER NOT NULL,
    difficulty TEXT NOT NULL,
    description TEXT,
    required_items JSONB,
    steps JSONB NOT NULL,
    audio_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User Ritual Sessions
CREATE TABLE user_ritual_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    ritual_template_id UUID NOT NULL REFERENCES ritual_templates(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    current_step INTEGER DEFAULT 1,
    status TEXT DEFAULT 'in_progress',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_ritual_templates_category ON ritual_templates(category);
CREATE INDEX idx_ritual_templates_deity ON ritual_templates(deity);
CREATE INDEX idx_user_ritual_sessions_user_id ON user_ritual_sessions(user_id);
CREATE INDEX idx_user_ritual_sessions_status ON user_ritual_sessions(status);

-- RLS Policies
ALTER TABLE user_ritual_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own ritual sessions"
    ON user_ritual_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own ritual sessions"
    ON user_ritual_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own ritual sessions"
    ON user_ritual_sessions FOR UPDATE
    USING (auth.uid() = user_id);

-- Ritual templates are public read-only
ALTER TABLE ritual_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view ritual templates"
    ON ritual_templates FOR SELECT
    TO authenticated
    USING (true);
```

---

## 📚 Resources

### Audio Sources
- **Sanskrit Mantras**: Pre-recorded by professional priests
- **Instructions**: TTS (Google Cloud TTS or Web Speech API)
- **Background Music**: Royalty-free bhajan/kirtan tracks

### Visual Assets
- **Diagrams**: Step-by-step illustrations
- **Photos**: High-quality ritual setup images
- **Videos**: Short clips for complex steps

### Reference Materials
- Vedic ritual manuals
- Puja vidhi texts
- Expert consultations

---

## ✅ Testing Checklist

### Functionality
- [ ] Can browse ritual library
- [ ] Can filter/search rituals
- [ ] Can start ritual session
- [ ] Can navigate steps (next/previous)
- [ ] Can pause and resume
- [ ] Progress saves correctly
- [ ] Can complete ritual
- [ ] Voice playback works
- [ ] Audio mantras play
- [ ] Visual aids display
- [ ] Timer works accurately
- [ ] Can view ritual history

### Performance
- [ ] Page loads < 2s
- [ ] API responses < 200ms
- [ ] Audio loads < 500ms
- [ ] TTS latency < 1s
- [ ] No memory leaks
- [ ] Works offline (PWA)

### UX
- [ ] Intuitive navigation
- [ ] Clear instructions
- [ ] Responsive design
- [ ] Dark mode support
- [ ] Accessibility (WCAG)
- [ ] Mobile-friendly
- [ ] Tablet optimized

---

## 🎉 Launch Announcement

**Feature Name**: Guided Rituals
**Tagline**: "Perform sacred Vedic rituals with step-by-step voice guidance"

**Key Benefits**:
1. Learn authentic Vedic rituals
2. Never miss a step
3. Perfect pronunciation with audio
4. Track your spiritual practice
5. Personalized to your birth chart

---

**Status**: Ready for Implementation
**Next Step**: Backend ritual service and database setup
