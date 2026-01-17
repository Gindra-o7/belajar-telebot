#!/bin/bash
set -e

# Script ini akan otomatis dijalankan saat PostgreSQL pertama kali start
echo "🚀 Initializing Stock Bot Database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable extensions
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Grant all privileges
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
    
    -- Create indexes untuk performa (tables dibuat oleh SQLAlchemy)
    -- Index akan ditambahkan setelah tables dibuat
    
    SELECT 'Database initialized successfully!' AS status;
EOSQL

echo "✅ Database initialization complete!"
