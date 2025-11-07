# Instant Onboarding Feature

**Magical 12 Feature #13 (Bonus)**
**Status:** 🟡 Ready for Testing
**Priority:** CRITICAL
**Version:** 1.0.0

## Overview

WhatsApp-to-chart in 90 seconds! Zero-friction onboarding that allows users to create their birth chart through WhatsApp, web, voice, or SMS in under 90 seconds without creating an account first.

## Quick Start

### 1. Run Database Migration

Execute the SQL script in Supabase SQL Editor:
```
File: backend/supabase_migration_instant_onboarding.sql
```

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed instructions.

### 2. Enable Feature Flag

```bash
export FEATURE_INSTANT_ONBOARDING=true
```

### 3. Test API

Visit: http://localhost:8000/docs#/Bonus%20Features

## Features

- 📱 WhatsApp Bot Integration
- 🌐 Web Forms
- 🎤 Voice Input (ready for integration)
- 📧 SMS (ready for integration)
- 🇬🇧 English / 🇮🇳 Hindi
- ⚡ Chart in <90 seconds
- 🔗 Shareable links

## API Endpoints

- `POST /api/v2/instant-onboarding/session/start` - Start session
- `POST /api/v2/instant-onboarding/session/collect` - Collect data
- `POST /api/v2/instant-onboarding/quick-chart` - Generate chart
- `POST /api/v2/instant-onboarding/whatsapp/webhook` - WhatsApp webhook
- `POST /api/v2/instant-onboarding/voice/process` - Voice input
- `GET /api/v2/instant-onboarding/stats` - Analytics

See full documentation in this README for detailed usage.

## Development

See PARALLEL_DEVELOPMENT_FRAMEWORK.md for complete workflow.

## Testing

```bash
pytest app/features/instant_onboarding/tests/test_service.py -v
pytest --cov=app/features/instant_onboarding
```

---

**Author:** Claude AI
**Generated:** 2025-11-07
**Status:** ✅ Implementation Complete
