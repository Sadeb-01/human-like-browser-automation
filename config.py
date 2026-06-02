"""
Configuration management for the browser automation system.

This module handles all configuration settings across different phases.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


@dataclass
class BrowserConfig:
    """Configuration for browser behavior."""
    
    headless: bool = False
    browser_type: str = "chromium"  # chromium, firefox, webkit
    viewport_width: int = 1920
    viewport_height: int = 1080
    disable_automation_features: bool = True
    user_agent: Optional[str] = None
    storage_state_path: Optional[str] = None
    
    # Timeout settings (in milliseconds)
    navigation_timeout: int = 30000
    action_timeout: int = 10000


@dataclass
class VLMConfig:
    """Configuration for Vision-Language Model (Phase 2+)."""
    
    provider: str = "deepseek"  # deepseek, openai, etc.
    model: str = "deepseek-vl2"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 1000


@dataclass
class InputConfig:
    """Configuration for OS-level input simulation (Phase 3+)."""
    
    use_os_level_input: bool = False
    mouse_speed: float = 0.5  # 0.0 to 1.0, where 1.0 is fastest
    typing_speed: float = 0.5  # 0.0 to 1.0, where 1.0 is fastest
    enable_human_like_movements: bool = True


@dataclass
class MemoryConfig:
    """Configuration for task memory persistence."""
    memory_dir: str = "./task_memory"

@dataclass
class AntiDetectionConfig:
    """Configuration for anti-detection measures (Phase 4+)."""
    
    enable_stealth_mode: bool = False
    use_residential_proxy: bool = False
    proxy_url: Optional[str] = None
    randomize_fingerprint: bool = False
    spoof_hardware_info: bool = False
    randomize_timing: bool = False


@dataclass
class SystemConfig:
    """Master configuration class."""
    
    browser: BrowserConfig
    vlm: VLMConfig
    input_config: InputConfig
    anti_detection: AntiDetectionConfig
    memory: MemoryConfig
    
    # Logging
    log_level: str = "INFO"
    save_screenshots: bool = True
    screenshots_dir: str = "./screenshots"
    
    @classmethod
    def from_env(cls) -> "SystemConfig":
        """Create configuration from environment variables."""
        return cls(
            browser=BrowserConfig(
                headless=os.getenv("BROWSER_HEADLESS", "false").lower() == "true",
                browser_type=os.getenv("BROWSER_TYPE", "chromium"),
                viewport_width=int(os.getenv("VIEWPORT_WIDTH", "1920")),
                viewport_height=int(os.getenv("VIEWPORT_HEIGHT", "1080")),
                disable_automation_features=os.getenv("DISABLE_AUTOMATION_FEATURES", "true").lower() == "true",
                storage_state_path=os.getenv("BROWSER_STORAGE_STATE_PATH"),
            ),
            vlm=VLMConfig(
                provider=os.getenv("VLM_PROVIDER", "deepseek"),
                model=os.getenv("VLM_MODEL", "deepseek-vl2"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                api_base=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            ),
            input_config=InputConfig(
                use_os_level_input=os.getenv("USE_OS_LEVEL_INPUT", "false").lower() == "true",
                mouse_speed=float(os.getenv("MOUSE_SPEED", "0.5")),
                typing_speed=float(os.getenv("TYPING_SPEED", "0.5")),
            ),
            anti_detection=AntiDetectionConfig(
                enable_stealth_mode=os.getenv("ENABLE_STEALTH_MODE", "false").lower() == "true",
                use_residential_proxy=os.getenv("USE_RESIDENTIAL_PROXY", "false").lower() == "true",
                proxy_url=os.getenv("PROXY_URL"),
            ),
            memory=MemoryConfig(
                memory_dir=os.getenv("MEMORY_DIR", "./task_memory"),
            ),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Default configuration instance
DEFAULT_CONFIG = SystemConfig.from_env()
