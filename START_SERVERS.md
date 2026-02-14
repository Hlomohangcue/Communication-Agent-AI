# Start Both Backend and Frontend Servers

## Quick Start (Copy & Paste)

```bash
# Stop any existing servers
pkill -f "python3 main.py"
kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}') 2>/dev/null

# Wait for processes to stop
sleep 2

# Start Backend (port 8000)
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
echo "Backend starting..."
sleep 5

# Start Frontend (port 3001)
cd ~/Communication-Agent-AI/frontend
nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 &
echo "Frontend starting..."
sleep 2

# Verify both servers are running
echo ""
echo "=== Server Status ==="
echo ""
echo "Backend (port 8000):"
ps aux | grep "python3 main.py" | grep -v grep
echo ""
echo "Frontend (port 3001):"
ps aux | grep "http.server 3001" | grep -v grep
echo ""
echo "=== Testing Backend ==="
curl http://localhost:8000/
echo ""
echo ""
echo "=== URLs ==="
echo "Frontend: https://3001-i1jp0gsn9.brevlab.com"
echo "Backend:  https://8000-i1jp0gsn9.brevlab.com"
echo ""
echo "✅ Servers started!"
```

## One-Liner Version

```bash
pkill -f "python3 main.py"; kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}') 2>/dev/null; sleep 2; cd ~/Communication-Agent-AI/backend && nohup /usr/bin/python3 main.py > server.log 2>&1 & sleep 5; cd ~/Communication-Agent-AI/frontend && nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 & sleep 2; echo "✅ Servers started!"; ps aux | grep -E "python3 main.py|http.server 3001" | grep -v grep
```

## Step-by-Step Instructions

### 1. Stop Existing Servers
```bash
# Stop backend
pkill -f "python3 main.py"

# Stop frontend
kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}')

# Wait for processes to stop
sleep 2
```

### 2. Start Backend
```bash
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
sleep 5
```

### 3. Start Frontend
```bash
cd ~/Communication-Agent-AI/frontend
nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 &
sleep 2
```

### 4. Verify Servers Running
```bash
# Check backend
ps aux | grep "python3 main.py" | grep -v grep

# Check frontend
ps aux | grep "http.server 3001" | grep -v grep

# Test backend API
curl http://localhost:8000/
```

## Expected Output

### Backend Process
```
ubuntu    230901  2.5  4.5 676708 170512 pts/0   Sl   07:30   0:01 /usr/bin/python3 main.py
```

### Frontend Process
```
ubuntu    230950  0.0  0.8  25432  31024 pts/0   S    07:30   0:00 /usr/bin/python3 -m http.server 3001
```

### Backend API Test
```json
{"status":"Communication Bridge AI is running","version":"1.0.0"}
```

## Check Logs

### Backend Logs
```bash
# Last 50 lines
tail -50 ~/Communication-Agent-AI/backend/server.log

# Follow logs in real-time
tail -f ~/Communication-Agent-AI/backend/server.log

# Check for MediaPipe initialization
grep -i "mediapipe" ~/Communication-Agent-AI/backend/server.log
```

### Frontend Logs
```bash
# Last 50 lines
tail -50 ~/Communication-Agent-AI/frontend/frontend.log

# Follow logs in real-time
tail -f ~/Communication-Agent-AI/frontend/frontend.log
```

## Access URLs

- **Frontend**: https://3001-i1jp0gsn9.brevlab.com
- **Backend**: https://8000-i1jp0gsn9.brevlab.com

## Troubleshooting

### Backend Won't Start
```bash
# Check if port 8000 is in use
lsof -i:8000

# Force kill process on port 8000
kill -9 $(lsof -t -i:8000)

# Check for errors in log
tail -30 ~/Communication-Agent-AI/backend/server.log
```

### Frontend Won't Start
```bash
# Check if port 3001 is in use
lsof -i:3001

# Force kill process on port 3001
kill -9 $(lsof -t -i:3001)

# Check for errors in log
tail -30 ~/Communication-Agent-AI/frontend/frontend.log
```

### MediaPipe Not Loading
```bash
# Check MediaPipe installation
/usr/bin/python3 -c "import mediapipe; print('Version:', mediapipe.__version__)"

# Should show: Version: 0.10.8
```

## Stop Servers

```bash
# Stop backend
pkill -f "python3 main.py"

# Stop frontend
kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}')

# Verify stopped
ps aux | grep -E "python3 main.py|http.server 3001" | grep -v grep
# Should show nothing
```

## Restart Servers (Quick)

```bash
# Stop both
pkill -f "python3 main.py"; kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}') 2>/dev/null; sleep 2

# Start both
cd ~/Communication-Agent-AI/backend && nohup /usr/bin/python3 main.py > server.log 2>&1 & sleep 5 && cd ~/Communication-Agent-AI/frontend && nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 & sleep 2 && echo "✅ Restarted!"
```

## Features Available

With both servers running, you have access to:

✅ 18 hand gestures with auto-response
✅ Speech-to-text input
✅ Text-based communication
✅ Webcam gesture detection
✅ Real-time AI responses
✅ Bidirectional communication (verbal ↔ non-verbal)
✅ Session management
✅ User authentication
✅ Message history

## Test the System

1. Open: https://3001-i1jp0gsn9.brevlab.com
2. Login with your credentials
3. Start a session
4. Try the webcam with new gestures:
   - 🤟 I Love You
   - 🙏 Thank You
   - 🤙 Call Me
   - 🤘 Rock On
   - And 14 more!

Enjoy your enhanced gesture communication system! 🎉
