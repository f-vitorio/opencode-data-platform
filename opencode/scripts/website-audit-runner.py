#!/usr/bin/env python3
"""
Website Audit Runner - Auditoria profunda via browser real
Usa playwright-automation + axe-core + PerformanceObserver + Security checks
"""

import sys
import os
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

# Adicionar skills ao path
skills_path = Path(__file__).parent.parent / "skills" / "playwright-automation"
sys.path.insert(0, str(skills_path))

try:
    from playwright_automation import BrowserTestRunner, BrowserManager
    from playwright_automation.devices import get_device
    from playwright_automation.navigation import goto_with_retry, scroll_page
    from playwright_automation.interactions import find_cta_candidates
    from playwright_automation.extraction import (
        extract_seo_data, extract_performance_metrics,
        extract_cro_elements, extract_mobile_usability
    )
    from playwright_automation.reporting import ensure_audit_dir, take_screenshot, take_viewport_screenshots, generate_json_report, generate_markdown_report
except ImportError as e:
    print(f"Erro ao importar skill: {e}")
    sys.exit(1)


class WebsiteAuditRunner:
    """Runner para auditoria profunda de websites."""
    
    MODES = {
        "COMPLETA": "Auditoria 360° (SEO + CRO + A11y + Perf + Sec + Mobile)",
        "SEO_DEEP": "SEO técnico runtime (meta, schema, CWV, canonical, redirects)",
        "CRO_DEEP": "Conversão + UX (CTA, forms, trust, social proof, funil)",
        "ACESSIBILIDADE": "WCAG 2.1 AA via axe-core",
        "PERFORMANCE": "Core Web Vitals reais + waterfall + otimizações",
        "SEGURANCA": "Headers, CSP, cookies, mixed content, certificado",
        "MOBILE_DEEP": "PWA + touch targets + viewport + forms mobile",
    }
    
    def __init__(self, url: str, mode: str = "COMPLETA", slug: str = None, headed: bool = False):
        self.url = url
        self.mode = mode.upper()
        self.slug = slug or self._generate_slug(url)
        self.headed = headed
        self.audit_dir = ensure_audit_dir(self.slug)
        self.start_time = time.time()
        self.console_logs = []
        self.network_failures = []
        self.screenshots = []
        self.axe_results = None
        
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
            "url": resp.url, "status": resp.status, "resource_type": resp.request.resource_type,
            "headers": dict(resp.headers)
        }) if resp.status >= 400 else None)
    
    def _inject_axe_core(self, page):
        """Injeta axe-core para testes de acessibilidade."""
        axe_script = """
        (async () => {
            if (window.axe) return window.axe;
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.8.2/axe.min.js';
            script.onload = () => console.log('axe-core loaded');
            document.head.appendChild(script);
            await new Promise(r => script.onload = r);
            return window.axe;
        })();
        """
        page.evaluate(axe_script)
        page.wait_for_timeout(2000)
    
    def _run_axe_audit(self, page):
        """Executa auditoria axe-core."""
        try:
            results = page.evaluate("""() => {
                return new Promise((resolve) => {
                    if (!window.axe) {
                        resolve({error: "axe-core not loaded"});
                        return;
                    }
                    axe.run(document, {
                        runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']},
                        resultTypes: ['violations', 'passes', 'incomplete', 'inapplicable']
                    }, (err, results) => {
                        if (err) resolve({error: err.message});
                        else resolve(results);
                    });
                });
            }""")
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def _collect_cwv_metrics(self, page):
        """Coleta Core Web Vitals reais via PerformanceObserver."""
        return page.evaluate("""() => {
            return new Promise((resolve) => {
                const metrics = {};
                let resolved = false;
                
                function tryResolve() {
                    if (!resolved && metrics.lcp && metrics.fid && metrics.cls !== undefined) {
                        resolved = true;
                        resolve(metrics);
                    }
                }
                
                // LCP
                try {
                    const lcpObserver = new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        const last = entries[entries.length - 1];
                        metrics.lcp = last.startTime;
                        tryResolve();
                    });
                    lcpObserver.observe({type: 'largest-contentful-paint', buffered: true});
                } catch (e) {}
                
                // FID
                try {
                    const fidObserver = new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        entries.forEach(entry => {
                            metrics.fid = entry.processingStart - entry.startTime;
                        });
                        tryResolve();
                    });
                    fidObserver.observe({type: 'first-input', buffered: true});
                } catch (e) {}
                
                // CLS
                try {
                    let cls = 0;
                    const clsObserver = new PerformanceObserver((list) => {
                        list.getEntries().forEach(entry => {
                            if (!entry.hadRecentInput) cls += entry.value;
                        });
                        metrics.cls = cls;
                        tryResolve();
                    });
                    clsObserver.observe({type: 'layout-shift', buffered: true});
                } catch (e) {}
                
                // FCP, TTFB from navigation
                try {
                    const nav = performance.getEntriesByType('navigation')[0];
                    if (nav) {
                        metrics.ttfb = nav.responseStart - nav.requestStart;
                        metrics.fcp = performance.getEntriesByType('paint')
                            .find(p => p.name === 'first-contentful-paint')?.startTime || null;
                    }
                } catch (e) {}
                
                // Timeout fallback
                setTimeout(() => {
                    if (!resolved) {
                        resolved = true;
                        resolve(metrics);
                    }
                }, 10000);
            });
        }""")
    
    def _analyze_security_headers(self, page):
        """Analisa headers de segurança."""
        # Pegar headers da resposta principal
        main_response = None
        for failure in self.network_failures:
            if failure["url"] == self.url or failure["url"] == page.url:
                main_response = failure
                break
        
        # Se não achou nas falhas, tentar pegar da navegação
        headers = {}
        try:
            headers = page.evaluate("""() => {
                // Não temos acesso direto aos headers da resposta principal via JS
                // Retornamos o que conseguimos inferir
                return {
                    hsts: document.querySelector('meta[http-equiv="Strict-Transport-Security"]')?.content || 'header',
                    csp: document.querySelector('meta[http-equiv="Content-Security-Policy"]')?.content || 'header',
                    xframe: document.querySelector('meta[http-equiv="X-Frame-Options"]')?.content || 'header',
                };
            }""")
        except:
            pass
        
        return {
            "headers_found_in_html": headers,
            "note": "Headers completos precisam de resposta HTTP real. Use curl ou devtools network tab."
        }
    
    def _check_mixed_content(self, page):
        """Verifica mixed content (HTTP em página HTTPS)."""
        return page.evaluate("""() => {
            const issues = [];
            if (location.protocol !== 'https:') return {mixed_content: false, reason: 'Not HTTPS'};
            
            // Scripts
            document.querySelectorAll('script[src^="http://"]').forEach(s => 
                issues.push({type: 'script', src: s.src, element: s.outerHTML.slice(0, 200)}));
            
            // Styles
            document.querySelectorAll('link[href^="http://"]').forEach(l => 
                issues.push({type: 'stylesheet', href: l.href}));
            
            // Images
            document.querySelectorAll('img[src^="http://"]').forEach(img => 
                issues.push({type: 'image', src: img.src}));
            
            // Iframes
            document.querySelectorAll('iframe[src^="http://"]').forEach(f => 
                issues.push({type: 'iframe', src: f.src}));
            
            // Forms
            document.querySelectorAll('form[action^="http://"]').forEach(f => 
                issues.push({type: 'form', action: f.action}));
            
            return {mixed_content: issues.length > 0, count: issues.length, issues: issues};
        }""")
    
    def _analyze_pwa(self, page):
        """Analisa PWA readiness."""
        return page.evaluate("""() => {
            const data = {manifest: null, sw: false, sw_details: {}};
            
            // Manifest
            const manifestLink = document.querySelector('link[rel="manifest"]');
            if (manifestLink) {
                fetch(manifestLink.href).then(r => r.json()).then(m => {
                    data.manifest = {
                        name: m.name,
                        short_name: m.short_name,
                        start_url: m.start_url,
                        display: m.display,
                        theme_color: m.theme_color,
                        background_color: m.background_color,
                        icons: m.icons?.map(i => ({src: i.src, sizes: i.sizes, type: i.type, purpose: i.purpose})) || []
                    };
                }).catch(() => {});
            }
            
            // Service Worker
            if ('serviceWorker' in navigator) {
                data.sw = true;
                navigator.serviceWorker.getRegistration().then(reg => {
                    if (reg) {
                        data.sw_details = {
                            scope: reg.scope,
                            update_via_cache: reg.updateViaCache,
                            active: !!reg.active,
                            installing: !!reg.installing,
                            waiting: !!reg.waiting
                        };
                    }
                });
            }
            
            // Theme color
            const themeColor = document.querySelector('meta[name="theme-color"]');
            if (themeColor) data.theme_color = themeColor.content;
            
            // Apple touch icons
            data.apple_touch_icon = document.querySelector('link[rel="apple-touch-icon"]')?.href || null;
            
            return data;
        }""")
    
    def _analyze_cookies(self, page):
        """Analisa cookies de segurança."""
        return page.evaluate("""() => {
            try {
                const cookies = document.cookie.split(';').map(c => c.trim());
                const analysis = {
                    total: cookies.length,
                    secure: 0,
                    httponly: 0,
                    samesite_lax: 0,
                    samesite_strict: 0,
                    samesite_none: 0,
                    host_prefix: 0,
                    issues: []
                };
                
                cookies.forEach(cookie => {
                    const parts = cookie.split(';');
                    const nameValue = parts[0].trim();
                    const attrs = parts.slice(1).map(a => a.trim().toLowerCase());
                    
                    if (attrs.includes('secure')) analysis.secure++;
                    if (attrs.includes('httponly')) analysis.httponly++;
                    if (attrs.some(a => a.startsWith('samesite='))) {
                        const ss = attrs.find(a => a.startsWith('samesite=')).split('=')[1];
                        if (ss === 'lax') analysis.samesite_lax++;
                        else if (ss === 'strict') analysis.samesite_strict++;
                        else if (ss === 'none') analysis.samesite_none++;
                    } else {
                        analysis.issues.push({cookie: nameValue, issue: 'No SameSite attribute'});
                    }
                    if (nameValue.startsWith('__Host-') || nameValue.startsWith('__Secure-')) analysis.host_prefix++;
                });
                
                return analysis;
            } catch (e) {
                return {error: "Cannot access cookies: " + e.message, total: 0};
            }
        }""")
    
    def run_seo_deep(self, page):
        """SEO técnico profundo."""
        scroll_page(page)
        seo_data = extract_seo_data(page)
        perf_data = extract_performance_metrics(page)
        cwv = self._collect_cwv_metrics(page)
        
        warnings = []
        critical = []
        score = 100
        
        # Title
        title_len = seo_data.get("title_length", 0)
        if title_len == 0:
            critical.append({"id": "seo-001", "category": "SEO", "severity": "P0", "title": "Title tag ausente", "fix": "Adicionar <title> único 30-60 chars com keyword principal"})
            score -= 25
        elif title_len > 60:
            warnings.append({"id": "seo-002", "priority": "P1", "category": "SEO", "title": f"Title com {title_len} chars (pode truncar no Google)", "fix": "Reduzir para ≤60 chars mantendo keyword no início"})
            score -= 5
        
        # Meta description
        desc_len = seo_data.get("meta_description_length", 0)
        if desc_len == 0:
            critical.append({"id": "seo-003", "category": "SEO", "severity": "P0", "title": "Meta description ausente", "fix": "Adicionar meta description 120-155 chars com CTA"})
            score -= 20
        elif desc_len > 160:
            warnings.append({"id": "seo-004", "priority": "P2", "category": "SEO", "title": f"Meta description com {desc_len} chars (pode truncar)", "fix": "Reduzir para ≤155 chars"})
            score -= 3
        
        # H1
        h1_count = seo_data.get("h1_count", 0)
        if h1_count == 0:
            critical.append({"id": "seo-005", "category": "SEO", "severity": "P0", "title": "H1 ausente", "fix": "Adicionar exatamente 1 <h1> above-fold com keyword principal"})
            score -= 20
        elif h1_count > 1:
            critical.append({"id": "seo-006", "category": "SEO", "severity": "P0", "title": f"Múltiplos H1 ({h1_count})", "fix": "Manter apenas 1 H1, converter outros para H2/H3"})
            score -= 15
        
        # Headings hierarchy
        headings = seo_data.get("headings", [])
        levels = [h["level"] for h in headings]
        for i in range(1, len(levels)):
            if levels[i] - levels[i-1] > 1:
                warnings.append({"id": f"seo-h{i}", "priority": "P2", "category": "SEO", "title": f"Skip heading: H{levels[i-1]} → H{levels[i]}", "fix": "Não pular níveis de heading"})
                score -= 3
        
        # Structured Data
        sd = seo_data.get("structured_data", [])
        if not sd:
            warnings.append({"id": "seo-007", "priority": "P1", "category": "SEO", "title": "Nenhum JSON-LD structured data", "fix": "Adicionar Organization, LocalBusiness, WebSite, FAQPage, BreadcrumbList"})
            score -= 15
        else:
            for i, item in enumerate(sd):
                if "error" in item:
                    warnings.append({"id": f"seo-sd{i}", "priority": "P1", "category": "SEO", "title": f"JSON-LD inválido #{i+1}: {item['error']}", "fix": "Corrigir sintaxe JSON"})
                    score -= 5
        
        # Images alt
        if seo_data.get("images_without_alt", 0) > 0:
            warnings.append({"id": "seo-008", "priority": "P1", "category": "SEO", "title": f"{seo_data['images_without_alt']} imagens sem alt text", "fix": "Adicionar alt descritivo ou alt='' para decorativas"})
            score -= min(15, seo_data["images_without_alt"] * 2)
        
        # Canonical
        if not seo_data.get("canonical"):
            warnings.append({"id": "seo-009", "priority": "P1", "category": "SEO", "title": "Canonical tag ausente", "fix": "Adicionar <link rel='canonical' href='URL_canonica'>"})
            score -= 10
        
        # Viewport
        if "width=device-width" not in seo_data.get("viewport", ""):
            critical.append({"id": "seo-010", "category": "SEO", "severity": "P0", "title": "Viewport meta tag ausente/incorreta", "fix": '<meta name="viewport" content="width=device-width, initial-scale=1">'})
            score -= 15
        
        # Open Graph
        og = seo_data.get("og", {})
        missing_og = [k for k in ['og:title', 'og:description', 'og:image', 'og:url', 'og:type'] if not og.get(k)]
        if missing_og:
            warnings.append({"id": "seo-011", "priority": "P2", "category": "SEO", "title": f"Open Graph incompleto: {', '.join(missing_og)}", "fix": "Adicionar meta tags OG completas"})
            score -= 5
        
        # Language
        if seo_data.get("lang") in ['não definido', '']:
            warnings.append({"id": "seo-012", "priority": "P2", "category": "SEO", "title": "Lang attribute ausente", "fix": 'Adicionar <html lang="pt-BR">'})
            score -= 3
        
        return {
            "score": max(0, score),
            "seo_data": seo_data,
            "perf_data": perf_data,
            "cwv": cwv,
            "warnings": warnings,
            "critical_issues": critical,
        }
    
    def run_cro_deep(self, page):
        """CRO + UX profundo."""
        scroll_page(page)
        cro_data = extract_cro_elements(page)
        seo_data = extract_seo_data(page)
        perf_data = extract_performance_metrics(page)
        mobile_data = extract_mobile_usability(page)
        
        warnings = []
        critical = []
        score = 100
        
        # Above-fold analysis
        fold = page.evaluate("window.innerHeight")
        above_fold_ctas = cro_data.get("above_fold_ctas", 0)
        if above_fold_ctas == 0:
            critical.append({"id": "cro-001", "category": "CRO", "severity": "P0", "title": "Nenhum CTA above-fold", "fix": "Adicionar CTA primário visível sem scroll (sticky mobile)"})
            score -= 30
        elif above_fold_ctas == 1:
            warnings.append({"id": "cro-002", "priority": "P2", "category": "CRO", "title": "Apenas 1 CTA above-fold", "fix": "Considerar CTA secundário ou trust signal"})
            score -= 5
        
        # CTA quality
        ctas = cro_data.get("ctas", [])
        primary_cta = None
        for cta in ctas:
            text = cta.get("text", "").lower()
            if any(w in text for w in ["whatsapp", "agendar", "contratar", "comprar", "solicitar", "orçamento"]):
                primary_cta = cta
                break
        
        if primary_cta:
            rect = primary_cta.get("rect", {})
            if rect and rect.get("height", 0) < 48:
                warnings.append({"id": "cro-003", "priority": "P1", "category": "CRO", "title": f"CTA primário height {rect.get('height')}px < 48px", "fix": "Aumentar padding/tamanho do botão para ≥48px touch target"})
                score -= 10
        
        # Forms
        forms = cro_data.get("forms", [])
        for i, form in enumerate(forms):
            fc = form.get("field_count", 0)
            if fc == 0:
                critical.append({"id": f"cro-form{i}", "category": "CRO", "severity": "P0", "title": f"Formulário #{i+1} sem campos", "fix": "Adicionar campos necessários (nome, email, telefone)"})
                score -= 20
            elif fc > 5:
                warnings.append({"id": f"cro-form{i}", "priority": "P1", "category": "CRO", "title": f"Formulário #{i+1} com {fc} campos (recomendado ≤5)", "fix": "Remover campos opcionais, usar progressive profiling"})
                score -= 10
            
            # Check field types
            for field in form.get("fields", []):
                if field.get("type") == "text" and "email" in field.get("name", ""):
                    warnings.append({"id": "cro-004", "priority": "P1", "category": "CRO", "title": "Campo email usa type=text", "fix": "Usar type=email para teclado nativo e validação"})
                    score -= 5
                if field.get("type") == "text" and ("tel" in field.get("name", "") or "phone" in field.get("name", "")):
                    warnings.append({"id": "cro-005", "priority": "P1", "category": "CRO", "title": "Campo telefone usa type=text", "fix": "Usar type=tel para teclado numérico"})
                    score -= 5
        
        # Trust signals
        if len(cro_data.get("trust_signals", [])) == 0:
            warnings.append({"id": "cro-006", "priority": "P1", "category": "CRO", "title": "Nenhum trust signal detectado", "fix": "Adicionar selos Google Partner, SSL, garantias, certificações"})
            score -= 15
        
        # Social proof
        if len(cro_data.get("social_proof", [])) == 0:
            warnings.append({"id": "cro-007", "priority": "P1", "category": "CRO", "title": "Nenhuma prova social detectada", "fix": "Adicionar depoimentos (foto+nome+cargo), logos clientes, cases com números"})
            score -= 15
        
        # FAQ
        if cro_data.get("faq_count", 0) == 0:
            warnings.append({"id": "cro-008", "priority": "P2", "category": "CRO", "title": "Nenhuma FAQ/objeções respondidas", "fix": "Adicionar seção FAQ com 5-8 perguntas principais + schema FAQPage"})
            score -= 10
        
        # Performance impact on CRO
        lcp = perf_data.get("lcp")
        if lcp and lcp > 2500:
            warnings.append({"id": "cro-009", "priority": "P1", "category": "CRO", "title": f"LCP {lcp:.0f}ms > 2500ms (impacta conversão)", "fix": "Otimizar hero image, critical CSS, preload"})
            score -= 15
        
        # Mobile CRO
        if mobile_data.get("issue_count", 0) > 0:
            for issue in mobile_data["issues"]:
                priority = "P1" if issue["type"] in ["touch_target", "viewport"] else "P2"
                warnings.append({"id": f"cro-mob-{issue['type']}", "priority": priority, "category": "CRO", "title": f"Mobile: {issue['message']}", "fix": "Corrigir para mobile-first"})
            score -= min(20, mobile_data["issue_count"] * 5)
        
        return {
            "score": max(0, score),
            "cro_data": cro_data,
            "seo_data": seo_data,
            "perf_data": perf_data,
            "mobile_data": mobile_data,
            "warnings": warnings,
            "critical_issues": critical,
        }
    
    def run_accessibilidade(self, page):
        """Auditoria de acessibilidade WCAG 2.1 AA via axe-core."""
        self._inject_axe_core(page)
        page.wait_for_timeout(1000)
        
        axe_results = self._run_axe_audit(page)
        self.axe_results = axe_results
        
        warnings = []
        critical = []
        score = 100
        
        if "error" in axe_results:
            warnings.append({"id": "a11y-001", "priority": "P1", "category": "Acessibilidade", "title": f"Erro ao executar axe-core: {axe_results['error']}", "fix": "Verificar se axe-core carregou corretamente"})
            score -= 20
        else:
            violations = axe_results.get("violations", [])
            by_impact = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
            
            for v in violations:
                impact = v.get("impact", "minor")
                by_impact[impact] = by_impact.get(impact, 0) + 1
                
                nodes = v.get("nodes", [])
                for node in nodes[:3]:  # Top 3 exemplos
                    target = " > ".join(node.get("target", []))
                    warnings.append({
                        "id": f"a11y-{v['id']}",
                        "priority": "P0" if impact in ["critical", "serious"] else "P1" if impact == "moderate" else "P2",
                        "category": "Acessibilidade",
                        "title": f"[{impact.upper()}] {v['description']}",
                        "fix": v.get("help", ""),
                        "selector": target,
                        "wcag": v.get("tags", [])
                    })
            
            # Score baseado em violações
            score -= by_impact.get("critical", 0) * 15
            score -= by_impact.get("serious", 0) * 10
            score -= by_impact.get("moderate", 0) * 5
            score -= by_impact.get("minor", 0) * 2
            
            if by_impact["critical"] > 0:
                critical.append({"id": "a11y-summary", "category": "Acessibilidade", "severity": "P0", 
                    "title": f"{by_impact['critical']} violações críticas + {by_impact['serious']} sérias", 
                    "fix": "Corrigir violações critical/serious primeiro (color contrast, keyboard, ARIA)"})
        
        return {
            "score": max(0, score),
            "axe_results": axe_results,
            "warnings": warnings,
            "critical_issues": critical,
        }
    
    def run_performance(self, page):
        """Performance profunda + CWV reais + waterfall."""
        perf_data = extract_performance_metrics(page)
        cwv = self._collect_cwv_metrics(page)
        
        # Waterfall analysis
        waterfall = page.evaluate("""() => {
            const resources = performance.getEntriesByType('resource');
            return resources.map(r => ({
                name: r.name,
                type: r.initiatorType,
                duration: r.duration,
                startTime: r.startTime,
                transferSize: r.transferSize,
                encodedBodySize: r.encodedBodySize,
                decodedBodySize: r.decodedBodySize,
                priority: r.priority || 'unknown'
            })).sort((a, b) => a.startTime - b.startTime);
        }""")
        
        warnings = []
        critical = []
        score = 100
        
        # CWV Scoring
        lcp = cwv.get("lcp") or perf_data.get("lcp")
        if lcp:
            if lcp > 4000:
                critical.append({"id": "perf-001", "category": "Performance", "severity": "P0", "title": f"LCP {lcp:.0f}ms (péssimo > 4s)", "fix": "Preload hero, optimize images, critical CSS, reduce server response"})
                score -= 30
            elif lcp > 2500:
                warnings.append({"id": "perf-002", "priority": "P1", "category": "Performance", "title": f"LCP {lcp:.0f}ms > 2.5s", "fix": "Otimizar LCP: preload, WebP, dimensions, font-display"})
                score -= 15
        
        fid = cwv.get("fid")
        if fid and fid > 300:
            critical.append({"id": "perf-003", "category": "Performance", "severity": "P0", "title": f"FID {fid:.0f}ms > 300ms", "fix": "Reduce main thread work, code split, web workers"})
            score -= 20
        elif fid and fid > 100:
            warnings.append({"id": "perf-004", "priority": "P1", "category": "Performance", "title": f"FID {fid:.0f}ms > 100ms", "fix": "Otimizar JS execution, break long tasks"})
            score -= 10
        
        cls = cwv.get("cls")
        if cls is not None:
            if cls > 0.25:
                critical.append({"id": "perf-005", "category": "Performance", "severity": "P0", "title": f"CLS {cls:.2f} > 0.25 (péssimo)", "fix": "Aspect-ratio containers, reserve space, font-display: swap"})
                score -= 20
            elif cls > 0.1:
                warnings.append({"id": "perf-006", "priority": "P1", "category": "Performance", "title": f"CLS {cls:.2f} > 0.1", "fix": "Reserve space for dynamic content, aspect-ratio"}
            )
                score -= 10
        
        ttfb = cwv.get("ttfb") or perf_data.get("ttfb")
        if ttfb and ttfb > 800:
            warnings.append({"id": "perf-007", "priority": "P1", "category": "Performance", "title": f"TTFB {ttfb:.0f}ms > 800ms", "fix": "Server optimization, caching, CDN, reduce redirects"})
            score -= 10
        
        # Resource analysis
        js_resources = [r for r in waterfall if r["type"] == "script"]
        css_resources = [r for r in waterfall if r["type"] == "stylesheet"]
        img_resources = [r for r in waterfall if r["type"] in ["img", "image"]]
        
        total_js = sum(r["transferSize"] or 0 for r in js_resources)
        total_css = sum(r["transferSize"] or 0 for r in css_resources)
        total_img = sum(r["transferSize"] or 0 for r in img_resources)
        
        if total_js > 500000:  # 500KB
            warnings.append({"id": "perf-008", "priority": "P1", "category": "Performance", "title": f"JS total {total_js/1024:.0f}KB > 500KB", "fix": "Code splitting, remove unused, tree shaking, defer non-critical"})
            score -= 10
        
        if total_css > 100000:  # 100KB
            warnings.append({"id": "perf-009", "priority": "P2", "category": "Performance", "title": f"CSS total {total_css/1024:.0f}KB > 100KB", "fix": "Critical CSS inline, remove unused, media queries"})
            score -= 5
        
        # Blocking resources
        blocking = [r for r in waterfall if r["type"] in ["script", "stylesheet"] and r["startTime"] < 100]
        if len(blocking) > 3:
            warnings.append({"id": "perf-010", "priority": "P1", "category": "Performance", "title": f"{len(blocking)} recursos bloqueantes no head", "fix": "Defer/async scripts, critical CSS inline, preload key resources"})
            score -= 10
        
        return {
            "score": max(0, score),
            "perf_data": perf_data,
            "cwv": cwv,
            "waterfall": waterfall[:50],  # Limit
            "resource_summary": {
                "js_count": len(js_resources),
                "js_size_kb": round(total_js/1024, 1),
                "css_count": len(css_resources),
                "css_size_kb": round(total_css/1024, 1),
                "img_count": len(img_resources),
                "img_size_kb": round(total_img/1024, 1),
                "total_resources": len(waterfall)
            },
            "warnings": warnings,
            "critical_issues": critical,
        }
    
    def run_seguranca(self, page):
        """Auditoria de segurança."""
        mixed = self._check_mixed_content(page)
        cookies = self._analyze_cookies(page)
        pwa = self._analyze_pwa(page)
        security_headers = self._analyze_security_headers(page)
        
        warnings = []
        critical = []
        score = 100
        
        # Mixed content
        if mixed.get("mixed_content"):
            critical.append({"id": "sec-001", "category": "Segurança", "severity": "P0", "title": f"Mixed content: {mixed['count']} recursos HTTP em HTTPS", "fix": "Migrar todos recursos para HTTPS"})
            score -= 25
        
        # Cookies
        if cookies.get("total", 0) > 0:
            if cookies.get("secure", 0) < cookies["total"]:
                warnings.append({"id": "sec-002", "priority": "P1", "category": "Segurança", "title": f"{cookies['total'] - cookies['secure']} cookies sem Secure flag", "fix": "Adicionar Secure flag a todos cookies HTTPS"})
                score -= 10
            if cookies.get("httponly", 0) < cookies["total"]:
                warnings.append({"id": "sec-003", "priority": "P1", "category": "Segurança", "title": f"{cookies['total'] - cookies['httponly']} cookies sem HttpOnly", "fix": "Adicionar HttpOnly a cookies de sessão/auth"})
                score -= 10
            if cookies.get("samesite_none", 0) > 0:
                warnings.append({"id": "sec-004", "priority": "P1", "category": "Segurança", "title": f"{cookies['samesite_none']} cookies com SameSite=None", "fix": "Usar SameSite=Lax ou Strict, None só se cross-site necessário + Secure"})
                score -= 5
        
        # Security headers (via HTML meta - limitado)
        # Nota: headers reais precisam de resposta HTTP
        if "CSP não encontrado" in str(security_headers):
            warnings.append({"id": "sec-005", "priority": "P2", "category": "Segurança", "title": "CSP não detectado no HTML", "fix": "Implementar Content-Security-Policy via header HTTP"})
            score -= 5
        
        return {
            "score": max(0, score),
            "mixed_content": mixed,
            "cookies": cookies,
            "pwa": pwa,
            "security_headers": security_headers,
            "warnings": warnings,
            "critical_issues": critical,
        }
    
    def run_mobile_deep(self, page):
        """Mobile profundo + PWA."""
        from playwright_automation.devices import DEVICES
        
        mobile_results = {}
        all_issues = []
        warnings = []
        score = 100
        
        for device_name in ["mobile_iphone_se", "mobile_iphone_12", "mobile_android", "tablet_ipad"]:
            device = get_device(device_name)
            page.set_viewport_size(device["viewport"])
            page.wait_for_timeout(500)
            
            mobile_data = extract_mobile_usability(page)
            mobile_results[device_name] = mobile_data
            all_issues.extend(mobile_data.get("issues", []))
            score -= min(15, mobile_data.get("issue_count", 0) * 3)
            
            shot = take_screenshot(page, self.audit_dir, f"{device_name}")
            self.screenshots.append(shot)
        
        # PWA Analysis
        page.set_viewport_size({"width": 390, "height": 844})
        pwa = self._analyze_pwa(page)
        
        if not pwa.get("manifest"):
            warnings.append({"id": "mob-001", "priority": "P2", "category": "Mobile", "title": "Web App Manifest ausente", "fix": "Criar manifest.json com name, icons, start_url, display: standalone"})
            score -= 10
        else:
            m = pwa["manifest"]
            if m.get("display") != "standalone":
                warnings.append({"id": "mob-002", "priority": "P2", "category": "Mobile", "title": f"Manifest display: {m.get('display')} (recomendado standalone)", "fix": "Alterar display para standalone"})
                score -= 3
            if not m.get("icons") or len(m["icons"]) < 2:
                warnings.append({"id": "mob-003", "priority": "P2", "category": "Mobile", "title": "Manifest icons insuficientes", "fix": "Adicionar icons 192x192 e 512x512 (maskable + any)"})
                score -= 5
        
        if not pwa.get("sw"):
            warnings.append({"id": "mob-004", "priority": "P2", "category": "Mobile", "title": "Service Worker não registrado", "fix": "Registrar SW para offline caching + PWA installability"})
            score -= 10
        
        # Deduplicate issues
        unique_issues = []
        seen = set()
        for issue in all_issues:
            key = (issue["type"], issue["message"])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        page.set_viewport_size({"width": 1280, "height": 720})
        
        return {
            "score": max(0, score),
            "device_results": mobile_results,
            "pwa": pwa,
            "issues": unique_issues,
            "issue_count": len(unique_issues),
            "warnings": warnings,
            "critical_issues": [],
        }
    
    def run_completa(self, page):
        """Auditoria completa - executa todos os modos e consolida."""
        results = {}
        
        # SEO Deep
        results["seo"] = self.run_seo_deep(page)
        
        # CRO Deep
        results["cro"] = self.run_cro_deep(page)
        
        # Acessibilidade
        results["acessibilidade"] = self.run_accessibilidade(page)
        
        # Performance
        results["performance"] = self.run_performance(page)
        
        # Segurança
        results["seguranca"] = self.run_seguranca(page)
        
        # Mobile Deep
        results["mobile"] = self.run_mobile_deep(page)
        
        # Consolidate
        all_critical = []
        all_warnings = []
        scores = {}
        
        for cat, res in results.items():
            scores[cat] = res.get("score", 0)
            all_critical.extend(res.get("critical_issues", []))
            all_warnings.extend(res.get("warnings", []))
        
        overall_score = int(sum(scores.values()) / len(scores)) if scores else 0
        
        return {
            "mode": "COMPLETA",
            "sub_results": results,
            "score": overall_score,
            "scores": scores,
            "critical_issues": all_critical,
            "warnings": all_warnings,
            "next_steps": self._generate_next_steps(all_critical, all_warnings),
        }
    
    def _generate_next_steps(self, critical, warnings):
        steps = []
        for c in critical:
            steps.append(f"[P0] {c['title']}: {c.get('fix', '')}")
        for w in sorted(warnings, key=lambda x: {"P0": 0, "P1": 1, "P2": 2, "P3": 3}.get(x.get("priority", "P2"), 2)):
            if len(steps) < 15:
                steps.append(f"[{w.get('priority', 'P2')}] {w['title']}: {w.get('fix', '')}")
        if not steps:
            steps.append("Nenhuma ação corretiva necessária")
        return steps
    
    def run(self):
        with BrowserManager(headed=self.headed) as bm:
            with bm.new_context() as ctx:
                with bm.new_page(ctx) as page:
                    self._setup_page_listeners(page)
                    
                    # Navigate to target URL
                    print(f"[DEBUG] Navegando para: {self.url}")
                    result = page.goto(self.url, wait_until="networkidle", timeout=60000)
                    if not result or result.status >= 400:
                        print(f"[ERROR] Falha ao carregar {self.url}: status={result.status if result else 'N/A'}")
                    page.wait_for_timeout(3000)
                    
                    # Desktop screenshots
                    self.screenshots.extend(take_viewport_screenshots(page, self.audit_dir, "desktop_"))
                    
                    # Run mode-specific audit
                    if self.mode == "COMPLETA":
                        mode_result = self.run_completa(page)
                    elif self.mode == "SEO_DEEP":
                        mode_result = self.run_seo_deep(page)
                    elif self.mode == "CRO_DEEP":
                        mode_result = self.run_cro_deep(page)
                    elif self.mode == "ACESSIBILIDADE":
                        mode_result = self.run_accessibilidade(page)
                    elif self.mode == "PERFORMANCE":
                        mode_result = self.run_performance(page)
                    elif self.mode == "SEGURANCA":
                        mode_result = self.run_seguranca(page)
                    elif self.mode == "MOBILE_DEEP":
                        mode_result = self.run_mobile_deep(page)
                    else:
                        mode_result = {"error": f"Modo desconhecido: {self.mode}"}
                    
                    # Mobile screenshots for non-mobile modes
                    if self.mode not in ["MOBILE_DEEP", "COMPLETA"]:
                        page.set_viewport_size({"width": 390, "height": 844})
                        page.wait_for_timeout(500)
                        self.screenshots.extend(take_viewport_screenshots(page, self.audit_dir, "mobile_"))
                        page.set_viewport_size({"width": 1280, "height": 720})
        
        duration_ms = int((time.time() - self.start_time) * 1000)
        
        # Consolidate results
        status = "PASS"
        if mode_result.get("critical_issues"):
            status = "FAIL"
        elif mode_result.get("warnings"):
            status = "WARN"
        
        score = mode_result.get("score", 0)
        
        # Extract metrics
        metrics = {}
        if "cwv" in mode_result:
            metrics.update(mode_result["cwv"])
        if "perf_data" in mode_result:
            metrics.update(mode_result["perf_data"])
        if "axe_violations" in str(mode_result):
            # From acessibilidade
            pass
        
        # Generate next_steps if not present (for non-COMPLETA modes)
        next_steps = mode_result.get("next_steps", [])
        if not next_steps:
            next_steps = self._generate_next_steps(
                mode_result.get("critical_issues", []),
                mode_result.get("warnings", [])
            )
        
        report = {
            "url": self.url,
            "mode": self.mode,
            "slug": self.slug,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "viewports_tested": ["desktop", "mobile_iphone_12"] if self.mode != "MOBILE_DEEP" else ["mobile_iphone_se", "mobile_iphone_12", "mobile_android", "tablet_ipad"],
            "overall_score": score,
            "scores": mode_result.get("scores", {}),
            "status": status,
            "critical_issues": mode_result.get("critical_issues", []),
            "warnings": mode_result.get("warnings", []),
            "metrics": metrics,
            "sub_results": mode_result.get("sub_results", {}),
            "screenshots": self.screenshots,
            "console_errors": [l for l in self.console_logs if l["type"] == "error"],
            "console_warnings": [l for l in self.console_logs if l["type"] == "warning"],
            "network_failures": self.network_failures,
            "next_steps": next_steps,
            "summary": f"Auditoria {self.mode} concluída. Score: {score}/100. Status: {status}",
        }
        
        # Save reports
        generate_json_report(report, self.audit_dir, self.slug)
        generate_markdown_report(report, self.audit_dir, self.slug, self.screenshots)
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Website Audit Runner - Auditoria profunda via browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modos disponíveis:
  COMPLETA        - Auditoria 360° (SEO + CRO + A11y + Perf + Sec + Mobile) ~5-8min
  SEO_DEEP        - SEO técnico runtime (meta, schema, CWV, canonical) ~3-4min
  CRO_DEEP        - Conversão + UX (CTA, forms, trust, social proof) ~3-4min
  ACESSIBILIDADE  - WCAG 2.1 AA via axe-core ~2-3min
  PERFORMANCE     - Core Web Vitals reais + waterfall ~3-4min
  SEGURANCA       - Headers, CSP, cookies, mixed content ~2min
  MOBILE_DEEP     - PWA + touch targets + viewport + forms ~2-3min

Exemplos:
  %(prog)s https://meusite.com --mode COMPLETA
  %(prog)s https://meusite.com --mode SEO_DEEP
  %(prog)s https://meusite.com --mode ACESSIBILIDADE --headed
  %(prog)s https://meusite.com --mode PERFORMANCE --json
        """
    )
    
    parser.add_argument("url", help="URL para auditar")
    parser.add_argument(
        "--mode", "-m",
        default="COMPLETA",
        choices=list(WebsiteAuditRunner.MODES.keys()),
        help="Modo de auditoria (padrão: COMPLETA)"
    )
    parser.add_argument(
        "--slug", "-s",
        help="Slug personalizado para diretório de relatório"
    )
    parser.add_argument(
        "--headed", "-H",
        action="store_true",
        help="Executar com browser visível"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Saída apenas JSON"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Diretório base para relatórios"
    )
    
    args = parser.parse_args()
    
    if args.output_dir:
        os.environ["AUDIT_BASE_DIR"] = args.output_dir
    
    print(f"\n{'='*70}")
    print(f"WEBSITE AUDIT RUNNER")
    print(f"{'='*70}")
    print(f"URL: {args.url}")
    print(f"Mode: {args.mode} - {WebsiteAuditRunner.MODES[args.mode]}")
    print(f"Headed: {'Sim' if args.headed else 'Não (headless)'}")
    print(f"{'='*70}\n")
    
    try:
        runner = WebsiteAuditRunner(args.url, args.mode, args.slug, args.headed)
        result = runner.run()
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*70}")
            print(f"RESULTADO DA AUDITORIA")
            print(f"{'='*70}")
            print(f"Status: {result['status']}")
            print(f"Score Geral: {result['overall_score']}/100")
            print(f"Duração: {result['duration_ms']/1000:.1f}s")
            print(f"Screenshots: {len(result['screenshots'])}")
            print(f"Console Errors: {len(result['console_errors'])}")
            print(f"Network Failures: {len(result['network_failures'])}")
            
            if result.get("scores"):
                print(f"\nScores por Categoria:")
                for cat, sc in result["scores"].items():
                    icon = "✅" if sc >= 80 else "⚠️" if sc >= 60 else "❌"
                    print(f"  {cat.capitalize()}: {sc}/100 {icon}")
            
            print(f"\nRelatório: {runner.audit_dir / f'{runner.slug}_report.md'}")
            print(f"JSON: {runner.audit_dir / f'{runner.slug}_report.json'}")
            print(f"{'='*70}\n")
            
            if result["critical_issues"]:
                print("PROBLEMAS CRÍTICOS (P0):")
                for issue in result["critical_issues"][:10]:
                    print(f"  🔴 {issue['title']}")
                    if issue.get('fix'):
                        print(f"     → {issue['fix']}")
                print()
            
            if result["warnings"]:
                print("AVISOS (P1/P2/P3):")
                for w in result["warnings"][:15]:
                    print(f"  [{w.get('priority', 'P2')}] {w['title']}")
                if len(result["warnings"]) > 15:
                    print(f"  ... e mais {len(result['warnings']) - 15} avisos")
                print()
            
            print("PRÓXIMOS PASSOS (Top 10):")
            for step in result["next_steps"][:10]:
                print(f"  {step}")
        
        if result["status"] == "FAIL":
            sys.exit(1)
        elif result["status"] == "WARN":
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        sys.exit(130)
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()