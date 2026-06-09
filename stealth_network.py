"""
Phase 4: Advanced Anti-Detection, Stealth, and Networking

This module handles residential proxy integration and TLS fingerprinting
to ensure the network identity of the agent is indistinguishable from a human.
"""

import random
from typing import Optional, Dict, Any

from curl_cffi import requests
from logger import system_logger
from config import DEFAULT_CONFIG


class StealthNetwork:
    """
    Manages stealthy network operations including proxies and TLS spoofing.
    
    This is the "Identity" component - ensuring the network footprint is clean.
    """
    
    def __init__(self, config=DEFAULT_CONFIG.anti_detection):
        self.config = config
        self.session = requests.Session()
        
        # Initialize proxy pool correctly
        if config.proxy_pool:
            self.proxy_pool = config.proxy_pool
        elif config.proxy_url:
            self.proxy_pool = [config.proxy_url]
        else:
            self.proxy_pool = []
            
        self.active_proxy = config.proxy_url if config.proxy_url else (self.proxy_pool[0] if self.proxy_pool else None)
        self.bad_proxies = set()
        system_logger.info(f"Stealth Network module initialized with {len(self.proxy_pool)} proxies.")

    def rotate_proxy(self) -> Optional[str]:
        """
        Rotates to the next available proxy in the pool.
        """
        if not self.proxy_pool:
            return None
            
        available_proxies = [p for p in self.proxy_pool if p not in self.bad_proxies]
        if not available_proxies:
            system_logger.warning("No healthy proxies available in the pool. Resetting bad proxies list.")
            self.bad_proxies.clear()
            available_proxies = self.proxy_pool
            
        self.active_proxy = random.choice(available_proxies)
        system_logger.info(f"Rotated to proxy: {self.active_proxy}")
        return self.active_proxy

    async def check_proxy_health(self, proxy_url: str) -> bool:
        """
        Checks if a proxy is healthy by performing a simple request.
        """
        system_logger.info(f"Checking health for proxy: {proxy_url}")
        try:
            # Using a simple blocking request for health check
            response = requests.get(
                self.config.proxy_health_check_url,
                proxies={"http": proxy_url, "https": proxy_url},
                timeout=10
            )
            is_healthy = response.status_code == 200
            if not is_healthy:
                system_logger.warning(f"Proxy {proxy_url} failed health check with status {response.status_code}")
                self.bad_proxies.add(proxy_url)
            return is_healthy
        except Exception as e:
            system_logger.warning(f"Proxy {proxy_url} failed health check with error: {e}")
            self.bad_proxies.add(proxy_url)
            return False

    def get_proxy_settings(self) -> Optional[Dict[str, str]]:
        """
        Configure residential proxy settings.
        """
        if not self.config.use_residential_proxy:
            return None
            
        proxy = self.active_proxy or self.rotate_proxy()
        if not proxy:
            return None
            
        return {
            "http": proxy,
            "https": proxy
        }

    def perform_stealth_request(
        self, 
        url: str, 
        method: str = "GET", 
        impersonate: str = "chrome110",
        **kwargs
    ) -> requests.Response:
        """
        Perform a request that impersonates a real browser's TLS fingerprint.
        
        Args:
            url: Target URL
            method: HTTP method
            impersonate: Browser profile to impersonate (e.g., 'chrome110', 'safari15')
        """
        proxies = self.get_proxy_settings()
        
        system_logger.info(f"Performing stealth {method} request to {url} impersonating {impersonate}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                impersonate=impersonate,
                proxies=proxies,
                **kwargs
            )
            return response
        except Exception as e:
            system_logger.error(f"Stealth request failed: {str(e)}")
            raise

    def get_random_browser_profile(self) -> str:
        """
        Returns a random browser profile for rotation.
        """
        profiles = ["chrome110", "chrome116", "chrome119", "safari15", "safari17", "edge101"]
        return random.choice(profiles)


class FingerprintManager:
    """
    Manages browser fingerprint randomization and hardware spoofing.
    """
    
    @staticmethod
    def get_random_viewport() -> Dict[str, int]:
        """Generate realistic common screen resolutions."""
        resolutions = [
            (1920, 1080), (1440, 900), (1536, 864), 
            (1366, 768), (1280, 720), (2560, 1440)
        ]
        w, h = random.choice(resolutions)
        return {"width": w, "height": h}

    @staticmethod
    def get_random_user_agent() -> str:
        """Generate realistic modern user agents."""
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        return random.choice(agents)


if __name__ == "__main__":
    # Test stealth request
    network = StealthNetwork()
    try:
        # Check IP and TLS fingerprint
        resp = network.perform_stealth_request("https://tls.browserleaks.com/json")
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
