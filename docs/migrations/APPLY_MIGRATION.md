# Apply Database Migration for Moon Chart

## Issue
The database constraint on the `charts` table only allows 'D1' and 'D9' chart types. We need to add 'Moon' as a valid type.

## Solution
Run the migration SQL to update the constraint.

## How to Apply

### Option 1: Supabase Dashboard (Recommended)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy and paste the contents of `add_moon_chart_type.sql`
5. Click **Run** to execute the migration
6. Verify success - you should see the updated constraint in the results

### Option 2: Command Line (if using psql)

```bash
# Connect to your database
psql "postgresql://[user]:[password]@[host]:5432/[database]"

# Run the migration file
\i docs/migrations/add_moon_chart_type.sql
```

### Option 3: Using Supabase CLI

```bash
# If you have Supabase CLI installed
supabase db push --db-url "postgresql://[connection-string]"
```

## Verify Migration

After applying, verify with:

```sql
-- Check the constraint
SELECT constraint_name, check_clause
FROM information_schema.check_constraints
WHERE constraint_name = 'charts_chart_type_check';

-- Should show: chart_type IN ('D1', 'D9', 'Moon')
```

## Test Moon Chart Creation

Once the migration is applied:

1. Restart your backend server: `cd backend && uvicorn main:app --reload`
2. Navigate to a birth chart page in the frontend
3. Click the "Moon Chart" tab
4. The chart should calculate and save successfully

## Rollback (if needed)

If you need to rollback:

```sql
ALTER TABLE charts DROP CONSTRAINT IF EXISTS charts_chart_type_check;
ALTER TABLE charts ADD CONSTRAINT charts_chart_type_check
  CHECK (chart_type IN ('D1', 'D9'));
```
