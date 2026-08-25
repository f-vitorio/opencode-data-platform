# PLAYWRIGHT AUTOMATION SKILL

Skill compartilhada para automação de navegador com Playwright. Fornece wrappers reutilizáveis, padrões de teste, helpers de extração de dados e utilitários para relatórios.

---

## INSTALAÇÃO E CONFIGURAÇÃO

```python
# Verificar se Playwright está disponível
import subprocess
import sys

def ensure_playwright():
    try:
        import playwright
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return True
```

---

## CORE WRAPPERS

### 1. Browser Manager

```python
# browser_manager.py
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
import os

class BrowserManager:
    def __init__(self, headed: bool = False, slow_mo: int = 0):
        self.headed = headed or os.getenv("HEADED", "0") == "1"
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser: Optional[Browser] = None

    def __enter__(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=not self.headed,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    @contextmanager
    def new_context(self, **kwargs) -> Generator[BrowserContext, None, None]:
        defaults = {
            "viewport": {"width": 1280, "height": 720},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "locale": "pt-BR",
            "timezone_id": "America/Sao_Paulo",
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "accept_downloads": False,
        }
        defaults.update(kwargs)
        context = self._browser.new_context(**defaults)
        try:
            yield context
        finally:
            context.close()

    @contextmanager
    def new_page(self, context: BrowserContext = None, **kwargs) -> Generator[Page, None, None]:
        ctx = context or self._browser.new_context()
        page = ctx.new_page()
        page.set_default_timeout(30000)
        page.set_default_navigation_timeout(30000)
        try:
            yield page
        finally:
            page.close()
            if context is None:
                ctx.close()

# Uso:
# with BrowserManager() as bm:
#     with bm.new_context() as ctx:
#         with bm.new_page(ctx) as page:
#             page.goto("https://example.com")
```

### 2. Device Profiles

```python
# devices.py
from playwright.sync_api import DeviceDescriptor

DEVICES = {
    "desktop": {
        "viewport": {"width": 1280, "height": 720},
        "device_scale_factor": 1,
        "is_mobile": False,
        "has_touch": False,
    },
    "desktop_large": {
        "viewport": {"width": 1920, "height": 1080},
        "device_scale_factor": 1,
        "is_mobile": False,
        "has_touch": False,
    },
    "mobile_iphone_se": {
        "viewport": {"width": 375, "height": 667},
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    },
    "mobile_iphone_12": {
        "viewport": {"width": 390, "height": 844},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    },
    "mobile_iphone_14_pro": {
        "viewport": {"width": 393, "height": 852},
        "device_scale_factor": 3,
        "is_mobile": True,
        "has_touch": True,
    },
    "mobile_android": {
        "viewport": {"width": 412, "height": 915},
        "device_scale_factor": 2.75,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    },
    "tablet_ipad": {
        "viewport": {"width": 768, "height": 1024},
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    },
    "tablet_android": {
        "viewport": {"width": 800, "height": 1280},
        "device_scale_factor": 1.5,
        "is_mobile": True,
        "has_touch": True,
    },
}

def get_device(device_name: str) -> Dict[str, Any]:
    return DEVICES.get(device_name, DEVICES["desktop"])
```

### 3. Navigation Helpers

```python
# navigation.py
from playwright.sync_api import Page
from typing import List, Dict, Any, Optional
import time

def goto_with_retry(page: Page, url: str, max_retries: int = 2, wait_until: str = "networkidle") -> Dict[str, Any]:
    """Navega com retry e retorna métricas."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            start = time.time()
            response = page.goto(url, wait_until=wait_until, timeout=30000)
            elapsed = (time.time() - start) * 1000
            return {
                "success": True,
                "status": response.status if response else None,
                "url": page.url,
                "load_time_ms": round(elapsed, 2),
                "attempt": attempt + 1,
                "redirect_chain": response.request().redirect_chain() if response else [],
            }
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)  # backoff exponencial
            continue
    return {"success": False, "error": str(last_error), "attempts": max_retries + 1}

def wait_for_network_idle(page: Page, timeout: int = 5000) -> bool:
    """Aguarda rede idle com timeout."""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
        return True
    except:
        return False

def scroll_page(page: Page, steps: int = 5, delay: float = 0.5) -> None:
    """Scroll suave pela página para trigger lazy loading."""
    for i in range(steps):
        page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {(i+1)/steps})")
        page.wait_for_timeout(delay * 1000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)
```

### 4. Element Interaction Helpers

```python
# interactions.py
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from typing import Optional, List, Dict, Any
import re

def safe_click(page: Page, selector: str, timeout: int = 10000, force: bool = False) -> Dict[str, Any]:
    """Click seguro com fallback e evidência."""
    try:
        locator = page.locator(selector).first
        locator.wait_for(state="visible", timeout=timeout)
        # Scroll into view se necessário
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
        # Verificar se valor foi preenchido
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
```

### 5. Data Extraction Helpers

```python
# extraction.py
from playwright.sync_api import Page
from typing import Dict, Any, List, Optional
import json
import re

def extract_seo_data(page: Page) -> Dict[str, Any]:
    """Extrai todos os dados de SEO técnico do DOM rendered."""
    return page.evaluate("""() => {
        const data = {};
        
        // Title
        data.title = document.title;
        data.title_length = document.title.length;
        
        // Meta tags
        const metas = document.querySelectorAll('meta');
        data.meta = {};
        metas.forEach(m => {
            const name = m.getAttribute('name') || m.getAttribute('property') || m.getAttribute('itemprop');
            const content = m.getAttribute('content');
            if (name && content) data.meta[name] = content;
        });
        
        // Meta description
        data.meta_description = data.meta['description'] || '';
        data.meta_description_length = data.meta_description.length;
        
        // Canonical
        const canonical = document.querySelector('link[rel="canonical"]');
        data.canonical = canonical?.href || null;
        
        // Robots meta
        data.robots_meta = data.meta['robots'] || 'index,follow';
        
        // Headings
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        data.headings = Array.from(headings).map(h => ({
            tag: h.tagName.toLowerCase(),
            text: h.innerText.trim(),
            level: parseInt(h.tagName[1])
        }));
        data.h1_count = data.headings.filter(h => h.level === 1).length;
        data.h1_text = data.headings.find(h => h.level === 1)?.text || '';
        
        // Structured Data (JSON-LD)
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        data.structured_data = [];
        scripts.forEach(s => {
            try {
                data.structured_data.push(JSON.parse(s.textContent));
            } catch (e) {
                data.structured_data.push({error: "Invalid JSON", content: s.textContent[:200]});
            }
        });
        
        // Open Graph
        data.og = {};
        ['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name'].forEach(prop => {
            const el = document.querySelector(`meta[property="${prop}"]`);
            if (el) data.og[prop] = el.getAttribute('content');
        });
        
        // Twitter Cards
        data.twitter = {};
        ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'].forEach(name => {
            const el = document.querySelector(`meta[name="${name}"]`);
            if (el) data.twitter[name] = el.getAttribute('content');
        });
        
        // Images
        const images = document.querySelectorAll('img');
        data.images = Array.from(images).map(img => ({
            src: img.src,
            alt: img.alt || '',
            width: img.naturalWidth,
            height: img.naturalHeight,
            loading: img.loading,
            has_alt: !!img.alt && img.alt.trim().length > 0
        }));
        data.images_without_alt = data.images.filter(i => !i.has_alt).length;
        
        // Links internos
        const links = document.querySelectorAll('a[href]');
        data.internal_links = Array.from(links)
            .filter(a => a.href && a.href.startsWith(window.location.origin))
            .map(a => ({href: a.href, text: a.innerText.trim(), title: a.title}));
        
        // Language
        data.lang = document.documentElement.lang || 'não definido';
        
        // Viewport
        const viewport = document.querySelector('meta[name="viewport"]');
        data.viewport = viewport?.getAttribute('content') || 'não definido';
        
        // Favicon
        const favicon = document.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
        data.favicon = favicon?.href || null;
        
        return data;
    }""")

def extract_performance_metrics(page: Page) -> Dict[str, Any]:
    """Extrai métricas de performance via Performance API."""
    return page.evaluate("""() => {
        const perf = performance;
        const nav = perf.getEntriesByType('navigation')[0];
        const paint = perf.getEntriesByType('paint');
        const resources = perf.getEntriesByType('resource');
        
        const metrics = {
            // Navigation Timing
            dns_lookup: nav ? nav.domainLookupEnd - nav.domainLookupStart : null,
            tcp_connect: nav ? nav.connectEnd - nav.connectStart : null,
            tls: nav ? nav.connectEnd - nav.secureConnectionStart : null,
            ttfb: nav ? nav.responseStart - nav.requestStart : null,
            download: nav ? nav.responseEnd - nav.responseStart : null,
            dom_interactive: nav ? nav.domInteractive - nav.startTime : null,
            dom_complete: nav ? nav.domComplete - nav.startTime : null,
            load_event: nav ? nav.loadEventEnd - nav.startTime : null,
            
            // Paint Timing
            fp: paint.find(p => p.name === 'first-paint')?.startTime || null,
            fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || null,
            
            // Resources
            resource_count: resources.length,
            total_transfer_size: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0),
            total_encoded_size: resources.reduce((sum, r) => sum + (r.encodedBodySize || 0), 0),
            slow_resources: resources.filter(r => r.duration > 1000).map(r => ({
                name: r.name,
                duration: r.duration,
                size: r.transferSize,
                type: r.initiatorType
            })).slice(0, 10),
        };
        
        // Core Web Vitals (se disponível via web-vitals library ou manual)
        // LCP - Largest Contentful Paint
        try {
            const lcpEntries = perf.getEntriesByType('largest-contentful-paint');
            if (lcpEntries.length > 0) {
                metrics.lcp = lcpEntries[lcpEntries.length - 1].startTime;
            }
        } catch (e) {}
        
        // FID - First Input Delay (precisa de polyfill ou event listener)
        // CLS - Cumulative Layout Shift
        try {
            const clsEntries = perf.getEntriesByType('layout-shift');
            let cls = 0;
            clsEntries.forEach(entry => {
                if (!entry.hadRecentInput) cls += entry.value;
            });
            metrics.cls = cls;
        } catch (e) {}
        
        return metrics;
    }""")

def extract_console_logs(page: Page) -> List[Dict[str, Any]]:
    """Captura logs do console durante a navegação."""
    logs = []
    page.on("console", lambda msg: logs.append({
        "type": msg.type,
        "text": msg.text,
        "location": msg.location,
        "args": [str(arg) for arg in msg.args]
    }))
    page.on("pageerror", lambda err: logs.append({
        "type": "error",
        "text": str(err),
        "location": {"url": page.url}
    }))
    return logs

def extract_network_failures(page: Page) -> List[Dict[str, Any]]:
    """Captura falhas de rede (4xx, 5xx, blocked)."""
    failures = []
    page.on("response", lambda resp: failures.append({
        "url": resp.url,
        "status": resp.status,
        "status_text": resp.status_text,
        "resource_type": resp.request.resource_type,
        "timing": resp.request.timing
    }) if resp.status >= 400 else None)
    return failures

def extract_cro_elements(page: Page) -> Dict[str, Any]:
    """Extrai elementos relevantes para CRO."""
    return page.evaluate("""() => {
        const data = {};
        
        // Forms
        const forms = document.querySelectorAll('form');
        data.forms = Array.from(forms).map(form => ({
            action: form.action,
            method: form.method,
            fields: Array.from(form.querySelectorAll('input, select, textarea')).map(f => ({
                type: f.type || f.tagName.toLowerCase(),
                name: f.name,
                id: f.id,
                placeholder: f.placeholder,
                required: f.required,
                autocomplete: f.autocomplete,
                label: f.labels?.[0]?.innerText || ''
            })),
            field_count: form.querySelectorAll('input, select, textarea').length,
            submit_button: form.querySelector('button[type="submit"], input[type="submit"]')?.innerText || ''
        }));
        
        // Trust signals
        const trustSelectors = [
            '[class*="trust"]', '[class*="badge"]', '[class*="certif"]', '[class*="seal"]',
            '[class*="guarantee"]', '[class*="secure"]', '[class*="ssl"]',
            'img[alt*="certificado" i]', 'img[alt*="seguro" i]', 'img[alt*="ssl" i]'
        ];
        data.trust_signals = [];
        trustSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                data.trust_signals.push({selector: sel, text: el.innerText.trim()[:200], html: el.outerHTML[:500]});
            });
        });
        
        // Social proof
        const socialSelectors = [
            '[class*="testimonial"]', '[class*="depoimento"]', '[class*="review"]',
            '[class*="avaliacao"]', '[class*="rating"]', '[class*="stars"]',
            '[class*="cliente"]', '[class*="logo-cliente"]', '[class*="partner"]'
        ];
        data.social_proof = [];
        socialSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                data.social_proof.push({selector: sel, text: el.innerText.trim()[:300]});
            });
        });
        
        // FAQ
        const faqItems = document.querySelectorAll('[class*="faq"], [class*="pergunta"], details, [itemscope][itemtype*="FAQPage"]');
        data.faq_count = faqItems.length;
        
        // CTA buttons
        const buttons = document.querySelectorAll('button, a[href], input[type="submit"], input[type="button"]');
        data.ctas = Array.from(buttons)
            .filter(b => b.offsetWidth > 0 && b.offsetHeight > 0)
            .map(b => ({
                tag: b.tagName.toLowerCase(),
                text: b.innerText?.trim() || b.value || '',
                href: b.href || '',
                classes: b.className,
                visible: b.offsetParent !== null,
                rect: b.getBoundingClientRect()
            }))
            .filter(c => c.text.length > 0 && c.text.length < 100);
        
        // Above fold detection
        const fold = window.innerHeight;
        data.above_fold_ctas = data.ctas.filter(c => c.rect && c.rect.top < fold).length;
        
        return data;
    }""")

def extract_mobile_usability(page: Page) -> Dict[str, Any]:
    """Verifica usabilidade mobile."""
    return page.evaluate("""() => {
        const issues = [];
        const viewport = window.innerWidth;
        
        // Touch targets
        const clickables = document.querySelectorAll('a, button, input, select, textarea, [role="button"], [tabindex]');
        let small_targets = 0;
        clickables.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.width < 48 || rect.height < 48) small_targets++;
        });
        if (small_targets > 0) issues.push({type: 'touch_target', count: small_targets, message: `${small_targets} elementos < 48x48px`});
        
        // Font size
        const texts = document.querySelectorAll('p, span, div, li, a, button, label, h1, h2, h3, h4, h5, h6');
        let small_fonts = 0;
        texts.forEach(el => {
            const style = getComputedStyle(el);
            const fs = parseFloat(style.fontSize);
            if (fs < 16 && el.innerText.trim().length > 0) small_fonts++;
        });
        if (small_fonts > 0) issues.push({type: 'font_size', count: small_fonts, message: `${small_fonts} elementos com font-size < 16px`});
        
        // Horizontal scroll
        if (document.body.scrollWidth > viewport) {
            issues.push({type: 'horizontal_scroll', message: `Body width (${document.body.scrollWidth}) > viewport (${viewport})`});
        }
        
        // Viewport meta
        const vp = document.querySelector('meta[name="viewport"]');
        if (!vp || !vp.content.includes('width=device-width')) {
            issues.push({type: 'viewport', message: 'Viewport meta tag ausente ou incorreta'});
        }
        
        // Input types
        const inputs = document.querySelectorAll('input');
        let wrong_types = 0;
        inputs.forEach(inp => {
            if (inp.type === 'text' && (inp.name?.includes('email') || inp.id?.includes('email'))) wrong_types++;
            if (inp.type === 'text' && (inp.name?.includes('tel') || inp.name?.includes('phone') || inp.id?.includes('tel'))) wrong_types++;
        });
        if (wrong_types > 0) issues.push({type: 'input_type', count: wrong_types, message: `${wrong_types} inputs deveriam usar type=email/tel`});
        
        return {viewport_width: viewport, issues: issues, issue_count: issues.length};
    }""")
```

### 6. Screenshot & Reporting Helpers

```python
# reporting.py
from playwright.sync_api import Page
from typing import Dict, Any, List
import os
import json
from datetime import datetime
from pathlib import Path

AUDIT_BASE_DIR = Path.home() / "Documents" / "PROJETOS" / "audits"

def ensure_audit_dir(slug: str) -> Path:
    """Cria diretório de auditoria para o slug."""
    audit_dir = AUDIT_BASE_DIR / slug
    audit_dir.mkdir(parents=True, exist_ok=True)
    return audit_dir

def take_screenshot(page: Page, audit_dir: Path, name: str, full_page: bool = True) -> str:
    """Captura screenshot e retorna caminho relativo."""
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{timestamp}_{name}.png"
    filepath = audit_dir / filename
    page.screenshot(path=str(filepath), full_page=full_page)
    return filename

def take_viewport_screenshots(page: Page, audit_dir: Path, prefix: str = "") -> List[str]:
    """Captura screenshots em múltiplos viewports."""
    from .devices import DEVICES
    screenshots = []
    original_viewport = page.viewport_size
    
    for device_name, device in DEVICES.items():
        if device.get("is_mobile") or device_name in ["desktop", "desktop_large"]:
            page.set_viewport_size(device["viewport"])
            page.wait_for_timeout(500)
            filename = take_screenshot(page, audit_dir, f"{prefix}{device_name}")
            screenshots.append(filename)
    
    if original_viewport:
        page.set_viewport_size(original_viewport)
    
    return screenshots

def generate_json_report(data: Dict[str, Any], audit_dir: Path, slug: str) -> str:
    """Gera relatório JSON."""
    filename = f"{slug}_report.json"
    filepath = audit_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return filename

def generate_markdown_report(data: Dict[str, Any], audit_dir: Path, slug: str, screenshots: List[str]) -> str:
    """Gera relatório Markdown legível."""
    filename = f"{slug}_report.md"
    filepath = audit_dir / filename
    
    mode = data.get("mode", "UNKNOWN")
    status = data.get("status", "UNKNOWN")
    score = data.get("score", {}).get("overall", 0)
    
    status_icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
    
    md = f"""# Browser Test Report — {data.get('url', 'N/A')}

**Mode:** {mode} | **Status:** {status_icon} {status} | **Score:** {score}/100
**Date:** {data.get('timestamp', datetime.now().isoformat())} | **Duration:** {data.get('duration_ms', 0)/1000:.1f}s

## Resumo Executivo
{data.get('summary', 'Relatório gerado automaticamente pelo browser-tester.')}

## Scores por Categoria
| Categoria | Score | Status |
|-----------|-------|--------|
"""
    
    for cat, cat_score in data.get("score", {}).items():
        if cat != "overall":
            cat_status = "✅" if cat_score >= 80 else "⚠️" if cat_score >= 60 else "❌"
            md += f"| {cat.upper()} | {cat_score} | {cat_status} |\n"
    
    md += "\n## Problemas Críticos (P0)\n"
    critical = data.get("critical_issues", [])
    if critical:
        for issue in critical:
            md += f"- **{issue.get('type', 'Geral')}**: {issue.get('message', '')}\n"
    else:
        md += "*Nenhum*\n"
    
    md += "\n## Avisos (P1/P2)\n"
    warnings = data.get("warnings", [])
    if warnings:
        md += "| Prioridade | Categoria | Problema | Evidência |\n|------------|-----------|----------|-----------|\n"
        for w in warnings:
            evidence = f"![screenshot]({w.get('evidence', '')})" if w.get('evidence') else ""
            md += f"| {w.get('priority', 'P2')} | {w.get('type', 'geral')} | {w.get('message', '')} | {evidence} |\n"
    else:
        md += "*Nenhum*\n"
    
    md += "\n## Screenshots\n"
    for i, shot in enumerate(screenshots):
        md += f"### Screenshot {i+1}\n![{shot}]({shot})\n\n"
    
    md += "## Métricas Core Web Vitals\n"
    md += "| Métrica | Valor | Alvo | Status |\n|---------|-------|------|--------|\n"
    metrics = data.get("metrics", {})
    targets = {"lcp": 2500, "fid": 100, "cls": 0.1, "ttfb": 600}
    for metric, value in metrics.items():
        if metric in targets:
            target = targets[metric]
            unit = "ms" if metric != "cls" else ""
            status = "✅" if (metric != "cls" and value <= target) or (metric == "cls" and value <= target) else "⚠️"
            md += f"| {metric.upper()} | {value}{unit} | < {target}{unit} | {status} |\n"
    
    md += "\n## Próximos Passos Recomendados\n"
    for i, step in enumerate(data.get("next_steps", []), 1):
        md += f"{i}. {step}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md)
    
    return filename
```

### 7. Main Test Runner (Orquestrador)

```python
# runner.py
from playwright.sync_api import sync_playwright
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from .browser_manager import BrowserManager
from .devices import get_device
from .navigation import goto_with_retry, scroll_page
from .interactions import find_cta_candidates, get_element_info, safe_click, safe_fill
from .extraction import (
    extract_seo_data, extract_performance_metrics, 
    extract_console_logs, extract_network_failures,
    extract_cro_elements, extract_mobile_usability
)
from .reporting import ensure_audit_dir, take_viewport_screenshots, generate_json_report, generate_markdown_report

class BrowserTestRunner:
    def __init__(self, url: str, mode: str = "SMOKE", slug: str = None, headed: bool = False):
        self.url = url
        self.mode = mode.upper()
        self.slug = slug or self._generate_slug(url)
        self.headed = headed
        self.audit_dir = ensure_audit_dir(self.slug)
        self.start_time = time.time()
        self.console_logs = []
        self.network_failures = []
        self.screenshots = []
        
    def _generate_slug(self, url: str) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace(".", "-").replace(":", "-")
    
    def _setup_page_listeners(self, page):
        page.on("console", lambda msg: self.console_logs.append({
            "type": msg.type, "text": msg.text, "location": msg.location
        }))
        page.on("pageerror", lambda err: self.console_logs.append({
            "type": "error", "text": str(err), "location": {"url": page.url}
        }))
        page.on("response", lambda resp: self.network_failures.append({
            "url": resp.url, "status": resp.status, "resource_type": resp.request.resource_type
        }) if resp.status >= 400 else None)

    def run_smoke(self, page) -> Dict[str, Any]:
        result = goto_with_retry(page, self.url)
        if not result["success"]:
            return {"status": "FAIL", "error": result["error"]}
        
        checks = {
            "http_status": result["status"] == 200,
            "has_title": bool(page.title()),
            "has_h1": page.locator("h1").count() > 0,
            "cta_above_fold": False,
            "console_errors": len([l for l in self.console_logs if l["type"] == "error"]) == 0,
            "network_critical_failures": len([f for f in self.network_failures if f["status"] >= 500]) == 0,
        }
        
        # Check CTA above fold
        ctas = find_cta_candidates(page)
        checks["cta_above_fold"] = len(ctas) > 0
        
        return {
            "checks": checks,
            "ctas_found": len(ctas),
            "load_time_ms": result["load_time_ms"],
            "title": page.title(),
        }

    def run_cro_validation(self, page) -> Dict[str, Any]:
        scroll_page(page)
        cro_data = extract_cro_elements(page)
        seo_data = extract_seo_data(page)
        perf_data = extract_performance_metrics(page)
        mobile_data = extract_mobile_usability(page)
        
        # Scoring logic
        score = 100
        warnings = []
        critical = []
        
        # CTA checks
        ctas = cro_data.get("ctas", [])
        above_fold = cro_data.get("above_fold_ctas", 0)
        if above_fold == 0:
            critical.append({"type": "cta", "message": "Nenhum CTA visível above-fold"})
            score -= 30
        elif above_fold == 1:
            warnings.append({"priority": "P2", "type": "cta", "message": "Apenas 1 CTA above-fold", "evidence": None})
            score -= 5
        
        # Form checks
        forms = cro_data.get("forms", [])
        for form in forms:
            if form["field_count"] > 5:
                warnings.append({"priority": "P1", "type": "form", "message": f"Formulário com {form['field_count']} campos (recomendado ≤5)", "evidence": None})
                score -= 10
            if form["field_count"] == 0:
                critical.append({"type": "form", "message": "Formulário sem campos"})
                score -= 20
        
        # Trust signals
        if len(cro_data.get("trust_signals", [])) == 0:
            warnings.append({"priority": "P2", "type": "trust", "message": "Nenhum sinal de confiança detectado", "evidence": None})
            score -= 10
        
        # Social proof
        if len(cro_data.get("social_proof", [])) == 0:
            warnings.append({"priority": "P2", "type": "social_proof", "message": "Nenhuma prova social detectada", "evidence": None})
            score -= 10
        
        # Performance
        lcp = perf_data.get("lcp")
        if lcp and lcp > 2500:
            warnings.append({"priority": "P1", "type": "performance", "message": f"LCP {lcp:.0f}ms > 2500ms", "evidence": None})
            score -= 15
        
        # Mobile
        if mobile_data.get("issue_count", 0) > 0:
            for issue in mobile_data["issues"]:
                warnings.append({"priority": "P1" if issue["type"] in ["touch_target", "viewport"] else "P2", 
                               "type": "mobile", "message": issue["message"], "evidence": None})
            score -= min(20, mobile_data["issue_count"] * 5)
        
        # SEO basics
        if seo_data.get("h1_count", 0) != 1:
            warnings.append({"priority": "P1", "type": "seo", "message": f"H1 count: {seo_data.get('h1_count', 0)} (deve ser 1)", "evidence": None})
            score -= 10
        if not seo_data.get("meta_description"):
            warnings.append({"priority": "P1", "type": "seo", "message": "Meta description ausente", "evidence": None})
            score -= 10
        
        return {
            "score": max(0, score),
            "cro_data": cro_data,
            "seo_data": seo_data,
            "perf_data": perf_data,
            "mobile_data": mobile_data,
            "warnings": warnings,
            "critical": critical,
        }

    def run_seo_technical(self, page) -> Dict[str, Any]:
        seo_data = extract_seo_data(page)
        perf_data = extract_performance_metrics(page)
        
        warnings = []
        critical = []
        score = 100
        
        # Title
        title_len = seo_data.get("title_length", 0)
        if title_len == 0:
            critical.append({"type": "title", "message": "Title tag ausente"})
            score -= 30
        elif title_len > 60:
            warnings.append({"priority": "P1", "type": "title", "message": f"Title com {title_len} chars (pode truncar no Google)", "evidence": None})
            score -= 5
        
        # Meta description
        desc_len = seo_data.get("meta_description_length", 0)
        if desc_len == 0:
            critical.append({"type": "meta_description", "message": "Meta description ausente"})
            score -= 20
        elif desc_len > 160:
            warnings.append({"priority": "P2", "type": "meta_description", "message": f"Meta description com {desc_len} chars (pode truncar)", "evidence": None})
            score -= 3
        
        # H1
        if seo_data.get("h1_count", 0) != 1:
            critical.append({"type": "h1", "message": f"H1 count: {seo_data.get('h1_count', 0)}"})
            score -= 20
        
        # Headings hierarchy
        headings = seo_data.get("headings", [])
        levels = [h["level"] for h in headings]
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                warnings.append({"priority": "P2", "type": "headings", "message": f"Skip heading level: H{levels[i-1]} → H{levels[i]}", "evidence": None})
                score -= 3
        
        # Structured data
        if not seo_data.get("structured_data"):
            warnings.append({"priority": "P2", "type": "schema", "message": "Nenhum dado estruturado (JSON-LD) encontrado", "evidence": None})
            score -= 10
        else:
            for sd in seo_data["structured_data"]:
                if "error" in sd:
                    warnings.append({"priority": "P1", "type": "schema", "message": f"JSON-LD inválido: {sd['error']}", "evidence": None})
                    score -= 5
        
        # Images alt
        if seo_data.get("images_without_alt", 0) > 0:
            warnings.append({"priority": "P1", "type": "images", "message": f"{seo_data['images_without_alt']} imagens sem alt text", "evidence": None})
            score -= min(15, seo_data["images_without_alt"] * 2)
        
        # Canonical
        if not seo_data.get("canonical"):
            warnings.append({"priority": "P2", "type": "canonical", "message": "Canonical tag ausente", "evidence": None})
            score -= 5
        
        # Viewport
        if "width=device-width" not in seo_data.get("viewport", ""):
            critical.append({"type": "viewport", "message": "Viewport meta tag ausente ou incorreta"})
            score -= 15
        
        return {
            "score": max(0, score),
            "seo_data": seo_data,
            "perf_data": perf_data,
            "warnings": warnings,
            "critical": critical,
        }

    def run_mobile_first(self, page) -> Dict[str, Any]:
        from .devices import DEVICES
        mobile_results = {}
        all_issues = []
        score = 100
        
        for device_name in ["mobile_iphone_se", "mobile_iphone_12", "mobile_android", "tablet_ipad"]:
            device = get_device(device_name)
            page.set_viewport_size(device["viewport"])
            page.wait_for_timeout(500)
            
            mobile_data = extract_mobile_usability(page)
            mobile_results[device_name] = mobile_data
            all_issues.extend(mobile_data.get("issues", []))
            score -= min(20, mobile_data.get("issue_count", 0) * 5)
            
            # Screenshot
            shot = take_screenshot(page, self.audit_dir, f"{device_name}")
            self.screenshots.append(shot)
        
        # Reset to desktop
        page.set_viewport_size({"width": 1280, "height": 720})
        
        # Deduplicate issues
        unique_issues = []
        seen = set()
        for issue in all_issues:
            key = (issue["type"], issue["message"])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return {
            "score": max(0, score),
            "device_results": mobile_results,
            "issues": unique_issues,
            "issue_count": len(unique_issues),
        }

    def run_full_e2e(self, page) -> Dict[str, Any]:
        # 1. Homepage
        result = goto_with_retry(page, self.url)
        if not result["success"]:
            return {"status": "FAIL", "error": result["error"]}
        
        scroll_page(page)
        
        # 2. Find and click CTA
        ctas = find_cta_candidates(page)
        cta_clicked = False
        form_result = None
        
        for cta in ctas[:3]:  # Try top 3 CTAs
            click_result = safe_click(page, cta.get("selector_used", ""))
            if click_result["success"]:
                cta_clicked = True
                page.wait_for_timeout(2000)
                
                # Check if form appeared
                forms = page.locator("form").all()
                if forms:
                    form_result = self._test_form(page, forms[0])
                break
        
        # 3. Check thank you / success
        thank_you = page.locator("text=/obrigado|sucesso|confirmado|enviado|agrade/i").count() > 0
        
        return {
            "homepage_load": result,
            "cta_clicked": cta_clicked,
            "cta_used": ctas[0] if ctas else None,
            "form_test": form_result,
            "thank_you_page": thank_you,
            "final_url": page.url,
        }

    def _test_form(self, page, form) -> Dict[str, Any]:
        fields = form.locator("input, select, textarea").all()
        filled = 0
        for field in fields[:5]:  # Max 5 fields
            field_type = field.get_attribute("type") or "text"
            name = field.get_attribute("name") or ""
            
            test_value = ""
            if field_type == "email" or "email" in name:
                test_value = "teste@exemplo.com"
            elif field_type == "tel" or "phone" in name or "tel" in name:
                test_value = "11999999999"
            elif field_type == "text" and "nome" in name:
                test_value = "João Silva"
            elif field_type == "text":
                test_value = "Teste"
            elif field.tag_name == "textarea":
                test_value = "Mensagem de teste"
            
            if test_value:
                field.fill(test_value)
                filled += 1
        
        # Submit
        submit = form.locator('button[type="submit"], input[type="submit"]').first
        if submit.count() > 0:
            submit.click()
            page.wait_for_timeout(3000)
        
        return {"fields_filled": filled, "submitted": submit.count() > 0}

    def run(self) -> Dict[str, Any]:
        with BrowserManager(headed=self.headed) as bm:
            with bm.new_context() as ctx:
                with bm.new_page(ctx) as page:
                    self._setup_page_listeners(page)
                    
                    # Desktop screenshots
                    self.screenshots.extend(take_viewport_screenshots(page, self.audit_dir, "desktop_"))
                    
                    # Run mode-specific test
                    if self.mode == "SMOKE":
                        mode_result = self.run_smoke(page)
                    elif self.mode == "CRO_VALIDATION":
                        mode_result = self.run_cro_validation(page)
                    elif self.mode == "SEO_TECHNICAL":
                        mode_result = self.run_seo_technical(page)
                    elif self.mode == "MOBILE_FIRST":
                        mode_result = self.run_mobile_first(page)
                    elif self.mode == "FULL_E2E":
                        mode_result = self.run_full_e2e(page)
                    else:
                        mode_result = {"error": f"Modo desconhecido: {self.mode}"}
                    
                    # Mobile screenshots for non-mobile modes
                    if self.mode != "MOBILE_FIRST":
                        page.set_viewport_size({"width": 390, "height": 844})
                        page.wait_for_timeout(500)
                        self.screenshots.extend(take_viewport_screenshots(page, self.audit_dir, "mobile_"))
                        page.set_viewport_size({"width": 1280, "height": 720})
        
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        # Consolidate results
        status = "PASS"
        if mode_result.get("critical"):
            status = "FAIL"
        elif mode_result.get("warnings"):
            status = "WARN"
        
        score = mode_result.get("score", 0)
        if "score" not in mode_result:
            # Calculate from checks for smoke
            checks = mode_result.get("checks", {})
            if checks:
                score = int((sum(checks.values()) / len(checks)) * 100)
        
        report = {
            "url": self.url,
            "mode": self.mode,
            "slug": self.slug,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "viewport": {"desktop": "1280x720", "mobile": "390x844"},
            "score": {
                "overall": score,
                "cro": mode_result.get("cro_data", {}).get("score", 0) if "cro_data" in mode_result else score,
                "seo": mode_result.get("seo_data", {}).get("score", 0) if "seo_data" in mode_result else score,
                "performance": 100 - len([w for w in mode_result.get("warnings", []) if w.get("type") == "performance"]) * 10,
                "mobile": 100 - mode_result.get("issue_count", 0) * 5,
            },
            "status": status,
            "critical_issues": mode_result.get("critical", []),
            "warnings": mode_result.get("warnings", []),
            "checks": mode_result.get("checks", {}),
            "screenshots": self.screenshots,
            "console_errors": [l for l in self.console_logs if l["type"] == "error"],
            "console_warnings": [l for l in self.console_logs if l["type"] == "warning"],
            "network_failures": self.network_failures,
            "metrics": mode_result.get("perf_data", {}),
            "next_steps": self._generate_next_steps(mode_result),
            "summary": self._generate_summary(mode_result, status, score),
        }
        
        # Save reports
        generate_json_report(report, self.audit_dir, self.slug)
        generate_markdown_report(report, self.audit_dir, self.slug, self.screenshots)
        
        return report

    def _generate_summary(self, mode_result: Dict, status: str, score: int) -> str:
        if status == "FAIL":
            return f"Teste {self.mode} FALHOU. {len(mode_result.get('critical', []))} problemas críticos encontrados. Score: {score}/100"
        elif status == "WARN":
            return f"Teste {self.mode} passou com avisos. {len(mode_result.get('warnings', []))} pontos de atenção. Score: {score}/100"
        return f"Teste {self.mode} APROVADO. Score: {score}/100"

    def _generate_next_steps(self, mode_result: Dict) -> List[str]:
        steps = []
        for issue in mode_result.get("critical", []):
            steps.append(f"[P0] Corrigir: {issue['message']}")
        for warning in mode_result.get("warnings", []):
            priority = warning.get("priority", "P2")
            steps.append(f"[{priority}] {warning['message']}")
        if not steps:
            steps.append("Nenhuma ação corretiva necessária no momento")
        return steps


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Browser Test Runner")
    parser.add_argument("url", help="URL to test")
    parser.add_argument("--mode", default="SMOKE", choices=["SMOKE", "FULL_E2E", "CRO_VALIDATION", "SEO_TECHNICAL", "MOBILE_FIRST"])
    parser.add_argument("--slug", help="Custom slug for report directory")
    parser.add_argument("--headed", action="store_true", help="Run headed (visible browser)")
    args = parser.parse_args()
    
    runner = BrowserTestRunner(args.url, args.mode, args.slug, args.headed)
    result = runner.run()
    
    print(f"\n{'='*60}")
    print(f"BROWSER TEST COMPLETE")
    print(f"{'='*60}")
    print(f"URL: {result['url']}")
    print(f"Mode: {result['mode']}")
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']['overall']}/100")
    print(f"Duration: {result['duration_ms']/1000:.1f}s")
    print(f"Report: {runner.audit_dir / f'{runner.slug}_report.md'}")
    print(f"{'='*60}\n")
    
    if result["status"] == "FAIL":
        sys.exit(1)