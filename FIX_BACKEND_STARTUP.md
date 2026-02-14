# 🔧 Fix Backend Startup Issue

## Current Status
- ✅ Git pull successful (2,560 lines updated)
- ✅ Frontend running (PID 62600)
- ❌ Backend failed to start (Connection refused on port 8000)

## Diagnosis Commands

Run these commands to see what went wrong:

### 1. Check Backend Error Log
```bash
cd ~/Communication-Agent-AI/backend
tail -50 server.log
```

### 2. Try Running Backend Directly (See Real-Time Errors)
```bash
cd ~/Communication-Agent-AI/backend
/usr/bin/python3 main.py
```

This will show you the exact error preventing startup.

---

## Common Issues & Fixes

### Issue 1: Import Error (Most Likely)
If you see: `ImportError` or `ModuleNotFoundError`

**Fix:**
```bash
cd ~/Communication-Agent-AI/backend
/usr/bin/python3 main.py
# Read the error, then press Ctrl+C
```

### Issue 2: Port Already in Use
If you see: `Address already in use`

**Fix:**
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 $(lsof -t -i:8000)

# Try starting again
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
```

### Issue 3: Database Lock
If you see: `database is locked`

**Fix:**
```bash
cd ~/Communication-Agent-AI/backend
rm -f communication_bridge.db-journal
nohup /usr/bin/python3 main.py > server.log 2>&1 &
```

---

## Quick Fix Commands

### Option A: Check Log First
```bash
cd ~/Communication-Agent-AI/backend && tail -50 server.log
```

### Option B: Run Directly to See Error
```bash
cd ~/Communication-Agent-AI/backend && /usr/bin/python3 main.py
```

### Option C: Force Restart Everything
```bash
# Kill everything
pkill -9 -f "python3 main.py"
kill -9 $(lsof -t -i:8000) 2>/dev/null

# Wait
sleep 2

# Start backend
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &

# Wait and check
sleep 5
ps aux | grep "python3 main.py" | grep -v grep
curl http://localhost:8000/
```

---

## Expected Error (Based on Update)

The most likely error is related to the `gesture_meanings.py` import. The file was updated with proper imports, but there might be a syntax issue.

### Check the File
```bash
cd ~/Communication-Agent-AI/backend
python3 -c "from services.gesture_meanings import GestureMeaningService; print('Import OK')"
```

If this fails, we need to check the file syntax.

---

## Step-by-Step Recovery

### Step 1: See the Error
```bash
cd ~/Communication-Agent-AI/backend
tail -30 server.log
```

### Step 2: Test Import
```bash
cd ~/Communication-Agent-AI/backend
python3 -c "from services.gesture_meanings import GestureMeaningService"
```

### Step 3: If Import Fails, Check File
```bash
cd ~/Communication-Agent-AI/backend
head -20 services/gesture_meanings.py
```

### Step 4: Restart Backend
```bash
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
sleep 3
curl http://localhost:8000/
```

---

## What to Send Me

Please run this and send me the output:

```bash
cd ~/Communication-Agent-AI/backend && \
echo "=== SERVER LOG ===" && \
tail -50 server.log && \
echo "" && \
echo "=== IMPORT TEST ===" && \
python3 -c "from services.gesture_meanings import GestureMeaningService; print('✅ Import successful')" 2>&1 && \
echo "" && \
echo "=== FILE CHECK ===" && \
head -10 services/gesture_meanings.py
```

This will show me:
1. The error from the log
2. Whether the import works
3. The first 10 lines of the file

Then I can tell you exactly what to fix!

---

## Quick Status Check

```bash
# Check what's running
ps aux | grep python3 | grep -E "main.py|http.server"

# Check ports
lsof -i :8000
lsof -i :3001
```

---

**Let's see what the error is, then we can fix it!** 🔧
