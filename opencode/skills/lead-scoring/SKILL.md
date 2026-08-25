# LEAD SCORING SKILL

Skill para qualificação e scoring de leads de prospecção. Combina múltiplos sinais (site quality, Google presence, ads gap, market fit) para classificar leads em QUENTE/MORNO/FRIO/DESCARTAR.

---

## ALGORITMO DE SCORING

### Pesos Configuráveis (Default)

```python
DEFAULT_WEIGHTS = {
    "site_quality_inverse": 0.30,      # Site ruim = oportunidade para nós
    "google_presence": 0.25,           # GBP forte = lead qualificado
    "ads_gap": 0.25,                   # Não anuncia = oportunidade
    "market_fit": 0.20,                # Nicho que atendemos bem
}
```

### Fórmula Final

```
FINAL_SCORE = 
    (site_quality_inverse * 0.30) +
    (google_presence * 0.25) +
    (ads_gap * 0.25) +
    (market_fit * 0.20)

Range: 0-100
```

---

## COMPONENTES DETALHADOS

### 1. Site Quality Inverse (0-100) - Peso 30%

**Lógica:** Quanto PIOR o site, MAIOR a oportunidade para nossos serviços.

```python
def calculate_site_quality_inverse(website_audit: Dict) -> int:
    """
    Converte score de qualidade do site (0-100, onde 100=ótimo)
    em score de oportunidade (0-100, onde 100=péssimo site=ótima oportunidade).
    """
    site_score = website_audit.get("overall_score", 50)
    
    # Inverter: site 100 -> oportunidade 0; site 0 -> oportunidade 100
    # Mas com curva: sites medianos (40-60) ainda têm oportunidade moderada
    if site_score >= 80:
        return max(0, 100 - site_score)  # 0-20
    elif site_score >= 60:
        return 40  # Oportunidade moderada
    elif site_score >= 40:
        return 60  # Boa oportunidade
    elif site_score >= 20:
        return 80  # Ótima oportunidade
    else:
        return 95  # Site muito ruim = oportunidade máxima
```

**Sinais que aumentam oportunidade (site ruim):**
- Score SEO < 40
- Score CRO < 40
- Performance CWV ruim (LCP > 4s, CLS > 0.25)
- Mobile issues (touch targets, viewport, font size)
- Sem CTA above-fold
- Sem formulário funcional
- Sem trust signals
- Sem schema/structured data
- Title/H1/meta description ausentes

---

### 2. Google Presence (0-100) - Peso 25%

**Lógica:** Presença forte no Google = negócio real, estabelecido, com budget.

```python
def calculate_google_presence(lead: Dict) -> int:
    score = 0
    
    # Rating GBP (0-30)
    rating = lead.get("rating", 0)
    reviews = lead.get("reviews_count", 0)
    
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
    
    # Horário de funcionamento preenchido (0-10)
    if lead.get("opening_hours"):
        score += 10
    
    # Plus code / localização precisa (0-10)
    if lead.get("plus_code"):
        score += 10
    
    # Website indexado + sitelinks (0-15) - vem do search_validation
    search_val = lead.get("search_validation", {})
    if search_val.get("indexed"):
        score += 5
    if search_val.get("has_sitelinks"):
        score += 10
    
    # Reviews recentes (últimos 3 meses) - bonus
    # (precisaria scrapear reviews individuais)
    
    return min(100, score)
```

---

### 3. Ads Gap (0-100) - Peso 25%

**Lógica:** Não anunciar no Google Ads quando concorrentes anunciam = oportunidade clara.

```python
def calculate_ads_gap(lead: Dict) -> int:
    search_val = lead.get("search_validation", {})
    
    # Lead NÃO anuncia = base 100
    if not search_val.get("running_ads", True):
        base = 100
    else:
        base = 0  # Já anuncia = menor prioridade (já tem provider?)
    
    # Concorrentes anunciam = bonus (valida mercado)
    competitors_ads = search_val.get("competitors_ads_count", 0)
    if competitors_ads >= 5:
        base = min(100, base + 10)
    elif competitors_ads >= 3:
        base = min(100, base + 5)
    elif competitors_ads >= 1:
        base = min(100, base + 2)
    
    # Estimativa de CPC do nicho (valida viabilidade econômica)
    estimated_cpc = search_val.get("estimated_cpc", 0)
    if estimated_cpc > 0:
        if estimated_cpc <= 5:
            base = min(100, base + 5)  # Nicho barato = mais viável
        elif estimated_cpc <= 15:
            base = min(100, base + 3)
        elif estimated_cpc <= 30:
            base = min(100, base + 1)
    
    # Palavras-chave de oportunidade identificadas
    kw_count = len(search_val.get("keywords_opportunity", []))
    if kw_count >= 10:
        base = min(100, base + 5)
    elif kw_count >= 5:
        base = min(100, base + 3)
    
    return base
```

---

### 4. Market Fit (0-100) - Peso 20%

**Lógica:** Nichos que a FVS7 domina = maior probabilidade de fechar e entregar resultado.

```python
# Mapeamento de nicho para fit score
MARKET_FIT_SCORES = {
    # Nichos CORE (atendemos com excelência)
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
    
    "marketing_digital": 70,  # Concorrência direta, mas sabemos vender
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
    
    # Default
    "default": 40,
}


def calculate_market_fit(lead: Dict) -> int:
    """
    Calcula fit baseado nas categorias do Google Places + nome do negócio.
    """
    categories = lead.get("categories", [])
    name = lead.get("name", "").lower()
    
    # Buscar match exato nas categorias normalizadas
    best_score = MARKET_FIT_SCORES["default"]
    
    for cat in categories:
        cat_lower = cat.lower().replace(" ", "_")
        if cat_lower in MARKET_FIT_SCORES:
            best_score = max(best_score, MARKET_FIT_SCORES[cat_lower])
    
    # Buscar no nome do negócio
    for keyword, score in MARKET_FIT_SCORES.items():
        if keyword in name and score > best_score:
            best_score = score
    
    # Bonus: se é nicho core E tem site ruim (oportunidade perfeita)
    site_audit = lead.get("website_audit", {})
    if best_score >= 85 and site_audit.get("overall_score", 100) < 50:
        best_score = min(100, best_score + 5)
    
    return best_score
```

---

## CLASSIFICAÇÃO FINAL

```python
def classify_lead(score: float) -> str:
    """Classifica lead baseado no score final."""
    if score >= 85:
        return "QUENTE"
    elif score >= 70:
        return "MORNO"
    elif score >= 50:
        return "FRIO"
    else:
        return "DESCARTAR"


def get_next_action(classification: str) -> str:
    """Retorna próxima ação recomendada."""
    actions = {
        "QUENTE": "ABORDAGEM_IMEDIATA",      # Ligação/Whatsapp hoje
        "MORNO": "NUTRIÇÃO_SEMANAL",         # LinkedIn + email educativo 1 sem
        "FRIO": "MONITORAMENTO_30_DIAS",     # Reavaliar em 30 dias
        "DESCARTAR": "ARQUIVAR",             # Não investir tempo
    }
    return actions.get(classification, "REVISAR")
```

---

## PITCH PERSONALIZADO (Gerado Automaticamente)

```python
def generate_pitch_data(lead: Dict) -> Dict[str, Any]:
    """
    Gera dados para pitch personalizado baseado nos problemas reais do site.
    """
    audit = lead.get("website_audit", {})
    search = lead.get("search_validation", {})
    scoring = lead.get("scoring", {})
    
    problems = []
    opportunities = []
    
    # Problemas do site
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
    monthly_budget = estimated_cpc * 100  # 100 cliques/mês estimado
    setup_fee = 3000  # LP + configuração Ads
    
    return {
        "headline": f"Seu site perde {estimate_lost_visitors(audit)}% dos visitantes no mobile",
        "problems": problems[:5],  # Top 5
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
    
    return min(80, lost)  # Cap at 80%
```

---

## EXEMPLO DE USO

```python
from lead_scoring import score_lead, classify_lead, generate_pitch_data

# Lead já com dados de auditoria e validação
lead = {
    "name": "Clínica Psicologia Vida",
    "rating": 4.5,
    "reviews_count": 87,
    "categories": ["psychologist", "mental_health_clinic"],
    "website": "https://clinicavida.com.br",
    "website_audit": {
        "overall_score": 35,
        "critical_issues": [
            {"title": "Title tag ausente"},
            {"title": "H1 ausente"},
            {"title": "Viewport meta tag ausente"},
        ],
        "warnings": [
            {"priority": "P1", "title": "Sem JSON-LD structured data"},
            {"priority": "P1", "title": "LCP 5.2s > 2.5s"},
        ],
        "metrics": {"lcp": 5200, "cls": 0.3},
        "cro_data": {"above_fold_ctas": 0, "forms": [{"field_count": 3}]},
        "mobile_data": {"issue_count": 3},
    },
    "search_validation": {
        "running_ads": False,
        "competitors_ads_count": 3,
        "estimated_cpc": 12,
        "keywords_opportunity": ["psicólogo sp", "terapia são paulo", "psicologia clínica"],
    },
}

# Calcular score
scoring = score_lead(lead)
# {
#   "site_quality_inverse": 65,
#   "google_presence": 85,
#   "ads_gap": 100,
#   "market_fit": 95,
#   "final_score": 83.5,
# }

classification = classify_lead(scoring["final_score"])
# "MORNO"

pitch = generate_pitch_data(lead)
# {
#   "headline": "Seu site perde 55% dos visitantes no mobile",
#   "problems": ["Title tag ausente", "H1 ausente", "Viewport meta tag ausente", "LCP 5.2s", "Sem CTA above-fold"],
#   "opportunities": ["Não está anunciando no Google Ads", "3 concorrentes anunciando = mercado validado"],
#   ...
# }
```

---

## INTEGRAÇÃO COM PROSPECTING-AGENT

```python
# No prospecting-runner.py
from lead_scoring import score_lead, classify_lead, get_next_action, generate_pitch_data

for lead in qualified_leads:
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
    
    # 5. Salvar no CRM
    save_to_supabase(lead)
```

---

## ARQUIVO DE CONFIGURAÇÃO (JSON)

```json
{
  "weights": {
    "site_quality_inverse": 0.30,
    "google_presence": 0.25,
    "ads_gap": 0.25,
    "market_fit": 0.20
  },
  "thresholds": {
    "quente": 85,
    "morno": 70,
    "frio": 50
  },
  "market_fit_scores": {
    "psicologia": 95,
    "advocacia": 90,
    "odontologia": 85,
    "contabilidade": 85,
    "fisioterapia": 80,
    "default": 40
  },
  "site_quality_inverse_mapping": {
    "excellent": {"min": 80, "max": 100, "score": 10},
    "good": {"min": 60, "max": 79, "score": 40},
    "average": {"min": 40, "max": 59, "score": 60},
    "poor": {"min": 20, "max": 39, "score": 80},
    "terrible": {"min": 0, "max": 19, "score": 95}
  }
}
```