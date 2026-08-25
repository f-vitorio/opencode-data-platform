#!/usr/bin/env python3
"""
RAG Search Script - Semantic search across agency knowledge bases
Usage: python3 rag-search.py "sua query aqui" [--limit 5] [--threshold 0.5] [--type skill|client|agent]
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

# Load environment variables
env_path = Path.home() / ".config" / "opencode" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import psycopg2
import httpx

EMBEDDING_MODEL = "gemini-embedding-2"

def get_google_api_key():
    key = os.environ.get('GOOGLE_API_KEY')
    if not key:
        print("ERROR: GOOGLE_API_KEY not found in ~/.config/opencode/.env")
        sys.exit(1)
    return key

def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if 'sslmode=' not in db_url:
        db_url += '?sslmode=require'
    return psycopg2.connect(db_url)

def generate_query_embedding(api_key: str, query: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBEDDING_MODEL}:embedContent?key={api_key}"
    payload = {
        "model": f"models/{EMBEDDING_MODEL}",
        "content": {"parts": [{"text": query}]},
        "taskType": "RETRIEVAL_QUERY"
    }
    response = httpx.post(url, json=payload, timeout=30.0)
    if response.status_code != 200:
        print(f"ERROR: Embedding failed - {response.text[:200]}")
        sys.exit(1)
    return response.json()['embedding']['values']

def search(query: str, limit: int = 5, threshold: float = 0.5, 
           source_type: Optional[str] = None, skill_name: Optional[str] = None,
           client_slug: Optional[str] = None):
    api_key = get_google_api_key()
    query_emb = generate_query_embedding(api_key, query)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Build query with proper casting
    emb_str = str(query_emb)
    
    conditions = [f"1 - (embedding <=> '{emb_str}'::vector) > {threshold}"]
    
    if source_type:
        conditions.append(f"source_type = '{source_type}'")
    if skill_name:
        conditions.append(f"skill_name = '{skill_name}'")
    if client_slug:
        conditions.append(f"client_slug = '{client_slug}'")
    
    where_clause = " AND ".join(conditions)
    
    cur.execute(f'''
        SELECT content, content_preview, source_type, source_file, 
               source_path, skill_name, client_slug, agent_name,
               1 - (embedding <=> '{emb_str}'::vector) AS similarity
        FROM embeddings
        WHERE {where_clause}
        ORDER BY embedding <=> '{emb_str}'::vector
        LIMIT {limit}
    ''')
    
    results = []
    for row in cur.fetchall():
        content, preview, src_type, src_file, src_path, skill, client, agent, sim = row
        results.append({
            "content": content,
            "preview": preview,
            "source_type": src_type,
            "source_file": src_file,
            "source_path": src_path,
            "skill_name": skill,
            "client_slug": client,
            "agent_name": agent,
            "similarity": round(float(sim), 4)
        })
    
    conn.close()
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="RAG Semantic Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Max results")
    parser.add_argument("--threshold", type=float, default=0.5, help="Min similarity")
    parser.add_argument("--type", dest="source_type", help="Filter: skill, client, agent")
    parser.add_argument("--skill", help="Filter by skill name")
    parser.add_argument("--client", help="Filter by client slug")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    results = search(
        args.query, 
        limit=args.limit,
        threshold=args.threshold,
        source_type=args.source_type,
        skill_name=args.skill,
        client_slug=args.client
    )
    
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("Nenhum resultado encontrado.")
            return
        
        print(f"\n{'='*60}")
        print(f"QUERY: {args.query}")
        print(f"RESULTADOS: {len(results)}")
        print(f"{'='*60}\n")
        
        for i, r in enumerate(results, 1):
            print(f"[{i}] [{r['similarity']:.3f}] {r['source_type']}/{r['source_file']}")
            if r.get('skill_name'):
                print(f"    Skill: {r['skill_name']}")
            if r.get('client_slug'):
                print(f"    Client: {r['client_slug']}")
            print(f"    {r['preview'][:150]}...")
            print()

if __name__ == "__main__":
    main()
