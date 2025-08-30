#!/usr/bin/env python3
"""
Simple test script to verify IB Gateway API connection
"""

import socket
import time

def test_api_connection(host='127.0.0.1', port=4002):  # 4002 is paper trading port
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

def test_with_ibapi():
    """Test using IB API library if available"""
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        import threading
        
        class TestApp(EWrapper, EClient):
            def __init__(self):
                EClient.__init__(self, self)
                self.connected = False
                
            def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
                print(f"Error {reqId} {errorCode}: {errorString}")
                
            def connectAck(self):
                print("✅ IB API connection established!")
                self.connected = True
                
            def connectionClosed(self):
                print("Connection closed")
        
        app = TestApp()
        app.connect("127.0.0.1", 4002, clientId=1)  # Paper trading port
        
        # Run for 5 seconds
        api_thread = threading.Thread(target=app.run, daemon=True)
        api_thread.start()
        time.sleep(5)
        
        if app.connected:
            app.disconnect()
            return True
        else:
            print("❌ Failed to establish IB API connection")
            return False
            
    except ImportError:
        print("📦 ibapi not installed. Install with: pip install ibapi")
        return None
    except Exception as e:
        print(f"❌ Error with IB API test: {e}")
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
    api_test = test_with_ibapi()
    
    print("\n" + "="*50)
    print("📈 Test Results Summary:")
    print(f"Paper API (4002): {'✅ Connected' if paper_ok else '❌ Failed'}")
    print(f"Live API (4001):  {'✅ Connected' if live_ok else '❌ Failed'}")
    if api_test is not None:
        print(f"IB API Test:      {'✅ Connected' if api_test else '❌ Failed'}")
    else:
        print("IB API Test:      ⚠️ Skipped (ibapi not installed)")