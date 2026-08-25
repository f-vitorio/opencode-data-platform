#!/usr/bin/env python3
"""
RAG Setup Script - Fase 1
Cria infraestrutura de embeddings no Supabase
"""

import os
import sys
from pathlib import Path

# Load environment variables
env_path = Path.home() / ".config/opencode/.env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    """Get PostgreSQL connection to Supabase"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        sys.exit(1)
    
    # Ensure sslmode=require
    if 'sslmode=' not in db_url:
        db_url += '?sslmode=require'
    
    return psycopg2.connect(db_url)

def setup_pgvector(conn):
    """Enable pgvector extension"""
    with conn.cursor() as cur:
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print("✅ pgvector extension enabled")
            return True
        except Exception as e:
            print(f"❌ Error enabling pgvector: {e}")
            conn.rollback()
            return False

def create_embeddings_table(conn):
    """Create embeddings table for RAG"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    
                    -- Content
                    content TEXT NOT NULL,
                    content_preview VARCHAR(500),
                    
                    -- Metadata
                    source_type VARCHAR(50) NOT NULL,  -- skill, client, company, agent
                    source_file VARCHAR(255) NOT NULL,
                    source_path TEXT,
                    chunk_index INTEGER DEFAULT 0,
                    chunk_total INTEGER DEFAULT 1,
                    
                    -- Skill-specific metadata
                    skill_name VARCHAR(100),
                    skill_area VARCHAR(100),
                    
                    -- Client metadata
                    client_slug VARCHAR(100),
                    client_name VARCHAR(200),
                    
                    -- Agent metadata
                    agent_name VARCHAR(100),
                    
                    -- Embedding vector (1536 dimensions for text-embedding-3-small)
                    embedding VECTOR(1536),
                    
                    -- Timestamps
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    
                    -- Tokens count
                    token_count INTEGER
                );
            """)
            
            # Create indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_source_type 
                ON embeddings(source_type);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_skill_name 
                ON embeddings(skill_name);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_client_slug 
                ON embeddings(client_slug);
            """)
            
            # Create HNSW index for vector search (faster than IVFFlat for small datasets)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
                ON embeddings 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            conn.commit()
            print("✅ Embeddings table created with indexes")
            return True
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            conn.rollback()
            return False

def create_search_function(conn):
    """Create semantic search function"""
    with conn.cursor() as cur:
        try:
            cur.execute("""
                CREATE OR REPLACE FUNCTION search_embeddings(
                    query_embedding VECTOR(1536),
                    match_count INTEGER DEFAULT 5,
                    match_threshold FLOAT DEFAULT 0.5,
                    filter_source_type VARCHAR DEFAULT NULL,
                    filter_skill_name VARCHAR DEFAULT NULL,
                    filter_client_slug VARCHAR DEFAULT NULL
                )
                RETURNS TABLE (
                    id UUID,
                    content TEXT,
                    content_preview VARCHAR(500),
                    source_type VARCHAR(50),
                    source_file VARCHAR(255),
                    skill_name VARCHAR(100),
                    client_slug VARCHAR(100),
                    similarity FLOAT
                )
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT
                        e.id,
                        e.content,
                        e.content_preview,
                        e.source_type,
                        e.source_file,
                        e.skill_name,
                        e.client_slug,
                        1 - (e.embedding <=> query_embedding) AS similarity
                    FROM embeddings e
                    WHERE
                        (filter_source_type IS NULL OR e.source_type = filter_source_type)
                        AND (filter_skill_name IS NULL OR e.skill_name = filter_skill_name)
                        AND (filter_client_slug IS NULL OR e.client_slug = filter_client_slug)
                        AND 1 - (e.embedding <=> query_embedding) > match_threshold
                    ORDER BY e.embedding <=> query_embedding
                    LIMIT match_count;
                END;
                $$;
            """)
            
            conn.commit()
            print("✅ Search function created")
            return True
        except Exception as e:
            print(f"❌ Error creating function: {e}")
            conn.rollback()
            return False

def verify_setup(conn):
    """Verify the setup"""
    with conn.cursor() as cur:
        try:
            # Check pgvector
            cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
            if cur.fetchone():
                print("✅ pgvector extension: OK")
            else:
                print("❌ pgvector extension: NOT FOUND")
                return False
            
            # Check table
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'embeddings'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            if columns:
                print(f"✅ Embeddings table: {len(columns)} columns")
            else:
                print("❌ Embeddings table: NOT FOUND")
                return False
            
            # Check function
            cur.execute("""
                SELECT proname 
                FROM pg_proc 
                WHERE proname = 'search_embeddings';
            """)
            if cur.fetchone():
                print("✅ Search function: OK")
            else:
                print("❌ Search function: NOT FOUND")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Error verifying: {e}")
            return False

def main():
    print("=" * 50)
    print("RAG SETUP - Fase 1: Infrastructure")
    print("=" * 50)
    
    try:
        conn = get_connection()
        print("✅ Connected to Supabase PostgreSQL")
        
        # Step 1: Enable pgvector
        print("\n[1/4] Enabling pgvector extension...")
        if not setup_pgvector(conn):
            return
        
        # Step 2: Create embeddings table
        print("\n[2/4] Creating embeddings table...")
        if not create_embeddings_table(conn):
            return
        
        # Step 3: Create search function
        print("\n[3/4] Creating search function...")
        if not create_search_function(conn):
            return
        
        # Step 4: Verify
        print("\n[4/4] Verifying setup...")
        if not verify_setup(conn):
            return
        
        print("\n" + "=" * 50)
        print("✅ RAG INFRASTRUCTURE READY")
        print("=" * 50)
        print("\nNext step: Run ingest.py to vectorize knowledge bases")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
