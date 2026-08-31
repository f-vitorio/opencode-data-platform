#!/usr/bin/env python3
"""
competitor-intel-mock.py — Gera dados mock de inteligência competitiva para Google Ads
Uso: python3 competitor-intel-mock.py --nicho "advogados trabalhistas" --geo "São Paulo - SP" --output-json
"""

import os
import sys
import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Base de conhecimento por nicho para gerar dados realísticos
NICHE_DATA = {
    "advogados": {
        "keywords_base": [
            "advogado trabalhista", "advogado previdenciario", "advogado empresarial",
            "advogado civil", "advogado criminal", "escritorio de advocacia",
            "consulta juridica", "acao trabalhista", "revisao de aposentadoria",
            "direito do consumidor", "inventario", "divorcio"
        ],
        "modifiers": ["sp", "sao paulo", "campinas", "santos", "ribeirao preto", "perto de mim", "online", "gratuito", "preco", "valor", "consulta"],
        "competitors": [
            "Martins & Advogados", "Silva Advocacia", "Rocha & Associados",
            "Oliveira Direito", "Costa & Pereira", "Fernandes Advogados",
            "Almeida Juridico", "Gomes & Lima", "Ribeiro Advocacia", "Carvalho Direito"
        ],
        "offers": [
            "Consulta inicial gratuita", "Honorários só se ganhar", "Atendimento 24h WhatsApp",
            "Especialista em [área]", "15 anos de experiência", "Mais de 500 casos ganhos",
            "Parcelamento em até 12x", "Atendimento online e presencial"
        ],
        "ctas": ["Agendar consulta", "Falar no WhatsApp", "Solicitar orçamento", "Ver casos de sucesso"]
    },
    "clinicas": {
        "keywords_base": [
            "clinica dermatologia", "clinica estetica", "harmonizacao facial",
            "botox", "preenchimento", "laser co2", "depilacao a laser",
            "clinica odontologia", "implante dentario", "lente de contato dental",
            "clinica fisioterapia", "fisioterapia esportiva", "rpg"
        ],
        "modifiers": ["sp", "sao paulo", "vila mariana", "jardins", "moema", "perto de mim", "preco", "valor", "agendar", "avaliacao"],
        "competitors": [
            "Clinica Derme", "Estetica Bella", "OdontoPrime", "FisioTop",
            "Harmoniza Clinic", "Laser Skin", "Sorriso Perfeito", "Corpo & Mente",
            "Clinica Vita", "Estetica Pro"
        ],
        "offers": [
            "Avaliação gratuita", "Parcelamento sem juros", "Resultado garantido ou devolvemos",
            "Especialistas certificados", "Tecnologia de ponta", "Atendimento humanizado",
            "Horário estendido", "Estacionamento no local"
        ],
        "ctas": ["Agendar avaliação", "WhatsApp para dúvidas", "Ver antes/depois", "Consultar valores"]
    },
    "arquitetos": {
        "keywords_base": [
            "arquiteto residencial", "arquiteto comercial", "projeto arquitetonico",
            "reforma apartamento", "projeto de interiores", "arquiteto de alto padrao",
            "regularizacao de imovel", "habite-se", "projeto legal", "retrofit"
        ],
        "modifiers": ["sp", "sao paulo", "alphaville", "jardins", "morumbi", "perto de mim", "preco", "valor", "portfolio", "orcamento"],
        "competitors": [
            "Arquitetura Prime", "Studio Arq", "Projeto & Forma", "ArqDesign",
            "Espaço Arquitetura", "Forma & Função", "ArqAtelier", "Projetarq",
            "Arquitetos Associados", "Design Arq"
        ],
        "offers": [
            "Visita técnica grátis", "Projeto 3D incluso", "Acompanhamento de obra",
            "Portfólio 50+ projetos", "Especialista em alto padrão", "Entrega no prazo",
            "Parcelamento por etapa", "Garantia de aprovação na prefeitura"
        ],
        "ctas": ["Solicitar orçamento", "Ver portfólio", "Agendar visita", "Falar no WhatsApp"]
    },
    "contadores": {
        "keywords_base": [
            "contador para empresa", "abertura de empresa", "contabilidade para mei",
            "planejamento tributario", "contador online", "escritorio contabilidade",
            "simples nacional", "lucro presumido", "folha de pagamento", "imposto de renda pj"
        ],
        "modifiers": ["sp", "sao paulo", "online", "digital", "preco", "valor", "mensalidade", "especialista", "consultoria"],
        "competitors": [
            "Contabilidade Prime", "Contador Online", "Fiscal Contabilidade",
            "Gestão Contábil", "Contabilidade Pro", "Conta Fácil", "Contador Certo",
            "Contabilidade 360", "Smart Contabilidade", "Exata Contabilidade"
        ],
        "offers": [
            "Abertura grátis", "Primeiro mês grátis", "Certificado digital incluso",
            "Atendimento WhatsApp", "Relatórios mensais", "Especialista no seu segmento",
            "Economia tributária comprovada", "Plataforma digital própria"
        ],
        "ctas": ["Simular economia", "Falar com contador", "Abrir empresa grátis", "Ver planos"]
    },
    "imobiliarias": {
        "keywords_base": [
            "imobiliaria alto padrao", "apartamento de luxo", "casa em alphaville",
            "lancamento imobiliario", "imoveis de luxo sp", "cobertura duplex",
            "terreno condominio fechado", "apartamento jardin", "imovel de alto valor"
        ],
        "modifiers": ["sp", "sao paulo", "alphaville", "tambore", "jardins", "morumbi", "vila nova conceicao", "preco", "valor", "visita", "financiamento"],
        "competitors": [
            "Imobiliaria Prime", "Luxury Imoveis", "Alto Padrão SP", "Mansões & Cia",
            "Imóveis Exclusivos", "Prime Properties", "Select Imoveis", "Unique Imoveis",
            "Top Imobiliaria", "Elite Imoveis"
        ],
        "offers": [
            "Portfólio exclusivo", "Visita agendada com especialista", "Assessoria jurídica inclusa",
            "Financiamento aprovado em 48h", "Imóveis off-market", "Corretor dedicado",
            "Avaliação grátis do seu imóvel", "Network de compradores qualificados"
        ],
        "ctas": ["Ver imóveis exclusivos", "Agendar visita", "Falar com corretor", "Avaliar meu imóvel"]
    },
    "saas": {
        "keywords_base": [
            "software gestao", "erp online", "crm vendas", "sistema para clinica",
            "sistema para advocacia", "automacao marketing", "plataforma cursos online",
            "sistema delivery", "gestao financeira", "bpm software"
        ],
        "modifiers": ["gratis", "teste gratis", "demo", "preco", "planos", "comparativo", "melhor", "brasileiro", "nuvem", "saas"],
        "competitors": [
            "TechSoft", "GestãoClick", "SistemaPro", "CloudGestao", "SmartERP",
            "VendaFacil", "ClinicaSystem", "AdvocaciaTech", "CursoOnline", "AutoMarketing"
        ],
        "offers": [
            "Teste grátis 14 dias", "Setup grátis", "Migração de dados inclusa",
            "Suporte humanizado", "API aberta", "LGPD compliant",
            "Treinamento da equipe", "Integração com contabilidade"
        ],
        "ctas": ["Testar grátis", "Agendar demo", "Ver preços", "Falar com especialista"]
    }
}


def detect_niche(nicho_str):
    """Detecta qual nicho do dicionário melhor corresponde"""
    nicho_lower = nicho_str.lower()
    for key in NICHE_DATA.keys():
        if key in nicho_lower or any(k in nicho_lower for k in [key, key.replace('clinicas', 'clinica'), key.replace('arquitetos', 'arquiteto')]):
            return key
    # Default para advogados se não encontrar
    return "advogados"


def generate_keywords(niche_data, geo, count=80):
    """Gera lista de keywords mockadas"""
    keywords = []
    base = niche_data["keywords_base"]
    mods = niche_data["modifiers"]
    
    intencoes = ["A", "B", "C", "D", "E"]
    comerciais = ["Alta", "Média", "Baixa"]
    concorrencias = ["Alta", "Média", "Baixa"]
    
    for _ in range(count):
        kw_base = random.choice(base)
        mod = random.choice(mods)
        keyword = f"{kw_base} {mod}" if random.random() > 0.3 else kw_base
        
        # Intenção baseada no modificador
        if any(m in keyword for m in ["preco", "valor", "orcamento", "contratar", "comprar", "agendar", "consulta"]):
            intencao = random.choice(["A", "B"])
            comercial = "Alta"
        elif any(m in keyword for m in ["gratis", "gratuito", "curso", "faculdade", "o que e", "como fazer"]):
            intencao = random.choice(["D", "E"])
            comercial = "Baixa"
        elif any(m in keyword for m in ["melhor", "recomendado", "avaliacao", "review", "comparar"]):
            intencao = "C"
            comercial = "Média"
        else:
            intencao = random.choice(["B", "C"])
            comercial = random.choice(["Alta", "Média"])
        
        volume = random.randint(50, 5000) if comercial != "Baixa" else random.randint(100, 10000)
        cpc = round(random.uniform(2.0, 45.0), 2) if comercial == "Alta" else round(random.uniform(0.5, 15.0), 2)
        concorrencia = random.choice(concorrencias)
        
        # Prioridade
        if intencao in ["A", "B"] and comercial == "Alta":
            prioridade = "P1"
        elif intencao in ["A", "B"] and comercial == "Média":
            prioridade = "P2"
        elif intencao == "C":
            prioridade = "P2"
        else:
            prioridade = "P3"
        
        keywords.append({
            "keyword": keyword,
            "intencao": intencao,
            "intencao_comercial": comercial,
            "volume_estimado": volume,
            "cpc_estimado": cpc,
            "concorrencia": concorrencia,
            "prioridade": prioridade,
            "grupo_sugerido": kw_base.title().replace(" ", ""),
            "lp_recomendada": f"/{kw_base.replace(' ', '-')}/",
            "concorrentes_que_compram": random.sample(niche_data["competitors"], k=min(3, len(niche_data["competitors"])))
        })
    
    # Remover duplicatas
    seen = set()
    unique = []
    for k in keywords:
        if k["keyword"] not in seen:
            seen.add(k["keyword"])
            unique.append(k)
    
    return unique[:count]


def generate_competitors(niche_data, count=8):
    """Gera dados de concorrentes mockados"""
    competitors = []
    names = niche_data["competitors"][:count]
    
    for i, name in enumerate(names):
        competitors.append({
            "nome": name,
            "anuncios_ativos": random.randint(5, 25),
            "keywords_estimadas": random.randint(30, 200),
            "trafego_pago_mensal_estimado": random.randint(500, 10000),
            "cpc_medio_estimado": round(random.uniform(5.0, 35.0), 2),
            "principais_keywords": random.sample(niche_data["keywords_base"], k=min(5, len(niche_data["keywords_base"]))),
            "ofertas_identificadas": random.sample(niche_data["offers"], k=min(3, len(niche_data["offers"]))),
            "ctas_usados": random.sample(niche_data["ctas"], k=min(2, len(niche_data["ctas"]))),
            "lp_score": random.randint(4, 9),
            "lp_velocidade_mobile": random.randint(40, 95),
            "extensoes_usadas": random.sample(["sitelinks", "callout", "snippet", "imagem", "chamada", "localizacao", "promocao"], k=random.randint(3, 6)),
            "historico_meses": random.randint(6, 24)
        })
    
    return competitors


def generate_gaps(keywords, niche_data):
    """Identifica gaps de oportunidade"""
    gaps = []
    high_intent_low_comp = [k for k in keywords if k["intencao"] in ["A", "B"] and k["concorrencia"] in ["Baixa", "Média"] and k["intencao_comercial"] == "Alta"]
    
    for k in high_intent_low_comp[:15]:
        gaps.append({
            "keyword": k["keyword"],
            "intencao": k["intencao"],
            "intencao_comercial": k["intencao_comercial"],
            "volume_estimado": k["volume_estimado"],
            "cpc_estimado": k["cpc_estimado"],
            "concorrencia": k["concorrencia"],
            "por_que_oportunidade": f"Alta intenção comercial ({k['intencao_comercial']}) com concorrência {k['concorrencia'].lower()}. Concorrentes focam em termos genéricos.",
            "grupo_sugerido": k["grupo_sugerido"],
            "lp_recomendada": k["lp_recomendada"]
        })
    
    return gaps


def generate_oferta_matrix(competitors, niche_data):
    """Gera matriz de ofertas dos concorrentes"""
    all_offers = []
    for c in competitors:
        for o in c["ofertas_identificadas"]:
            all_offers.append({"concorrente": c["nome"], "oferta": o})
    
    # Agrupar ofertas similares
    offer_groups = {}
    for item in all_offers:
        key = item["oferta"][:30]  # Agrupar por início da oferta
        if key not in offer_groups:
            offer_groups[key] = {"oferta_base": item["oferta"], "concorrentes": []}
        offer_groups[key]["concorrentes"].append(item["concorrente"])
    
    matrix = []
    for group in offer_groups.values():
        matrix.append({
            "oferta_comum": group["oferta_base"],
            "concorrentes_que_usam": group["concorrentes"],
            "gap_sua_oferta": f"Diferenciar adicionando: {random.choice(niche_data['offers'])}" if len(group["concorrentes"]) > 2 else "Oportunidade de ser único"
        })
    
    return matrix


def generate_campaign_structure(keywords, niche_data):
    """Gera estrutura sugerida de campanhas/grupos"""
    grupos = {}
    for k in keywords:
        grupo = k["grupo_sugerido"]
        if grupo not in grupos:
            grupos[grupo] = {"keywords": [], "intencao_principal": k["intencao"], "orçamento_sugerido_pct": 0}
        grupos[grupo]["keywords"].append(k["keyword"])
    
    # Distribuir orçamento por prioridade
    total_p1 = sum(1 for k in keywords if k["prioridade"] == "P1")
    total_p2 = sum(1 for k in keywords if k["prioridade"] == "P2")
    total_all = len(keywords)
    
    structure = []
    for grupo, data in grupos.items():
        p1_count = sum(1 for k in keywords if k["grupo_sugerido"] == grupo and k["prioridade"] == "P1")
        p2_count = sum(1 for k in keywords if k["grupo_sugerido"] == grupo and k["prioridade"] == "P2")
        
        if p1_count > 0:
            orcamento_pct = round((p1_count / max(total_p1, 1)) * 60, 1)
        elif p2_count > 0:
            orcamento_pct = round((p2_count / max(total_p2, 1)) * 30, 1)
        else:
            orcamento_pct = round((len(data["keywords"]) / total_all) * 10, 1)
        
        structure.append({
            "campanha": f"{niche_data['keywords_base'][0].title()} - {grupo}",
            "grupo": grupo,
            "keywords_count": len(data["keywords"]),
            "intencao_principal": data["intencao_principal"],
            "orcamento_pct_sugerido": orcamento_pct,
            "keywords_exemplo": data["keywords"][:5]
        })
    
    return structure


def generate_investment_estimate(keywords, geo, verba_base=5000):
    """Gera estimativa de investimento inicial"""
    p1_keywords = [k for k in keywords if k["prioridade"] == "P1"]
    p2_keywords = [k for k in keywords if k["prioridade"] == "P2"]
    
    cpc_medio_p1 = sum(k["cpc_estimado"] for k in p1_keywords) / max(len(p1_keywords), 1)
    cpc_medio_p2 = sum(k["cpc_estimado"] for k in p2_keywords) / max(len(p2_keywords), 1)
    
    # Estimativa: 30 cliques/dia para P1, 20 para P2
    cliques_dia_p1 = min(30, len(p1_keywords) * 2)
    cliques_dia_p2 = min(20, len(p2_keywords) * 1.5)
    
    investimento_dia = (cliques_dia_p1 * cpc_medio_p1) + (cliques_dia_p2 * cpc_medio_p2)
    investimento_mes = round(investimento_dia * 30, 2)
    
    # Ajustar para verba base
    if investimento_mes > verba_base:
        factor = verba_base / investimento_mes
        investimento_mes = verba_base
        cliques_dia_p1 = round(cliques_dia_p1 * factor)
        cliques_dia_p2 = round(cliques_dia_p2 * factor)
    
    return {
        "verba_mensal_recomendada": investimento_mes,
        "verba_diaria_recomendada": round(investimento_mes / 30, 2),
        "cliques_estimados_dia_p1": cliques_dia_p1,
        "cliques_estimados_dia_p2": cliques_dia_p2,
        "cpc_medio_p1": round(cpc_medio_p1, 2),
        "cpc_medio_p2": round(cpc_medio_p2, 2),
        "cpa_estimado_p1": round(cpc_medio_p1 / 0.12, 2),  # assumindo 12% conv rate
        "cpa_estimado_p2": round(cpc_medio_p2 / 0.08, 2),  # assumindo 8% conv rate
        "observacao": f"Baseado em verba de R$ {verba_base}/mês. Ajustar conforme capacidade de atendimento."
    }


def main():
    parser = argparse.ArgumentParser(description='Gera inteligência competitiva mock para Google Ads')
    parser.add_argument('--nicho', required=True, help='Nicho do cliente (ex: advogados trabalhistas)')
    parser.add_argument('--geo', required=True, help='Geografia (ex: São Paulo - SP)')
    parser.add_argument('--concorrentes', help='Lista de concorrentes conhecidos (separados por vírgula)')
    parser.add_argument('--verba-base', type=int, default=5000, help='Verba base mensal para estimativa (default: 5000)')
    parser.add_argument('--output-json', action='store_true', help='Saída como JSON')
    parser.add_argument('--output-file', help='Arquivo para salvar JSON')
    args = parser.parse_args()

    niche_key = detect_niche(args.nicho)
    niche_data = NICHE_DATA[niche_key]
    
    print(f"Gerando inteligência para: {args.nicho} ({niche_key}) em {args.geo}", file=sys.stderr)
    
    # Gerar dados
    keywords = generate_keywords(niche_data, args.geo, count=100)
    competitors = generate_competitors(niche_data, count=8)
    gaps = generate_gaps(keywords, niche_data)
    oferta_matrix = generate_oferta_matrix(competitors, niche_data)
    campaign_structure = generate_campaign_structure(keywords, niche_data)
    investment = generate_investment_estimate(keywords, args.geo, args.verba_base)
    
    result = {
        "metadata": {
            "nicho": args.nicho,
            "geo": args.geo,
            "niche_detectado": niche_key,
            "gerado_em": datetime.now().isoformat(),
            "versao": "1.0-mock",
            "total_keywords": len(keywords),
            "total_concorrentes": len(competitors),
            "total_gaps": len(gaps)
        },
        "concorrentes": competitors,
        "keywords_map": keywords,
        "gaps_oportunidade": gaps,
        "matriz_ofertas": oferta_matrix,
        "estrutura_campanhas_sugerida": campaign_structure,
        "estimativa_investimento": investment
    }
    
    json_str = json.dumps(result, indent=2, ensure_ascii=False)
    
    if args.output_file:
        Path(args.output_file).write_text(json_str, encoding='utf-8')
        print(f"Salvo em: {args.output_file}", file=sys.stderr)
    elif args.output_json:
        print(json_str)
    else:
        # Resumo legível
        print(f"\n=== INTELIGÊNCIA COMPETITIVA MOCK ===")
        print(f"Nicho: {args.nicho} | Geo: {args.geo}")
        print(f"Concorrentes analisados: {len(competitors)}")
        print(f"Keywords mapeadas: {len(keywords)}")
        print(f"Gaps de oportunidade: {len(gaps)}")
        print(f"\nVerba recomendada: R$ {investment['verba_mensal_recomendada']:,.2f}/mês")
        print(f"CPA estimado P1: R$ {investment['cpa_estimado_p1']:,.2f}")
        print(f"CPA estimado P2: R$ {investment['cpa_estimado_p2']:,.2f}")
        print(f"\nTop 5 Gaps:")
        for g in gaps[:5]:
            print(f"  - {g['keyword']} (intenção {g['intencao']}, concorrência {g['concorrencia']})")


if __name__ == "__main__":
    main()