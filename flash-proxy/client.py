#!/usr/bin/env python3
"""
HTTP Client for flash-proxy
Sends directory paths to the flash proxy server
"""

import json
import requests
import argparse
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlashClient:
    def __init__(self, server_url):
        """Initialize the flash client"""
        self.server_url = server_url.rstrip('/')
        
    def send_flash_request(self, directory_path):
        """Send a flash request to the server"""
        # Validate directory exists
        if not os.path.isdir(directory_path):
            logger.error(f"Directory does not exist: {directory_path}")
            return False
        
        # Convert to absolute path
        directory_path = os.path.abspath(directory_path)
        
        # Prepare request data
        request_data = {
            'directory_path': directory_path
        }
        
        logger.info(f"Sending flash request for directory: {directory_path}")
        
        try:
            # Send POST request
            response = requests.post(
                f"{self.server_url}/",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=600  # 10 minute timeout
            )
            
            # Check response status
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    logger.info("Flash operation completed successfully!")
                    print("✅ Flash operation completed successfully!")
                    
                    if result.get('stdout'):
                        print(f"\nOutput:\n{result['stdout']}")
                    
                    return True
                else:
                    logger.error("Flash operation failed!")
                    print("❌ Flash operation failed!")
                    
                    if result.get('stderr'):
                        print(f"\nError output:\n{result['stderr']}")
                    if result.get('stdout'):
                        print(f"\nStandard output:\n{result['stdout']}")
                    
                    print(f"Return code: {result.get('returncode', 'unknown')}")
                    return False
            else:
                logger.error(f"Server returned error: {response.status_code}")
                print(f"❌ Server error: {response.status_code}")
                
                try:
                    error_data = response.json()
                    print(f"Error message: {error_data}")
                except:
                    print(f"Error response: {response.text}")
                
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            print("❌ Request timed out")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to server at {self.server_url}")
            print(f"❌ Could not connect to server at {self.server_url}")
            print("Make sure the server is running!")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            print(f"❌ Unexpected error: {str(e)}")
            return False
    
    def check_server_status(self):
        """Check if the server is running"""
        try:
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ Server is running: {status_data.get('message', 'OK')}")
                return True
            else:
                print(f"❌ Server returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to server at {self.server_url}")
            return False
        except Exception as e:
            print(f"❌ Error checking server status: {str(e)}")
            return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Flash Proxy HTTP Client')
    parser.add_argument('directory_path', help='Directory path containing images to flash')
    parser.add_argument('--server', default='http://localhost:8080', 
                       help='Server URL (default: http://localhost:8080)')
    parser.add_argument('--check-status', action='store_true', 
                       help='Check server status only')
    
    args = parser.parse_args()
    
    # Create client
    client = FlashClient(args.server)
    
    # Check status only
    if args.check_status:
        client.check_server_status()
        return
    
    # Validate directory path
    if not os.path.exists(args.directory_path):
        print(f"❌ Error: Directory does not exist: {args.directory_path}")
        sys.exit(1)
    
    if not os.path.isdir(args.directory_path):
        print(f"❌ Error: Path is not a directory: {args.directory_path}")
        sys.exit(1)
    
    # Send flash request
    success = client.send_flash_request(args.directory_path)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
