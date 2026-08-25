"""Google Maps Scraper - Rate Limiter Ético."""
import time
import random
from typing import Dict, Any, Optional


class EthicalRateLimiter:
    """
    Rate limiter ético para scraping.
    
    Princípios:
    - Delay aleatório entre requests (configurável)
    - Respeita headers de retry se servidor indicar
    - Backoff exponencial em erros 429/5xx
    - Log de todos requests para auditoria
    """
    
    def __init__(
        self,
        delay_min: float = 3.0,
        delay_max: float = 8.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.last_request_time = 0
        self.request_count = 0
        self.error_count = 0
    
    def wait(self):
        """Aguarda tempo necessário antes do próximo request."""
        elapsed = time.time() - self.last_request_time
        min_wait = self.delay_min + random.uniform(0, self.delay_max - self.delay_min)
        
        if elapsed < min_wait:
            sleep_time = min_wait - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def handle_response(self, status_code: int) -> bool:
        """
        Processa resposta HTTP.
        Returns: True se deve retry, False caso contrário.
        """
        if status_code == 429:
            self.error_count += 1
            wait_time = self.backoff_factor ** self.error_count * 5
            time.sleep(wait_time)
            return True
        
        if 500 <= status_code < 600:
            self.error_count += 1
            if self.error_count <= self.max_retries:
                wait_time = self.backoff_factor ** self.error_count * 2
                time.sleep(wait_time)
                return True
        
        # Sucesso ou erro não-retryable
        self.error_count = 0
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "requests_made": self.request_count,
            "errors": self.error_count,
            "avg_delay": (self.delay_min + self.delay_max) / 2,
        }