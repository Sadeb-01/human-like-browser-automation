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

All core development phases (Phase 1-5) are **Completed**.

## Feature Roadmap

This section outlines the current status of key features and planned upgrades.

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Core System (Phases 1-5)** | ✅ Completed | All foundational components are implemented and integrated. |
| **Virtual Display Integration** | ⬜ To Do | Integration with Xvfb/VNC for VPS deployment. |
| **Docker Containerization** | ⬜ To Do | Create Dockerfiles for easy deployment. |
| **Advanced Proxy Management** | ⬜ To Do | Implement proxy rotation and health checks. |
| **TLS/HTTP2 Fingerprint Rotation** | ✅ Completed | Implemented via `curl_cffi` in Phase 4. |
| **Canvas/WebGL Noise** | ⬜ To Do | Advanced hardware fingerprint spoofing. |
| **Font Fingerprint Randomization** | ⬜ To Do | Further anti-detection measures. |
| **Self-Correction Logic** | ⬜ To Do | AI-driven error recovery and adaptive strategies. |
| **Local VLM Hosting** | ⬜ To Do | Option to run DeepSeek-VL2 locally for performance/cost. |
| **OpenClaw Full Integration** | ✅ Completed | Orchestration framework is in place. |
| **Comprehensive Test Suite** | ⬜ To Do | Automated tests for reliability and regression. |
| **CI/CD Pipeline** | ⬜ To Do | Automated build, test, and deployment. |

## Deployment Guide

For detailed instructions on deploying and upgrading this system to a production environment, including infrastructure requirements and advanced stealth techniques, please refer to the [DEPLOYMENT.md](docs/DEPLOYMENT.md) file in the `docs/` directory.

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
