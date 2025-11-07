# Claude CLI Parallel Development Guide

## Overview

This guide explains how to run multiple Claude CLI instances in parallel, each working on different Magical 12 features simultaneously without conflicts.

## Prerequisites

- Claude CLI installed and authenticated
- JioAstro repository cloned
- Multiple terminal sessions available (Terminal, iTerm2, tmux, or VS Code terminals)

## Quick Start (3 Parallel Claude Instances)

### Setup Summary

```
Terminal 1: Claude working on Feature #1 (Life Snapshot)
Terminal 2: Claude working on Feature #2 (Life Threads)
Terminal 3: Claude working on Feature #3 (Decision Copilot)
```

---

## Step-by-Step Setup

### 1. Prepare Your Environment

```bash
# Create a working directory for parallel development
cd /Users/arvind.tiwari/Desktop/jioastro

# Ensure you're on the latest main branch
git fetch origin
git checkout main
git pull origin main

# Verify the framework is in place
ls -la PARALLEL_DEVELOPMENT_FRAMEWORK.md
ls -la backend/scripts/feature_generator.py
```

### 2. Create Feature Assignment Document

Create a file to track which Claude instance is working on which feature:

```bash
cat > FEATURE_ASSIGNMENTS.md << 'EOF'
# Feature Assignments for Parallel Development

## Active Development

| Feature # | Feature Name | Claude Instance | Branch | Status |
|-----------|--------------|-----------------|--------|--------|
| 1 | Life Snapshot | Claude-1 | feature/life-snapshot-MAG-001 | 🟡 In Progress |
| 2 | Life Threads | Claude-2 | feature/life-threads-MAG-002 | 🟡 In Progress |
| 3 | Decision Copilot | Claude-3 | feature/decision-copilot-MAG-003 | 🟡 In Progress |
| 4 | Transit Pulse | - | - | ⚪ Available |
| 5 | Remedy Planner | - | - | ⚪ Available |
| 6 | AstroTwin Graph | - | - | ⚪ Available |
| 7 | Guided Rituals | - | - | ⚪ Available |
| 8 | Evidence Mode | - | - | ⚪ Available |
| 9 | Expert Console | - | - | ⚪ Available |
| 10 | Reality Check | - | - | ⚪ Available |
| 11 | Hyperlocal Panchang | - | - | ⚪ Available |
| 12 | Story Reels | - | - | ⚪ Available |

## Coordination

- Each Claude instance works in its own feature branch
- No cross-feature dependencies
- Daily sync at EOD to merge completed features

Last Updated: $(date)
EOF
```

### 3. Open Multiple Terminal Sessions

**Option A: Using iTerm2 (Recommended for Mac)**

```bash
# Split terminal into 3 panes
# Cmd+D (split vertically)
# Cmd+Shift+D (split horizontally)
```

**Option B: Using tmux**

```bash
# Create new tmux session
tmux new -s jioastro-dev

# Split into 3 panes
Ctrl+b %  # Split vertically
Ctrl+b "  # Split horizontally

# Navigate between panes
Ctrl+b arrow-keys
```

**Option C: Using VS Code**

```bash
# Open VS Code
code /Users/arvind.tiwari/Desktop/jioastro

# Terminal → Split Terminal (multiple times)
# Or use Cmd+\ to split
```

### 4. Start Claude CLI in Each Terminal

**Terminal 1 - Feature #1: Life Snapshot**

```bash
# Navigate to project
cd /Users/arvind.tiwari/Desktop/jioastro

# Start Claude CLI
claude

# Once Claude starts, give it this instruction:
```

**Prompt for Claude Instance 1:**
```
I'm assigning you to implement Magical 12 Feature #1: Life Snapshot.

Your task:
1. Read PARALLEL_DEVELOPMENT_FRAMEWORK.md
2. Read MAGICAL_12_PRODUCT_ROADMAP.md (Feature #1 section)
3. Create feature branch: feature/life-snapshot-MAG-001
4. Generate feature scaffold using: python scripts/feature_generator.py generate life_snapshot --description "60-second personalized life insights" --author "Claude-1" --magical-number 1
5. Implement the feature following the checklist in DEVELOPER_QUICK_START.md
6. Write comprehensive tests (≥90% coverage)
7. Create PR when complete

Important rules:
- Work ONLY on life_snapshot feature
- Use table prefix: life_snapshot_*
- API prefix: /api/v2/life-snapshot/*
- Don't modify other features
- Feature flag: FEATURE_LIFE_SNAPSHOT=true

Report progress regularly and ask questions if unclear.

Begin by confirming you understand the assignment and reading the framework documentation.
```

---

**Terminal 2 - Feature #2: Life Threads**

```bash
# Navigate to project (in separate terminal)
cd /Users/arvind.tiwari/Desktop/jioastro

# Start Claude CLI
claude

# Once Claude starts, give it this instruction:
```

**Prompt for Claude Instance 2:**
```
I'm assigning you to implement Magical 12 Feature #2: Life Threads.

Your task:
1. Read PARALLEL_DEVELOPMENT_FRAMEWORK.md
2. Read MAGICAL_12_PRODUCT_ROADMAP.md (Feature #2 section)
3. Create feature branch: feature/life-threads-MAG-002
4. Generate feature scaffold using: python scripts/feature_generator.py generate life_threads --description "Zoomable life journey timeline visualization" --author "Claude-2" --magical-number 2
5. Implement the feature following the checklist in DEVELOPER_QUICK_START.md
6. Write comprehensive tests (≥90% coverage)
7. Create PR when complete

Important rules:
- Work ONLY on life_threads feature
- Use table prefix: life_threads_*
- API prefix: /api/v2/life-threads/*
- Don't modify other features
- Feature flag: FEATURE_LIFE_THREADS=true

Report progress regularly and ask questions if unclear.

Begin by confirming you understand the assignment and reading the framework documentation.
```

---

**Terminal 3 - Feature #3: Decision Copilot**

```bash
# Navigate to project (in separate terminal)
cd /Users/arvind.tiwari/Desktop/jioastro

# Start Claude CLI
claude

# Once Claude starts, give it this instruction:
```

**Prompt for Claude Instance 3:**
```
I'm assigning you to implement Magical 12 Feature #3: Decision Copilot.

Your task:
1. Read PARALLEL_DEVELOPMENT_FRAMEWORK.md
2. Read MAGICAL_12_PRODUCT_ROADMAP.md (Feature #3 section)
3. Create feature branch: feature/decision-copilot-MAG-003
4. Generate feature scaffold using: python scripts/feature_generator.py generate decision_copilot --description "Calendar-integrated Muhurta recommendations" --author "Claude-3" --magical-number 3
5. Implement the feature following the checklist in DEVELOPER_QUICK_START.md
6. Write comprehensive tests (≥90% coverage)
7. Create PR when complete

Important rules:
- Work ONLY on decision_copilot feature
- Use table prefix: decision_copilot_*
- API prefix: /api/v2/decision-copilot/*
- Don't modify other features
- Feature flag: FEATURE_DECISION_COPILOT=true

Report progress regularly and ask questions if unclear.

Begin by confirming you understand the assignment and reading the framework documentation.
```

---

### 5. Monitor Progress

**Create a monitoring script:**

```bash
cat > monitor_parallel_dev.sh << 'EOF'
#!/bin/bash

echo "=== JioAstro Parallel Development Monitor ==="
echo ""
echo "Feature Branches:"
git branch | grep feature/

echo ""
echo "Recent Commits:"
git log --oneline --graph --all -10

echo ""
echo "Modified Files:"
git status --short

echo ""
echo "Active Claude Processes:"
ps aux | grep claude | grep -v grep

echo ""
echo "Database Migrations:"
ls -ltr backend/migrations/versions/ | tail -5

echo ""
echo "Test Results:"
if [ -f backend/.pytest_cache/v/cache/lastfailed ]; then
    echo "❌ Some tests failed"
    cat backend/.pytest_cache/v/cache/lastfailed
else
    echo "✅ All tests passing"
fi
EOF

chmod +x monitor_parallel_dev.sh

# Run monitor
./monitor_parallel_dev.sh
```

---

## Managing Multiple Branches

### Branch Strategy

Each Claude instance works on its own feature branch:

```bash
# Claude-1
git checkout -b feature/life-snapshot-MAG-001

# Claude-2
git checkout -b feature/life-threads-MAG-002

# Claude-3
git checkout -b feature/decision-copilot-MAG-003
```

### Handling Migrations

**Migration Naming Convention:**

```bash
# Claude-1 creates:
alembic revision -m "life_snapshot: add snapshot tables"
# Result: 20251107_001_life_snapshot_add_snapshot_tables.py

# Claude-2 creates:
alembic revision -m "life_threads: add timeline tables"
# Result: 20251107_002_life_threads_add_timeline_tables.py

# Claude-3 creates:
alembic revision -m "decision_copilot: add recommendation tables"
# Result: 20251107_003_decision_copilot_add_recommendation_tables.py
```

**If Migration Conflicts Occur:**

```bash
# Check for conflicts
alembic heads

# If multiple heads exist, merge them
alembic merge -m "merge parallel feature migrations" <head1> <head2>
```

---

## Running Backend in Parallel

### Option 1: Single Backend Instance (Recommended)

All features share one backend instance:

```bash
# Terminal 4 - Backend
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate

# Enable all features being developed
export FEATURE_LIFE_SNAPSHOT=true
export FEATURE_LIFE_THREADS=true
export FEATURE_DECISION_COPILOT=true

# Start backend
uvicorn main:app --reload --port 8000
```

### Option 2: Separate Backend Instances (Advanced)

Run separate backend instances on different ports:

```bash
# Terminal 4 - Backend for Feature #1
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate
export FEATURE_LIFE_SNAPSHOT=true
uvicorn main:app --reload --port 8001

# Terminal 5 - Backend for Feature #2
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate
export FEATURE_LIFE_THREADS=true
uvicorn main:app --reload --port 8002

# Terminal 6 - Backend for Feature #3
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate
export FEATURE_DECISION_COPILOT=true
uvicorn main:app --reload --port 8003
```

---

## Running Frontend in Parallel

### Option 1: Single Frontend Instance (Recommended)

```bash
# Terminal 7 - Frontend
cd /Users/arvind.tiwari/Desktop/jioastro/frontend

# Enable all features
export NEXT_PUBLIC_FEATURE_LIFE_SNAPSHOT=true
export NEXT_PUBLIC_FEATURE_LIFE_THREADS=true
export NEXT_PUBLIC_FEATURE_DECISION_COPILOT=true

npm run dev
# Runs on http://localhost:3000
```

### Option 2: Separate Frontend Instances

```bash
# Terminal 7 - Frontend for Feature #1
cd /Users/arvind.tiwari/Desktop/jioastro/frontend
export NEXT_PUBLIC_FEATURE_LIFE_SNAPSHOT=true
export PORT=3001
npm run dev

# Terminal 8 - Frontend for Feature #2
cd /Users/arvind.tiwari/Desktop/jioastro/frontend
export NEXT_PUBLIC_FEATURE_LIFE_THREADS=true
export PORT=3002
npm run dev

# Terminal 9 - Frontend for Feature #3
cd /Users/arvind.tiwari/Desktop/jioastro/frontend
export NEXT_PUBLIC_FEATURE_DECISION_COPILOT=true
export PORT=3003
npm run dev
```

---

## Testing Parallel Features

### Run Tests for Each Feature Independently

```bash
# Terminal 1 - Claude-1 runs tests
cd /Users/arvind.tiwari/Desktop/jioastro/backend
pytest app/features/life_snapshot/tests/ -v

# Terminal 2 - Claude-2 runs tests
pytest app/features/life_threads/tests/ -v

# Terminal 3 - Claude-3 runs tests
pytest app/features/decision_copilot/tests/ -v
```

### Run Full Test Suite (After Each Feature)

```bash
# Check for regressions
pytest tests/ -v
```

---

## Coordination & Communication

### Daily Standup Template

```bash
cat > daily_standup.md << 'EOF'
# Daily Standup - $(date +%Y-%m-%d)

## Claude-1 (Life Snapshot)
- **Yesterday:** [Summary]
- **Today:** [Plan]
- **Blockers:** [Any issues]
- **Status:** [% complete]

## Claude-2 (Life Threads)
- **Yesterday:** [Summary]
- **Today:** [Plan]
- **Blockers:** [Any issues]
- **Status:** [% complete]

## Claude-3 (Decision Copilot)
- **Yesterday:** [Summary]
- **Today:** [Plan]
- **Blockers:** [Any issues]
- **Status:** [% complete]

## Actions
- [ ] Resolve conflicts (if any)
- [ ] Merge completed features
- [ ] Update FEATURE_ASSIGNMENTS.md
EOF
```

### Conflict Prevention Checklist

Before starting work, each Claude instance should verify:

```bash
# 1. Working on correct branch
git branch --show-current

# 2. Feature directory exists
ls -la backend/app/features/$(basename $(git branch --show-current) | cut -d'-' -f2-3)/

# 3. No table name conflicts
grep "table.*=" backend/app/features/*/models.py | grep -v $(basename $(git branch --show-current))

# 4. No API endpoint conflicts
grep "prefix=" backend/app/features/*/feature.py
```

---

## Merging Completed Features

When a Claude instance completes a feature:

```bash
# Step 1: Ensure tests pass
pytest app/features/<feature_name>/tests/ -v --cov

# Step 2: Rebase on latest main
git fetch origin main
git rebase origin/main

# Step 3: Resolve any conflicts
git status
# Fix conflicts if any
git add .
git rebase --continue

# Step 4: Push feature branch
git push origin feature/<feature-name>-MAG-###

# Step 5: Create PR
gh pr create --title "feat: <Feature Name>" --body "Implements Magical 12 Feature #X"

# Step 6: After PR approval and merge
git checkout main
git pull origin main

# Step 7: Update assignments
# Mark feature as complete in FEATURE_ASSIGNMENTS.md
```

---

## Troubleshooting

### Issue: Claude instances interfering with each other

**Solution:**
```bash
# Ensure each Claude is on its own branch
# Terminal 1
git checkout feature/life-snapshot-MAG-001

# Terminal 2
git checkout feature/life-threads-MAG-002

# Terminal 3
git checkout feature/decision-copilot-MAG-003
```

### Issue: Database migration conflicts

**Solution:**
```bash
# Check current heads
alembic heads

# Merge migrations
alembic merge -m "merge feature migrations" <head1> <head2>

# Apply merged migration
alembic upgrade head
```

### Issue: Backend reload conflicts

**Solution:**
Use one backend instance with all feature flags enabled:

```bash
export FEATURE_LIFE_SNAPSHOT=true
export FEATURE_LIFE_THREADS=true
export FEATURE_DECISION_COPILOT=true
uvicorn main:app --reload
```

### Issue: Test data conflicts

**Solution:**
Each feature should use unique test data prefixes:

```python
# Feature 1
test_user_id = "test_life_snapshot_user_123"

# Feature 2
test_user_id = "test_life_threads_user_456"

# Feature 3
test_user_id = "test_decision_copilot_user_789"
```

---

## Advanced: Using Docker for Isolation

For complete isolation, run each feature in its own Docker container:

```bash
# docker-compose.parallel.yml
version: '3.8'

services:
  feature_1_backend:
    build: ./backend
    ports:
      - "8001:8000"
    environment:
      - FEATURE_LIFE_SNAPSHOT=true
    volumes:
      - ./backend/app/features/life_snapshot:/app/app/features/life_snapshot

  feature_2_backend:
    build: ./backend
    ports:
      - "8002:8000"
    environment:
      - FEATURE_LIFE_THREADS=true
    volumes:
      - ./backend/app/features/life_threads:/app/app/features/life_threads

  feature_3_backend:
    build: ./backend
    ports:
      - "8003:8000"
    environment:
      - FEATURE_DECISION_COPILOT=true
    volumes:
      - ./backend/app/features/decision_copilot:/app/app/features/decision_copilot
```

---

## Summary: Quick Reference

### Start 3 Claude Instances

```bash
# Terminal 1
cd /Users/arvind.tiwari/Desktop/jioastro && claude
# Assign: Feature #1 (Life Snapshot)

# Terminal 2
cd /Users/arvind.tiwari/Desktop/jioastro && claude
# Assign: Feature #2 (Life Threads)

# Terminal 3
cd /Users/arvind.tiwari/Desktop/jioastro && claude
# Assign: Feature #3 (Decision Copilot)
```

### Start Backend & Frontend

```bash
# Terminal 4 - Backend
cd /Users/arvind.tiwari/Desktop/jioastro/backend
source venv/bin/activate
export FEATURE_LIFE_SNAPSHOT=true FEATURE_LIFE_THREADS=true FEATURE_DECISION_COPILOT=true
uvicorn main:app --reload

# Terminal 5 - Frontend
cd /Users/arvind.tiwari/Desktop/jioastro/frontend
export NEXT_PUBLIC_FEATURE_LIFE_SNAPSHOT=true NEXT_PUBLIC_FEATURE_LIFE_THREADS=true NEXT_PUBLIC_FEATURE_DECISION_COPILOT=true
npm run dev
```

### Monitor Progress

```bash
# Check all branches
git branch -a

# Check recent commits across all branches
git log --oneline --graph --all -20

# Check which Claude is working on what
ps aux | grep claude

# Run monitor script
./monitor_parallel_dev.sh
```

---

## Success Criteria

Parallel development is working correctly when:

✅ Each Claude instance works on its own feature branch
✅ No merge conflicts between features
✅ All tests pass independently per feature
✅ Features can be enabled/disabled via flags
✅ Database migrations don't conflict
✅ API endpoints don't overlap
✅ Features complete and merge smoothly

---

**Happy Parallel Development! 🚀**

*Last Updated: 2025-11-07*
