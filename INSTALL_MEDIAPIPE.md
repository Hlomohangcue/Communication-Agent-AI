# 🔧 Install MediaPipe

## Quick Fix

Run these commands on your Brev server:

### Step 1: Check if MediaPipe is Installed
```bash
/usr/bin/python3 -c "import mediapipe; print('MediaPipe version:', mediapipe.__version__)"
```

### Step 2: If Not Installed, Install It
```bash
/usr/bin/python3 -m pip install mediapipe==0.10.8
```

### Step 3: Verify Installation
```bash
/usr/bin/python3 -c "import mediapipe; print('✅ MediaPipe installed:', mediapipe.__version__)"
```

### Step 4: Restart Backend
```bash
cd ~/Communication-Agent-AI/backend
pkill -f "python3 main.py"
sleep 2
nohup /usr/bin/python3 main.py > server.log 2>&1 &
sleep 3
curl http://localhost:8000/
```

---

## All-in-One Command

```bash
echo "=== Checking MediaPipe ===" && \
/usr/bin/python3 -c "import mediapipe; print('Already installed:', mediapipe.__version__)" 2>&1 || \
(echo "Installing MediaPipe..." && /usr/bin/python3 -m pip install mediapipe==0.10.8) && \
echo "" && \
echo "=== Restarting Backend ===" && \
cd ~/Communication-Agent-AI/backend && \
pkill -f "python3 main.py" && \
sleep 2 && \
nohup /usr/bin/python3 main.py > server.log 2>&1 & \
sleep 3 && \
echo "=== Testing Backend ===" && \
curl http://localhost:8000/ && \
echo "" && \
echo "✅ Done! MediaPipe should now work."
```

---

## Expected Output

If MediaPipe is already installed:
```
=== Checking MediaPipe ===
Already installed: 0.10.8
```

If it needs to be installed:
```
Installing MediaPipe...
Collecting mediapipe==0.10.8
...
Successfully installed mediapipe-0.10.8
```

---

## Why This Might Happen

MediaPipe might not be installed if:
1. The backend is using a different Python environment
2. MediaPipe was installed for a different user
3. The installation didn't complete properly before

---

## After Installation

1. Refresh your browser: https://3001-i1jp0gsn9.brevlab.com
2. Click "Start Webcam"
3. The warning should be gone
4. Gesture detection should work!

---

**Run the all-in-one command above!** 🚀
