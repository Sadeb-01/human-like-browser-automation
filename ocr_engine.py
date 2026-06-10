try:
    import easyocr
except ImportError:
    class MockEasyOCR:
        def Reader(self, *args, **kwargs):
            class MockReader:
                def readtext(self, *args, **kwargs): return []
            return MockReader()
    easyocr = MockEasyOCR()
import numpy as np
try:
    from PIL import Image
except ImportError:
    class Image: pass
from pathlib import Path
from typing import List, Dict, Any

from logger import system_logger

class OCREngine:
    """
    Provides OCR capabilities as a fallback for the VLM.
    """

    def __init__(self, languages: List[str] = ['en']):
        self.languages = languages
        self.reader = None
        system_logger.info(f"OCREngine initialized with languages: {self.languages}")

    def _initialize_reader(self):
        """Lazy initialization of the EasyOCR reader."""
        if self.reader is None:
            system_logger.info("Initializing EasyOCR reader (this may take a moment)...")
            self.reader = easyocr.Reader(self.languages, gpu=False) # GPU disabled for sandbox compatibility

    def extract_text(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts text and coordinates from an image.
        """
        self._initialize_reader()
        system_logger.info(f"Performing OCR on image: {image_path}")
        
        try:
            results = self.reader.readtext(str(image_path))
            
            extracted_data = []
            for (bbox, text, prob) in results:
                # bbox is [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
                x_min = min([p[0] for p in bbox])
                y_min = min([p[1] for p in bbox])
                x_max = max([p[0] for p in bbox])
                y_max = max([p[1] for p in bbox])
                
                extracted_data.append({
                    "text": text,
                    "confidence": float(prob),
                    "bbox": {
                        "x": int(x_min),
                        "y": int(y_min),
                        "width": int(x_max - x_min),
                        "height": int(y_max - y_min)
                    }
                })
            
            system_logger.info(f"OCR extracted {len(extracted_data)} text segments.")
            return extracted_data
        except Exception as e:
            system_logger.error(f"Error during OCR extraction: {e}")
            return []

    def find_text_coordinates(self, image_path: Path, target_text: str) -> List[Dict[str, Any]]:
        """
        Finds the coordinates of a specific text in an image.
        """
        all_text = self.extract_text(image_path)
        matches = [item for item in all_text if target_text.lower() in item["text"].lower()]
        
        if matches:
            system_logger.info(f"Found {len(matches)} matches for text \'{target_text}\'.")
        else:
            system_logger.info(f"No matches found for text \'{target_text}\'.")
            
        return matches
