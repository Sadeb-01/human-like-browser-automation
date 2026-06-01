# Phase 5: Human-Like Automation Orchestrator

## Overview

Phase 5 is the final integration phase where the **"Body," "Brain," "Hands,"** and **"Identity"** are unified into a single, cohesive system. This phase implements the **Orchestrator**, which manages the high-level logic and state transitions required for autonomous task completion.

## Components

### Orchestrator (`orchestrator.py`)

The central nervous system of the project. Key responsibilities:

- **Component Coordination**: Manages the lifecycle and communication between the Browser Controller, VLM Client, Input Simulator, and Stealth Network.
- **Task Execution Loop**: Implements the "Observe-Think-Act" loop common in advanced AI agents.
- **State Management**: (Integrated with OpenClaw) Maintains the history of actions and observations to ensure progress toward the goal.
- **Error Recovery**: Handles unexpected UI changes or network issues by consulting the VLM for new strategies.

## The "Observe-Think-Act" Loop

1. **Observe (Body)**: Capture a full-page screenshot and extract the accessibility tree.
2. **Think (Brain)**: Send the visual and structural data to DeepSeek-VL2 with the current task description. The AI determines the next logical step and identifies target coordinates.
3. **Act (Hands)**: The Input Simulator executes the move and click/type actions using human-like trajectories and timing.
4. **Verify (Identity)**: Throughout the process, the Stealth Network ensures all communications and fingerprints remain clean and untraceable.

## Integration with OpenClaw

The orchestrator is designed to be compatible with the **OpenClaw** framework. OpenClaw provides the high-level "Skill" system and "Memory" needed for long-running or highly complex tasks that require multiple page navigations and persistent context.

## Usage

```python
import asyncio
from orchestrator import HumanAutomationOrchestrator

async def main():
    orchestrator = HumanAutomationOrchestrator()
    try:
        await orchestrator.startup()
        # Example task - uncomment and modify as needed
        # await orchestrator.perform_task(
        #     "Navigate to the search page, type \'AI Agents\', and click the first result.",
        #     "https://www.example.com"
        # )
    finally:
        await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

**Note on `pyautogui` and Headless Environments:**

The `pyautogui` library, used for OS-level input simulation, relies on a graphical display server (X server) and `tkinter`. In headless environments (like many CI/CD pipelines or remote servers), this dependency may cause issues. If you encounter errors related to `Xlib` or `tkinter`, you may need to:

1.  Install a virtual display server (e.g., Xvfb) and run your application within it.
2.  Install `tkinter` (`sudo apt-get install python3-tk python3-dev` on Debian/Ubuntu).

For full functionality of the `InputSimulator`, a graphical environment is required. If running in a headless setup, consider disabling or mocking `InputSimulator` functionality, or ensure a virtual display is configured.

## Summary of the Completed System

| Component | Layer | Technology | Role |
| :--- | :--- | :--- | :--- |
| **Body** | Engine | Custom Chromium / Playwright | Core browser environment and data capture. |
| **Brain** | Intelligence | DeepSeek-VL2 / OpenClaw | Visual understanding and task planning. |
| **Hands** | Interaction | PyAutoGUI / Bezier Curves | OS-level, non-synthetic human-like input. |
| **Identity** | Stealth | `curl_cffi` / Residential Proxies | Network and fingerprint anti-detection. |

This architecture provides a complete, professional-grade solution for human-like web automation that can operate effectively even in highly protected environments.
