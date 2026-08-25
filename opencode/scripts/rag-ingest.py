#!/usr/bin/env python3
"""
RAG Ingest Script - Vectorize knowledge bases using Google Gemini
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
import json

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

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMS = 3072

def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if 'sslmode=' not in db_url:
        db_url += '?sslmode=require'
    return psycopg2.connect(db_url)

def get_google_api_key():
    key = os.environ.get('GOOGLE_API_KEY')
    if not key:
        print("GOOGLE_API_KEY not found in ~/.config/opencode/.env")
        sys.exit(1)
    return key

def discover_files() -> List[Dict]:
    files = []
    base_path = Path.home() / ".config" / "opencode"
    
    # Skills
    skills_path = base_path / "skills"
    if skills_path.exists():
        for skill_dir in skills_path.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    files.append({
                        "path": str(skill_md),
                        "source_type": "skill",
                        "source_file": skill_md.name,
                        "source_path": str(skill_md.relative_to(base_path)),
                        "skill_name": skill_dir.name,
                    })
    
    # Company profile
    for p in ["company-profile/COMPANY.md", "company/company-profile.md"]:
        cp = base_path / p
        if cp.exists():
            files.append({
                "path": str(cp),
                "source_type": "company",
                "source_file": cp.name,
                "source_path": p,
                "skill_name": None,
            })
    
    # Clients
    clients_path = base_path / "clients"
    if clients_path.exists():
        for client_md in clients_path.glob("*.md"):
            slug = client_md.stem
            files.append({
                "path": str(client_md),
                "source_type": "client",
                "source_file": client_md.name,
                "source_path": f"clients/{client_md.name}",
                "skill_name": None,
                "client_slug": slug,
            })
    
    # Agents
    agents_path = base_path / "agents"
    if agents_path.exists():
        for agent_md in agents_path.glob("*.md"):
            files.append({
                "path": str(agent_md),
                "source_type": "agent",
                "source_file": agent_md.name,
                "source_path": f"agents/{agent_md.name}",
                "skill_name": None,
                "agent_name": agent_md.stem,
            })
    
    # Knowledge (general operational reference docs)
    knowledge_path = base_path / "knowledge"
    if knowledge_path.exists():
        for kb_md in knowledge_path.glob("*.md"):
            files.append({
                "path": str(kb_md),
                "source_type": "knowledge",
                "source_file": kb_md.name,
                "source_path": f"knowledge/{kb_md.name}",
                "skill_name": None,
            })

    # Agency knowledge
    ak = Path.home() / ".claude" / "AGENCY-KNOWLEDGE.md"
    if ak.exists():
        files.append({
            "path": str(ak),
            "source_type": "agency",
            "source_file": ak.name,
            "source_path": "AGENCY-KNOWLEDGE.md",
            "skill_name": None,
        })
    
    return files

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
        if start + overlap >= len(text):
            break
    return chunks if chunks else [text[:chunk_size]]

def generate_embeddings_gemini(api_key: str, texts: List[str]) -> List[List[float]]:
    """Generate embeddings using Google Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{EMBEDDING_MODEL}:embedContent?key={api_key}"
    
    embeddings = []
    for text in texts:
        payload = {
            "model": f"models/{EMBEDDING_MODEL}",
            "content": {"parts": [{"text": text}]},
            "taskType": "RETRIEVAL_DOCUMENT"
        }
        
        response = httpx.post(url, json=payload, timeout=30.0)
        
        if response.status_code == 200:
            data = response.json()
            embedding = data["embedding"]["values"]
            embeddings.append(embedding)
        else:
            print(f"\n  ⚠️ Error generating embedding: {response.status_code}")
            # Return zero vector on error
            embeddings.append([0.0] * EMBEDDING_DIMS)
    
    return embeddings

def ingest_file(conn, api_key: str, file_info: Dict) -> int:
    path = Path(file_info["path"])
    if not path.exists():
        return 0
    
    content = path.read_text(encoding='utf-8', errors='ignore')
    if not content.strip():
        return 0
    
    chunks = chunk_text(content)
    embeddings = generate_embeddings_gemini(api_key, chunks)
    
    with conn.cursor() as cur:
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            cur.execute("""
                INSERT INTO embeddings (
                    content, content_preview, source_type, source_file,
                    source_path, chunk_index, chunk_total,
                    skill_name, client_slug, agent_name, embedding, token_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s)
            """, (
                chunk,
                chunk[:500],
                file_info["source_type"],
                file_info["source_file"],
                file_info["source_path"],
                i,
                len(chunks),
                file_info.get("skill_name"),
                file_info.get("client_slug"),
                file_info.get("agent_name"),
                str(embedding),
                len(chunk.split())
            ))
    
    conn.commit()
    return len(chunks)

def main():
    print("=" * 50)
    print("RAG INGEST - Google Gemini Embeddings")
    print("=" * 50)
    
    conn = get_connection()
    api_key = get_google_api_key()
    
    files = discover_files()
    print(f"\nFound {len(files)} files to vectorize\n")
    
    total_chunks = 0
    for i, file_info in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {file_info['source_path']}...", end=" ")
        chunks = ingest_file(conn, api_key, file_info)
        total_chunks += chunks
        print(f"({chunks} chunks)")
    
    print(f"\n{'=' * 50}")
    print(f"COMPLETE: {total_chunks} chunks from {len(files)} files")
    print(f"{'=' * 50}")
    
    conn.close()

if __name__ == "__main__":
    main()
