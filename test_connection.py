#!/usr/bin/env python3
"""
Comprehensive test script to verify IB Gateway API connection
"""
import sys
import socket
import time
from ib_insync import IB

def test_socket_connection(host, port):
    """Test if port is accepting TCP connections"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_ib_api_connection(host, port, client_id=1):
    """Test full IB API connection with proper cleanup"""
    ib = IB()
    try:
        print(f"Connecting to IB Gateway at {host}:{port} (client ID {client_id})...")
        ib.connect(host, port, clientId=client_id, timeout=15, readonly=True)

        # Get account info
        accounts = ib.managedAccounts()

        print(f"✅ Connected successfully!")
        print(f"   Status: {ib.isConnected()}")
        print(f"   Account(s): {accounts}")

        time.sleep(1)  # Brief pause before disconnect
        return True

    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
        return False

    finally:
        # Always disconnect, even if there was an error
        if ib.isConnected():
            ib.disconnect()
            print("   Disconnected.")

if __name__ == "__main__":
    print("🔍 Testing IB Gateway Connection\n")
    print("="*60)

    # Test socket connectivity first
    print("\n📡 Step 1: Testing TCP Socket Connectivity")
    print("-" * 60)

    paper_socket = test_socket_connection('127.0.0.1', 4002)
    live_socket = test_socket_connection('127.0.0.1', 4001)

    print(f"Paper Trading Port (4002): {'✅ Open' if paper_socket else '❌ Closed'}")
    print(f"Live Trading Port (4001):  {'✅ Open' if live_socket else '❌ Closed'}")

    if not paper_socket:
        print("\n❌ Paper trading port is not accessible!")
        print("Make sure the container is running: docker compose ps")
        sys.exit(1)

    # Test IB API connection
    print("\n🐍 Step 2: Testing IB API Protocol Connection")
    print("-" * 60)

    api_success = test_ib_api_connection('127.0.0.1', 4002, client_id=1)

    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Socket Connectivity:  {'✅ Pass' if paper_socket and live_socket else '❌ Fail'}")
    print(f"IB API Connection:    {'✅ Pass' if api_success else '❌ Fail'}")
    print("="*60)

    if api_success:
        print("\n🎉 All tests passed! IB Gateway is ready for trading.")
        sys.exit(0)
    else:
        print("\n❌ API connection test failed.")
        print("\nTroubleshooting:")
        print("• Check Gateway is fully initialized (wait 30-60 seconds after start)")
        print("• Verify API is enabled in Gateway GUI (via VNC)")
        print("• Restart the Gateway if needed: docker compose restart")
        sys.exit(1)
