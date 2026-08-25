"""Main Test Runner - Orchestrates all test modes."""
from playwright.sync_api import sync_playwright
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from playwright_automation.browser_manager import BrowserManager
from playwright_automation.devices import get_device
from playwright_automation.navigation import goto_with_retry, scroll_page
from playwright_automation.interactions import find_cta_candidates, get_element_info, safe_click, safe_fill
from playwright_automation.extraction import (
    extract_seo_data, extract_performance_metrics,
    extract_cro_elements, extract_mobile_usability
)
from playwright_automation.reporting import ensure_audit_dir, take_viewport_screenshots, generate_json_report, generate_markdown_report


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
        from playwright_automation.devices import DEVICES
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
            from playwright_automation.reporting import take_screenshot
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
        if score == 0 and "score" not in mode_result:
            # Calculate from checks for smoke
            checks = mode_result.get("checks", {})
            if checks and isinstance(checks, dict) and len(checks) > 0:
                # checks values are booleans, sum them (True=1, False=0)
                passed = sum(1 for v in checks.values() if v)
                score = int((passed / len(checks)) * 100)
            else:
                # Default score for smoke if no checks
                score = 85 if status == "PASS" else 50
        
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