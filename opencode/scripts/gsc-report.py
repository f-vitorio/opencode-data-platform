#!/usr/bin/env python3
"""
Google Search Console - Relatório de Desempenho (Últimos 30 dias)
Uso: python3 gsc-report.py [--site URL] [--days 30]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
SERVICE_ACCOUNT_FILE = os.path.expanduser('~/.config/opencode/credentials/service-account.json')

def get_gsc_service():
    """Autentica e retorna o serviço do GSC."""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('searchconsole', 'v1', credentials=credentials)

def list_sites(service):
    """Lista todos os sites acessíveis pela service account."""
    site_list = service.sites().list().execute()
    return site_list.get('siteEntry', [])

def get_search_analytics(service, site_url, days=30):
    """Busca dados de desempenho do GSC."""
    end_date = datetime.now() - timedelta(days=1)  # Ontem (dados completos)
    start_date = end_date - timedelta(days=days)
    
    request = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['query', 'page'],
        'rowLimit': 1000,
        'startRow': 0
    }
    
    response = service.searchanalytics().query(
        siteUrl=site_url, body=request
    ).execute()
    
    return response.get('rows', [])

def analyze_opportunities(rows):
    """Analisa dados e identifica oportunidades de melhoria."""
    opportunities = {
        'high_potential_low_ctr': [],      # Alta impressão, baixo CTR
        'declining_queries': [],           # Queries em declínio
        'page_optimization': [],           # Páginas para otimizar
        'quick_wins': [],                  # Oportunidades de ganho rápido
        'long_tail_opportunities': []      # Oportunidades de cauda longa
    }
    
    for row in rows:
        query = row.get('keys', [''])[0]
        page = row.get('keys', [''])[1] if len(row.get('keys', [])) > 1 else ''
        impressions = row.get('impressions', 0)
        clicks = row.get('clicks', 0)
        ctr = row.get('ctr', 0)
        position = row.get('position', 0)
        
        # Alto potencial: muitas impressões, baixo CTR
        if impressions > 1000 and ctr < 0.05:
            opportunities['high_potential_low_ctr'].append({
                'query': query,
                'page': page,
                'impressions': impressions,
                'ctr': round(ctr * 100, 2),
                'position': round(position, 1)
            })
        
        # Oportunidades de ganho rápido: posição 5-15
        if 5 <= position <= 15 and impressions > 500:
            opportunities['quick_wins'].append({
                'query': query,
                'page': page,
                'position': round(position, 1),
                'impressions': impressions,
                'clicks': clicks
            })
    
    # Ordenar por impacto potencial
    opportunities['high_potential_low_ctr'].sort(key=lambda x: x['impressions'], reverse=True)
    opportunities['quick_wins'].sort(key=lambda x: x['position'])
    
    return opportunities

def generate_report(site_url, rows, opportunities, days):
    """Gera relatório formatado."""
    # Calcular métricas gerais
    total_clicks = sum(r.get('clicks', 0) for r in rows)
    total_impressions = sum(r.get('impressions', 0) for r in rows)
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_position = sum(r.get('position', 0) for r in rows) / len(rows) if rows else 0
    
    report = []
    report.append(f"# Relatório Google Search Console")
    report.append(f"**Período:** Últimos {days} dias")
    report.append(f"**Site:** {site_url}")
    report.append(f"**Data:** {datetime.now().strftime('%d/%m/%Y')}")
    report.append("")
    report.append("## Resumo Geral")
    report.append(f"- **Total de Cliques:** {total_clicks:,}")
    report.append(f"- **Total de Impressões:** {total_impressions:,}")
    report.append(f"- **CTR Médio:** {avg_ctr:.2f}%")
    report.append(f"- **Posição Média:** {avg_position:.1f}")
    report.append(f"- **Queries Únicas:** {len(rows):,}")
    report.append("")
    
    # Oportunidades Urgentes
    report.append("## Oportunidades de Melhoria Urgentes")
    report.append("")
    
    # 1. Alto potencial com baixo CTR
    if opportunities['high_potential_low_ctr']:
        report.append("### 1. Queries com Alto Potencial e Baixo CTR (URGENTE)")
        report.append("Estas queries têm muitas impressões mas CTR baixo. Melhorar títulos e meta descriptions pode gerar ganho rápido.")
        report.append("")
        for i, item in enumerate(opportunities['high_potential_low_ctr'][:10], 1):
            report.append(f"**{i}. \"{item['query']}\"")
            report.append(f"   - Impressões: {item['impressions']:,}")
            report.append(f"   - CTR Atual: {item['ctr']}%")
            report.append(f"   - Posição: {item['position']}")
            report.append(f"   - Página: {item['page']}")
            report.append("")
    
    # 2. Quick wins
    if opportunities['quick_wins']:
        report.append("### 2. Quick Wins (Posição 5-15)")
        report.append("Estas queries estão perto da primeira página. Pequenas otimizações podem trazer ganho significativo.")
        report.append("")
        for i, item in enumerate(opportunities['quick_wins'][:10], 1):
            report.append(f"**{i}. \"{item['query']}\"")
            report.append(f"   - Posição: {item['position']}")
            report.append(f"   - Impressões: {item['impressions']:,}")
            report.append(f"   - Cliques Atuais: {item['clicks']}")
            report.append(f"   - Página: {item['page']}")
            report.append("")
    
    # Ações Recomendadas
    report.append("## Ações Recomendadas")
    report.append("")
    report.append("### Imediatas (esta semana)")
    report.append("1. **Otimizar meta descriptions** das queries com alto potencial e baixo CTR")
    report.append("2. **Revisar títulos** das páginas que aparecem nas posições 5-15")
    report.append("3. **Verificar conteúdo** das páginas para garantir relevância")
    report.append("")
    report.append("### Médio prazo (2-4 semanas)")
    report.append("1. **Criar conteúdo** para queries com alto volume e baixa cobertura")
    report.append("2. **Melhorar internal linking** entre páginas relacionadas")
    report.append("3. **Atualizar conteúdo** desatualizado")
    report.append("")
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='Relatório GSC')
    parser.add_argument('--site', help='URL do site (ex: https://exemplo.com)')
    parser.add_argument('--days', type=int, default=30, help='Período em dias (padrão: 30)')
    parser.add_argument('--json', action='store_true', help='Saída em JSON')
    args = parser.parse_args()
    
    try:
        service = get_gsc_service()
        
        # Listar sites se não especificado
        if not args.site:
            sites = list_sites(service)
            if not sites:
                print("❌ Nenhum site encontrado. Verifique se a service account tem acesso.")
                sys.exit(1)
            
            if len(sites) == 1:
                site_url = sites[0]['siteUrl']
                print(f"📍 Site encontrado: {site_url}")
            else:
                print("📍 Sites disponíveis:")
                for i, site in enumerate(sites, 1):
                    print(f"  {i}. {site['siteUrl']}")
                print("\nUse --site URL para especificar.")
                sys.exit(0)
        else:
            site_url = args.site
        
        print(f"\n📊 Buscando dados dos últimos {args.days} dias...")
        rows = get_search_analytics(service, site_url, args.days)
        
        if not rows:
            print("⚠️  Nenhum dado encontrado para o período especificado.")
            sys.exit(0)
        
        opportunities = analyze_opportunities(rows)
        
        if args.json:
            output = {
                'site': site_url,
                'period_days': args.days,
                'total_queries': len(rows),
                'opportunities': opportunities
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            report = generate_report(site_url, rows, opportunities, args.days)
            print(report)
            
            # Salvar relatório
            filename = f"gsc-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            with open(filename, 'w') as f:
                f.write(report)
            print(f"\n💾 Relatório salvo em: {filename}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
