# GOOGLE MAPS SCRAPER SKILL

Skill para scraping estruturado do Google Maps via Playwright. Extrai dados de empresas locais com rate limiting, user-agent rotation e validação de dados.

---

## ARQUITETURA

```
google-maps-scraper/
├── __init__.py
├── maps_scraper.py       # Core scraper
├── search_parser.py      # Parser de resultados
├── detail_extractor.py   # Extractor de página de detalhes
├── validators.py         # Validadores de dados
└── rate_limiter.py       # Rate limiting ético
```

---

## CORE SCRAPER

```python
# maps_scraper.py
from playwright.sync_api import sync_playwright, Page
from typing import List, Dict, Any, Optional
import time
import random
import re
from urllib.parse import quote_plus, urlparse
import json

from .rate_limiter import EthicalRateLimiter
from .search_parser import parse_search_results
from .detail_extractor import extract_place_details
from .validators import validate_place_data


class GoogleMapsScraper:
    """
    Scraper ético do Google Maps para prospecção B2B.
    
    Features:
    - Rate limiting configurável (3-8s entre requests)
    - User-agent rotation
    - Extração estruturada: nome, endereço, telefone, site, rating, reviews, categoria
    - Filtros: rating mínimo, reviews mínimos, tem site, categorias
    - Paginação automática
    - Validação de dados
    """
    
    def __init__(
        self,
        min_rating: float = 4.0,
        min_reviews: int = 10,
        must_have_website: bool = True,
        target_categories: List[str] = None,
        max_results: int = 200,
        delay_min: float = 3.0,
        delay_max: float = 8.0,
        headed: bool = False,
    ):
        self.min_rating = min_rating
        self.min_reviews = min_reviews
        self.must_have_website = must_have_website
        self.target_categories = target_categories or []
        self.max_results = max_results
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.headed = headed
        
        self.rate_limiter = EthicalRateLimiter(delay_min, delay_max)
        self.collected = []
        self.seen_place_ids = set()
    
    def search(self, query: str, location: str = "") -> List[Dict[str, Any]]:
        """
        Busca principal no Google Maps.
        
        Args:
            query: Termo de busca (ex: "clínica psicologia")
            location: Localização (ex: "São Paulo, SP")
        
        Returns:
            Lista de leads brutos validados
        """
        full_query = f"{query} {location}".strip()
        search_url = f"https://www.google.com/maps/search/{quote_plus(full_query)}"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=not self.headed,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent=self._get_random_ua(),
                viewport={"width": 1280, "height": 720},
                locale="pt-BR",
            )
            page = context.new_page()
            
            try:
                # Navegar para busca
                page.goto(search_url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                
                # Verificar se há resultados
                if page.locator('text="No results"').count() > 0:
                    return []
                
                # Scroll para carregar mais resultados
                self._scroll_results(page)
                
                # Parse resultados
                raw_results = parse_search_results(page)
                
                # Filtrar e validar
                validated = []
                for place in raw_results:
                    if self._passes_filters(place):
                        # Extrair detalhes completos
                        details = extract_place_details(page, place)
                        merged = {**place, **details}
                        if validate_place_data(merged, self.must_have_website):
                            validated.append(merged)
                            
                            if len(validated) >= self.max_results:
                                break
                
                self.collected = validated
                return validated
                
            finally:
                browser.close()
    
    def _scroll_results(self, page: Page, max_scrolls: int = 10):
        """Scroll na lista de resultados para carregar mais."""
        results_panel = page.locator('[role="feed"]').first
        if results_panel.count() == 0:
            results_panel = page.locator('.m6QErb').first
        
        for i in range(max_scrolls):
            # Scroll down
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1500)
            
            # Verificar se carregou mais
            current_count = page.locator('[data-result-index]').count()
            page.wait_for_timeout(500)
            new_count = page.locator('[data-result-index]').count()
            
            if new_count == current_count:
                # Tentar mais uma vez
                page.wait_for_timeout(1000)
                if page.locator('[data-result-index]').count() == current_count:
                    break
    
    def _passes_filters(self, place: Dict[str, Any]) -> bool:
        """Aplica filtros de qualificação."""
        # Rating
        rating = place.get("rating", 0)
        if rating and rating < self.min_rating:
            return False
        
        # Reviews
        reviews = place.get("reviews_count", 0)
        if reviews < self.min_reviews:
            return False
        
        # Website
        if self.must_have_website and not place.get("website"):
            return False
        
        # Categorias alvo
        if self.target_categories:
            place_cats = place.get("categories", [])
            if not any(cat in place_cats for cat in self.target_categories):
                # Verificar também no nome/descrição
                name = place.get("name", "").lower()
                if not any(cat.lower() in name for cat in self.target_categories):
                    return False
        
        # Duplicados
        place_id = place.get("place_id")
        if place_id and place_id in self.seen_place_ids:
            return False
        if place_id:
            self.seen_place_ids.add(place_id)
        
        return True
    
    def _get_random_ua(self) -> str:
        """Retorna user-agent aleatório realístico."""
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(uas)


def search_places(
    query: str,
    location: str = "",
    min_rating: float = 4.0,
    min_reviews: int = 10,
    must_have_website: bool = True,
    target_categories: List[str] = None,
    max_results: int = 200,
    headed: bool = False,
) -> List[Dict[str, Any]]:
    """Função de conveniência para busca única."""
    scraper = GoogleMapsScraper(
        min_rating=min_rating,
        min_reviews=min_reviews,
        must_have_website=must_have_website,
        target_categories=target_categories,
        max_results=max_results,
        headed=headed,
    )
    return scraper.search(query, location)
```

---

## SEARCH PARSER

```python
# search_parser.py
from playwright.sync_api import Page, Locator
from typing import List, Dict, Any
import re


def parse_search_results(page: Page) -> List[Dict[str, Any]]:
    """
    Extrai dados da lista de resultados do Google Maps.
    """
    results = []
    
    # Seletores dos cards de resultado
    cards = page.locator('[data-result-index]').all()
    
    for i, card in enumerate(cards):
        try:
            data = _extract_card_data(card, i)
            if data and data.get("name"):
                results.append(data)
        except Exception:
            continue
    
    return results


def _extract_card_data(card: Locator, index: int) -> Dict[str, Any]:
    """Extrai dados de um card individual."""
    data = {
        "result_index": index,
        "place_id": None,
        "name": None,
        "address": None,
        "phone": None,
        "website": None,
        "rating": None,
        "reviews_count": 0,
        "categories": [],
        "price_level": None,
        "latitude": None,
        "longitude": None,
    }
    
    try:
        # Place ID (no link do nome)
        name_link = card.locator('a[href*="/maps/place/"]').first
        if name_link.count() > 0:
            href = name_link.get_attribute("href")
            data["place_id"] = _extract_place_id_from_url(href)
            data["name"] = name_link.inner_text().strip()
        
        # Rating e reviews
        rating_elem = card.locator('[role="img"][aria-label*="star"]').first
        if rating_elem.count() > 0:
            aria = rating_elem.get_attribute("aria-label")
            rating_match = re.search(r"(\d+\.?\d*)", aria)
            if rating_match:
                data["rating"] = float(rating_match.group(1))
            
            # Reviews count
            reviews_elem = card.locator('text=/\(\d+\)/').first
            if reviews_elem.count() > 0:
                reviews_text = reviews_elem.inner_text()
                reviews_match = re.search(r"\((\d+)\)", reviews_text)
                if reviews_match:
                    data["reviews_count"] = int(reviews_match.group(1))
        
        # Endereço
        address_elem = card.locator('[data-item-id="address"]').first
        if address_elem.count() == 0:
            # Fallback: primeiro texto que parece endereço
            texts = card.locator('.fontBodyMedium').all()
            for t in texts:
                text = t.inner_text().strip()
                if any(kw in text.lower() for kw in ["rua", "av.", "avenida", "praça", "alameda", "rodovia", "br-", "sp-", "r.", "av "]):
                    data["address"] = text
                    break
        else:
            data["address"] = address_elem.inner_text().strip()
        
        # Telefone
        phone_elem = card.locator('[data-item-id*="phone"]').first
        if phone_elem.count() == 0:
            phone_elem = card.locator('text=/\(\d{2}\)\s*\d{4,5}-?\d{4}/').first
        if phone_elem.count() > 0:
            data["phone"] = phone_elem.inner_text().strip()
        
        # Website
        website_elem = card.locator('[data-item-id="authority"]').first
        if website_elem.count() > 0:
            href = website_elem.get_attribute("href")
            if href and href.startswith("http"):
                data["website"] = href
        
        # Categorias (aria-label do pin)
        category_elem = card.locator('[jsaction*="category"]').first
        if category_elem.count() > 0:
            cat_text = category_elem.get_attribute("aria-label") or category_elem.inner_text()
            data["categories"] = [c.strip() for c in cat_text.split("·") if c.strip()]
        
        # Price level (sinais de $)
        price_elem = card.locator('text=/\$+/').first
        if price_elem.count() > 0:
            data["price_level"] = len(price_elem.inner_text().strip())
        
    except Exception:
        pass
    
    return data


def _extract_place_id_from_url(url: str) -> Optional[str]:
    """Extrai place_id da URL do Google Maps."""
    # Formato: https://www.google.com/maps/place/Nome/@lat,lng,17z/data=!3m1!4b1!4m6!3m5!1s0x...!8m2!3d...!4d...!16s%2Fg%2F...
    # Place ID está em /g/ ou no data
    import re
    
    # Tentar /g/
    match = re.search(r'/g/([^/?#]+)', url)
    if match:
        return match.group(1)
    
    # Tentar data=!1s
    match = re.search(r'!1s([^!]+)', url)
    if match:
        return match.group(1)
    
    return None
```

---

## DETAIL EXTRACTOR

```python
# detail_extractor.py
from playwright.sync_api import Page
from typing import Dict, Any, Optional
import re


def extract_place_details(page: Page, place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Abre página de detalhes do lugar e extrai dados completos.
    """
    details = {
        "website": place.get("website"),
        "phone": place.get("phone"),
        "address": place.get("address"),
        "opening_hours": None,
        "photos_count": 0,
        "plus_code": None,
        "description": None,
        "reviews_snippets": [],
        "popular_times": None,
    }
    
    place_id = place.get("place_id")
    if not place_id:
        return details
    
    # URL de detalhes
    detail_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    
    try:
        # Abrir em nova aba para não perder lista
        with page.context.expect_page() as new_page_info:
            page.locator(f'a[href*="{place_id}"]').first.click()
        detail_page = new_page_info.value
        detail_page.wait_for_load_state("networkidle", timeout=30000)
        detail_page.wait_for_timeout(2000)
        
        # Extrair dados da página de detalhes
        details = _extract_detail_page_data(detail_page, details)
        
        detail_page.close()
        
    except Exception:
        pass
    
    return details


def _extract_detail_page_data(page: Page, details: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai dados da página de detalhes aberta."""
    
    # Website (botão "Site")
    website_btn = page.locator('[data-item-id="authority"], a[aria-label*="Site"]').first
    if website_btn.count() > 0:
        href = website_btn.get_attribute("href")
        if href and href.startswith("http"):
            details["website"] = href
    
    # Telefone
    phone_btn = page.locator('[data-item-id*="phone"], button[aria-label*="Telefone"]').first
    if phone_btn.count() > 0:
        details["phone"] = phone_btn.inner_text().strip()
    
    # Endereço completo
    address_btn = page.locator('[data-item-id="address"], button[aria-label*="Endereço"]').first
    if address_btn.count() > 0:
        details["address"] = address_btn.inner_text().strip()
    
    # Horário de funcionamento
    hours_btn = page.locator('[data-item-id="oh"], button[aria-label*="Horário"]').first
    if hours_btn.count() > 0:
        # Clicar para expandir se necessário
        try:
            hours_btn.click()
            page.wait_for_timeout(500)
        except:
            pass
        hours_container = page.locator('[role="region"][aria-label*="Horário"], .y0skZc').first
        if hours_container.count() > 0:
            details["opening_hours"] = hours_container.inner_text().strip()
    
    # Plus Code
    plus_code_elem = page.locator('[data-item-id="plus_code"], text=/[A-Z]{2,}\+[A-Z0-9]{2,}/').first
    if plus_code_elem.count() > 0:
        details["plus_code"] = plus_code_elem.inner_text().strip()
    
    # Fotos count
    photos_tab = page.locator('[role="tab"]:has-text("Fotos")').first
    if photos_tab.count() > 0:
        try:
            photos_tab.click()
            page.wait_for_timeout(1000)
            photo_count = page.locator('text=/(\d+)\s*fotos?/i').first
            if photo_count.count() > 0:
                match = re.search(r'(\d+)', photo_count.inner_text())
                if match:
                    details["photos_count"] = int(match.group(1))
        except:
            pass
    
    # Snippets de reviews
    review_cards = page.locator('[data-review-id], .jftiEf').all()
    for card in review_cards[:5]:  # Top 5
        try:
            text = card.locator('.wiI7pd, .MyEned').first.inner_text().strip()
            rating = card.locator('[role="img"][aria-label*="star"]').first.get_attribute("aria-label")
            author = card.locator('.d4r55, .TSUbDb').first.inner_text().strip()
            if text:
                details["reviews_snippets"].append({
                    "author": author,
                    "rating": rating,
                    "text": text[:300]
                })
        except:
            pass
    
    return details
```

---

## VALIDATORS

```python
# validators.py
from typing import Dict, Any, List
import re
from urllib.parse import urlparse


def validate_place_data(place: Dict[str, Any], must_have_website: bool = True) -> bool:
    """
    Valida se o lead tem dados mínimos para prospecção.
    """
    # Nome obrigatório
    if not place.get("name") or len(place["name"].strip()) < 2:
        return False
    
    # Endereço ou localização
    if not place.get("address") and not (place.get("latitude") and place.get("longitude")):
        return False
    
    # Website se obrigatório
    if must_have_website:
        website = place.get("website")
        if not website or not _is_valid_url(website):
            return False
        
        # Filtrar domínios que não são sites de negócio
        if _is_non_business_domain(website):
            return False
    
    # Rating mínimo (se disponível)
    rating = place.get("rating")
    if rating is not None and rating < 3.0:
        return False
    
    return True


def _is_valid_url(url: str) -> bool:
    """Valida se URL é bem formada."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False


def _is_non_business_domain(url: str) -> bool:
    """Filtra domínios que não são sites de negócio próprios."""
    non_business = [
        "facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com",
        "youtube.com", "tiktok.com", "pinterest.com",
        "google.com", "maps.google.com", "goo.gl",
        "waze.com", "yelp.com", "tripadvisor.com", "foursquare.com",
        "wikipedia.org", "wikidata.org",
        "blogspot.com", "wordpress.com", "medium.com",
        "linktr.ee", "bio.link", "linkin.bio",
    ]
    
    domain = urlparse(url).netloc.lower().replace("www.", "")
    return any(nb in domain for nb in non_business)


def enrich_with_domain_info(place: Dict[str, Any]) -> Dict[str, Any]:
    """Adiciona info do domínio (TLD, subdomínio, etc)."""
    website = place.get("website")
    if website:
        parsed = urlparse(website)
        place["domain"] = parsed.netloc.lower().replace("www.", "")
        place["tld"] = "." + place["domain"].split(".")[-1] if "." in place["domain"] else ""
        place["is_br_domain"] = place["tld"] == ".br" or place["domain"].endswith(".com.br")
    return place
```

---

## RATE LIMITER

```python
# rate_limiter.py
import time
import random
from typing import Optional


class EthicalRateLimiter:
    """
    Rate limiter ético para scraping.
    
    Princípios:
    - Delay aleatório entre requests (configurável)
    - Respeita headers de retry se servidor indicar
    - Backoff exponencial em erros 429/5xx
    - Log de todos requests para auditoria
    """
    
    def __init__(
        self,
        delay_min: float = 3.0,
        delay_max: float = 8.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.last_request_time = 0
        self.request_count = 0
        self.error_count = 0
    
    def wait(self):
        """Aguarda tempo necessário antes do próximo request."""
        elapsed = time.time() - self.last_request_time
        min_wait = self.delay_min + random.uniform(0, self.delay_max - self.delay_min)
        
        if elapsed < min_wait:
            sleep_time = min_wait - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def handle_response(self, status_code: int) -> bool:
        """
        Processa resposta HTTP.
        Returns: True se deve retry, False caso contrário.
        """
        if status_code == 429:
            self.error_count += 1
            wait_time = self.backoff_factor ** self.error_count * 5
            time.sleep(wait_time)
            return True
        
        if 500 <= status_code < 600:
            self.error_count += 1
            if self.error_count <= self.max_retries:
                wait_time = self.backoff_factor ** self.error_count * 2
                time.sleep(wait_time)
                return True
        
        # Sucesso ou erro não-retryable
        self.error_count = 0
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "requests_made": self.request_count,
            "errors": self.error_count,
            "avg_delay": (self.delay_min + self.delay_max) / 2,
        }
```

---

## EXEMPLO DE USO COMPLETO

```python
# Uso direto
from google_maps_scraper import search_places

leads = search_places(
    query="clínica psicologia",
    location="São Paulo, SP",
    min_rating=4.0,
    min_reviews=10,
    must_have_website=True,
    target_categories=["psychologist", "clinic", "mental_health"],
    max_results=100,
    headed=False,
)

print(f"Encontrados: {len(leads)} leads qualificados")

for lead in leads[:5]:
    print(f"- {lead['name']} | {lead['rating']}★ ({lead['reviews_count']}) | {lead['website']}")
```

---

## INTEGRAÇÃO COM PROSPECTING-AGENT

O `prospecting-agent` usa esta skill assim:

```python
# No prospecting-runner.py
from google_maps_scraper import search_places
from website_audit_runner import WebsiteAuditRunner
from lead_scoring import score_lead

# 1. Buscar leads brutos
raw_leads = search_places(
    query=nicho,
    location=cidade,
    min_rating=4.0,
    min_reviews=10,
    must_have_website=True,
    target_categories=categorias_alvo,
    max_results=200,
)

# 2. Para cada lead, validar no Google Search
for lead in raw_leads:
    lead["search_validation"] = validate_via_google_search(lead)

# 3. Filtrar: não anuncia no Ads
leads_with_gap = [l for l in raw_leads if not l["search_validation"].get("running_ads")]

# 4. Auditar sites (amostragem ou todos)
for lead in leads_with_gap[:50]:
    audit = WebsiteAuditRunner(lead["website"], mode="COMPLETA").run()
    lead["website_audit"] = audit

# 5. Scoring final
for lead in leads_with_gap:
    lead["scoring"] = score_lead(lead)
    lead["classification"] = classify_lead(lead["scoring"]["final_score"])

# 6. Salvar no CRM
save_to_supabase(leads_with_gap)
```

---

## DADOS EXTRAÍDOS (Schema Final)

```json
{
  "source": "google_maps",
  "place_id": "ChIJ...",
  "name": "Clínica Psicologia Vida",
  "address": "R. Augusta, 123 - Consolação, São Paulo - SP, 01305-000",
  "phone": "(11) 3333-4444",
  "website": "https://clinicavida.com.br",
  "domain": "clinicavida.com.br",
  "tld": ".br",
  "is_br_domain": true,
  "rating": 4.5,
  "reviews_count": 87,
  "categories": ["psychologist", "mental_health_clinic", "health"],
  "price_level": 2,
  "latitude": -23.5612,
  "longitude": -46.6565,
  "opening_hours": "Seg-Sex 8h-20h; Sáb 8h-14h; Dom Fechado",
  "photos_count": 12,
  "plus_code": "58WC+3J São Paulo",
  "reviews_snippets": [
    {"author": "Maria S.", "rating": "5 stars", "text": "Excelente atendimento..."},
    {"author": "João P.", "rating": "4 stars", "text": "Profissionais muito atenciosos..."}
  ],
  "collected_at": "2026-08-24T10:30:00Z"
}
```