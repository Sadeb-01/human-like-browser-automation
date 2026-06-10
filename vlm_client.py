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
import re
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

    def parse_vlm_response(self, vlm_response: str) -> Dict[str, Any]:
        """
        Parse the structured JSON response from the VLM.
        Expected format: {\"action\": \"click\", \"x\": <x>, \"y\": <y>}
        or {\"action\": \"type\", \"text\": \"<text>\"}
        or {\"action\": \"scroll\", \"direction\": \"up\"/\"down\", \"amount\": <amount>}
        or {\"action\": \"complete\"}
        or {\"action\": \"error\", \"message\": \"<message>\", \"target_text\": \"<optional_text_for_ocr_fallback>\"}
        """
        system_logger.debug(f"Parsing VLM response: {vlm_response[:200]}...")
        try:
            # Attempt to find a JSON object in the response
            # The VLM might embed the JSON within other text, so we need to extract it
            json_start = vlm_response.find('{')
            json_end = vlm_response.rfind('}')
            
            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = vlm_response[json_start : json_end + 1]
                action_data = json.loads(json_str)
                
                # Validate the action structure
                if "action" not in action_data:
                    raise ValueError("Missing 'action' key in VLM response JSON.")
                
                return action_data
            else:
                # If no JSON is found, try to infer simple actions or return an error
                if "TASK_COMPLETE" in vlm_response:
                    return {"action": "complete"}
                elif "error" in vlm_response.lower() or "stuck" in vlm_response.lower():
                    # Attempt to extract target_text if present in the unstructured error message
                    match = re.search(r"target_text\":\s*\"(.*?)\"", vlm_response)
                    target_text = match.group(1) if match else None
                    return {"action": "error", "message": vlm_response, "target_text": target_text}
                else:
                    # Fallback for unstructured responses, log and return a generic error
                    system_logger.warning(f"VLM response not in expected JSON format: {vlm_response}")
                    return {"action": "error", "message": "VLM response not parsable as JSON or simple action."}
        except json.JSONDecodeError as e:
            system_logger.error(f"JSON parsing failed: {e}. Raw response: {vlm_response}")
            return {"action": "error", "message": f"JSON parsing failed: {e}"}
        except ValueError as e:
            system_logger.error(f"VLM response validation failed: {e}. Raw response: {vlm_response}")
            return {"action": "error", "message": f"VLM response validation failed: {e}"}


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
