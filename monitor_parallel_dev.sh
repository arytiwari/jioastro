#!/bin/bash

echo "=== JioAstro Parallel Development Monitor ==="
echo ""
echo "📅 $(date)"
echo ""

echo "🌿 Active Feature Branches:"
git branch | grep feature/ || echo "No feature branches yet"

echo ""
echo "📝 Recent Commits (last 10):"
git log --oneline --graph --all -10

echo ""
echo "📂 Modified Files:"
git status --short

echo ""
echo "🔧 Active Claude Processes:"
ps aux | grep -E "(claude|Claude)" | grep -v grep || echo "No Claude processes running"

echo ""
echo "🗄️  Database Migrations:"
if [ -d "backend/migrations/versions" ]; then
    ls -ltr backend/migrations/versions/ | tail -5
else
    echo "No migrations yet"
fi

echo ""
echo "✅ Test Results:"
if [ -f "backend/.pytest_cache/v/cache/lastfailed" ]; then
    echo "❌ Some tests failed"
    cat backend/.pytest_cache/v/cache/lastfailed
else
    echo "✅ All tests passing (or not run yet)"
fi

echo ""
echo "🎯 Feature Status:"
if [ -f "FEATURE_ASSIGNMENTS.md" ]; then
    grep "🟡\|✅\|❌" FEATURE_ASSIGNMENTS.md || echo "No features in progress"
else
    echo "FEATURE_ASSIGNMENTS.md not found"
fi
