# Phase 1: Basic Browser Control & Screenshot Capture

## Overview

Phase 1 establishes the foundation for the browser automation system. It provides:

- Non-headless browser initialization with Playwright
- Screenshot capture functionality
- Accessibility tree extraction for later VLM integration
- Configuration management system
- Logging infrastructure

## Components

### BrowserController (`browser_controller.py`)

The main class for managing browser instances. Key methods:

- `initialize()`: Launch browser and create context
- `navigate_to(url)`: Navigate to a URL
- `take_screenshot()`: Capture full-page screenshot
- `get_accessibility_tree()`: Extract DOM elements with coordinates
- `close()`: Clean up resources

### Configuration (`config.py`)

Manages all system settings through dataclasses:

- `BrowserConfig`: Browser behavior settings
- `VLMConfig`: Vision-Language Model settings (for Phase 2)
- `InputConfig`: Input simulation settings (for Phase 3)
- `AntiDetectionConfig`: Anti-detection settings (for Phase 4)
- `SystemConfig`: Master configuration

### Logger (`logger.py`)

Provides centralized logging to console and file.

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update settings:

```bash
cp .env.example .env
```

### 3. Run Phase 1 Example

```bash
python browser_controller.py
```

This will:
1. Launch a non-headless Chromium browser
2. Navigate to https://example.com
3. Take a screenshot
4. Extract the accessibility tree
5. Display element information

## Key Features

### Non-Headless Mode

The browser runs with a visible window (`headless=False`), making it easier to debug and observe behavior.

### Anti-Detection Measures (Phase 1)

- Disables the `AutomationControlled` blink feature
- Sets realistic user agent strings
- Configures proper viewport and locale

### Accessibility Tree Extraction

The `get_accessibility_tree()` method extracts:
- Element tags and roles
- Text content and ARIA labels
- Bounding box coordinates (x, y, width, height)
- Element IDs and classes

This data will be used by the VLM in Phase 2 for precise element grounding.

## Testing

To test Phase 1 with different websites:

```python
import asyncio
from browser_controller import BrowserController

async def test_website():
    controller = BrowserController(headless=False)
    try:
        await controller.initialize()
        await controller.navigate_to("https://www.google.com")
        await controller.take_screenshot("google.png")
        tree = await controller.get_accessibility_tree()
        print(f"Found {len(tree['elements'])} elements")
    finally:
        await controller.close()

asyncio.run(test_website())
```

## Next Steps

Phase 2 will integrate DeepSeek-VL2 to analyze screenshots and accessibility trees, enabling the system to:
- Identify UI elements visually
- Understand page context
- Ground coordinates for interaction

## Troubleshooting

### Browser Won't Launch

Ensure Playwright browsers are installed:
```bash
playwright install
```

### Screenshots Not Saving

Check that the `./screenshots` directory exists and is writable.

### Accessibility Tree Empty

Some websites may have minimal semantic HTML. The VLM in Phase 2 will handle visual element detection as a fallback.

## Architecture Notes

Phase 1 implements the **"Body"** component of the system:
- Provides the browser engine foundation
- Establishes non-headless operation
- Captures visual and structural data for AI analysis

The accessibility tree extraction is crucial for Phase 2, as it provides structured data that the VLM can correlate with visual information from screenshots.
