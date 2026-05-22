# Phase 2: DeepSeek-VL2 Integration for Visual Element Grounding

## Overview

Phase 2 introduces the **"Brain"** of the system: the Vision-Language Model (VLM) integration. This layer allows the automation agent to "see" the webpage, understand its context, and pinpoint the exact coordinates of UI elements for interaction.

## Components

### VLM Client (`vlm_client.py`)

A specialized client for interacting with multimodal models, primarily **DeepSeek-VL2**. Key features:

- **Screenshot Analysis**: Sends captured images to the VLM with specific instructions.
- **Contextual Grounding**: Combines visual data with the accessibility tree from Phase 1 to improve accuracy.
- **Coordinate Extraction**: Identifies bounding boxes for buttons, input fields, and other interactive elements.

## Configuration

To enable Phase 2, you must provide a DeepSeek API key in your `.env` file:

```env
DEEPSEEK_API_KEY=your_api_key_here
VLM_MODEL=deepseek-vl2
```

## How it Works

1. **Capture**: The `BrowserController` (Phase 1) navigates to a page and takes a high-resolution screenshot.
2. **Describe**: The `VLMClient` sends the screenshot along with a prompt (e.g., "Find the search bar") to DeepSeek.
3. **Analyze**: DeepSeek processes the image, using its spatial reasoning to locate the requested element.
4. **Ground**: The model returns the coordinates, which are then used to guide the "Hands" (Phase 3) for interaction.

## Why DeepSeek-VL2?

DeepSeek-VL2 is chosen for its:
- **Spatial Precision**: Excellent at identifying exact pixel coordinates.
- **OCR Capability**: Can read text within images accurately, even in complex layouts.
- **Cost-Efficiency**: Significantly lower cost per token compared to other top-tier VLMs.

## Next Steps

Phase 3 will implement the **"Hands"** of the system: OS-level input simulation. This will use the coordinates provided by the VLM to perform actual mouse movements and keystrokes that mimic human behavior.
