"""
Test script for Computer Vision implementation
Tests the vision service without requiring a webcam
"""

import sys
sys.path.append('backend')

print("=" * 60)
print("COMPUTER VISION IMPLEMENTATION TEST")
print("=" * 60)

# Test 1: Import vision service
print("\n[Test 1] Importing vision service...")
try:
    from services.vision_service import VisionService
    print("✓ Vision service imported successfully")
except ImportError as e:
    print(f"✗ Failed to import vision service: {e}")
    sys.exit(1)

# Test 2: Initialize vision service
print("\n[Test 2] Initializing vision service...")
try:
    vision = VisionService()
    print("✓ Vision service initialized")
    
    if vision.mediapipe_available:
        print("  ✓ MediaPipe is available")
    else:
        print("  ⚠ MediaPipe not installed (vision features disabled)")
        print("  Install with: pip install mediapipe opencv-python")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    sys.exit(1)

# Test 3: Get supported gestures
print("\n[Test 3] Getting supported gestures...")
try:
    gestures = vision.get_supported_gestures()
    print(f"✓ Found {len(gestures)} supported gestures:")
    for g in gestures:
        print(f"  - {g['emoji']} {g['gesture']}")
except Exception as e:
    print(f"✗ Failed to get gestures: {e}")

# Test 4: Test process_frame with dummy data (will fail gracefully)
print("\n[Test 4] Testing process_frame method...")
try:
    # This will fail without a real image, but tests the method exists
    result = vision.process_frame("dummy_data")
    if "error" in result or "hands_detected" in result:
        print("✓ process_frame method works (graceful error handling)")
        print(f"  Result: {result}")
    else:
        print("⚠ Unexpected result format")
except Exception as e:
    print(f"✗ process_frame failed: {e}")

# Test 5: Check main.py imports
print("\n[Test 5] Checking main.py integration...")
try:
    from main import app
    print("✓ Main app imports successfully")
    
    # Check if vision endpoints exist
    routes = [route.path for route in app.routes]
    vision_routes = [r for r in routes if 'vision' in r]
    
    if vision_routes:
        print(f"✓ Found {len(vision_routes)} vision endpoints:")
        for route in vision_routes:
            print(f"  - {route}")
    else:
        print("⚠ No vision endpoints found")
        
except Exception as e:
    print(f"✗ Failed to import main: {e}")

# Test 6: Check dependencies
print("\n[Test 6] Checking dependencies...")
dependencies = {
    'mediapipe': False,
    'cv2': False,
    'numpy': False
}

try:
    import mediapipe
    dependencies['mediapipe'] = True
    print("✓ mediapipe installed")
except ImportError:
    print("✗ mediapipe not installed")
    print("  Install with: pip install mediapipe")

try:
    import cv2
    dependencies['cv2'] = True
    print("✓ opencv-python installed")
except ImportError:
    print("✗ opencv-python not installed")
    print("  Install with: pip install opencv-python")

try:
    import numpy
    dependencies['numpy'] = True
    print("✓ numpy installed")
except ImportError:
    print("✗ numpy not installed")
    print("  Install with: pip install numpy")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

all_deps = all(dependencies.values())
if all_deps:
    print("✓ All dependencies installed")
    print("✓ Vision service ready to use")
    print("\nNext steps:")
    print("1. Start backend: cd backend && python main.py")
    print("2. Open frontend: frontend/dashboard.html")
    print("3. Click '📹 Webcam' tab and test gestures")
else:
    print("⚠ Some dependencies missing")
    print("\nInstall missing dependencies:")
    if not dependencies['mediapipe']:
        print("  pip install mediapipe")
    if not dependencies['cv2']:
        print("  pip install opencv-python")
    if not dependencies['numpy']:
        print("  pip install numpy")
    print("\nOr install all at once:")
    print("  pip install -r requirements.txt")

print("\n" + "=" * 60)
