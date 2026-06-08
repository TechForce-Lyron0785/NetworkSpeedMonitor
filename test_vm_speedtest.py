#!/usr/bin/env python3
"""
Test script for VMware speedtest connectivity issues.
Run this to test if the speedtest fixes work in your VM environment.
"""

import sys
import os
import logging

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.poller.adapter import get_physical_adapter
from backend.poller.speedtest import measure_speed, get_adapter_ip

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_speedtest():
    """Test the speedtest functionality in VM environment."""
    print("=" * 50)
    print("VMware Speedtest Connectivity Test")
    print("=" * 50)
    
    # Step 1: Find physical adapter
    print("\n1. Finding physical network adapter...")
    try:
        adapter_name, adapter_hwid = get_physical_adapter()
        if adapter_name:
            print(f"   [OK] Found adapter: {adapter_name}")
            print(f"   Hardware ID: {adapter_hwid}")
        else:
            print("   [FAIL] No physical adapter found")
            return False
    except Exception as e:
        print(f"   [FAIL] Error finding adapter: {e}")
        return False
    
    # Step 2: Get adapter IP
    print("\n2. Getting adapter IP address...")
    try:
        ip = get_adapter_ip(adapter_name)
        if ip:
            print(f"   [OK] Adapter IP: {ip}")
        else:
            print("   [FAIL] No IP address found for adapter")
            return False
    except Exception as e:
        print(f"   [FAIL] Error getting IP: {e}")
        return False
    
    # Step 3: Run speed test
    print("\n3. Running speed test...")
    print("   This may take 30-60 seconds...")
    try:
        results = measure_speed(adapter_name)
        
        print(f"\n   Results:")
        print(f"   Download: {results['download_mbps']} Mbps")
        print(f"   Upload: {results['upload_mbps']} Mbps") 
        print(f"   Latency: {results['latency_ms']} ms")
        
        if results['download_mbps'] > 0:
            print("   [OK] Speed test successful!")
            return True
        else:
            print("   [FAIL] Speed test returned 0 Mbps (check network connectivity)")
            return False
            
    except Exception as e:
        print(f"   [FAIL] Speed test error: {e}")
        return False

def main():
    """Main test function."""
    success = test_speedtest()
    
    print("\n" + "=" * 50)
    if success:
        print("[OK] All tests passed! The speedtest should work in your VM.")
        print("  You can now start the poller service.")
    else:
        print("[FAIL] Tests failed. Check your VM network configuration:")
        print("  - Ensure VM has internet access")
        print("  - Check firewall settings")
        print("  - Verify VMware network adapter settings")
        print("  - Try running as administrator")
    print("=" * 50)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())