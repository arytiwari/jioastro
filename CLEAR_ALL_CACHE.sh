#!/bin/bash

echo "=========================================="
echo "CLEARING ALL CACHED DATA"
echo "=========================================="
echo ""

echo "1. Clearing database reading sessions..."
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate
python -c "
from app.services.supabase_service import supabase_service
try:
    result = supabase_service.client.table('reading_sessions').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f'✅ Deleted {len(result.data) if result.data else 0} reading sessions')
except Exception as e:
    print(f'Note: {e}')
"

echo ""
echo "✅ Database cache cleared!"
echo ""
echo "📝 Next steps:"
echo "   1. In your browser, press F12 to open DevTools"
echo "   2. In the Console tab, run:"
echo "      sessionStorage.clear(); localStorage.clear(); location.reload();"
echo ""
echo "   OR visit: http://localhost:3001/clear-cache.html"
echo ""
