"""Browser Manager - Context manager for Playwright browser instances."""
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