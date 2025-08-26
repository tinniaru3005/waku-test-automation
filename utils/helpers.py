import time
import logging
import base64
from typing import Any, Dict

def wait_for_condition(condition_func, timeout: int = 30, interval: int = 1) -> bool:
    """Wait for a condition to be true"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False

def decode_base64_payload(encoded_payload: str) -> str:
    """Decode base64 encoded payload"""
    try:
        return base64.b64decode(encoded_payload).decode('utf-8')
    except Exception as e:
        logging.error(f"Failed to decode payload: {e}")
        return ""

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_automation.log')
        ]
    )