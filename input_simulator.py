"""
Phase 3: Advanced Human-Like Input Simulation (The "Hands")

This module implements OS-level input simulation using realistic human-like 
movement patterns, including Bezier curves and variable keystroke timing.
"""

import random
import time
import math
from typing import Tuple, List, Optional

try:
    import pyautogui
except ImportError:
    class MockPyAutoGUI:
        FAILSAFE = True
        def position(self): return (0, 0)
        def moveTo(self, *args, **kwargs): pass
        def mouseDown(self, *args, **kwargs): pass
        def mouseUp(self, *args, **kwargs): pass
        def write(self, *args, **kwargs): pass
        def scroll(self, *args, **kwargs): pass
    pyautogui = MockPyAutoGUI()
from logger import system_logger
from config import DEFAULT_CONFIG


class InputSimulator:
    """
    Simulates human-like mouse and keyboard interactions at the OS level.
    
    This is the "Hands" component - bypassing synthetic browser events.
    """
    
    def __init__(self, config=DEFAULT_CONFIG.input_config):
        self.config = config
        # Fail-safe: move mouse to corner to abort
        pyautogui.FAILSAFE = True
        system_logger.info("Input Simulator initialized with OS-level simulation.")

    def _generate_bezier_curve(
        self, start: Tuple[int, int], end: Tuple[int, int], points_count: int = 50
    ) -> List[Tuple[int, int]]:
        """
        Generate a cubic Bezier curve between two points for realistic movement.
        """
        x1, y1 = start
        x2, y2 = end
        
        # Random control points to create natural variance
        ctrl1_x = x1 + (x2 - x1) * random.uniform(0.1, 0.4)
        ctrl1_y = y1 + (y2 - y1) * random.uniform(0.1, 0.9)
        ctrl2_x = x1 + (x2 - x1) * random.uniform(0.6, 0.9)
        ctrl2_y = y1 + (y2 - y1) * random.uniform(0.1, 0.9)
        
        curve = []
        for i in range(points_count):
            t = i / float(points_count - 1)
            # Cubic Bezier formula
            x = (1-t)**3 * x1 + 3*(1-t)**2 * t * ctrl1_x + 3*(1-t) * t**2 * ctrl2_x + t**3 * x2
            y = (1-t)**3 * y1 + 3*(1-t)**2 * t * ctrl1_y + 3*(1-t) * t**2 * ctrl2_y + t**3 * y2
            curve.append((int(x), int(y)))
            
        return curve

    def move_mouse_humanlike(self, x: int, y: int):
        """
        Move the mouse to (x, y) using a human-like trajectory.
        """
        start_pos = pyautogui.position()
        target_pos = (x, y)
        
        # Calculate distance to determine speed and number of points
        distance = math.sqrt((target_pos[0] - start_pos[0])**2 + (target_pos[1] - start_pos[1])**2)
        if distance < 5:
            return # Already there or too close
            
        points_count = max(10, int(distance / 10 * (1.5 - self.config.mouse_speed)))
        curve = self._generate_bezier_curve(start_pos, target_pos, points_count)
        
        system_logger.debug(f"Moving mouse to ({x}, {y}) over {len(curve)} points.")
        
        for point in curve:
            pyautogui.moveTo(point[0], point[1])
            # Small variable delay between points for jitter
            time.sleep(random.uniform(0.001, 0.005) * (1.1 - self.config.mouse_speed))

    def click_humanlike(self, x: int, y: int, button: str = 'left'):
        """
        Move to and click a location with human-like timing.
        """
        self.move_mouse_humanlike(x, y)
        
        # Small delay before pressing
        time.sleep(random.uniform(0.1, 0.3))
        
        # Press and release with variable duration
        pyautogui.mouseDown(button=button)
        time.sleep(random.uniform(0.05, 0.15))
        pyautogui.mouseUp(button=button)
        
        system_logger.info(f"Human-like click performed at ({x}, {y})")

    def type_humanlike(self, text: str):
        """
        Type text with variable delays between keystrokes to mimic human typing.
        """
        system_logger.info(f"Typing text: {text[:20]}...")
        
        for char in text:
            pyautogui.write(char)
            # Realistic typing delay (average 150-300ms per char with variance)
            delay = random.uniform(0.05, 0.25) * (1.2 - self.config.typing_speed)
            
            # Simulate "thinking" pauses for longer strings or specific characters
            if char in ".,!? ":
                delay += random.uniform(0.1, 0.4)
            if random.random() < 0.05: # 5% chance of a longer pause
                delay += random.uniform(0.5, 1.2)
                
            time.sleep(delay)

    def scroll_humanlike(self, clicks: int):
        """
        Scroll the page with human-like rhythm.
        """
        direction = 1 if clicks > 0 else -1
        total_clicks = abs(clicks)
        
        system_logger.info(f"Scrolling {'down' if clicks < 0 else 'up'} {total_clicks} clicks.")
        
        for _ in range(total_clicks):
            pyautogui.scroll(direction * 100)
            time.sleep(random.uniform(0.05, 0.2))


if __name__ == "__main__":
    # Test simulation (be careful, this controls your real mouse!)
    simulator = InputSimulator()
    print("Testing mouse movement in 3 seconds...")
    time.sleep(3)
    # simulator.move_mouse_humanlike(500, 500)
    print("Test complete.")
