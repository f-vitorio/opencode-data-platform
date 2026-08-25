"""Google Maps Scraper - Extractor de Página de Detalhes (Versão Corrigida)."""
from playwright.sync_api import Page
from typing import Dict, Any, List
import re
import time
import json


def extract_place_details(page: Page, place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Abre página de detalhes do lugar e extrai dados completos.
    Versão baseada na estrutura real do Google Maps.
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
        "categories": [],
        "price_level": place.get("price_level"),
        "rating": place.get("rating"),
        "reviews_count": place.get("reviews_count"),
        "service_options": [],
        "amenities": [],
        "accessibility": [],
        "payment_options": [],
        "highlights": [],
        "owner_info": {},
        "hours_raw": {},
    }
    
    place_id = place.get("place_id")
    if not place_id:
        return details
    
    detail_page = None
    
    try:
        # Estratégia 1: Tentar clicar no link da lista de resultados
        detail_page = _click_place_link(page, place_id)
        
        # Estratégia 2: Fallback - navegar direto para URL
        if not detail_page:
            detail_page = page.context.new_page()
            detail_page.goto(
                f"https://www.google.com/maps/place/?q=place_id:{place_id}", 
                wait_until="domcontentloaded", 
                timeout=30000
            )
        
        # Aguardar carregamento completo
        detail_page.wait_for_load_state("domcontentloaded", timeout=20000)
        detail_page.wait_for_timeout(3000)
        
        # Scroll para carregar conteúdo lazy-loaded
        _scroll_detail_page(detail_page)
        
        # Extrair dados da página de detalhes
        details = _extract_detail_page_data(detail_page, details, place)
        
        if detail_page != page:
            detail_page.close()
        
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair detalhes: {e}")
    
    return details


def _click_place_link(page: Page, place_id: str):
    """Tenta clicar no link do lugar na lista de resultados."""
    link_selectors = [
        f'a[href*="{place_id}"]',
        f'a[href*="/maps/place/"]',
        '.hfpxzc',
        'a[jsaction*="place"]',
        '[data-result-index] a',
    ]
    
    for selector in link_selectors:
        try:
            links = page.locator(selector).all()
            for link in links:
                if link.count() > 0:
                    href = link.get_attribute("href")
                    if href and place_id in href:
                        with page.context.expect_page(timeout=5000) as new_page_info:
                            link.click()
                        return new_page_info.value
        except:
            continue
    
    return None


def _scroll_detail_page(page: Page):
    """Scroll na página de detalhes para carregar conteúdo lazy-loaded."""
    try:
        for i in range(4):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
    except:
        pass


def extract_place_details(page: Page, place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Abre página de detalhes do lugar e extrai dados completos.
    Versão baseada na estrutura real do Google Maps.
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
        "categories": [],
        "price_level": place.get("price_level"),
        "rating": place.get("rating"),
        "reviews_count": place.get("reviews_count"),
        "service_options": [],
        "amenities": [],
        "accessibility": [],
        "payment_options": [],
        "highlights": [],
        "owner_info": {},
        "hours_raw": {},
    }
    
    place_id = place.get("place_id")
    if not place_id:
        return details
    
    detail_page = None
    
    try:
        detail_page = _click_place_link(page, place_id)
        
        if not detail_page:
            detail_page = page.context.new_page()
            detail_page.goto(
                f"https://www.google.com/maps/place/?q=place_id:{place_id}", 
                wait_until="domcontentloaded", 
                timeout=30000
            )
        
        detail_page.wait_for_load_state("domcontentloaded", timeout=20000)
        detail_page.wait_for_timeout(3000)
        _scroll_detail_page(detail_page)
        
        details = _extract_detail_page_data(detail_page, details, place)
        
        if detail_page != page:
            detail_page.close()
        
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair detalhes: {e}")
    
    return details


# ==================== FUNÇÕES DE EXTRAÇÃO BASEADAS EM data-item-id ====================

def _extract_detail_page_data(page: Page, details: Dict[str, Any], original_place: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai dados da página de detalhes usando data-item-id (estrutura real do Google Maps)."""
    
    print("[DEBUG] Iniciando extração de dados da página de detalhes")
    
    # 1. ENDEREÇO - data-item-id="address"
    _extract_by_data_item_id(page, details, "address", "address")
    
    # 2. WEBSITE - data-item-id="authority"
    _extract_by_data_item_id(page, details, "authority", "website")
    
    # 3. TELEFONE - data-item-id*="phone"
    _extract_by_data_item_id(page, details, "phone", "phone")
    
    # 4. PLUS CODE - data-item-id="oloc"
    _extract_by_data_item_id(page, details, "oloc", "plus_code")
    
    # 5. CATEGORIAS - jsaction*="category"
    _extract_categories_via_jsaction(page, details)
    
    # 6. HORÁRIOS - buttons com aria-label contendo dias da semana
    _extract_opening_hours_via_aria(page, details)
    
    # 7. PLUS CODE - também pode estar em botão com "Plus Code"
    _extract_plus_code_via_aria(page, details)
    
    # 8. WEBSITE - também pode estar em botão "Copiar website"
    _extract_website_via_aria(page, details)
    
    # 9. TELEFONE - também pode estar em botão "Copiar número"
    _extract_phone_via_aria(page, details)
    
    # 10. FOTOS - aba Fotos
    _extract_photos_count(page, details)
    
    # 11. REVIEWS
    _extract_reviews_snippets(page, details)
    
    # 12. POPULAR TIMES
    _extract_popular_times_via_aria(page, details)
    
    # 12b. PREÇO
    _extract_price_level(page, details)
    
    # 13. RATING E REVIEWS
    _extract_rating_reviews(page, details)
    
    # 14. SERVIÇOS E AMENIDADES
    _extract_service_options_via_aria(page, details)
    
    # 15. ACESSIBILIDADE
    _extract_accessibility_via_aria(page, details)
    
    # 16. PAGAMENTO
    _extract_payment_options_via_aria(page, details)
    
    # 17. DESTAQUES
    _extract_highlights_via_aria(page, details)
    
    # 18. INFO DO PROPRIETÁRIO
    _extract_owner_info(page, details)
    
    # 19. DESCRIÇÃO
    _extract_description(page, details)
    
    return details


# ==================== HELPERS BASEADOS EM data-item-id ====================

def _extract_by_data_item_id(page: Page, details: Dict[str, Any], item_id: str, target_key: str):
    """Extrai valor pelo data-item-id."""
    try:
        # Tentar button primeiro
        btn = page.locator(f'button[data-item-id="{item_id}"]').first
        if btn.count() > 0:
            value = btn.inner_text().strip()
            if value:
                details[target_key] = value
                print(f"[DEBUG] {target_key} via data-item-id: {value[:100]}")
                return
        
        # Tentar a tag
        link = page.locator(f'a[data-item-id="{item_id}"]').first
        if link.count() > 0:
            href = link.get_attribute("href")
            if href and href.startswith("http"):
                details[target_key] = href
                print(f"[DEBUG] {target_key} via data-item-id href: {href}")
                return
            text = link.inner_text().strip()
            if text:
                details[target_key] = text
                print(f"[DEBUG] {target_key} via data-item-id text: {text[:100]}")
                return
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair {item_id}: {e}")


# ==================== EXTRAÇÃO VIA ARIA-LABEL (botões) ====================

def _extract_categories_via_jsaction(page: Page, details: Dict[str, Any]):
    """Extrai categorias via jsaction*='category'."""
    all_categories = []
    
    try:
        # Seletor principal que funcionou no teste
        category_elements = page.locator('[jsaction*="category"]').all()
        for elem in category_elements:
            if elem.count() > 0:
                text = elem.inner_text().strip()
                if text and len(text) > 1:
                    all_categories.append(text)
        
        # Também tentar botão com jsaction*="category"
        buttons = page.locator('button[jsaction*="category"]').all()
        for btn in buttons:
            text = btn.inner_text().strip()
            if text and len(text) > 1:
                all_categories.append(text)
        
        # Deduplicar
        unique = []
        seen = set()
        for cat in all_categories:
            cat_lower = cat.strip().lower()
            if cat_lower not in seen and len(cat_lower) > 1:
                seen.add(cat_lower)
                unique.append(cat.strip())
        
        details["categories"] = unique
        print(f"[DEBUG] Categorias via jsaction: {unique}")
        
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair categorias: {e}")


def _extract_opening_hours_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai horários de funcionamento via aria-label dos botões."""
    try:
        hours = {}
        days_pt = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        days_en = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        buttons = page.locator('button[aria-label]').all()
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            aria_lower = aria.lower()
            
            # Verificar se é horário de funcionamento (contém dia da semana)
            for day in days_pt + days_en:
                if day in aria_lower and ("a " in aria or "at " in aria or "fechado" in aria_lower or "closed" in aria_lower):
                    # Extrair o dia e horário
                    # Formato: "segunda-feira, 09:00 a 20:00, Copiar horário de funcionamento"
                    text = aria
                    # Remover "Copiar horário de funcionamento" e "Copiar horário"
                    clean = re.sub(r',?\s*Copiar horário.*', '', text, flags=re.IGNORECASE)
                    clean = clean.strip()
                    if clean:
                        # Extrair dia
                        for d in days_pt + days_en:
                            if d in clean.lower():
                                hours[clean] = clean
                                break
                        break
        
        if hours:
            details["opening_hours"] = "; ".join(hours.keys())
            details["hours_raw"] = hours
            print(f"[DEBUG] Horários encontrados: {len(hours)} dias")
        
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair horários: {e}")


def _extract_plus_code_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai Plus Code via aria-label."""
    try:
        buttons = page.locator('button[aria-label*="Plus code"], button[aria-label*="Plus Code"], button[aria-label*="Código plus"]').all()
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            match = re.search(r'[A-Z]{2,}\+[A-Z0-9]{2,}', aria)
            if match:
                details["plus_code"] = match.group(0)
                print(f"[DEBUG] Plus Code via aria: {details['plus_code']}")
                return
    except:
        pass


def _extract_website_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai website via aria-label 'Copiar website'."""
    try:
        buttons = page.locator('button[aria-label*="Copiar website"], button[aria-label*="Copiar website"], button[aria-label*="Copy website"]').all()
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            # O aria-label pode ser "Copiar website: rselicorrea.com.br"
            if "website" in aria.lower() or "site" in aria.lower():
                # Tentar extrair URL do aria-label
                url_match = re.search(r'https?://[^\s,]+|[\w.-]+\.[a-z]{2,}', aria)
                if url_match:
                    url = url_match.group(0)
                    if not url.startswith("http"):
                        url = "https://" + url
                    details["website"] = url
                    print(f"[DEBUG] Website via aria: {details['website']}")
                    return
    except:
        pass


def _extract_phone_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai telefone via aria-label 'Copiar número'."""
    try:
        buttons = page.locator('button[aria-label*="Copiar número"], button[aria-label*="Copy number"], button[aria-label*="Telefone:"]').all()
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            if "telefone" in aria.lower() or "phone" in aria.lower() or "número" in aria.lower():
                # Extrair número do aria-label
                match = re.search(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', aria)
                if match:
                    details["phone"] = match.group(0)
                    print(f"[DEBUG] Phone via aria: {details['phone']}")
                    return
    except:
        pass


def _extract_photos_count(page: Page, details: Dict[str, Any]):
    """Extrai contagem de fotos via aba Fotos."""
    try:
        # Clicar na aba Fotos
        for selector in ['[role="tab"]:has-text("Fotos")', '[role="tab"]:has-text("Photos")', 'button:has-text("Fotos")', 'button:has-text("Photos")']:
            try:
                tab = page.locator(selector).first
                if tab.count() > 0:
                    tab.click()
                    page.wait_for_timeout(1500)
                    break
            except:
                pass
        
        # Procurar contador
        count_selectors = [
            'text=/(\\d+)\\s*fotos?/i',
            'text=/(\\d+)\\s*photos?/i',
            '[aria-label*="foto"]',
            '[aria-label*="photo"]',
        ]
        
        for selector in count_selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0:
                    text = elem.inner_text()
                    match = re.search(r'(\d+)', text)
                    if match:
                        details["photos_count"] = int(match.group(1))
                        print(f"[DEBUG] Fotos: {details['photos_count']}")
                        return
            except:
                pass
    except:
        pass


def _extract_reviews_snippets(page: Page, details: Dict[str, Any]):
    """Extrai snippets de reviews."""
    try:
        # Clicar na aba de avaliações
        for selector in ['[role="tab"]:has-text("Avaliações")', '[role="tab"]:has-text("Reviews")', 'button:has-text("Avaliações")', 'button:has-text("Reviews")']:
            try:
                tab = page.locator(selector).first
                if tab.count() > 0:
                    tab.click()
                    page.wait_for_timeout(1500)
                    break
            except:
                pass
        
        # Extrair reviews
        review_cards = page.locator('[data-review-id], .jftiEf, .MyEned, .jxjCnc').all()
        snippets = []
        
        for card in review_cards[:8]:
            try:
                text_elem = card.locator('.wiI7pd, .MyEned, .Jtu6Td, .rsqaWe').first
                rating_elem = card.locator('[role="img"][aria-label*="star"], [aria-label*="estrela"]').first
                author_elem = card.locator('.d4r55, .TSUbDb, .WNxzHc, .x3AX1-LfntMc-header-title-title').first
                date_elem = card.locator('.rsqaWe, .x3AX1-LfntMc-header-title-date, .DU9Pgd').first
                
                text = text_elem.inner_text().strip() if text_elem.count() > 0 else ""
                rating = rating_elem.get_attribute("aria-label") if rating_elem.count() > 0 else ""
                author = author_elem.inner_text().strip() if author_elem.count() > 0 else ""
                date = date_elem.inner_text().strip() if date_elem.count() > 0 else ""
                
                if text and len(text) > 10:
                    snippets.append({
                        "author": author,
                        "rating": rating,
                        "text": text[:400],
                        "date": date_elem.inner_text().strip() if date_elem.count() > 0 else "",
                    })
                    if len(snippets) >= 6:
                        break
            except:
                continue
        
        details["reviews_snippets"] = snippets
        print(f"[DEBUG] Reviews snippets: {len(snippets)}")
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair reviews: {e}")


def _extract_popular_times_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai horários populares via aria-label."""
    try:
        buttons = page.locator('button[aria-label*="%"], button[aria-label*="popular"], button[aria-label*="pico"]').all()
        popular_data = {}
        
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            if aria and ("%" in aria or "popular" in aria.lower() or "pico" in aria.lower()):
                popular_data[aria] = aria
        
        if popular_data:
            details["popular_times"] = popular_data
            print(f"[DEBUG] Popular times: {len(popular_data)} entries")
    except:
        pass


def _extract_website_via_aria(page: Page, details: Dict[str, Any]):
    """Já coberto por _extract_by_data_item_id, mas tenta via aria também."""
    if details.get("website"):
        return
    try:
        buttons = page.locator('button[aria-label*="Copiar website"], button[aria-label*="Copiar website"], button[aria-label*="Copy website"]').all()
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            if "website" in aria.lower() or "site" in aria.lower():
                # Tentar extrair do aria-label
                url_match = re.search(r'https?://[^\s,]+|[\w.-]+\.[a-z]{2,}', aria)
                if url_match:
                    url = url_match.group(0)
                    if not url.startswith("http"):
                        url = "https://" + url
                    details["website"] = url
                    print(f"[DEBUG] Website via aria: {details['website']}")
                    return
    except:
        pass


def _extract_phone_via_aria(page: Page, details: Dict[str, Any]):
    """Já coberto por _extract_by_data_item_id, mas tenta via aria também."""
    if details.get("phone"):
        return
    try:
        buttons = page.locator('button[aria-label*="Copiar número"], button[aria-label*="Copy number"], button[aria-label*="Telefone:"]').all()
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            if "telefone" in aria.lower() or "phone" in aria.lower() or "número" in aria.lower():
                match = re.search(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}', aria)
                if match:
                    details["phone"] = match.group(0)
                    print(f"[DEBUG] Phone via aria: {details['phone']}")
                    return
    except:
        pass


def _extract_price_level(page: Page, details: Dict[str, Any]):
    """Extrai nível de preço."""
    try:
        selectors = [
            '[aria-label*="Preço"]',
            '[aria-label*="Price"]',
            'text=/\\$+/',
            '.MW4etd',
        ]
        
        for selector in selectors:
            try:
                elem = page.locator(selector).first
                if elem.count() > 0:
                    text = elem.inner_text().strip() or elem.get_attribute("aria-label") or ""
                    if "$" in text:
                        count = text.count("$")
                        if 1 <= count <= 4:
                            details["price_level"] = count
                            print(f"[DEBUG] Price level: {details['price_level']}")
                            return
            except:
                pass
    except:
        pass


def _extract_rating_reviews(page: Page, details: Dict[str, Any]):
    """Extrai rating e reviews atualizados."""
    # Rating
    try:
        rating_elements = page.locator('[role="img"][aria-label*="star"], [role="img"][aria-label*="estrela"]').all()
        for elem in rating_elements:
            aria = elem.get_attribute("aria-label") or elem.inner_text()
            match = re.search(r'(\d+\.?\d*)', aria)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    details["rating"] = rating
                    break
    except:
        pass
    
    # Reviews count
    try:
        buttons = page.locator('button[aria-label*="avaliação"], button[aria-label*="review"], [data-item-id="reviews"]').all()
        for btn in buttons:
            text = btn.inner_text().strip() or btn.get_attribute("aria-label") or ""
            match = re.search(r'(\d[\d.,]*)', text.replace(".", "").replace(",", ""))
            if match:
                count = int(match.group(1))
                if count > 0:
                    details["reviews_count"] = count
                    break
    except:
        pass


def _extract_popular_times_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai horários populares via aria-label."""
    try:
        buttons = page.locator('button[aria-label*="%"], button[aria-label*="popular"], button[aria-label*="pico"]').all()
        popular_data = {}
        
        for btn in buttons:
            aria = btn.get_attribute("aria-label") or ""
            if aria and ("%" in aria or "popular" in aria.lower() or "pico" in aria.lower()):
                popular_data[aria] = aria
        
        if popular_data:
            details["popular_times"] = popular_data
            print(f"[DEBUG] Popular times: {len(popular_data)} entries")
    except:
        pass


def _extract_service_options_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai opções de serviço via aria-label."""
    try:
        services = []
        # Procurar checkboxes/switches com labels de serviço
        items = page.locator('[role="checkbox"][aria-label], [role="switch"][aria-label], button[aria-label*="Entrega"], button[aria-label*="Delivery"], button[aria-label*="Retirada"], button[aria-label*="Takeout"], button[aria-label*="No local"], button[aria-label*="Dine-in"]').all()
        
        for item in items:
            label = item.get_attribute("aria-label") or item.inner_text().strip()
            checked = item.get_attribute("aria-checked") == "true"
            if label and len(label) > 2:
                services.append({"service": label, "available": checked})
        
        if services:
            details["service_options"] = services
            print(f"[DEBUG] Service options: {len(services)}")
    except:
        pass


def _extract_accessibility_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai acessibilidade via aria-label."""
    try:
        acc = []
        items = page.locator('button[aria-label*="Acessibilidade"], button[aria-label*="Accessibility"], button[aria-label*="Acesso"], [role="checkbox"][aria-label*="Acesso"], [role="switch"][aria-label*="Acesso"]').all()
        
        for item in items:
            label = item.get_attribute("aria-label") or item.inner_text().strip()
            checked = item.get_attribute("aria-checked") == "true"
            if label and len(label) > 2:
                acc.append({"feature": label, "available": checked})
        
        if acc:
            details["accessibility"] = acc
            print(f"[DEBUG] Accessibility: {len(acc)}")
    except:
        pass


def _extract_payment_options_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai opções de pagamento."""
    try:
        payments = []
        # Procurar imagens de bandeiras de cartão
        images = page.locator('img[alt*="Visa"], img[alt*="Mastercard"], img[alt*="Elo"], img[alt*="Amex"], img[alt*="Pix"], img[alt*="Dinheiro"], [role="img"][alt*="cartão"]').all()
        
        for img in images:
            alt = img.get_attribute("alt") or ""
            if alt and len(alt) > 1:
                payments.append(alt)
        
        # Também procurar botões/texto
        buttons = page.locator('button[aria-label*="Visa"], button[aria-label*="Mastercard"], button[aria-label*="Elo"], button[aria-label*="Pix"], button[aria-label*="Dinheiro"]').all()
        for btn in buttons:
            label = btn.get_attribute("aria-label") or btn.inner_text().strip()
            if label:
                payments.append(label)
        
        if payments:
            details["payment_options"] = list(set(payments))
            print(f"[DEBUG] Payment options: {payments}")
    except:
        pass


def _extract_highlights_via_aria(page: Page, details: Dict[str, Any]):
    """Extrai destaques via aria-label."""
    try:
        highlights = []
        items = page.locator('button[aria-label*="Destaque"], button[aria-label*="Highlight"], button[aria-label*="Conhecido"], button[aria-label*="Known for"]').all()
        
        for item in items:
            text = item.get_attribute("aria-label") or item.inner_text().strip()
            if text and len(text) > 2:
                highlights.append(text)
        
        if highlights:
            details["highlights"] = highlights[:10]
            print(f"[DEBUG] Highlights: {highlights}")
    except:
        pass


def _extract_owner_info(page: Page, details: Dict[str, Any]):
    """Extrai info do proprietário."""
    try:
        owner_selectors = [
            'button[aria-label*="Proprietário"]',
            'button[aria-label*="Owner"]',
            'button[aria-label*="Gerente"]',
            'button[aria-label*="Manager"]',
        ]
        
        for selector in owner_selectors:
            container = page.locator(selector).first
            if container.count() > 0:
                name_elem = container.locator('.fontHeadlineSmall, .fontBodyLarge, [role="heading"]').first
                if name_elem.count() > 0:
                    details["owner_info"]["name"] = name_elem.inner_text().strip()
                
                claimed = container.locator('text=/reivindicado|claimed|verificado|verified/i').first
                if claimed.count() > 0:
                    details["owner_info"]["claimed"] = True
                
                if details["owner_info"]:
                    print(f"[DEBUG] Owner info: {details['owner_info']}")
                    return
    except:
        pass


def _extract_description(page: Page, details: Dict[str, Any]):
    """Extrai descrição do lugar."""
    try:
        desc_selectors = [
            '[data-item-id="description"]',
            '[aria-label*="Descrição"]',
            '[aria-label*="Description"]',
            '.PyZSLd',
            '.lMbq3e',
        ]
        
        for selector in desc_selectors:
            elem = page.locator(selector).first
            if elem.count() > 0:
                try:
                    more_btn = elem.locator('button:has-text("Mais"), button:has-text("More"), button:has-text("Ver mais")').first
                    if more_btn.count() > 0:
                        more_btn.click()
                        page.wait_for_timeout(500)
                except:
                    pass
                
                desc = elem.inner_text().strip()
                if desc and len(desc) > 20:
                    details["description"] = desc[:1000]
                    print(f"[DEBUG] Description: {desc[:100]}...")
                    return
    except:
        pass


def _scroll_detail_page(page: Page):
    """Scroll na página de detalhes para carregar conteúdo lazy-loaded."""
    try:
        for i in range(4):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
    except:
        pass


# ==================== FUNÇÕES LEGADAS (MANTIDAS PARA COMPATIBILIDADE) ====================

def _click_place_link(page: Page, place_id: str):
    """Tenta clicar no link do lugar na lista de resultados."""
    link_selectors = [
        f'a[href*="{place_id}"]',
        f'a[href*="/maps/place/"]',
        '.hfpxzc',
        'a[jsaction*="place"]',
        '[data-result-index] a',
    ]
    
    for selector in link_selectors:
        try:
            links = page.locator(selector).all()
            for link in links:
                if link.count() > 0:
                    href = link.get_attribute("href")
                    if href and place_id in href:
                        with page.context.expect_page(timeout=5000) as new_page_info:
                            link.click()
                        return new_page_info.value
        except:
            continue
    return None


def _scroll_detail_page(page: Page):
    """Scroll na página de detalhes para carregar conteúdo lazy-loaded."""
    try:
        for i in range(4):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
    except:
        pass


def extract_place_details(page: Page, place: Dict[str, Any]) -> Dict[str, Any]:
    """
    Abre página de detalhes do lugar e extrai dados completos.
    Versão baseada na estrutura real do Google Maps (data-item-id + aria-label).
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
        "categories": [],
        "price_level": place.get("price_level"),
        "rating": place.get("rating"),
        "reviews_count": place.get("reviews_count"),
        "service_options": [],
        "amenities": [],
        "accessibility": [],
        "payment_options": [],
        "highlights": [],
        "owner_info": {},
        "hours_raw": {},
    }
    
    place_id = place.get("place_id")
    if not place_id:
        return details
    
    detail_page = None
    
    try:
        # A página de busca JÁ é a página de detalhes no Google Maps atual
        # Verificar se já estamos na página de detalhes
        current_url = page.url
        if "/maps/place/" in current_url and "place_id" not in current_url and "search" not in current_url:
            # Já estamos na página de detalhes!
            detail_page = page
            print("[DEBUG] Já estamos na página de detalhes, usando página atual")
        else:
            # Tentar clicar no link
            detail_page = _click_place_link(page, place.get("place_id", ""))
            
            if not detail_page:
                detail_page = page.context.new_page()
                detail_page.goto(
                    f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id', '')}", 
                    wait_until="domcontentloaded", 
                    timeout=30000
                )
        
        if detail_page:
            detail_page.wait_for_load_state("domcontentloaded", timeout=20000)
            detail_page.wait_for_timeout(3000)
            _scroll_detail_page(detail_page)
            
            details = _extract_detail_page_data(detail_page, details, place)
            
            if detail_page != page:
                detail_page.close()
        
    except Exception as e:
        print(f"[DEBUG] Erro ao extrair detalhes: {e}")
    
    return details