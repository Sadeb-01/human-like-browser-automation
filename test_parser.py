import json
from vlm_client import VLMClient

def test_parsing():
    client = VLMClient()
    
    test_cases = [
        {
            "name": "Click Action",
            "response": "I see the login button. {\"action\": \"click\", \"x\": 100, \"y\": 200}",
            "expected": {"action": "click", "x": 100, "y": 200}
        },
        {
            "name": "Type Action",
            "response": "I will type the username. {\"action\": \"type\", \"text\": \"my_username\"}",
            "expected": {"action": "type", "text": "my_username"}
        },
        {
            "name": "Scroll Action",
            "response": "Scrolling down for more content. {\"action\": \"scroll\", \"direction\": \"down\", \"amount\": 5}",
            "expected": {"action": "scroll", "direction": "down", "amount": 5}
        },
        {
            "name": "Complete Action",
            "response": "The task is done. {\"action\": \"complete\"}",
            "expected": {"action": "complete"}
        },
        {
            "name": "Error Action",
            "response": "Something went wrong. {\"action\": \"error\", \"message\": \"Button not found\"}",
            "expected": {"action": "error", "message": "Button not found"}
        },
        {
            "name": "Fallback Complete",
            "response": "TASK_COMPLETE",
            "expected": {"action": "complete"}
        },
        {
            "name": "Fallback Error",
            "response": "I am stuck and cannot find the element.",
            "expected": {"action": "error", "message": "I am stuck and cannot find the element."}
        }
    ]
    
    for case in test_cases:
        result = client.parse_vlm_response(case["response"])
        print(f"Test: {case['name']}")
        print(f"  Input: {case['response']}")
        print(f"  Result: {result}")
        assert result == case["expected"], f"Failed {case['name']}: expected {case['expected']}, got {result}"
        print(f"  ✓ Passed")

if __name__ == "__main__":
    try:
        test_parsing()
        print("\nAll parser tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
