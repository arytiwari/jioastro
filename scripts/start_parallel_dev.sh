#!/bin/bash

# Start Parallel Development Environment for JioAstro
# This script sets up everything needed for multiple Claude instances to work in parallel

set -e

echo "🚀 Starting JioAstro Parallel Development Environment"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if [ ! -f "PARALLEL_DEVELOPMENT_FRAMEWORK.md" ]; then
    echo "❌ Error: PARALLEL_DEVELOPMENT_FRAMEWORK.md not found"
    echo "Please ensure you're in the project root directory"
    exit 1
fi

if [ ! -f "backend/scripts/feature_generator.py" ]; then
    echo "❌ Error: Feature generator not found"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Create feature assignments file if it doesn't exist
if [ ! -f "FEATURE_ASSIGNMENTS.md" ]; then
    echo "📝 Creating FEATURE_ASSIGNMENTS.md..."
    cat > FEATURE_ASSIGNMENTS.md << 'EOF'
# Feature Assignments for Parallel Development

## Active Development

| Feature # | Feature Name | Claude Instance | Branch | Status |
|-----------|--------------|-----------------|--------|--------|
| 1 | Life Snapshot | - | - | ⚪ Available |
| 2 | Life Threads | - | - | ⚪ Available |
| 3 | Decision Copilot | - | - | ⚪ Available |
| 4 | Transit Pulse | - | - | ⚪ Available |
| 5 | Remedy Planner | - | - | ⚪ Available |
| 6 | AstroTwin Graph | - | - | ⚪ Available |
| 7 | Guided Rituals | - | - | ⚪ Available |
| 8 | Evidence Mode | - | - | ⚪ Available |
| 9 | Expert Console | - | - | ⚪ Available |
| 10 | Reality Check | - | - | ⚪ Available |
| 11 | Hyperlocal Panchang | - | - | ⚪ Available |
| 12 | Story Reels | - | - | ⚪ Available |

## Coordination Rules

1. Each Claude instance must work on its own feature branch
2. No cross-feature dependencies allowed
3. Feature flags must be used for all endpoints
4. Database tables must be prefixed with feature name
5. Daily sync to merge completed features

Last Updated: $(date)
EOF
    echo -e "${GREEN}✅ Created FEATURE_ASSIGNMENTS.md${NC}"
fi

# Create monitoring script
echo "📊 Setting up monitoring..."
cat > monitor_parallel_dev.sh << 'EOF'
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
EOF

chmod +x monitor_parallel_dev.sh
echo -e "${GREEN}✅ Created monitoring script${NC}"

# Create feature-specific environment setup script
echo "⚙️  Creating environment setup helpers..."

for feature_num in {1..12}; do
    feature_names=("life_snapshot" "life_threads" "decision_copilot" "transit_pulse" "remedy_planner" "astrotwin_graph" "guided_rituals" "evidence_mode" "expert_console" "reality_check" "hyperlocal_panchang" "story_reels")
    feature_name="${feature_names[$((feature_num-1))]}"
    feature_upper=$(echo "$feature_name" | tr '[:lower:]' '[:upper:]')

    cat > "scripts/setup_feature_${feature_num}.sh" << EOF
#!/bin/bash
# Setup environment for Feature #${feature_num}: ${feature_name}

export FEATURE_${feature_upper}=true
export NEXT_PUBLIC_FEATURE_${feature_upper}=true

echo "✅ Environment configured for Feature #${feature_num}: ${feature_name}"
echo "   Feature flag: FEATURE_${feature_upper}=true"
echo ""
echo "To use in your terminal:"
echo "   source scripts/setup_feature_${feature_num}.sh"
EOF
    chmod +x "scripts/setup_feature_${feature_num}.sh"
done

echo -e "${GREEN}✅ Created 12 feature environment setup scripts${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Parallel Development Environment Ready!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo "📖 Next Steps:"
echo ""
echo "1️⃣  Read the guide:"
echo "    cat CLAUDE_PARALLEL_DEVELOPMENT_GUIDE.md"
echo ""
echo "2️⃣  Open multiple terminal sessions (3 recommended)"
echo ""
echo "3️⃣  In each terminal, start Claude CLI:"
echo "    Terminal 1: cd $PROJECT_ROOT && claude"
echo "    Terminal 2: cd $PROJECT_ROOT && claude"
echo "    Terminal 3: cd $PROJECT_ROOT && claude"
echo ""
echo "4️⃣  Assign features to each Claude instance:"
echo "    Claude-1: Feature #1 (Life Snapshot)"
echo "    Claude-2: Feature #2 (Life Threads)"
echo "    Claude-3: Feature #3 (Decision Copilot)"
echo ""
echo "5️⃣  Give each Claude this prompt:"
echo "    See CLAUDE_PARALLEL_DEVELOPMENT_GUIDE.md for exact prompts"
echo ""
echo "6️⃣  Start backend (in separate terminal):"
echo "    cd backend && source venv/bin/activate"
echo "    source ../scripts/setup_feature_1.sh"
echo "    source ../scripts/setup_feature_2.sh"
echo "    source ../scripts/setup_feature_3.sh"
echo "    uvicorn main:app --reload"
echo ""
echo "7️⃣  Start frontend (in separate terminal):"
echo "    cd frontend"
echo "    source ../scripts/setup_feature_1.sh"
echo "    source ../scripts/setup_feature_2.sh"
echo "    source ../scripts/setup_feature_3.sh"
echo "    npm run dev"
echo ""
echo "8️⃣  Monitor progress:"
echo "    ./monitor_parallel_dev.sh"
echo ""
echo -e "${YELLOW}📚 Documentation:${NC}"
echo "   - PARALLEL_DEVELOPMENT_FRAMEWORK.md (comprehensive guide)"
echo "   - CLAUDE_PARALLEL_DEVELOPMENT_GUIDE.md (Claude CLI specific)"
echo "   - DEVELOPER_QUICK_START.md (quick reference)"
echo "   - FEATURE_ASSIGNMENTS.md (track assignments)"
echo ""
echo -e "${BLUE}Happy Parallel Development! 🚀${NC}"
