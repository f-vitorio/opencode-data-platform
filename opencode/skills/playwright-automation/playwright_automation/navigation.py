"""Navigation Helpers - Page navigation with retry and metrics."""
from playwright.sync_api import Page
from typing import Dict, Any, List
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