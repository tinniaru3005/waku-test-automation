#!/usr/bin/env python3
"""
Cleanup script for Docker resources used by Waku tests
Run this before starting tests to ensure clean state
"""

import docker
import logging

def cleanup_waku_resources():
    """Clean up all Waku-related Docker resources"""
    client = docker.from_env()
    
    print("Cleaning up Waku test resources...")
    
    # Stop and remove containers
    containers_removed = 0
    for container in client.containers.list(all=True):
        if container.name.startswith('waku_node'):
            try:
                print(f"Stopping container: {container.name}")
                container.stop()
                container.remove()
                containers_removed += 1
            except Exception as e:
                print(f"Error removing container {container.name}: {e}")
    
    print(f"Removed {containers_removed} containers")
    
    # Remove networks
    networks_removed = 0
    for network in client.networks.list():
        if network.name == 'waku':
            try:
                print(f"Removing network: {network.name}")
                network.remove()
                networks_removed += 1
            except Exception as e:
                print(f"Error removing network {network.name}: {e}")
    
    print(f"Removed {networks_removed} networks")
    
    # Remove unused images (optional)
    try:
        pruned = client.images.prune()
        print(f"Pruned unused images, freed: {pruned.get('SpaceReclaimed', 0)} bytes")
    except Exception as e:
        print(f"Error pruning images: {e}")
    
    print("Cleanup completed!")

if __name__ == "__main__":
    cleanup_waku_resources()