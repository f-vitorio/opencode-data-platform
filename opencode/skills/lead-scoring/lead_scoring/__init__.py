"""Lead Scoring - Core Scoring Algorithm."""
from typing import Dict, Any, List


# Pesos padrão (configuráveis)
DEFAULT_WEIGHTS = {
    "site_quality_inverse": 0.30,
    "google_presence": 0.25,
    "ads_gap": 0.25,
    "market_fit": 0.20,
}


# Thresholds de classificação
CLASSIFICATION_THRESHOLDS = {
    "quente": 85,
    "morno": 70,
    "frio": 50,
}


# Market Fit Scores - Nichos que a FVS7 domina
MARKET_FIT_SCORES = {
    # Nichos CORE
    "psicologia": 95,
    "psicólogo": 95,
    "terapia": 90,
    "clínica_psicologia": 95,
    "saúde_mental": 90,
    
    "advocacia": 90,
    "advogado": 90,
    "escritório_advocacia": 90,
    "direito_trabalhista": 85,
    "direito_civil": 85,
    
    "odontologia": 85,
    "dentista": 85,
    "clínica_odontológica": 85,
    "implante_dentário": 90,
    "ortodontia": 85,
    
    "fisioterapia": 80,
    "fisioterapeuta": 80,
    "clínica_fisioterapia": 80,
    
    "nutrição": 75,
    "nutricionista": 75,
    
    "contabilidade": 85,
    "contador": 85,
    "escritório_contabilidade": 85,
    "abertura_empresa": 80,
    
    "imobiliária": 80,
    "corretor_imóveis": 75,
    
    "marketing_digital": 70,
    "agência_marketing": 60,
    
    # Nichos SECUNDÁRIOS
    "médico": 70,
    "clínica_médica": 75,
    "dermatologia": 80,
    "ortopedia": 75,
    "cardiologia": 75,
    "pediatria": 70,
    "ginecologia": 75,
    
    "veterinária": 70,
    "pet_shop": 65,
    
    "escola": 60,
    "curso": 60,
    "educação": 55,
    
    "restaurante": 50,
    "delivery": 45,
    "varejo": 40,
    "ecommerce": 55,
    
    "default": 40,
}


# Site Quality Inverse Mapping
SITE_QUALITY_INVERSE = {
    "excellent": {"min": 80, "max": 100, "score": 10},
    "good": {"min": 60, "max": 79, "score": 40},
    "average": {"min": 40, "max": 59, "score": 60},
    "poor": {"min": 20, "max": 39, "score": 80},
    "terrible": {"min": 0, "max": 19, "score": 95},
}


def calculate_site_quality_inverse(website_audit: Dict) -> int:
    """
    Converte score de qualidade do site (0-100) em score de oportunidade.
    Site ruim = alta oportunidade para nossos serviços.
    """
    site_score = website_audit.get("overall_score") or 50
    
    if site_score >= 80:
        return max(0, 100 - site_score)
    elif site_score >= 60:
        return 40
    elif site_score >= 40:
        return 60
    elif site_score >= 20:
        return 80
    else:
        return 95


def calculate_google_presence(lead: Dict) -> int:
    """
    Calcula presença no Google baseada em GBP, reviews, fotos, sitelinks, horários, plus_code, categorias.
    """
    score = 0
    
    # Rating GBP + Reviews (0-30)
    rating = lead.get("rating") or 0
    reviews = lead.get("reviews_count") or 0
    
    if rating >= 4.5 and reviews >= 50:
        score += 30
    elif rating >= 4.0 and reviews >= 20:
        score += 25
    elif rating >= 4.0 and reviews >= 10:
        score += 20
    elif rating >= 3.5 and reviews >= 10:
        score += 15
    elif rating >= 3.0:
        score += 10
    
    # Fotos no GBP (0-15)
    photos = lead.get("photos_count", 0)
    if photos >= 20:
        score += 15
    elif photos >= 10:
        score += 10
    elif photos >= 5:
        score += 5
    
    # Horário de funcionamento (0-15) - AUMENTADO
    if lead.get("opening_hours"):
        score += 15
    
    # Plus code (0-10)
    if lead.get("plus_code"):
        score += 10
    
    # Categorias definidas (0-10) - NOVO
    if lead.get("categories") and len(lead["categories"]) > 0:
        score += 10
    
    # Search validation: indexado + sitelinks (0-15)
    search_val = lead.get("search_validation", {})
    if search_val.get("indexed"):
        score += 5
    if search_val.get("has_sitelinks"):
        score += 10
    
    # Website presente (0-5) - NOVO
    if lead.get("website"):
        score += 5
    
    # Telefone presente (0-5) - NOVO
    if lead.get("phone"):
        score += 5
    
    return min(100, score)


def calculate_ads_gap(lead: Dict) -> int:
    """
    Calcula gap de anúncios: não anunciar quando concorrentes anunciam = oportunidade.
    """
    search_val = lead.get("search_validation", {})
    
    # Lead NÃO anuncia = base 100
    if not search_val.get("running_ads", True):
        base = 100
    else:
        base = 0  # Já anuncia
    
    # Concorrentes anunciam = bonus
    competitors_ads = search_val.get("competitors_ads_count", 0)
    if competitors_ads >= 5:
        base = min(100, base + 10)
    elif competitors_ads >= 3:
        base = min(100, base + 5)
    elif competitors_ads >= 1:
        base = min(100, base + 2)
    
    # Estimativa de CPC (valida viabilidade)
    estimated_cpc = search_val.get("estimated_cpc", 0)
    if estimated_cpc > 0:
        if estimated_cpc <= 5:
            base = min(100, base + 5)
        elif estimated_cpc <= 15:
            base = min(100, base + 3)
        elif estimated_cpc <= 30:
            base = min(100, base + 1)
    
    # Palavras-chave de oportunidade
    kw_count = len(search_val.get("keywords_opportunity", []))
    if kw_count >= 10:
        base = min(100, base + 5)
    elif kw_count >= 5:
        base = min(100, base + 3)
    
    return base


def calculate_market_fit(lead: Dict) -> int:
    """
    Calcula fit de mercado baseado nas categorias + nome do negócio.
    """
    categories = lead.get("categories", [])
    name = lead.get("name", "").lower()
    
    best_score = MARKET_FIT_SCORES["default"]
    
    # Match nas categorias
    for cat in categories:
        cat_lower = cat.lower().replace(" ", "_")
        if cat_lower in MARKET_FIT_SCORES:
            best_score = max(best_score, MARKET_FIT_SCORES[cat_lower])
    
    # Match no nome
    for keyword, score in MARKET_FIT_SCORES.items():
        if keyword in name and score > best_score:
            best_score = score
    
    # Bonus: nicho core + site ruim = oportunidade perfeita
    site_audit = lead.get("website_audit", {})
    if best_score >= 85 and site_audit.get("overall_score", 100) < 50:
        best_score = min(100, best_score + 5)
    
    return best_score


def score_lead(lead: Dict, weights: Dict = None) -> Dict[str, Any]:
    """
    Calcula score final do lead combinando todos os componentes.
    
    Returns:
        Dict com scores individuais + final_score
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Calcular cada componente
    site_quality_inv = calculate_site_quality_inverse(lead.get("website_audit", {}))
    google_pres = calculate_google_presence(lead)
    ads_gap = calculate_ads_gap(lead)
    market_fit = calculate_market_fit(lead)
    
    # Score final ponderado
    final_score = (
        site_quality_inv * weights["site_quality_inverse"] +
        google_pres * weights["google_presence"] +
        ads_gap * weights["ads_gap"] +
        market_fit * weights["market_fit"]
    )
    
    return {
        "site_quality_inverse": round(site_quality_inv, 1),
        "google_presence": round(google_pres, 1),
        "ads_gap": round(ads_gap, 1),
        "market_fit": round(market_fit, 1),
        "final_score": round(final_score, 1),
        "weights_used": weights,
    }


def classify_lead(score: float, thresholds: Dict = None) -> str:
    """Classifica lead baseado no score final."""
    if thresholds is None:
        thresholds = CLASSIFICATION_THRESHOLDS
    
    if score >= thresholds["quente"]:
        return "QUENTE"
    elif score >= thresholds["morno"]:
        return "MORNO"
    elif score >= thresholds["frio"]:
        return "FRIO"
    else:
        return "DESCARTAR"


def get_next_action(classification: str) -> str:
    """Retorna próxima ação recomendada."""
    actions = {
        "QUENTE": "ABORDAGEM_IMEDIATA",
        "MORNO": "NUTRIÇÃO_SEMANAL",
        "FRIO": "MONITORAMENTO_30_DIAS",
        "DESCARTAR": "ARQUIVAR",
    }
    return actions.get(classification, "REVISAR")


def estimate_lost_visitors(audit: Dict) -> int:
    """Estima % de visitantes perdidos por problemas de performance/UX."""
    lost = 0
    perf = audit.get("metrics", {})
    
    # LCP impact
    lcp = perf.get("lcp", 0)
    if lcp > 4000:
        lost += 40
    elif lcp > 2500:
        lost += 25
    
    # Mobile issues
    mobile_issues = audit.get("mobile_data", {}).get("issue_count", 0)
    lost += min(20, mobile_issues * 5)
    
    # CTA above fold
    cro = audit.get("cro_data", {})
    if cro.get("above_fold_ctas", 0) == 0:
        lost += 15
    
    # Form issues
    forms = cro.get("forms", [])
    for f in forms:
        if f.get("field_count", 0) > 5:
            lost += 10
    
    return min(80, lost)


def generate_pitch_data(lead: Dict) -> Dict[str, Any]:
    """
    Gera dados para pitch personalizado baseado nos problemas reais.
    """
    audit = lead.get("website_audit", {})
    search = lead.get("search_validation", {})
    scoring = lead.get("scoring", {})
    
    problems = []
    opportunities = []
    
    # Problemas do site (críticos + P0/P1 warnings)
    for issue in audit.get("critical_issues", []):
        problems.append(issue["title"])
    for warning in audit.get("warnings", []):
        if warning.get("priority") in ["P0", "P1"]:
            problems.append(warning["title"])
    
    # Oportunidades de mercado
    if not search.get("running_ads"):
        opportunities.append("Não está anunciando no Google Ads")
        kw_count = len(search.get("keywords_opportunity", []))
        if kw_count > 0:
            opportunities.append(f"{kw_count} palavras-chave de oportunidade identificadas")
    
    competitors = search.get("competitors_ads_count", 0)
    if competitors > 0:
        opportunities.append(f"{competitors} concorrentes anunciando = mercado validado")
    
    # Estimativa de investimento
    estimated_cpc = search.get("estimated_cpc", 15)
    monthly_budget = estimated_cpc * 100
    setup_fee = 3000
    
    return {
        "headline": f"Seu site perde {estimate_lost_visitors(audit)}% dos visitantes no mobile",
        "problems": problems[:5],
        "opportunities": opportunities[:3],
        "market_data": {
            "monthly_searches": search.get("monthly_searches", "N/A"),
            "estimated_cpc": f"R$ {estimated_cpc:.0f}-{estimated_cpc*2:.0f}",
            "competitors_ads": competitors,
        },
        "proposed_solution": "Landing Page otimizada para conversão + Google Ads geo-localizado",
        "estimated_investment": f"R$ {setup_fee:,} setup + R$ {monthly_budget:,}/mês mídia",
        "estimated_roi": "3-5x no primeiro trimestre (baseado em benchmarks do nicho)",
        "cta": "Vamos conversar? 15 min para mostrar o diagnóstico completo do seu site",
    }


def enrich_lead_with_scoring(lead: Dict) -> Dict:
    """
    Função completa: scoreia, classifica, define ação e gera pitch.
    """
    # 1. Score
    scoring = score_lead(lead)
    lead["scoring"] = scoring
    
    # 2. Classificar
    classification = classify_lead(scoring["final_score"])
    lead["classification"] = classification
    
    # 3. Próxima ação
    lead["next_action"] = get_next_action(classification)
    
    # 4. Pitch personalizado
    lead["pitch_data"] = generate_pitch_data(lead)
    
    return lead