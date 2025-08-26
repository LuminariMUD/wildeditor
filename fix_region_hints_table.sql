-- Fix region_hints table by adding missing ai_agent_id column
-- This is a hotfix for the production database

USE luminari_mudprod;

-- Check if column exists before adding it
SELECT COUNT(*) AS column_exists 
FROM information_schema.columns 
WHERE table_schema = 'luminari_mudprod' 
  AND table_name = 'region_hints' 
  AND column_name = 'ai_agent_id';

-- Add the missing column if it doesn't exist
ALTER TABLE region_hints 
ADD COLUMN IF NOT EXISTS ai_agent_id VARCHAR(100) DEFAULT NULL 
COMMENT 'Which AI agent created this hint'
AFTER resource_triggers;

-- Verify the column was added
DESCRIBE region_hints;