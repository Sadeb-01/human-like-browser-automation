# Phase 4: Advanced Anti-Detection, Stealth, and Networking

## Overview

Phase 4 focuses on the **"Identity"** of the automation agent. Even with perfect "Hands" (Phase 3), an agent can be detected by its network signature or browser fingerprint. This phase implements professional-grade stealth measures to ensure the agent is indistinguishable from a legitimate human user.

## Components

### Stealth Network (`stealth_network.py`)

Handles the networking footprint of the agent. Key features:

- **TLS Fingerprinting**: Uses `curl_cffi` to impersonate the JA3/TLS handshake of real browsers (Chrome, Safari, Firefox). This bypasses low-level network filters that flag standard Python `requests` or `playwright` signatures.
- **Residential Proxy Integration**: Support for rotating residential proxies to ensure IP addresses belong to home ISPs rather than datacenters.
- **Profile Rotation**: Dynamically switches between different browser profiles (e.g., Chrome 110 on Windows vs. Safari 17 on macOS) to avoid pattern detection.

### Fingerprint Manager

Provides utilities for randomizing hardware and browser attributes:

- **Viewport Randomization**: Sets common, realistic screen resolutions.
- **User-Agent Management**: Generates and rotates modern, high-reputation User-Agent strings.
- **Hardware Spoofing**: (Integrated with Phase 1) Configures the browser to report realistic CPU cores, memory, and GPU info.

## Key Techniques

### JA3 Impersonation

Most modern anti-bots (Cloudflare, Akamai) use JA3 fingerprinting to identify the underlying TLS library. Standard automation tools have distinct signatures. By using `curl_cffi`, we "impersonate" the exact handshake pattern of a specific browser version.

### Residential Proxy Strategy

Datacenter IPs are the #1 reason for immediate flagging. This module is designed to work with providers like Bright Data or Oxylabs, using backconnect proxies to ensure every session appears to originate from a unique, legitimate residential location.

## Usage

```python
from stealth_network import StealthNetwork

network = StealthNetwork()

# Perform a request that looks like it's coming from a real Chrome 110 browser
response = network.perform_stealth_request(
    "https://api.example.com/data",
    impersonate="chrome110"
)
```

## Next Steps

Phase 5 will bring everything together using the **OpenClaw** framework, creating a high-level orchestrator that uses the "Body," "Brain," "Hands," and "Identity" to complete complex, multi-step tasks autonomously.
