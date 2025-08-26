import pytest
import time
import logging
from src.waku_client import WakuClient

@pytest.mark.advanced
class TestInterNodeCommunication:
    """Test Suite 2: Inter-Node Communication"""
    
    @pytest.fixture(autouse=True)
    def setup_class_data(self):
        """Initialize class data"""
        self.node1_enr = None
    
    def test_create_docker_network(self, docker_manager):
        """Create Docker network for node communication"""
        docker_manager.create_network("waku", "172.18.0.0/16", "172.18.0.1")
        assert "waku" in docker_manager.networks
    
    def test_setup_first_node(self, docker_manager, node1_config, test_topic):
        """Setup first node (repeat of Test Suite 1)"""
        # Start node1
        container_id = docker_manager.start_waku_node(
            node1_config["name"],
            node1_config["ports"],
            node1_config["extip"]
        )
        
        assert container_id is not None
        
        # Connect to network first
        docker_manager.connect_to_network(
            node1_config["name"], 
            "waku", 
            node1_config["extip"]
        )
        
        # Wait longer for node to be fully ready
        time.sleep(20)
        
        # Get ENR URI and store it
        client = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        debug_info = client.get_debug_info()
        self.node1_enr = debug_info["enrUri"]
        logging.info(f"Node1 ENR: {self.node1_enr}")
        
        # Subscribe to topic
        success = client.subscribe_to_topic([test_topic])
        assert success
    
    def test_start_second_node(self, docker_manager, node1_config, node2_config):
        """Start second node with bootstrap"""
        # Ensure we have the ENR URI from node1
        if not self.node1_enr:
            client = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
            debug_info = client.get_debug_info()
            self.node1_enr = debug_info["enrUri"]
        
        # Start node2 with bootstrap
        container_id = docker_manager.start_waku_node(
            node2_config["name"],
            node2_config["ports"],
            node2_config["extip"],
            bootstrap_node=self.node1_enr
        )
        
        assert container_id is not None
        
        # Connect node2 to network
        docker_manager.connect_to_network(
            node2_config["name"],
            "waku", 
            node2_config["extip"]
        )
        
        # Wait for node to be ready and connect
        time.sleep(20)
    
    def test_verify_autoconnection(self, docker_manager, node1_config, node2_config):
        """Verify nodes have connected to each other"""
        client1 = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        client2 = WakuClient(f"http://127.0.0.1:{node2_config['ports']['rest']}")
        
        # Wait for peer connections with longer timeout
        max_wait = 120  # 2 minutes
        connected = False
        
        for i in range(max_wait // 10):
            peers1 = client1.get_peers()
            peers2 = client2.get_peers()
            
            logging.info(f"Attempt {i+1}: Node1 peers: {len(peers1)}, Node2 peers: {len(peers2)}")
            
            if len(peers1) >= 1 and len(peers2) >= 1:
                connected = True
                break
                
            time.sleep(10)
        
        if not connected:
            # Try to diagnose the issue
            logging.error("Nodes failed to connect. Checking debug info...")
            try:
                debug1 = client1.get_debug_info()
                debug2 = client2.get_debug_info()
                logging.error(f"Node1 info: {debug1}")
                logging.error(f"Node2 info: {debug2}")
            except Exception as e:
                logging.error(f"Failed to get debug info: {e}")
        
        assert connected, "Nodes failed to connect to each other within timeout"
        
        logging.info(f"Successfully connected - Node1 peers: {len(peers1)}, Node2 peers: {len(peers2)}")
    
    def test_subscribe_node2_to_topic(self, docker_manager, node2_config, test_topic):
        """Subscribe node2 to the same topic as node1"""
        client2 = WakuClient(f"http://127.0.0.1:{node2_config['ports']['rest']}")
        
        success = client2.subscribe_to_topic([test_topic])
        assert success, "Failed to subscribe node2 to topic"
        
        # Wait for subscription to propagate across the network
        time.sleep(10)
    
    def test_message_transmission_between_nodes(self, docker_manager, node1_config, 
                                              node2_config, test_topic):
        """Test message transmission from node1 to node2"""
        client1 = WakuClient(f"http://127.0.0.1:{node1_config['ports']['rest']}")
        client2 = WakuClient(f"http://127.0.0.1:{node2_config['ports']['rest']}")
        
        test_message = "Inter-node communication test message"
        
        # Double-check that both nodes are subscribed
        time.sleep(5)
        
        # Publish message from node1
        success = client1.publish_message(test_topic, test_message)
        assert success, "Failed to publish message from node1"
        
        # Wait longer for message propagation
        time.sleep(15)
        
        # Check if message was received by node2
        messages = client2.get_messages(test_topic)
        logging.info(f"Node2 received {len(messages)} messages")
        
        if len(messages) == 0:
            # Try getting messages from node1 to see if publishing worked
            messages1 = client1.get_messages(test_topic)
            logging.info(f"Node1 has {len(messages1)} messages")
            
        assert len(messages) > 0, "No messages received by node2"
        
        # Verify the message content
        from utils.helpers import decode_base64_payload
        found_message = False
        for msg in messages:
            if "payload" in msg:
                decoded = decode_base64_payload(msg["payload"])
                logging.info(f"Received message: '{decoded}'")
                if decoded == test_message:
                    found_message = True
                    break
        
        assert found_message, f"Test message not found in node2 messages"