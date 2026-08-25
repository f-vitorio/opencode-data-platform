"""Data Extraction Helpers - SEO, Performance, CRO, Mobile usability extraction."""
from playwright.sync_api import Page
from typing import Dict, Any, List


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
        data.canonical = canonical ? canonical.href : null;
        
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
        const h1 = data.headings.find(h => h.level === 1);
        data.h1_text = h1 ? h1.text : '';
        
        // Structured Data (JSON-LD)
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        data.structured_data = [];
        scripts.forEach(s => {
            try {
                data.structured_data.push(JSON.parse(s.textContent));
            } catch (e) {
                data.structured_data.push({error: "Invalid JSON", content: s.textContent.slice(0, 200)});
            }
        });
        
        // Open Graph
        data.og = {};
        ['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:site_name'].forEach(prop => {
            const el = document.querySelector('meta[property="' + prop + '"]');
            if (el) data.og[prop] = el.getAttribute('content');
        });
        
        // Twitter Cards
        data.twitter = {};
        ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'].forEach(name => {
            const el = document.querySelector('meta[name="' + name + '"]');
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
        data.viewport = viewport ? viewport.getAttribute('content') : 'não definido';
        
        // Favicon
        const favicon = document.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
        data.favicon = favicon ? favicon.href : null;
        
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
            fp: null,
            fcp: null,
        };
        
        // Paint Timing - find manually to avoid optional chaining
        for (let i = 0; i < paint.length; i++) {
            if (paint[i].name === 'first-paint') metrics.fp = paint[i].startTime;
            if (paint[i].name === 'first-contentful-paint') metrics.fcp = paint[i].startTime;
        }
        
        // Resources
        metrics.resource_count = resources.length;
        metrics.total_transfer_size = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
        metrics.total_encoded_size = resources.reduce((sum, r) => sum + (r.encodedBodySize || 0), 0);
        metrics.slow_resources = resources.filter(r => r.duration > 1000).map(r => ({
            name: r.name,
            duration: r.duration,
            size: r.transferSize,
            type: r.initiatorType
        })).slice(0, 10);
        
        // LCP
        try {
            const lcpEntries = perf.getEntriesByType('largest-contentful-paint');
            if (lcpEntries.length > 0) {
                metrics.lcp = lcpEntries[lcpEntries.length - 1].startTime;
            }
        } catch (e) {}
        
        // CLS
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
                label: (f.labels && f.labels[0]) ? f.labels[0].innerText : ''
            })),
            field_count: form.querySelectorAll('input, select, textarea').length,
            submit_button: form.querySelector('button[type="submit"], input[type="submit"]') ? form.querySelector('button[type="submit"], input[type="submit"]').innerText : ''
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
                data.trust_signals.push({selector: sel, text: el.innerText.trim().slice(0, 200), html: el.outerHTML.slice(0, 500)});
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
                data.social_proof.push({selector: sel, text: el.innerText.trim().slice(0, 300)});
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
                text: (b.innerText || b.value || '').trim(),
                href: b.href || '',
                classes: b.className,
                visible: b.offsetParent !== null,
                rect: b.getBoundingClientRect ? {
                    top: b.getBoundingClientRect().top,
                    left: b.getBoundingClientRect().left,
                    width: b.getBoundingClientRect().width,
                    height: b.getBoundingClientRect().height
                } : null
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
        if (small_targets > 0) issues.push({type: 'touch_target', count: small_targets, message: small_targets + ' elementos < 48x48px'});
        
        // Font size
        const texts = document.querySelectorAll('p, span, div, li, a, button, label, h1, h2, h3, h4, h5, h6');
        let small_fonts = 0;
        texts.forEach(el => {
            const style = getComputedStyle(el);
            const fs = parseFloat(style.fontSize);
            if (fs < 16 && el.innerText.trim().length > 0) small_fonts++;
        });
        if (small_fonts > 0) issues.push({type: 'font_size', count: small_fonts, message: small_fonts + ' elementos com font-size < 16px'});
        
        // Horizontal scroll
        if (document.body.scrollWidth > viewport) {
            issues.push({type: 'horizontal_scroll', message: 'Body width (' + document.body.scrollWidth + ') > viewport (' + viewport + ')'});
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
            if (inp.type === 'text' && (inp.name && inp.name.includes('email') || inp.id && inp.id.includes('email'))) wrong_types++;
            if (inp.type === 'text' && (inp.name && inp.name.includes('tel') || inp.name && inp.name.includes('phone') || inp.id && inp.id.includes('tel'))) wrong_types++;
        });
        if (wrong_types > 0) issues.push({type: 'input_type', count: wrong_types, message: wrong_types + ' inputs deveriam usar type=email/tel'});
        
        return {viewport_width: viewport, issues: issues, issue_count: issues.length};
    }""")