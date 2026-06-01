"""
Phase 2: DeepSeek-VL2 Integration for Visual Element Grounding

This module handles communication with the DeepSeek API to analyze screenshots
and identify UI elements with their coordinates.
"""

import base64
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from openai import OpenAI
from config import DEFAULT_CONFIG
from logger import system_logger


class VLMClient:
    """
    Client for interacting with Vision-Language Models (primarily DeepSeek-VL2).
    
    This is the "Brain" component - handling visual understanding and grounding.
    """
    
    def __init__(self, config=DEFAULT_CONFIG.vlm):
        self.config = config
        self.client = None
        
        if self.config.api_key:
            self.client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base
            )
            system_logger.info(f"VLM Client initialized with {self.config.provider} ({self.config.model})")
        else:
            system_logger.warning("VLM Client initialized without API key. Vision features will be disabled.")

    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def analyze_screenshot(
        self, 
        screenshot_path: Path, 
        prompt: str,
        accessibility_tree: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a screenshot using the VLM.
        
        Args:
            screenshot_path: Path to the screenshot file
            prompt: Instructions for the VLM
            accessibility_tree: Optional structured DOM data to assist the VLM
            
        Returns:
            VLM analysis results including identified elements and coordinates
        """
        if not self.client:
            raise RuntimeError("VLM Client not initialized with API key.")
            
        base64_image = self._encode_image(screenshot_path)
        
        # Enhance prompt with accessibility tree data if provided
        full_prompt = prompt
        if accessibility_tree:
            # We only send a summary of the tree to avoid token limits
            elements_summary = [
                f"{e['tag']}[{e['role']}]: '{e['text'][:30]}'" 
                for e in accessibility_tree.get('elements', [])[:20]
            ]
            full_prompt += f"\n\nContext from accessibility tree (first 20 elements):\n" + "\n".join(elements_summary)
            
        system_logger.info(f"Sending vision request to {self.config.model}...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": full_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            },
                        ],
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            
            result_text = response.choices[0].message.content
            system_logger.info("VLM analysis complete.")
            
            return {
                "raw_response": result_text,
                "usage": response.usage.to_dict() if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            system_logger.error(f"VLM API request failed: {str(e)}")
            raise

    def parse_coordinates(self, vlm_response: str) -> List[Dict[str, Any]]:
        """
        Parse bounding box coordinates from the VLM's natural language response.
        
        DeepSeek-VL2 often returns coordinates in a specific format like [x, y, width, height]
         or as normalized points. This method should be adapted based on the specific
         output format of the model being used.
        """
        # Placeholder for coordinate parsing logic
        # In a real implementation, this would use regex or structured output parsing
        system_logger.debug(f"Parsing coordinates from: {vlm_response[:100]}...")
        return []


async def example_vision_task():
    """Example of using the VLM client to find a login button."""
    client = VLMClient()
    
    # This assumes Phase 1 has already captured a screenshot
    screenshot = Path("./screenshots/latest_page.png")
    if not screenshot.exists():
        print("Please run browser_controller.py first to generate a screenshot.")
        return
        
    prompt = (
        "Analyze this webpage screenshot. Identify the 'Login' or 'Sign In' button. "
        "Provide its exact coordinates [x, y, width, height] in pixels relative to the top-left corner."
    )
    
    try:
        result = await client.analyze_screenshot(screenshot, prompt)
        print("\n--- VLM Analysis ---\n")
        print(result["raw_response"])
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    # To run this, you'll need to set DEEPSEEK_API_KEY in your .env file
    # asyncio.run(example_vision_task())
    print("VLM Client module loaded. Run with an API key to test.")
