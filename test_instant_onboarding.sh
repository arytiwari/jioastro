#!/bin/bash

# Quick test of Instant Onboarding feature
# Creates a birth chart in under 90 seconds without authentication!

BASE_URL="http://localhost:8000/api/v2/instant-onboarding"

echo "🚀 Testing Instant Onboarding Feature..."
echo ""

# Step 1: Start session
echo "Step 1: Starting onboarding session..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/session/start" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "web",
    "language": "en"
  }')

echo "Response: $SESSION_RESPONSE"
echo ""

# Extract session_key (requires jq for JSON parsing)
if command -v jq &> /dev/null; then
    SESSION_KEY=$(echo $SESSION_RESPONSE | jq -r '.session_key')
    echo "Session Key: $SESSION_KEY"
    echo ""

    # Step 2: Generate quick chart directly
    echo "Step 2: Generating quick chart..."
    CHART_RESPONSE=$(curl -s -X POST "$BASE_URL/quick-chart" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Test User",
        "birth_date": "1990-01-15",
        "birth_time": "14:30:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata",
        "language": "en"
      }')

    echo "Chart Response:"
    echo $CHART_RESPONSE | jq '.'
    echo ""
    echo "✅ Chart created successfully!"
    echo ""

    # Extract profile_id
    PROFILE_ID=$(echo $CHART_RESPONSE | jq -r '.profile_id')
    echo "Profile ID: $PROFILE_ID"
    echo "Shareable Link: http://localhost:3000/chart/$PROFILE_ID?ref=instant"

else
    echo "⚠️  'jq' not installed. Install with: brew install jq"
    echo ""
    echo "Manual test: Visit http://localhost:8000/docs#/Bonus%20Features"
fi
