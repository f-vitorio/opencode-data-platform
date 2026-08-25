"""Element Interaction Helpers - Safe click, fill, select, and element info extraction."""
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from typing import Optional, List, Dict, Any


def safe_click(page: Page, selector: str, timeout: int = 10000, force: bool = False) -> Dict[str, Any]:
    """Click seguro com fallback e evidência."""
    try:
        locator = page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout)
        locator.scroll_into_view_if_needed()
        locator.click(force=force, timeout=timeout)
        return {"success": True, "selector": selector}
    except PlaywrightTimeoutError:
        return {"success": False, "selector": selector, "error": "Timeout - elemento não encontrado ou não visível"}
    except Exception as e:
        return {"success": False, "selector": selector, "error": str(e)}


def safe_fill(page: Page, selector: str, value: str, timeout: int = 10000, clear_first: bool = True) -> Dict[str, Any]:
    """Preenche input com validação."""
    try:
        locator = page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout)
        if clear_first:
            locator.clear()
        locator.fill(value)
        actual = locator.input_value()
        return {"success": actual == value, "selector": selector, "expected": value, "actual": actual}
    except Exception as e:
        return {"success": False, "selector": selector, "error": str(e)}


def safe_select_option(page: Page, selector: str, value: str, timeout: int = 10000) -> Dict[str, Any]:
    """Seleciona opção em select."""
    try:
        locator = page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout)
        locator.select_option(value=value)
        return {"success": True, "selector": selector, "value": value}
    except Exception as e:
        return {"success": False, "selector": selector, "error": str(e)}


def get_element_info(page: Page, selector: str) -> Dict[str, Any]:
    """Extrai informações completas de um elemento."""
    try:
        locator = page.locator(selector).first
        if locator.count() == 0:
            return {"found": False, "selector": selector}

        box = locator.bounding_box()
        return {
            "found": True,
            "selector": selector,
            "tag_name": locator.evaluate("el => el.tagName.toLowerCase()"),
            "text": locator.inner_text().strip()[:500],
            "html": locator.evaluate("el => el.outerHTML")[:2000],
            "attributes": locator.evaluate("el => Array.from(el.attributes).reduce((acc, attr) => { acc[attr.name] = attr.value; return acc }, {})"),
            "visible": locator.is_visible(),
            "enabled": locator.is_enabled(),
            "bounding_box": box,
            "computed_style": locator.evaluate("""el => {
                const cs = getComputedStyle(el);
                return {
                    display: cs.display,
                    visibility: cs.visibility,
                    opacity: cs.opacity,
                    color: cs.color,
                    backgroundColor: cs.backgroundColor,
                    fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight,
                    width: cs.width,
                    height: cs.height,
                    margin: cs.margin,
                    padding: cs.padding,
                };
            }"""),
        }
    except Exception as e:
        return {"found": False, "selector": selector, "error": str(e)}


def find_cta_candidates(page: Page) -> List[Dict[str, Any]]:
    """Encontra candidatos a CTA na página."""
    selectors = [
        'a[href*="whatsapp"]', 'a[href*="zap"]', 'a[href*="wa.me"]',
        'a[href*="tel:"]', 'button:has-text("WhatsApp")', 'button:has-text("Zap")',
        'a:has-text("Agendar")', 'a:has-text("Agende")', 'a:has-text("Marcar")',
        'a:has-text("Comprar")', 'a:has-text("Contratar")', 'a:has-text("Solicitar")',
        'a:has-text("Orçamento")', 'a:has-text("Contato")', 'a:has-text("Fale")',
        'button[type="submit"]', 'input[type="submit"]',
        '.cta', '.btn-primary', '.btn-cta', '[class*="cta"]', '[class*="btn-primary"]',
        'a.btn', 'button.btn',
    ]

    candidates = []
    for sel in selectors:
        try:
            locators = page.locator(sel).all()
            for loc in locators:
                if loc.is_visible():
                    info = get_element_info(page, sel)
                    info["selector_used"] = sel
                    info["priority"] = _cta_priority(sel, info.get("text", ""))
                    candidates.append(info)
        except:
            continue

    # Deduplicar por bounding box similar
    unique = []
    seen_boxes = set()
    for c in candidates:
        box = c.get("bounding_box")
        if box:
            key = (round(box["x"]), round(box["y"]), round(box["width"]), round(box["height"]))
            if key not in seen_boxes:
                seen_boxes.add(key)
                unique.append(c)

    return sorted(unique, key=lambda x: -x.get("priority", 0))


def _cta_priority(selector: str, text: str) -> int:
    text_lower = text.lower()
    score = 0
    if any(w in text_lower for w in ["whatsapp", "zap", "wa.me"]): score += 100
    if any(w in text_lower for w in ["agendar", "agende", "marcar"]): score += 90
    if any(w in text_lower for w in ["comprar", "contratar", "solicitar", "orçamento"]): score += 80
    if "btn-primary" in selector or "cta" in selector: score += 50
    if selector.startswith("button"): score += 30
    if selector.startswith("a[href"): score += 20
    return score