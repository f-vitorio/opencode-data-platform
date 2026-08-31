#!/usr/bin/env python3
"""
proposal-create-template.py — Cria templates de proposta no banco + markdown
Uso: python3 proposal-create-template.py --template-file template.yaml [--client-slug templates-fvs7] [--dry-run]
"""

import os
import sys
import argparse
import yaml
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


def get_client_id(conn, client_slug):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM clients WHERE slug = %s", (client_slug,))
        result = cur.fetchone()
        if not result:
            print(f"ERRO: Cliente '{client_slug}' não encontrado")
            sys.exit(1)
        return result[0]


def check_template_exists(conn, client_id, title):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM proposals WHERE client_id = %s AND title = %s AND status = 'TEMPLATE'",
            (client_id, title)
        )
        return cur.fetchone()


def create_proposal(conn, client_id, template_data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO proposals (
                client_id, title, services,
                total_value, monthly_value, status,
                document_path, created_at, updated_at
            ) VALUES (
                %s, %s, %s::jsonb,
                %s, %s, %s,
                %s, NOW(), NOW()
            ) RETURNING id
        """, (
            client_id,
            template_data['title'],
            json.dumps(template_data['services']),
            template_data['total_value'],
            template_data.get('monthly_value', 0),
            'TEMPLATE',
            template_data.get('document_path', '')
        ))
        result = cur.fetchone()
        conn.commit()
        return result[0] if result else None


def create_interaction(conn, client_id, proposal_title):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO interactions (client_id, interaction_type, subject, content)
            VALUES (%s, %s, %s, %s)
        """, (
            client_id,
            'CADASTRO_TEMPLATE',
            f'Template criado: {proposal_title}',
            f'Template de proposta "{proposal_title}" cadastrado no sistema.'
        ))
        conn.commit()


def generate_markdown(template_data, client_slug):
    """Gera arquivo markdown da proposta"""
    md_dir = Path.home() / ".config" / "opencode" / "proposals"
    md_dir.mkdir(parents=True, exist_ok=True)
    
    services_md = '\n'.join(
        f"- **{s['servico']}**: R$ {s['valor']:,.2f} ({s['tipo']})"
        for s in template_data['services']
    )
    
    content = f"""# TEMPLATE DE PROPOSTA — {template_data['title']}

**Cliente:** TEMPLATES FVS7 ({client_slug})
**Status:** TEMPLATE (modelo reutilizável)
**Criado em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Valor Total:** R$ {template_data['total_value']:,.2f}
**Valor Mensal:** R$ {template_data.get('monthly_value', 0):,.2f}

---

## SERVIÇOS INCLUÍDOS

{services_md}

---

## CONTEÚDO COMPLETO DA PROPOSTA

{template_data.get('markdown_content', 'Conteúdo não definido.')}

---

## METADADOS

- **Template ID:** {template_data.get('slug', 'auto')}
- **Última atualização:** {datetime.now().strftime('%Y-%m-%d')}
- **Versão:** 1.0
"""
    slug = template_data.get('slug', template_data['title'].lower().replace(' ', '-').replace('/', '-'))
    path = md_dir / f"{slug}.md"
    path.write_text(content, encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description='Cria template de proposta no banco + markdown')
    parser.add_argument('--template-file', required=True, help='Arquivo YAML com definição do template')
    parser.add_argument('--client-slug', default='templates-fvs7', help='Slug do cliente (default: templates-fvs7)')
    parser.add_argument('--dry-run', action='store_true', help='Apenas mostra o que faria, não executa')
    args = parser.parse_args()

    # Carregar YAML
    template_path = Path(args.template_file)
    if not template_path.exists():
        print(f"ERRO: Arquivo não encontrado: {template_path}")
        sys.exit(1)
    
    with open(template_path) as f:
        template_data = yaml.safe_load(f)
    
    # Validações básicas
    required = ['title', 'services', 'total_value']
    for field in required:
        if field not in template_data:
            print(f"ERRO: Campo obrigatório ausente no YAML: {field}")
            sys.exit(1)
    
    if not isinstance(template_data['services'], list) or len(template_data['services']) == 0:
        print("ERRO: 'services' deve ser uma lista não vazia")
        sys.exit(1)
    
    for i, s in enumerate(template_data['services']):
        if 'servico' not in s or 'valor' not in s or 'tipo' not in s:
            print(f"ERRO: Serviço {i} deve ter 'servico', 'valor' e 'tipo'")
            sys.exit(1)
    
    print(f"Template: {template_data['title']}")
    print(f"Cliente: {args.client_slug}")
    print(f"Valor total: R$ {template_data['total_value']:,.2f}")
    print(f"Serviços: {len(template_data['services'])}")
    
    if args.dry_run:
        print("\n[DRY-RUN] Não executando inserção no banco.")
        md_path = generate_markdown(template_data, args.client_slug)
        print(f"[DRY-RUN] Markdown seria salvo em: {md_path}")
        return
    
    # Conectar e executar
    conn = get_connection()
    try:
        client_id = get_client_id(conn, args.client_slug)
        
        existing = check_template_exists(conn, client_id, template_data['title'])
        if existing:
            print(f"AVISO: Template já existe (id={existing[0]}). Atualizando...")
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE proposals 
                    SET services = %s::jsonb, total_value = %s, monthly_value = %s,
                        document_path = %s, updated_at = NOW()
                    WHERE id = %s
                """, (
                    json.dumps(template_data['services']),
                    template_data['total_value'],
                    template_data.get('monthly_value', 0),
                    template_data.get('document_path', ''),
                    existing[0]
                ))
                conn.commit()
                proposal_id = existing[0]
                print(f"Template atualizado (id={proposal_id})")
        else:
            proposal_id = create_proposal(conn, client_id, template_data)
            if not proposal_id:
                print("ERRO: Falha ao criar template")
                sys.exit(1)
            create_interaction(conn, client_id, template_data['title'])
            print(f"Template criado com id={proposal_id}")
        
        # Gerar markdown
        md_path = generate_markdown(template_data, args.client_slug)
        print(f"Markdown salvo em: {md_path}")
        
        # Atualizar document_path no banco
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE proposals SET document_path = %s WHERE id = %s",
                (str(md_path), proposal_id)
            )
            conn.commit()
        
        print("✅ Concluído com sucesso!")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()