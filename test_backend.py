import requests
import json

API_BASE = "http://localhost:8000"

print("Testing Communication Bridge AI Backend\n")
print("=" * 50)

# Test 1: Check if backend is running
print("\n1. Testing backend connection...")
try:
    response = requests.get(f"{API_BASE}/")
    print(f"✓ Backend is running: {response.json()}")
except Exception as e:
    print(f"✗ Backend connection failed: {e}")
    exit(1)

# Test 2: Start simulation
print("\n2. Starting simulation...")
try:
    response = requests.post(f"{API_BASE}/simulate/start")
    data = response.json()
    session_id = data["session_id"]
    print(f"✓ Simulation started: {session_id[:8]}...")
except Exception as e:
    print(f"✗ Failed to start simulation: {e}")
    exit(1)

# Test 3: Send a message
print("\n3. Sending test message...")
try:
    test_input = "👋 Hello"
    response = requests.post(
        f"{API_BASE}/simulate/step",
        json={
            "session_id": session_id,
            "input_text": test_input
        }
    )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Message processed successfully!")
        print(f"\nResponse structure:")
        print(json.dumps(data, indent=2))
        
        print(f"\n--- Results ---")
        print(f"Input: {test_input}")
        print(f"Output: {data['communication_result']['output']}")
        print(f"Intent: {data['communication_result']['intent']}")
        print(f"Confidence: {data['communication_result']['confidence']}")
        print(f"Simulation steps: {len(data['simulation_steps'])}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"✗ Failed to send message: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test complete!")
