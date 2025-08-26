import docker
import time
import logging
from typing import Optional, Dict, Any

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.containers = {}
        self.networks = {}
        
    def create_network(self, name: str, subnet: str = "172.18.0.0/16", 
                      gateway: str = "172.18.0.1") -> None:
        """Create a Docker network"""
        try:
            network = self.client.networks.create(
                name,
                driver="bridge",
                ipam=docker.types.IPAMConfig(
                    pool_configs=[
                        docker.types.IPAMPool(
                            subnet=subnet,
                            gateway=gateway
                        )
                    ]
                )
            )
            self.networks[name] = network
            logging.info(f"Created network: {name}")
        except docker.errors.APIError as e:
            if "already exists" in str(e):
                self.networks[name] = self.client.networks.get(name)
                logging.info(f"Using existing network: {name}")
            else:
                raise
    
    def start_waku_node(self, node_name: str, ports: Dict[str, str], 
                       extip: str, bootstrap_node: Optional[str] = None) -> str:
        """Start a Waku node container"""
        
        # Clean up any existing container with the same name
        try:
            existing = self.client.containers.get(node_name)
            existing.stop()
            existing.remove()
            logging.info(f"Removed existing container: {node_name}")
        except docker.errors.NotFound:
            pass  # Container doesn't exist, which is fine
        except Exception as e:
            logging.warning(f"Error cleaning up existing container {node_name}: {e}")
        
        # Base command
        command = [
            f"--listen-address=0.0.0.0",
            "--rest=true",
            "--rest-admin=true",
            "--websocket-support=true",
            "--log-level=INFO",  # Changed from TRACE to reduce noise
            "--rest-relay-cache-capacity=100",
            f"--websocket-port={ports['websocket']}",
            f"--rest-port={ports['rest']}",
            f"--tcp-port={ports['tcp']}",
            f"--discv5-udp-port={ports['discv5']}",
            "--rest-address=0.0.0.0",
            f"--nat=extip:{extip}",
            "--peer-exchange=true",
            "--discv5-discovery=true",
            "--relay=true"
        ]
        
        # Add bootstrap node if provided
        if bootstrap_node:
            command.append(f"--discv5-bootstrap-node={bootstrap_node}")
        
        # Port mappings for Docker
        port_mappings = {
            f"{ports['rest']}/tcp": ports['rest'],
            f"{ports['tcp']}/tcp": ports['tcp'],
            f"{ports['websocket']}/tcp": ports['websocket'],
            f"{ports['discv5']}/udp": ports['discv5'],
            f"{ports['rpc']}/tcp": ports['rpc']
        }
        
        try:
            container = self.client.containers.run(
                "wakuorg/nwaku:v0.24.0",
                command=command,
                ports=port_mappings,
                detach=True,
                name=node_name,
                remove=False  # Don't auto-remove so we can manage cleanup
            )
            
            self.containers[node_name] = container
            logging.info(f"Started container: {node_name}")
            
            # Wait for container to be ready
            time.sleep(15)  # Increased wait time
            
            return container.id
            
        except docker.errors.APIError as e:
            logging.error(f"Failed to start container {node_name}: {e}")
            raise
    
    def connect_to_network(self, container_name: str, network_name: str, 
                          ip_address: str) -> None:
        """Connect container to network with specific IP"""
        if container_name in self.containers and network_name in self.networks:
            try:
                self.networks[network_name].connect(
                    self.containers[container_name],
                    ipv4_address=ip_address
                )
                logging.info(f"Connected {container_name} to {network_name} with IP {ip_address}")
            except docker.errors.APIError as e:
                logging.warning(f"Failed to connect {container_name} to network: {e}")
    
    def cleanup(self) -> None:
        """Clean up all containers and networks"""
        for name, container in self.containers.items():
            try:
                container.stop()
                container.remove()
                logging.info(f"Stopped and removed container: {name}")
            except Exception as e:
                logging.warning(f"Error cleaning up container {name}: {e}")
        
        for name, network in self.networks.items():
            try:
                network.remove()
                logging.info(f"Removed network: {name}")
            except Exception as e:
                logging.warning(f"Error removing network {name}: {e}")
        
        self.containers.clear()
        self.networks.clear()
        
        # Also clean up any orphaned containers that might exist
        try:
            client = docker.from_env()
            for container in client.containers.list(all=True):
                if container.name.startswith('waku_node'):
                    try:
                        container.stop()
                        container.remove()
                        logging.info(f"Cleaned up orphaned container: {container.name}")
                    except:
                        pass
        except Exception as e:
            logging.warning(f"Error during orphan cleanup: {e}")