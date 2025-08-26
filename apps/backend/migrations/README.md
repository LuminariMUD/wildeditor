# Database Migrations

This directory contains SQL migration scripts for the Wildeditor backend database.

## Running Migrations

### Production Database

To apply migrations to the production database:

1. Connect to the production MySQL database:
```bash
mysql -h [host] -u [username] -p luminari_mudprod
```

2. Run the migration script:
```bash
mysql -h [host] -u [username] -p luminari_mudprod < 002_add_region_hints_tables.sql
```

### Verifying Migration

After running the migration, verify the tables were created:

```bash
cd apps/backend/src
python check_hints_tables.py
```

## Migration Files

- **001_initial_schema.sql** - Initial database schema (if needed)
- **002_add_region_hints_tables.sql** - Adds tables for region hints system:
  - `region_hints` - Stores AI-generated hints for dynamic descriptions
  - `region_profiles` - Stores region personality profiles
  - `hint_usage_log` - Tracks hint usage for analytics

## Important Notes

1. **Always backup the database before running migrations**
2. **Test migrations on a development database first**
3. **The backend will work without these tables** - it returns empty responses if tables don't exist
4. **CORS errors are prevented** by proper error handling

## Troubleshooting

If you see 500 errors or CORS issues:
1. Check if the tables exist using `check_hints_tables.py`
2. Run the migration if tables are missing
3. Restart the backend service after migration

## Table Schema

### region_hints
- Stores categorized hints for regions
- Categories: atmosphere, fauna, flora, geography, etc.
- Supports seasonal and weather-based variations
- Priority system for hint selection

### region_profiles
- Stores overall theme and mood for regions
- Controls description style and complexity
- One profile per region

### hint_usage_log
- Optional analytics table
- Tracks when and where hints are used
- Can be omitted if analytics aren't needed