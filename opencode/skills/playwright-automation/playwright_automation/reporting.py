"""Reporting Helpers - Screenshots, JSON and Markdown report generation."""
from playwright.sync_api import Page
from typing import Dict, Any, List
import os
import json
from datetime import datetime
from pathlib import Path

# Try to get AUDIT_BASE_DIR from env, fallback to default
AUDIT_BASE_DIR = Path(os.getenv("AUDIT_BASE_DIR", Path.home() / "Documents" / "PROJETOS" / "audits"))


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