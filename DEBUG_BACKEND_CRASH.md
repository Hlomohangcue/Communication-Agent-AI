# 🔍 Debug Backend Crash

## Current Situation
- MediaPipe IS installed (0.10.8) ✅
- Backend starts but immediately crashes ❌
- Need to see the actual error

## Get the Real Error

Run this to see what's crashing the backend:

```bash
cd ~/Communication-Agent-AI/backend
tail -100 server.log | grep -A 20 "Error\|Exception\|Traceback"
```

Or see the full recent log:

```bash
cd ~/Communication-Agent-AI/backend
tail -100 server.log
```

## Try Running Directly

This will show the error in real-time:

```bash
cd ~/Communication-Agent-AI/backend
/usr/bin/python3 main.py
```

Then press Ctrl+C after you see the error.

---

## Most Likely Issues

### 1. Import Error in gesture_meanings.py
The file might have a syntax error from the update.

**Check:**
```bash
cd ~/Communication-Agent-AI/backend
python3 -c "from services.gesture_meanings import GestureMeaningService; print('Import OK')"
```

### 2. Port 8000 Already in Use
Another process might be using port 8000.

**Check:**
```bash
lsof -i :8000
```

**Fix:**
```bash
kill -9 $(lsof -t -i:8000)
```

### 3. Database Lock
The database might be locked.

**Fix:**
```bash
cd ~/Communication-Agent-AI/backend
rm -f communication_bridge.db-journal
rm -f *.db-journal
```

---

## Quick Diagnostic

Run this all-in-one diagnostic:

```bash
cd ~/Communication-Agent-AI/backend && \
echo "=== 1. Check Import ===" && \
python3 -c "from services.gesture_meanings import GestureMeaningService; print('✅ Import OK')" 2>&1 && \
echo "" && \
echo "=== 2. Check Port 8000 ===" && \
lsof -i :8000 && \
echo "" && \
echo "=== 3. Last 50 Lines of Log ===" && \
tail -50 server.log && \
echo "" && \
echo "=== 4. Try Direct Run (Ctrl+C to stop) ===" && \
timeout 5 /usr/bin/python3 main.py 2>&1 || echo "Backend started but may have crashed"
```

---

## After Finding the Error

Send me the output and I'll tell you exactly how to fix it!

---

**Run the diagnostic command above!** 🔍
