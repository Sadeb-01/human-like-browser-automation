import asyncio
import os
from browser_controller import BrowserController

async def test_xvfb():
    print("Testing Xvfb integration...")
    # Initialize BrowserController with Xvfb enabled
    controller = BrowserController(headless=False)
    
    try:
        # We'll use a custom display to avoid conflicts
        await controller.initialize(
            use_xvfb=True, 
            xvfb_display=":100", 
            xvfb_width=1280, 
            xvfb_height=720
        )
        
        print(f"DISPLAY environment variable: {os.environ.get('DISPLAY')}")
        assert os.environ.get("DISPLAY") == ":100"
        
        print("Xvfb integration test passed!")
        
    except Exception as e:
        print(f"Xvfb integration test failed: {e}")
    finally:
        await controller.close()

if __name__ == "__main__":
    asyncio.run(test_xvfb())
