#!/usr/bin/env python3
"""
Simple test script to verify IB Gateway API connection
"""
import sys
import socket
from ib_insync import IB

def test_api_connection(host, port):
    """Test if IB Gateway API is accepting connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ Successfully connected to IB Gateway API at {host}:{port}")
            return True
        else:
            print(f"❌ Failed to connect to IB Gateway API at {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_with_ibapi(host, port, client):
    """Test using IB API library if available"""
    ib = IB()
    print(f"Connecting to IB Gateway on {host}:{port} …")
    try:
        ib.connect(host, port, clientId=client, timeout=5, readonly=True)
        print("Connected successfully!")

    except Exception as e:
        print(f"Connection failed: {e}")
        print("❌ Failed to establish IB API connection")
        print("Make sure:")
        print("1. IBKR Gateway is running")
        print("2. API is enabled in Gateway configuration")
        print("3. Client ID {client} is not already in use")
        print("4. Port {port} matches Gateway API settings")
        return False

    ib.disconnect()
    return True


def test_connection():
    """Test using IB API library if available"""
    ib = IB()
    try:
        print("Attempting to connect to IB Gateway...")
        # Use a very short timeout to fail fast
        ib.connect('127.0.0.1', 4002, clientId=999, timeout=5, readonly=True)
        print("SUCCESS: Connected to IB Gateway!")

        # Test if we can get basic info
        print(f"Connection status: {ib.isConnected()}")

        ib.disconnect()
        return True

    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing IB Gateway connection...")

    # Test both paper (4002) and live (4001) ports
    print("\n📊 Testing Paper Trading API (port 4002):")
    paper_ok = test_api_connection('127.0.0.1', 4002)

    print("\n💰 Testing Live Trading API (port 4001):")
    live_ok = test_api_connection('127.0.0.1', 4001)

    # Test with IB API if available
    print("\n🐍 Testing with IB Python API:")
    api_test = test_with_ibapi('127.0.0.1', 4002, 999)

    print("\n" + "="*50)
    print("📈 Test Results Summary:")
    print(f"Paper API (4002):    {'✅ Connected' if paper_ok else '❌ Failed'}")
    print(f"Live API (4001):     {'✅ Connected' if live_ok else '❌ Failed'}")
    print(f"IB API Test (4002):  {'✅ Connected' if api_test else '❌ Failed'}")

    success = test_connection()

    sys.exit(0)
