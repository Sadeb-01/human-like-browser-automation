"""
Phase 1: Basic Browser Control & Screenshot Capture

This module provides the foundation for non-headless browser automation.
It handles browser initialization, page navigation, and screenshot capture.
"""

import asyncio
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class BrowserController:
    """
    Manages non-headless browser instances with screenshot capture capabilities.
    
    This is the foundation of the "Body" component - the core browser engine.
    """
    
    def __init__(
        self,
        headless: bool = False,
        browser_type: str = "chromium",
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        user_agent: Optional[str] = None,
        disable_blink_features: bool = True,
        storage_state_path: Optional[str] = None,
    ):
        """
        Initialize the browser controller.
        
        Args:
            headless: Whether to run in headless mode (default: False for non-headless)
            browser_type: Type of browser to use ('chromium', 'firefox', 'webkit')
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
            user_agent: Custom user agent string
            disable_blink_features: Disable automation-specific blink features
        """
        self.headless = headless
        self.browser_type = browser_type
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = user_agent or self._get_default_user_agent()
        self.disable_blink_features = disable_blink_features
        self.storage_state_path = Path(storage_state_path) if storage_state_path else None
        
        # Xvfb state
        self.use_xvfb = False
        self.xvfb_process = None
        self.xvfb_display = ":99"
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Create screenshots directory
        self.screenshots_dir = Path("./screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        
    def _get_default_user_agent(self) -> str:
        """Get a realistic default user agent string."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    
    async def initialize(self, use_xvfb: bool = False, xvfb_display: str = ":99", xvfb_width: int = 1920, xvfb_height: int = 1080) -> None:
        """Initialize the Playwright browser instance."""
        self.use_xvfb = use_xvfb
        self.xvfb_display = xvfb_display

        if self.use_xvfb:
            print(f"Starting Xvfb on display {self.xvfb_display} ({xvfb_width}x{xvfb_height})...")
            self.xvfb_process = subprocess.Popen(
                ["Xvfb", self.xvfb_display, "-screen", "0", f"{xvfb_width}x{xvfb_height}x24"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            os.environ["DISPLAY"] = self.xvfb_display
            # Give Xvfb a moment to start
            time.sleep(2)
            print(f"✓ Xvfb started on {self.xvfb_display}")

        self.playwright = await async_playwright().start()
        
        # Prepare launch arguments
        launch_args = {
            "headless": self.headless,
        }
        
        # Anti-detection: Disable the automation-controlled flag
        if self.disable_blink_features:
            launch_args["args"] = ["--disable-blink-features=AutomationControlled"]
        
        # Launch browser
        if self.browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(**launch_args)
        elif self.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(**launch_args)
        elif self.browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(**launch_args)
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # Create context with custom settings
        context_args = {
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "user_agent": self.user_agent,
            "locale": "en-US",
            "timezone_id": "America/New_York",
        }
        if self.storage_state_path and self.storage_state_path.exists():
            context_args["storage_state"] = str(self.storage_state_path)
            print(f"✓ Loading browser storage state from {self.storage_state_path}")
        
        self.context = await self.browser.new_context(**context_args)
        
        # Create a new page
        self.page = await self.context.new_page()
        
        print(f"✓ Browser initialized ({self.browser_type}, headless={self.headless})")
    
    async def navigate_to(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            wait_until: When to consider navigation succeeded ('load', 'domcontentloaded', 'networkidle')
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        await self.page.goto(url, wait_until=wait_until)
        print(f"✓ Navigated to {url}")
    
    async def take_screenshot(self, filename: Optional[str] = None) -> Path:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional custom filename. If not provided, generates timestamp-based name.
            
        Returns:
            Path to the saved screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.png"
        
        filepath = self.screenshots_dir / filename
        await self.page.screenshot(path=str(filepath), full_page=True)
        print(f"✓ Screenshot saved: {filepath}")
        return filepath
    
    async def get_page_content(self) -> str:
        """Get the full HTML content of the current page."""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        return await self.page.content()
    
    async def get_accessibility_tree(self) -> Dict[str, Any]:
        """
        Get the accessibility tree of the current page.
        This will be used by the VLM for element grounding in Phase 2.
        """
        if not self.page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        
        # Extract accessibility information using JavaScript
        accessibility_data = await self.page.evaluate("""
            () => {
                const elements = [];
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_ELEMENT,
                    null,
                    false
                );
                
                let node;
                while (node = walker.nextNode()) {
                    const role = node.getAttribute('role') || node.tagName.toLowerCase();
                    const text = node.innerText?.substring(0, 100) || '';
                    const ariaLabel = node.getAttribute('aria-label') || '';
                    
                    if (role && (text || ariaLabel)) {
                        const rect = node.getBoundingClientRect();
                        elements.push({
                            tag: node.tagName.toLowerCase(),
                            role: role,
                            text: text,
                            ariaLabel: ariaLabel,
                            id: node.id,
                            className: node.className,
                            x: Math.round(rect.x),
                            y: Math.round(rect.y),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                        });
                    }
                }
                return elements;
            }
        """)
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "elements": accessibility_data,
        }
    
    async def save_storage_state(self):
        """
        Saves the current browser context storage state (cookies, localStorage) to a file.
        """
        if not self.context:
            raise RuntimeError("Browser context not initialized. Call initialize() first.")
        if not self.storage_state_path:
            print("No storage_state_path configured. Skipping saving storage state.")
            return
        
        self.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        await self.context.storage_state(path=str(self.storage_state_path))
        print(f"✓ Browser storage state saved to {self.storage_state_path}")

    async def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        if self.xvfb_process:
            print("Stopping Xvfb...")
            self.xvfb_process.terminate()
            self.xvfb_process.wait()
            print("✓ Xvfb stopped")
            
        if self.storage_state_path:
            await self.save_storage_state()
        print("✓ Browser closed")


async def main():
    """Example usage of the BrowserController."""
    controller = BrowserController(headless=False)
    
    try:
        # Initialize browser
        await controller.initialize()
        
        # Navigate to a website
        await controller.navigate_to("https://example.com")
        
        # Take a screenshot
        screenshot_path = await controller.take_screenshot()
        
        # Get accessibility tree
        accessibility_tree = await controller.get_accessibility_tree()
        print(f"✓ Found {len(accessibility_tree['elements'])} elements in accessibility tree")
        
        # Print first few elements
        for elem in accessibility_tree["elements"][:5]:
            print(f"  - {elem['tag']} ({elem['role']}): {elem['text'][:50]}")
        
    finally:
        await controller.close()


if __name__ == "__main__":
    asyncio.run(main())
