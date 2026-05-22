# Phase 3: Advanced Human-Like Input Simulation (The "Hands")

## Overview

Phase 3 implements the **"Hands"** of the system. Instead of using detectable JavaScript events (like `element.click()`), this module simulates physical hardware interactions at the OS level. This is critical for bypassing modern bot detection that monitors event properties and timing.

## Components

### Input Simulator (`input_simulator.py`)

A high-fidelity simulation layer using **PyAutoGUI**. Key features:

- **Bezier Curve Trajectories**: Mouse movements follow natural, non-linear paths instead of robotic straight lines.
- **Variable Speed & Jitter**: Movements include subtle speed variations and micro-jitters characteristic of human motor control.
- **Natural Typing Rhythm**: Keystrokes have variable delays, with longer pauses for punctuation and occasional "thinking" breaks.
- **OS-Level Injection**: Clicks and keys are injected into the system input buffer, making them appear as genuine hardware events to the browser.

## Key Algorithms

### Cubic Bezier Curves

We use cubic Bezier curves with randomized control points to generate trajectories. This ensures that no two movements to the same target are identical, a key indicator used by anti-bot systems.

### Typing Variance

The typing engine simulates a realistic "Words Per Minute" (WPM) with a standard deviation. It also adds extra delays after specific characters (like periods or commas) to mimic the way humans process language while typing.

## Usage

```python
from input_simulator import InputSimulator

simulator = InputSimulator()

# Move and click with human-like timing
simulator.click_humanlike(x=500, y=300)

# Type text with realistic delays
simulator.type_humanlike("Hello, this is a human typing.")
```

## Security & Safety

- **Fail-Safe**: Moving the mouse to any corner of the screen will immediately abort the automation (PyAutoGUI feature).
- **Non-Synthetic**: By avoiding the `isTrusted` property issues in browser events, we bypass a major detection vector.

## Next Steps

Phase 4 will focus on **Stealth & Networking**, including residential proxy integration, TLS fingerprinting, and deeper browser-level patches to ensure the "Identity" of the agent is as realistic as its "Hands."
