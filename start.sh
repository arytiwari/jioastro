#!/bin/bash
# Quick Start Script for JioAstro with VedAstro Integration

echo "🚀 Starting JioAstro Application..."
echo ""

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    cd backend
    python -m venv venv
    cd ..
fi

# Start backend in background
echo "📦 Starting Backend Server..."
cd backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Check if VedAstro is installed
python -c "import vedastro" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing VedAstro library..."
    pip install vedastro
fi

echo "✅ Backend dependencies ready"
echo "🌐 Starting FastAPI server on http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo ""
echo "📦 Starting Frontend Server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

echo "✅ Frontend dependencies ready"
echo "🌐 Starting Next.js server on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ ✅ ✅  ALL SERVERS STARTED  ✅ ✅ ✅"
echo ""
echo "📍 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To stop servers, press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🎯 To see VedAstro features:"
echo "   1. Visit http://localhost:3000"
echo "   2. Login or Sign up"
echo "   3. Go to 'My Profiles' and create a birth profile"
echo "   4. Click 'View Enhanced Chart' button"
echo "   5. Explore the tabs: Overview, D1, D9, Dasha"
echo "   6. Click 'Knowledge' in the menu for Vedic knowledge base"
echo ""

# Keep script running
wait
