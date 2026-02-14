# 🚀 Restart Backend Now

## Current Situation
- Old backend was killed successfully
- New backend tried to start but failed (Exit 1)
- Frontend is still running fine
- Log shows old successful requests, but no new startup

## Quick Fix Commands

### Step 1: Check if Backend is Actually Running
```bash
ps aux | grep "python3 main.py" | grep -v grep
```

### Step 2: Check Port 8000
```bash
lsof -i :8000
```

### Step 3: Start Backend Fresh
```bash
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
```

### Step 4: Wait and Verify
```bash
sleep 5
ps aux | grep "python3 main.py" | grep -v grep
curl http://localhost:8000/
```

### Step 5: If Still Failing, Check New Log Entries
```bash
tail -20 server.log
```

---

## All-in-One Command

```bash
cd ~/Communication-Agent-AI/backend && \
pkill -9 -f "python3 main.py" && \
sleep 2 && \
nohup /usr/bin/python3 main.py > server.log 2>&1 & \
sleep 5 && \
echo "=== Process Status ===" && \
ps aux | grep "python3 main.py" | grep -v grep && \
echo "" && \
echo "=== Backend Test ===" && \
curl http://localhost:8000/ && \
echo "" && \
echo "=== Latest Log (if failed) ===" && \
tail -10 server.log
```

---

## Expected Success Output

```
=== Process Status ===
ubuntu     XXXXX  X.X  X.X XXXXXX XXXXXX pts/0   Sl   XX:XX   0:XX /usr/bin/python3 main.py

=== Backend Test ===
{"status":"Communication Bridge AI is running","version":"1.0.0"}
```

---

## If It Still Fails

Run this to see the actual error:
```bash
cd ~/Communication-Agent-AI/backend
/usr/bin/python3 main.py
```

Then press Ctrl+C and send me the error message.

---

**Run the all-in-one command above!** 🚀
