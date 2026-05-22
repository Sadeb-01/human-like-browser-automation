# Human-Like Browser Automation System

A sophisticated, non-headless browser automation system designed to perform complex web interactions while evading modern bot detection mechanisms. This system combines a custom Chromium build, OS-level input simulation, and advanced AI (DeepSeek-VL2) for visual understanding.

## Project Architecture

The system is built on a multi-layered architecture:

- **The "Body":** Custom Chromium build with anti-detection patches
- **The "Hands":** OS-level input simulation for human-like interactions
- **The "Brain":** DeepSeek-VL2 for visual understanding and decision-making
- **The "Orchestrator":** OpenClaw framework for task management and AI coordination

## Development Phases

1. **Phase 1:** Basic browser control and screenshot capture
2. **Phase 2:** DeepSeek-VL2 integration for visual element grounding
3. **Phase 3:** OS-level human-like input simulation
4. **Phase 4:** Anti-detection and stealth enhancements
5. **Phase 5:** OpenClaw integration and advanced AI orchestration

## Current Status

**Phase 1 - In Progress:** Setting up basic browser control with Playwright and screenshot capture functionality.

## Installation

```bash
git clone https://github.com/Sadeb-01/human-like-browser-automation.git
cd human-like-browser-automation
pip install -r requirements.txt
```

## Requirements

- Python 3.11+
- Playwright
- DeepSeek API key (for Phase 2+)
- Residential proxy credentials (for Phase 4+)

## Usage

See `docs/` directory for detailed usage instructions for each phase.

## License

MIT

## Author

Manus AI - Autonomous AI Agent Development
