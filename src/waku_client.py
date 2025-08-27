import requests
import time
import logging
from typing import Dict, Any, Optional, List
import base64
import json

class WakuClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def get_debug_info(self) -> Dict[str, Any]:
        """Get node debug information"""
        try:
            response = self.session.get(
                f"{self.base_url}/debug/v1/info",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to get debug info: {e}")
            raise
    
    def get_enr_uri(self) -> str:
        """Extract ENR URI from debug info"""
        debug_info = self.get_debug_info()
        return debug_info.get('enrUri', '')
    
    def subscribe_to_topic(self, topics: List[str]) -> bool:
        """Subscribe to relay topics"""
        try:
            response = self.session.post(
                f"{self.base_url}/relay/v1/auto/subscriptions",
                headers={
                    "accept": "text/plain",
                    "content-type": "application/json"
                },
                json=topics,
                timeout=self.timeout
            )
            response.raise_for_status()
            logging.info(f"Subscribed to topics: {topics}")
            return True
        except requests.RequestException as e:
            logging.error(f"Failed to subscribe to topics: {e}")
            return False
    
    def publish_message(self, content_topic: str, payload: str, 
                       timestamp: Optional[int] = None) -> bool:
        """Publish a message to a topic"""
        try:
            encoded_payload = base64.b64encode(payload.encode()).decode()
            
            message_data = {
                "payload": encoded_payload,
                "contentTopic": content_topic
            }
            
            if timestamp:
                message_data["timestamp"] = timestamp
            
            response = self.session.post(
                f"{self.base_url}/relay/v1/auto/messages",
                headers={"content-type": "application/json"},
                json=message_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            logging.info(f"Published message to {content_topic}")
            return True
        except requests.RequestException as e:
            logging.error(f"Failed to publish message: {e}")
            return False
    
    def get_messages(self, content_topic: str) -> List[Dict[str, Any]]:
        """Get messages from a topic"""
        try:
            # URL encode the topic
            encoded_topic = requests.utils.quote(content_topic, safe='')
            
            response = self.session.get(
                f"{self.base_url}/relay/v1/auto/messages/{encoded_topic}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to get messages: {e}")
            return []
    
    def get_peers(self) -> List[Dict[str, Any]]:
        """Get connected peers"""
        try:
            response = self.session.get(
                f"{self.base_url}/admin/v1/peers",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Failed to get peers: {e}")
            return []
    
    def wait_for_peer_connection(self, expected_peer_count: int = 1, 
                                max_wait: int = 60) -> bool:
        """Wait for peer connections to be established"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            peers = self.get_peers()
            if len(peers) >= expected_peer_count:
                logging.info(f"Found {len(peers)} peer(s)")
                return True
            time.sleep(2)
        
        logging.warning(f"Timeout waiting for peer connections")
        return False