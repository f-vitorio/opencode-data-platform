#!/usr/bin/env python3
"""
proposal-render.py — Renderiza proposta do banco para JSON + Markdown + HTML
Uso: python3 proposal-render.py --proposal-id 3 [--format json|md|html|all]
"""

import os
import sys
import argparse
import json
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

import psycopg2


def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERRO: DATABASE_URL não encontrada")
        sys.exit(1)
    if 'sslmode=' not in db_url:
        db_url += '?sslmode=require'
    return psycopg2.connect(db_url)


def get_proposal(conn, proposal_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.id, p.client_id, p.title, p.services, p.total_value, p.monthly_value,
                   p.status, p.sent_at, p.approved_at, p.document_path, p.created_at,
                   c.company_name, c.slug as client_slug
            FROM proposals p
            JOIN clients c ON c.id = p.client_id
            WHERE p.id = %s
        """, (proposal_id,))
        return cur.fetchone()


def render_json(proposal):
    return {
        "id": proposal[0],
        "client_id": proposal[1],
        "title": proposal[2],
        "services": proposal[3],
        "total_value": float(proposal[4]),
        "monthly_value": float(proposal[5]),
        "status": proposal[6],
        "sent_at": proposal[7].isoformat() if proposal[7] else None,
        "approved_at": proposal[8].isoformat() if proposal[8] else None,
        "document_path": proposal[9],
        "created_at": proposal[10].isoformat() if proposal[10] else None,
        "client_name": proposal[11],
        "client_slug": proposal[12]
    }


def render_markdown(proposal):
    client_name = proposal[11]
    client_slug = proposal[12]
    services = proposal[3]
    total = float(proposal[4])
    monthly = float(proposal[5])
    
    services_md = '\n'.join(
        f"- **{s['servico']}**: R$ {s['valor']:,.2f} ({s['tipo']})"
        for s in services
    )
    
    # Ler markdown original se existir
    doc_path = proposal[9]
    full_content = ""
    if doc_path and Path(doc_path).exists():
        full_content = Path(doc_path).read_text(encoding='utf-8')
    else:
        full_content = "Conteúdo completo não disponível (arquivo markdown não encontrado)."
    
    return f"""# {proposal[2]}

**Cliente:** {client_name} ({client_slug})
**Status:** {proposal[6]}
**Criado em:** {proposal[10].strftime('%Y-%m-%d %H:%M') if proposal[10] else 'N/A'}
**Valor Total:** R$ {total:,.2f}
**Valor Mensal:** R$ {monthly:,.2f}

---

## SERVIÇOS INCLUÍDOS

{services_md}

---

## CONTEÚDO COMPLETO

{full_content}

---

## METADADOS DO BANCO

- **Proposal ID:** {proposal[0]}
- **Client ID:** {proposal[1]}
- **Document Path:** {proposal[9] or 'N/A'}
- **Sent At:** {proposal[7].strftime('%Y-%m-%d %H:%M') if proposal[7] else 'N/A'}
- **Approved At:** {proposal[8].strftime('%Y-%m-%d %H:%M') if proposal[8] else 'N/A'}
"""


def render_html(proposal):
    md = render_markdown(proposal)
    # Simple markdown to HTML (basic)
    html = md.replace('\n', '<br>')
    html = html.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')
    html = html.replace('**', '<strong>').replace('**', '</strong>')
    html = html.replace('- ', '<li>') + '</li>'
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{proposal[2]}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }}
        h1 {{ color: #1a1a2e; border-bottom: 2px solid #e94560; padding-bottom: 0.5rem; }}
        h2 {{ color: #16213e; margin-top: 2rem; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
        th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
        th {{ background: #1a1a2e; color: white; }}
        code {{ background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px; }}
        pre {{ background: #1a1a2e; color: #eee; padding: 1rem; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description='Renderiza proposta do banco para JSON/Markdown/HTML')
    parser.add_argument('--proposal-id', type=int, required=True, help='ID da proposta no banco')
    parser.add_argument('--format', choices=['json', 'md', 'html', 'all'], default='all', help='Formato de saída')
    parser.add_argument('--output-dir', help='Diretório para salvar arquivos (default: stdout)')
    args = parser.parse_args()

    conn = get_connection()
    try:
        proposal = get_proposal(conn, args.proposal_id)
        if not proposal:
            print(f"ERRO: Proposta {args.proposal_id} não encontrada")
            sys.exit(1)
        
        output_dir = Path(args.output_dir) if args.output_dir else None
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        if args.format in ('json', 'all'):
            json_data = render_json(proposal)
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            if output_dir:
                path = output_dir / f"proposal_{args.proposal_id}.json"
                path.write_text(json_str, encoding='utf-8')
                print(f"JSON salvo em: {path}")
            else:
                print(json_str)
        
        if args.format in ('md', 'all'):
            md_content = render_markdown(proposal)
            if output_dir:
                path = output_dir / f"proposal_{args.proposal_id}.md"
                path.write_text(md_content, encoding='utf-8')
                print(f"Markdown salvo em: {path}")
            else:
                print(md_content)
        
        if args.format in ('html', 'all'):
            html_content = render_html(proposal)
            if output_dir:
                path = output_dir / f"proposal_{args.proposal_id}.html"
                path.write_text(html_content, encoding='utf-8')
                print(f"HTML salvo em: {path}")
            else:
                print(html_content)
                
    finally:
        conn.close()


if __name__ == "__main__":
    main()