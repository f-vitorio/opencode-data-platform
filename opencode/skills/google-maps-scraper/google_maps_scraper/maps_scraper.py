"""Google Maps Scraper - Core Scraper Module."""
from playwright.sync_api import sync_playwright, Page
from typing import List, Dict, Any, Optional
import time
import random
import re
from urllib.parse import quote_plus

from .rate_limiter import EthicalRateLimiter
from .search_parser import parse_search_results
from .detail_extractor import extract_place_details
from .validators import validate_place_data, enrich_with_domain_info


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
                page.goto(search_url, wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(5000)
                
                # Aceitar cookies se aparecer
                try:
                    cookie_btn = page.locator('button:has-text("Aceitar"), button:has-text("Accept"), button:has-text("Concordar")').first
                    if cookie_btn.count() > 0:
                        cookie_btn.click()
                        page.wait_for_timeout(1000)
                except:
                    pass
                
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
                        merged = enrich_with_domain_info(merged)
                        if validate_place_data(merged, self.must_have_website):
                            validated.append(merged)
                            
                            if len(validated) >= self.max_results:
                                break
                
                self.collected = validated
                return validated
                
            finally:
                browser.close()
    
    def _scroll_results(self, page: Page, max_scrolls: int = 20):
        """Scroll na lista de resultados para carregar mais."""
        # Tentar múltiplos seletores para o painel de resultados
        results_panel = page.locator('[role="feed"]').first
        if results_panel.count() == 0:
            results_panel = page.locator('.m6QErb').first
        if results_panel.count() == 0:
            results_panel = page.locator('.Nv2PK').first
        
        for i in range(max_scrolls):
            # Scroll down
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(2000)
            
            # Verificar se carregou mais - usar o mesmo seletor do parser
            current_count = page.locator('.Nv2PK').count()
            page.wait_for_timeout(1000)
            new_count = page.locator('.Nv2PK').count()
            
            if new_count == current_count:
                # Tentar mais uma vez
                page.wait_for_timeout(2000)
                if page.locator('.Nv2PK').count() == current_count:
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
        
        # Website check is done AFTER detail extraction
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