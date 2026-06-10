import asyncio
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
from orchestrator import HumanAutomationOrchestrator

class TestOCRFallback(unittest.IsolatedAsyncioTestCase):
    @patch('orchestrator.BrowserController')
    @patch('orchestrator.VLMClient')
    @patch('orchestrator.InputSimulator')
    @patch('orchestrator.StealthNetwork')
    @patch('orchestrator.TaskMemoryManager')
    @patch('orchestrator.OCREngine')
    async def test_ocr_fallback_success(self, MockOCR, MockMemory, MockStealth, MockInput, MockVLM, MockBody):
        # Setup mocks
        orchestrator = HumanAutomationOrchestrator()
        
        async def async_none(*args, **kwargs): return None
        async def async_path(*args, **kwargs): return Path("dummy.png")
        async def async_dict(*args, **kwargs): return {}
        
        orchestrator.body.navigate_to = async_none
        orchestrator.body.take_screenshot = async_path
        orchestrator.body.get_accessibility_tree = async_dict
        orchestrator.body.page = MagicMock()
        orchestrator.body.page.url = "http://example.com"
        
        # Mock VLM returning an error with target_text
        orchestrator.brain.parse_vlm_response = MagicMock()
        
        # Mock OCR finding the text
        orchestrator.ocr_engine.find_text_coordinates = MagicMock(return_value=[{"bbox": {"x": 100, "y": 200, "width": 50, "height": 20}}])
        
        # We need to stop the loop after one step or mock the next step to complete
        # Let's mock the calls
        async def mock_analyze(*args, **kwargs):
            if not hasattr(mock_analyze, 'call_count'): mock_analyze.call_count = 0
            mock_analyze.call_count += 1
            if mock_analyze.call_count == 1:
                return {"raw_response": "Error response"}
            return {"raw_response": "{\"action\": \"complete\"}"}
        
        orchestrator.brain.analyze_screenshot = mock_analyze
        
        orchestrator.brain.parse_vlm_response.side_effect = [
            {"action": "error", "message": "Not found", "target_text": "Login"},
            {"action": "complete"}
        ]
        
        await orchestrator.perform_task("test_task", "Test OCR Fallback", "http://example.com")
        
        # Verify OCR was called
        orchestrator.ocr_engine.find_text_coordinates.assert_called_with(Path("dummy.png"), "Login")
        # Verify click was performed at the correct coordinates (100 + 50//2, 200 + 20//2) = (125, 210)
        orchestrator.hands.click_humanlike.assert_called_with(125, 210)

if __name__ == "__main__":
    unittest.main()
