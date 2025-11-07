#!/bin/bash

# Test script to create a sample birth profile
# This requires authentication token from your frontend

echo "Creating test birth profile..."
echo ""
echo "You need to get your auth token from the frontend first:"
echo "1. Open browser console (F12)"
echo "2. Go to: http://localhost:3000/dashboard"
echo "3. Run: localStorage.getItem('sb-YOUR_PROJECT-auth-token')"
echo "4. Copy the access_token value"
echo ""
echo "Then run:"
echo ""
echo 'curl -X POST "http://localhost:8000/api/v1/profiles" \'
echo '  -H "Content-Type: application/json" \'
echo '  -H "Authorization: Bearer YOUR_TOKEN_HERE" \'
echo '  -d '"'"'{
    "name": "Test User",
    "birth_date": "1990-01-15",
    "birth_time": "14:30:00",
    "birth_place": "New Delhi, India",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "timezone": "Asia/Kolkata"
  }'"'"''
echo ""
