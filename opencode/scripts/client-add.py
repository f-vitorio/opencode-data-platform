#!/usr/bin/env python3
"""
client-add.py — Cadastro rápido de cliente em 1 chamada
Uso: python3 client-add.py --name "Nome" --slug "slug" [opções]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Load environment
env_path = Path.home() / ".config" / "opencode" / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

import json
import psycopg2


def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERRO: DATABASE_URL não encontrada")
        sys.exit(1)
    if 'sslmode=' not in db_url:
        db_url += '?sslmode=require'
    return psycopg2.connect(db_url)


def check_duplicate(conn, slug):
    with conn.cursor() as cur:
        cur.execute("SELECT id, company_name FROM clients WHERE slug = %s", (slug,))
        return cur.fetchone()


def create_client(conn, args):
    services = json.dumps([s.strip() for s in args.services.split(',')] if args.services else [])
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (
                slug, company_name, segment, website, location,
                contact_name, contact_role, contact_channel,
                contact_phone, contact_email,
                agency_services, stage, origin, priority,
                first_contact_date, next_followup_note, notes
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s,
                %s::jsonb, %s, %s, %s,
                %s, %s, %s
            ) RETURNING id
        """, (
            args.slug, args.name, args.segment, args.website, args.location,
            args.contact or args.name, args.role, args.channel or 'WhatsApp',
            args.phone, args.email, services,
            'LEAD', args.origin or 'Cadastro manual', args.priority or 'MEDIA',
            datetime.now().strftime('%Y-%m-%d'),
            args.note or f"Cliente {args.name} cadastrado via client-add.py",
            args.note
        ))
        result = cur.fetchone()
        conn.commit()
        return result[0] if result else None


def create_interaction(conn, client_id, client_name):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO interactions (client_id, interaction_type, subject, content)
            VALUES (%s, %s, %s, %s)
        """, (client_id, 'CADASTRO', 'Cadastro inicial',
              f'Cliente {client_name} cadastrado via client-add.py.'))
        conn.commit()


def create_markdown(args):
    md_dir = Path.home() / ".config" / "opencode" / "clients"
    md_dir.mkdir(parents=True, exist_ok=True)
    services = [s.strip() for s in args.services.split(',')] if args.services else []
    services_md = '\n'.join(f"- {s}" for s in services) if services else '- Não informado'
    today = datetime.now().strftime('%Y-%m-%d')
    content = f"""# CLIENTE — {args.name}

## DADOS DA EMPRESA

- **Nome**: {args.name}
- **Segmento**: {args.segment or 'Não informado'}
- **Site**: {args.website or 'Não informado'}
- **Localizacao**: {args.location or 'Não informado'}

## CONTATO

- **Nome**: {args.contact or args.name}
- **Cargo**: {args.role or 'Não informado'}
- **Canal**: {args.channel or 'WhatsApp'}
- **Telefone**: {args.phone or 'Não informado'}
- **Email**: {args.email or 'Não informado'}

## SERVICOS

{services_md}

## PIPELINE

- **Etapa**: LEAD
- **Origem**: {args.origin or 'Cadastro manual'}
- **Prioridade**: {args.priority or 'MEDIA'}
- **Data**: {today}

## NOTAS

{args.note or 'Nenhuma nota adicional.'}

## HISTORICO

### {today} — CADASTRO

Cliente cadastrado via client-add.py.
"""
    path = md_dir / f"{args.slug}.md"
    path.write_text(content, encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description='Cadastro rápido de cliente')
    parser.add_argument('--name', required=True, help='Nome da empresa/cliente')
    parser.add_argument('--slug', required=True, help='Slug único')
    parser.add_argument('--segment', help='Segmento')
    parser.add_argument('--website', help='URL do site')
    parser.add_argument('--location', help='Localização')
    parser.add_argument('--contact', help='Nome do contato')
    parser.add_argument('--role', help='Cargo do contato')
    parser.add_argument('--phone', help='Telefone/WhatsApp')
    parser.add_argument('--email', help='Email')
    parser.add_argument('--channel', default='WhatsApp', help='Canal (default: WhatsApp)')
    parser.add_argument('--services', help='Serviços separados por vírgula')
    parser.add_argument('--origin', help='Origem do lead')
    parser.add_argument('--priority', default='MEDIA', help='ALTA/MEDIA/BAIXA')
    parser.add_argument('--note', help='Nota adicional')
    parser.add_argument('--no-markdown', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if ' ' in args.slug:
        print("ERRO: Slug não pode conter espaços")
        sys.exit(1)

    conn = get_connection()
    try:
        existing = check_duplicate(conn, args.slug)
        if existing:
            print(f"ERRO: Cliente já existe (id={existing[0]}, nome='{existing[1]}')")
            sys.exit(1)

        client_id = create_client(conn, args)
        if not client_id:
            print("ERRO: Falha ao criar cliente")
            sys.exit(1)

        create_interaction(conn, client_id, args.name)

        md_path = None
        if not args.no_markdown:
            md_path = create_markdown(args)

        if args.json:
            import json
            print(json.dumps({
                "success": True,
                "client_id": client_id,
                "slug": args.slug,
                "name": args.name,
                "markdown": str(md_path) if md_path else None
            }, indent=2))
        else:
            print(f"✅ Cliente cadastrado: {args.name} (id={client_id})")
            if md_path:
                print(f"📄 Markdown: {md_path}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
