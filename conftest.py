import pytest
import logging
import docker
from src.docker_manager import DockerManager
from src.waku_client import WakuClient
from utils.helpers import setup_logging

# Setup logging
setup_logging()

def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    # Clean up any existing resources before starting tests
    print("\n=== Cleaning up existing Docker resources ===")
    client = docker.from_env()
    
    # Remove existing containers
    for container in client.containers.list(all=True):
        if container.name.startswith('waku_node'):
            try:
                container.stop()
                container.remove()
                print(f"Cleaned up existing container: {container.name}")
            except:
                pass
    
    # Remove existing networks
    for network in client.networks.list():
        if network.name == 'waku':
            try:
                network.remove()
                print(f"Cleaned up existing network: {network.name}")
            except:
                pass

@pytest.fixture(scope="session")
def docker_manager():
    """Docker manager fixture"""
    manager = DockerManager()
    yield manager
    manager.cleanup()

@pytest.fixture
def test_topic():
    """Test topic for messaging"""
    return "/my-app/2/chatroom-1/proto"

@pytest.fixture
def test_message():
    """Test message payload"""
    return "Relay works!!"

# Node configurations
@pytest.fixture
def node1_config():
    return {
        "name": "waku_node1",
        "ports": {
            "rest": "21161",
            "tcp": "21162", 
            "websocket": "21163",
            "discv5": "21164",
            "rpc": "21165"
        },
        "extip": "172.18.111.226"
    }

@pytest.fixture  
def node2_config():
    return {
        "name": "waku_node2",
        "ports": {
            "rest": "21171",
            "tcp": "21172",
            "websocket": "21173", 
            "discv5": "21174",
            "rpc": "21175"
        },
        "extip": "172.18.111.227"
    }