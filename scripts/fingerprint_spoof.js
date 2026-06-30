/**
 * Advanced Canvas and WebGL Fingerprint Spoofing Script
 * 
 * This script injects subtle noise into Canvas and WebGL rendering to create 
 * a unique but non-suspicious hardware fingerprint for every session.
 */

(function() {
    // Helper to generate a small random float between -range and range
    const getNoise = (range = 0.00001) => (Math.random() * 2 - 1) * range;

    // 1. Canvas Spoofing
    const originalGetImageData = HTMLCanvasElement.prototype.getContext('2d').constructor.prototype.getImageData;
    HTMLCanvasElement.prototype.getContext('2d').constructor.prototype.getImageData = function(x, y, width, height) {
        const imageData = originalGetImageData.apply(this, arguments);
        const data = imageData.data;
        // Inject very subtle noise into the pixel data
        for (let i = 0; i < data.length; i += 4) {
            // Only modify a small percentage of pixels to remain "human-like"
            if (Math.random() < 0.01) {
                data[i] = data[i] + (Math.random() > 0.5 ? 1 : -1);     // R
                data[i+1] = data[i+1] + (Math.random() > 0.5 ? 1 : -1); // G
                data[i+2] = data[i+2] + (Math.random() > 0.5 ? 1 : -1); // B
            }
        }
        return imageData;
    };

    // 2. WebGL Spoofing
    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // Spoof common WebGL fingerprinting parameters
        if (parameter === 37445) return 'Intel Open Source Technology Center'; // UNMASKED_VENDOR_WEBGL
        if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 620 (Kaby Lake GT2)'; // UNMASKED_RENDERER_WEBGL
        return originalGetParameter.apply(this, arguments);
    };

    const originalReadPixels = WebGLRenderingContext.prototype.readPixels;
    WebGLRenderingContext.prototype.readPixels = function(x, y, width, height, format, type, pixels) {
        originalReadPixels.apply(this, arguments);
        // Add subtle noise to WebGL pixels
        for (let i = 0; i < pixels.length; i++) {
            if (Math.random() < 0.01) {
                pixels[i] = pixels[i] + (Math.random() > 0.5 ? 1 : -1);
            }
        }
    };

    // 3. Font Fingerprint Spoofing
    const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth').get;
    const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight').get;

    Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
        get: function() {
            const width = originalOffsetWidth.apply(this);
            // Add subtle noise to font-related measurements
            if (this.style && this.style.fontFamily) {
                return width + (Math.random() > 0.5 ? 1 : 0);
            }
            return width;
        }
    });

    Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
        get: function() {
            const height = originalOffsetHeight.apply(this);
            if (this.style && this.style.fontFamily) {
                return height + (Math.random() > 0.5 ? 1 : 0);
            }
            return height;
        }
    });

    console.log("✓ Canvas/WebGL/Font Fingerprint Spoofing Active");
})();
