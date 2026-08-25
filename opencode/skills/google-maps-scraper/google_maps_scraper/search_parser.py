"""Google Maps Scraper - Parser de Resultados de Busca."""
from playwright.sync_api import Page, Locator
from typing import List, Dict, Any, Optional
import re


def parse_search_results(page: Page) -> List[Dict[str, Any]]:
    """
    Extrai dados da lista de resultados do Google Maps.
    """
    results = []
    
    # Tentar múltiplos seletores para cards de resultado (Google Maps muda frequentemente)
    card_selectors = [
        '[data-result-index]',           # Seletor clássico
        '.Nv2PK',                        # Seletor atual comum
        '.hfpxzc',                       # Link do lugar
        '[jsaction*="pane.rating"]',     # Cards com rating
        '.bfdHYd',                       # Container de resultado
        'article',                       # Genérico
    ]
    
    cards = []
    for selector in card_selectors:
        found = page.locator(selector).all()
        if found:
            print(f"[DEBUG] Encontrados {len(found)} cards com seletor: {selector}")
            cards = found
            break
    
    if not cards:
        print("[DEBUG] Nenhum card encontrado com seletores conhecidos")
        # Debug: listar todos elementos visíveis
        all_elements = page.locator('*').all()
        print(f"[DEBUG] Total elementos na página: {len(all_elements)}")
        return []
    
    for i, card in enumerate(cards):
        try:
            data = _extract_card_data(card, i)
            if data and data.get("name"):
                results.append(data)
        except Exception as e:
            print(f"[DEBUG] Erro ao extrair card {i}: {e}")
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
        # Place ID (no link do nome) - tentar múltiplos seletores
        name_link = None
        for selector in [
            'a[href*="/maps/place/"]',
            'a.hfpxzc',
            '.hfpxzc',
            'a[jsaction*="place"]',
        ]:
            name_link = card.locator(selector).first
            if name_link.count() > 0:
                break
        
        if name_link and name_link.count() > 0:
            href = name_link.get_attribute("href")
            data["place_id"] = _extract_place_id_from_url(href)
            # Nome pode estar no aria-label ou no texto
            name = name_link.get_attribute("aria-label") or name_link.inner_text().strip()
            data["name"] = name
        
        # Rating e reviews
        for selector in ['[role="img"][aria-label*="star"]', '.MW4etd', '[aria-label*="estrela"]']:
            rating_elem = card.locator(selector).first
            if rating_elem.count() > 0:
                aria = rating_elem.get_attribute("aria-label") or rating_elem.inner_text()
                rating_match = re.search(r"(\d+\.?\d*)", aria)
                if rating_match:
                    data["rating"] = float(rating_match.group(1))
                break
        
        # Reviews count - mais específico para evitar pegar telefones
        for selector in ['[aria-label*="avaliação"]', '[aria-label*="review"]', '[aria-label*="avaliações"]', '[aria-label*="reviews"]', '.UY7F9']:
            reviews_elem = card.locator(selector).first
            if reviews_elem.count() > 0:
                aria = reviews_elem.get_attribute("aria-label") or ""
                text = reviews_elem.inner_text()
                # Procurar padrões como "123 avaliações", "123 reviews", "(123)"
                reviews_match = re.search(r"(\d[\d.,]*)\s*(avaliações?|reviews?|avaliações?)", text, re.IGNORECASE)
                if not reviews_match:
                    reviews_match = re.search(r"\((\d[\d.,]*)\)", text)
                if reviews_match:
                    count_str = reviews_match.group(1).replace(".", "").replace(",", "")
                    data["reviews_count"] = int(count_str)
                    break
        
        # Fallback: buscar em todo o texto do card
        if data["reviews_count"] == 0:
            try:
                card_text = card.inner_text()
                # Padrões: "4.5 (123)", "4,5 (123 avaliações)", "123 avaliações"
                match = re.search(r"[\(（]\s*(\d[\d.,]*)\s*(?:avaliações?|reviews?|avaliações?)\s*[\)）]", card_text, re.IGNORECASE)
                if not match:
                    match = re.search(r"(\d[\d.,]*)\s*(?:avaliações?|reviews?)\s*[\(\)]", card_text, re.IGNORECASE)
                if match:
                    count_str = match.group(1).replace(".", "").replace(",", "")
                    data["reviews_count"] = int(count_str)
            except:
                pass
        
        # Endereço - evitar pegar rating como endereço
        address_selectors = [
            '[data-item-id="address"]',
            'button[data-item-id="address"]',
            '[aria-label*="Endereço"]',
            '[aria-label*="Address"]',
        ]
        
        for selector in address_selectors:
            address_elem = card.locator(selector).first
            if address_elem.count() > 0:
                text = address_elem.inner_text().strip()
                # Validar que parece endereço (não rating)
                if text and len(text) > 5 and not re.match(r'^[\d.,]+$', text):
                    data["address"] = text
                    break
        
        if not data["address"]:
            # Fallback: buscar texto que parece endereço
            texts = card.locator('.fontBodyMedium, .W4Efsd').all()
            for t in texts:
                text = t.inner_text().strip()
                if any(kw in text.lower() for kw in ["rua", "av.", "avenida", "praça", "alameda", "rodovia", "br-", "sp-", "r.", "av ", "número", "nº"]):
                    # Validar que não é apenas números (rating)
                    if not re.match(r'^[\d.,]+$', text):
                        data["address"] = text
                        break
        
        # Telefone - mais preciso para evitar pegar contagens de avaliações
        phone_selectors = [
            '[data-item-id*="phone"]',
            'button[aria-label*="Telefone"]',
            'button[aria-label*="Phone"]',
            '[data-item-id="phone"]',
            'a[href^="tel:"]',
        ]
        
        for selector in phone_selectors:
            try:
                phone_elem = card.locator(selector).first
                if phone_elem.count() > 0:
                    phone = phone_elem.inner_text().strip() or phone_elem.get_attribute("href") or phone_elem.get_attribute("aria-label")
                    if phone:
                        # Validar que parece um telefone brasileiro
                        digits = re.sub(r'\D', '', phone)
                        if len(digits) >= 10 and len(digits) <= 11:
                            data["phone"] = phone.strip()
                            break
            except:
                pass
        
        # Fallback: regex mais específico para telefone brasileiro
        if not data["phone"]:
            try:
                card_text = card.inner_text()
                # Padrão: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX ou XX XXXXX-XXXX
                phone_match = re.search(r'(?:\(?\d{2}\)?[\s-]?\d{4,5}[\s-]?\d{4})', card_text)
                if phone_match:
                    data["phone"] = phone_match.group(0).strip()
            except:
                pass
        
        # Website - mais robusto, filtrando redes sociais
        website_selectors = [
            '[data-item-id="authority"]',
            'a[aria-label*="Site"]',
            'a[aria-label*="Website"]',
            'button:has-text("Site")',
            'a[href^="http"]:not([href*="google"]):not([href*="maps"]):not([href*="facebook"]):not([href*="instagram"]):not([href*="twitter"]):not([href*="x.com"]):not([href*="linkedin"]):not([href*="youtube"]):not([href*="tiktok"]):not([href*="pinterest"]):not([href*="linktr.ee"]):not([href*="bio.link"]):not([href*="linkin.bio"]):not([href*="wa.me"]):not([href*="wa.link"]):not([href*="api.whatsapp"])',
        ]
        
        for selector in website_selectors:
            elements = card.locator(selector).all()
            for elem in elements:
                if elem.count() > 0:
                    href = elem.get_attribute("href")
                    if href and href.startswith("http"):
                        # Filtrar domínios não-comerciais
                        bad_domains = ["google.com", "facebook.com", "instagram.com", "linkedin.com", "twitter.com", "x.com", "youtube.com", "tiktok.com", "pinterest.com", "maps.google", "goo.gl", "wa.me", "linktr.ee", "bio.link", "linkin.bio", "wa.me", "wa.link", "api.whatsapp", "trinks.com", "agendamento.com", "agendamentos.com", "bookimed.com", "doctoralia.com.br", "doctoralia.com", "drconsulta.com", "zenklub.com", "vitat.com", "somostop.com", "trinks.com"]
                        if not any(bad in href for bad in bad_domains):
                            data["website"] = href
                            print(f"[DEBUG] Website encontrado: {href}")
                            break
            if data["website"]:
                break
        
        # Categorias
        for selector in ['[jsaction*="category"]', '.W4Efsd span', '[aria-label*="Categoria"]']:
            category_elem = card.locator(selector).first
            if category_elem.count() > 0:
                cat_text = category_elem.get_attribute("aria-label") or category_elem.inner_text()
                data["categories"] = [c.strip() for c in cat_text.split("·") if c.strip()]
                break
        
        # Price level
        for selector in ['text=/\$+/', '.MW4etd']:
            price_elem = card.locator(selector).first
            if price_elem.count() > 0:
                text = price_elem.inner_text().strip()
                if '$' in text:
                    data["price_level"] = text.count('$')
                break
        
    except Exception as e:
        print(f"[DEBUG] Erro geral ao extrair card: {e}")
    
    return data


def _extract_place_id_from_url(url: str) -> Optional[str]:
    """Extrai place_id da URL do Google Maps."""
    if not url:
        return None
    import re
    
    # Formato: https://www.google.com/maps/place/Nome/@lat,lng,17z/data=!3m1!4b1!4m6!3m5!1s0x...!8m2!3d...!4d...!16s%2Fg%2F...
    # Place ID está em /g/ ou no data
    
    # Tentar /g/
    match = re.search(r'/g/([^/?#]+)', url)
    if match:
        return match.group(1)
    
    # Tentar data=!1s
    match = re.search(r'!1s([^!]+)', url)
    if match:
        return match.group(1)
    
    # Tentar place_id direto
    match = re.search(r'place_id=([^&]+)', url)
    if match:
        return match.group(1)
    
    return None