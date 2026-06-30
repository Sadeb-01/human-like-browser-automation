# Use the official Playwright image as the base
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:99
ENV USE_XVFB=true

# Install system dependencies for Xvfb, Tkinter, and EasyOCR
RUN apt-get update && apt-get install -y \
    xvfb \
    python3-tk \
    python3-dev \
    libx11-dev \
    libxkbcommon-x11-0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy the rest of the application code
COPY . .

# Create directory for screenshots
RUN mkdir -p screenshots

# Command to run the application
# We use a shell script to start Xvfb and then run the orchestrator
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x24 &\npython3 orchestrator.py' > /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
