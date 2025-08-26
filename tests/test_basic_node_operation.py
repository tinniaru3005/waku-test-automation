import pytest
import time
import logging
from src.waku_client import WakuClient

@pytest.mark.basic
class TestBasicNodeOperation:
    """Test Suite 1: Basic Node Operation"""
    
    def test_start_single_waku_node(self, docker_manager, node1_config):
        """Test starting a single Waku node"""
        # Start the node
        container_id = docker_manager.start_waku_node(
            node1_config["name"],
            node1_config["ports"], 
            node1_config["extip"]
        )
        
        assert container_id is not None
        assert node1_config["name"] in docker_manager.containers
        
        # Wait for node to be ready
        time.sleep(15)
    
    def test_verify_node_debug_info(self, docker_manager, node1_config):
        """Test node debug information accessibility"""
        # Ensure node is running
        if node1_config["name"] not in docker_manager.containers:
            docker_manager.start_waku_node(
                node1_config["name"],
                node1_config["ports"],
                node1_config["extip"] 
            )
            time.sleep(15)
        
        # Create client and get debug info
        client = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        debug_info = client.get_debug_info()
        
        assert debug_info is not None
        assert "enrUri" in debug_info
        assert debug_info["enrUri"] != ""
        
        # Store ENR URI for later use
        self.enr_uri = debug_info["enrUri"]
        logging.info(f"Node ENR URI: {self.enr_uri}")
    
    def test_subscribe_to_topic(self, docker_manager, node1_config, test_topic):
        """Test subscribing to a relay topic"""
        client = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        
        # Subscribe to topic
        success = client.subscribe_to_topic([test_topic])
        assert success, "Failed to subscribe to topic"
    
    def test_publish_message(self, docker_manager, node1_config, test_topic, test_message):
        """Test publishing a message"""
        client = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        
        # Publish message
        success = client.publish_message(test_topic, test_message)
        assert success, "Failed to publish message"
    
    def test_confirm_message_publication(self, docker_manager, node1_config, 
                                       test_topic, test_message):
        """Test confirming message was published"""
        client = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        
        # Wait a bit for message to be processed
        time.sleep(3)
        
        # Get messages
        messages = client.get_messages(test_topic)
        
        assert len(messages) > 0, "No messages found"
        
        # Verify our message is there
        from utils.helpers import decode_base64_payload
        found_message = False
        for msg in messages:
            if "payload" in msg:
                decoded = decode_base64_payload(msg["payload"])
                if decoded == test_message:
                    found_message = True
                    break
        
        assert found_message, f"Published message '{test_message}' not found in retrieved messages"