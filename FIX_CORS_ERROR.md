# Fix: CORS Error - Backend Not Responding

## Problem
```
Access to fetch at 'https://8000-i1jp0gsn9.brevlab.com/simulate/step' 
from origin 'https://3001-i1jp0gsn9.brevlab.com' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Root Cause
The backend server needs to be restarted to:
1. Apply the latest code changes
2. Ensure CORS middleware is properly loaded
3. Refresh all endpoints

## Solution: Restart Backend Server

Run these commands on your Brev server (34.6.169.63):

```bash
# Step 1: Pull latest changes
cd ~/Communication-Agent-AI
git pull origin master

# Step 2: Stop backend
pkill -f "python3 main.py"
sleep 2

# Step 3: Verify backend stopped
ps aux | grep "python3 main.py" | grep -v grep
# Should show nothing

# Step 4: Restart backend
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
sleep 5

# Step 5: Verify backend is running
curl http://localhost:8000/
# Should show: {"status":"Communication Bridge AI is running","version":"1.0.0"}

# Step 6: Check backend process
ps aux | grep "python3 main.py" | grep -v grep
# Should show the running process

# Step 7: Restart frontend
cd ~/Communication-Agent-AI
kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}')
cd frontend
nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 &
sleep 2

# Step 8: Verify frontend is running
ps aux | grep "http.server 3001" | grep -v grep
# Should show the running process
```

## Quick One-Liner (Copy & Paste)

```bash
cd ~/Communication-Agent-AI && git pull origin master && pkill -f "python3 main.py" && sleep 2 && cd backend && nohup /usr/bin/python3 main.py > server.log 2>&1 & sleep 5 && curl http://localhost:8000/ && cd ~/Communication-Agent-AI && kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}') 2>/dev/null; cd frontend && nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 & sleep 2 && echo "✅ Servers restarted!"
```

## Verify Fix

1. Open browser: https://3001-i1jp0gsn9.brevlab.com
2. Open browser console (F12)
3. Try sending a message or capturing a gesture
4. **Expected**: No CORS errors, messages send successfully
5. **Backend logs**: `tail -f ~/Communication-Agent-AI/backend/server.log`

## Why This Happens

CORS errors occur when:
- Backend server is not running
- Backend crashed and needs restart
- CORS middleware not properly initialized
- Code changes not applied (need restart)

## Check Backend Status Anytime

```bash
# Check if backend is running
ps aux | grep "python3 main.py" | grep -v grep

# Check backend logs
tail -50 ~/Communication-Agent-AI/backend/server.log

# Test backend directly
curl http://localhost:8000/

# Check what's using port 8000
lsof -i:8000
```

## Emergency: Force Kill and Restart

If backend won't stop:

```bash
# Force kill
kill -9 $(lsof -t -i:8000)

# Restart
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
```
