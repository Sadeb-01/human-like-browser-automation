"""
Phase 5: Human-Like Automation Orchestrator

This is the central brain of the system, coordinating the Body, Brain, Hands, 
and Identity to perform complex tasks autonomously.
"""

import asyncio
from pathlib import Path
from typing import Optional

from browser_controller import BrowserController
from vlm_client import VLMClient
from input_simulator import InputSimulator
from stealth_network import StealthNetwork
from logger import system_logger
from config import DEFAULT_CONFIG
from task_memory import TaskMemoryManager
from ocr_engine import OCREngine


class HumanAutomationOrchestrator:
    """
    Coordinates all components to perform human-like automation.
    """
    
    def __init__(self, config=DEFAULT_CONFIG):
        self.config = config
        self.body = BrowserController(
            headless=config.browser.headless,
            browser_type=config.browser.browser_type,
            viewport_width=config.browser.viewport_width,
            viewport_height=config.browser.viewport_height,
            disable_blink_features=config.browser.disable_automation_features,
            storage_state_path=config.browser.storage_state_path
        )
        self.brain = VLMClient(config=config.vlm)
        self.hands = InputSimulator(config=config.input_config)
        self.identity = StealthNetwork(config=config.anti_detection)
        self.memory_manager = TaskMemoryManager(config.memory.memory_dir)
        self.ocr_engine = OCREngine()
        
        system_logger.info("Human Automation Orchestrator initialized.")

    async def startup(self):
        """Initialize all components."""
        await self.body.initialize(
            use_xvfb=self.config.browser.use_xvfb,
            xvfb_display=self.config.browser.xvfb_display,
            xvfb_width=self.config.browser.xvfb_width,
            xvfb_height=self.config.browser.xvfb_height
        )
        
        # Perform initial proxy health checks if pool is configured
        if self.identity.proxy_pool:
            system_logger.info("Performing initial proxy health checks...")
            for proxy in self.identity.proxy_pool:
                await self.identity.check_proxy_health(proxy)
        
        system_logger.info("System startup complete.")

    async def perform_task(self, task_name: str, task_description: str, start_url: str, max_retries: int = 3):
        """
        Perform a complex task autonomously.
        
        Args:
            task_description: Natural language description of the task
            start_url: The URL to begin the task at
        """
        system_logger.info(f"Starting task: {task_name} - {task_description}")
        task_memory = self.memory_manager.load_task_memory(task_name)

        if task_memory and task_memory["status"] == "in-progress":
            system_logger.info(f"Resuming task \'{task_name}\' from step: {task_memory['current_step']}")
            if task_memory["browser_state_path"] and Path(task_memory["browser_state_path"]).exists():
                self.body.storage_state_path = Path(task_memory["browser_state_path"])
            await self.body.navigate_to(task_memory.get("last_url", start_url))
        else:
            system_logger.info(f"Starting new task \'{task_name}\' from scratch.")
            self.memory_manager.update_task_progress(task_name, status="in-progress", current_step="start")
            await self.body.navigate_to(start_url)

        # Update browser state path in memory
        if self.body.storage_state_path:
            self.memory_manager.update_task_progress(task_name, browser_state_path=str(self.body.storage_state_path))
        
        # This is a simplified loop representing the AI agent's logic
        # In a full implementation, this would use OpenClaw for complex state management
        max_steps = 10
        retry_count = 0
        try:
            for step in range(max_steps):
                system_logger.info(f"Step {step + 1}/{max_steps}")
                
                # 1. Capture (Body)
                screenshot_path = await self.body.take_screenshot(f"task_step_{step}.png")
                accessibility_tree = await self.body.get_accessibility_tree()
                
                # 2. Think (Brain)
                # Load current task memory for planning context
                current_memory = self.memory_manager.load_task_memory(task_name) or {}
                
                prompt = (
                    f"Task: {task_description}\n"
                    f"History: {current_memory.get('history', 'No history available')}\n"
                    f"Current Step: {step + 1}\n"
                    "Analyze the screenshot and accessibility tree. \n"
                    "1. Provide a short summary of what you see.\n"
                    "2. Determine the next logical action to achieve the task.\n"
                    "3. Respond with a JSON object containing the action. Supported actions are:\n"
                    "   - Click: {\"action\": \"click\", \"x\": <x_coordinate>, \"y\": <y_coordinate>}\n"
                    "   - Type: {\"action\": \"type\", \"text\": \"<text_to_type>\"}\n"
                    "   - Scroll: {\"action\": \"scroll\", \"direction\": \"up\"/\"down\", \"amount\": <scroll_amount>}\n"
                    "   - Complete: {\"action\": \"complete\"}\n"
                    "   - Error/Stuck: {\"action\": \"error\", \"message\": \"<error_message>\", \"target_text\": \"<optional_text_for_ocr_fallback>\"}\n"
                    "4. If the task is complete, use the 'complete' action.\n"
                    "5. If you are stuck or encounter an error, use the 'error' action with a descriptive message."
                )
                
                analysis = await self.brain.analyze_screenshot(
                    screenshot_path, prompt, accessibility_tree
                )
                raw_response = analysis["raw_response"]
                system_logger.info(f"AI Raw Response: {raw_response[:100]}...")

                action_data = self.brain.parse_vlm_response(raw_response)
                system_logger.info(f"Parsed Action: {action_data}")

                # Update task memory with current step, URL, and AI history
                history = current_memory.get("history", [])
                history.append(f"Step {step+1}: {raw_response[:100]}")
                self.memory_manager.update_task_progress(
                    task_name, 
                    current_step=f"step_{step+1}", 
                    last_url=self.body.page.url if self.body.page else None,
                    history=history[-5:] # Keep last 5 steps for context
                )

                # 3. Act (Hands)
                action_type = action_data.get("action")

                if action_type == "click":
                    x = action_data.get("x")
                    y = action_data.get("y")
                    if x is not None and y is not None:
                        self.hands.click_humanlike(x, y)
                    else:
                        system_logger.error(f"Click action missing coordinates: {action_data}")
                        raise ValueError("Click action requires x and y coordinates.")
                elif action_type == "type":
                    text = action_data.get("text")
                    if text is not None:
                        self.hands.type_humanlike(text)
                    else:
                        system_logger.error(f"Type action missing text: {action_data}")
                        raise ValueError("Type action requires text to type.")
                elif action_type == "scroll":
                    direction = action_data.get("direction")
                    amount = action_data.get("amount")
                    if direction == "up":
                        self.hands.scroll_humanlike(amount)
                    elif direction == "down":
                        self.hands.scroll_humanlike(-amount)
                    else:
                        system_logger.error(f"Scroll action missing direction or invalid: {action_data}")
                        raise ValueError("Scroll action requires 'up' or 'down' direction.")
                elif action_type == "complete":
                    system_logger.info("Task completed successfully by VLM.")
                    self.memory_manager.update_task_progress(task_name, status="completed", current_step="end")
                    break
                elif action_type == "error":
                    error_message = action_data.get("message", "Unknown VLM error.")
                    target_text = action_data.get("target_text")
                    system_logger.warning(f"AI reported an issue: {error_message}. Initiating self-correction...")

                    if target_text:
                        system_logger.info(f"Attempting OCR fallback for target text: '{target_text}'")
                        ocr_results = self.ocr_engine.find_text_coordinates(screenshot_path, target_text)
                        if ocr_results:
                            # For simplicity, click the center of the first found text
                            bbox = ocr_results[0]["bbox"]
                            click_x = bbox["x"] + bbox["width"] // 2
                            click_y = bbox["y"] + bbox["height"] // 2
                            system_logger.info(f"OCR found '{target_text}' at ({click_x}, {click_y}). Clicking...")
                            self.hands.click_humanlike(click_x, click_y)
                            await asyncio.sleep(2) # Natural pause after OCR click
                            continue # Continue to the next step after successful OCR click
                        else:
                            system_logger.warning(f"OCR fallback failed to find '{target_text}'.")

                    if retry_count < max_retries:
                        retry_count += 1
                        system_logger.info(f"Retrying step {step+1} (Attempt {retry_count}/{max_retries})...")
                        await asyncio.sleep(5) # Wait for potential dynamic content
                        continue # Retry the same step
                    else:
                        system_logger.error("Max retries reached for self-correction. Task failed.")
                        raise Exception(f"Self-correction failed after {max_retries} retries: {error_message}")
                else:
                    system_logger.error(f"Unknown action type received from VLM: {action_type}. Raw response: {raw_response}")
                    raise ValueError(f"Unknown action type: {action_type}")
                
                await asyncio.sleep(2) # Natural pause between steps

        except Exception as e:
            system_logger.error(f"Error during task \'{task_name}\' at step {step+1}: {e}")
            self.memory_manager.update_task_progress(task_name, status="failed", last_error=str(e))
            raise # Re-raise the exception to stop execution or allow higher-level handling

    async def shutdown(self):
        """Clean up all resources."""
        await self.body.close()
        system_logger.info("System shutdown complete.")


async def main():
    """Run a sample task."""
    orchestrator = HumanAutomationOrchestrator()
    try:
        await orchestrator.startup()
        await orchestrator.perform_task("sample_login_task", "Login to the site", "https://example.com/login")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    # asyncio.run(main())
    print("Orchestrator module loaded.")
