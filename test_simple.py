from ib_insync import IB
import time

ib = IB()
print("Connecting...")
try:
    ib.connect('127.0.0.1', 4002, clientId=1, timeout=15, readonly=True)
    print(f"✅ Connected! Status: {ib.isConnected()}")
    print(f"Account: {ib.managedAccounts()}")
    time.sleep(2)
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
finally:
    # Always disconnect, even if there was an error
    if ib.isConnected():
        ib.disconnect()
        print("Disconnected.")
