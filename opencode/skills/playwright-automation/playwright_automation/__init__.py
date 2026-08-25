"""Playwright Automation Package - Core modules for browser testing."""
from .browser_manager import BrowserManager
from .devices import DEVICES, get_device
from .navigation import goto_with_retry, wait_for_network_idle, scroll_page
from .interactions import (
    safe_click, safe_fill, safe_select_option, 
    get_element_info, find_cta_candidates
)
from .extraction import (
    extract_seo_data, extract_performance_metrics,
    extract_cro_elements, extract_mobile_usability
)
from .reporting import (
    ensure_audit_dir, take_screenshot, take_viewport_screenshots,
    generate_json_report, generate_markdown_report
)
from .runner import BrowserTestRunner

__all__ = [
    "BrowserManager",
    "DEVICES", "get_device",
    "goto_with_retry", "wait_for_network_idle", "scroll_page",
    "safe_click", "safe_fill", "safe_select_option",
    "get_element_info", "find_cta_candidates",
    "extract_seo_data", "extract_performance_metrics",
    "extract_cro_elements", "extract_mobile_usability",
    "ensure_audit_dir", "take_screenshot", "take_viewport_screenshots",
    "generate_json_report", "generate_markdown_report",
    "BrowserTestRunner",
]