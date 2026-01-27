-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cis TO cis;
