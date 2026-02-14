# 🔄 Pull Changes and Restart Production Server

## Commands to Run on Your Brev Instance

Copy and paste these commands into your SSH terminal:

### Step 1: Navigate to Project Directory
```bash
cd ~/Communication-Agent-AI
```

### Step 2: Check Current Status
```bash
# Check current git status
git status

# Check current branch
git branch
```

### Step 3: Pull Latest Changes from GitHub
```bash
# Pull latest changes
git pull origin master
```

### Step 4: Stop Running Servers
```bash
# Stop backend
pkill -f "python3 main.py"

# Stop frontend
kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}')

# Verify servers stopped
ps aux | grep python3 | grep -E "main.py|http.server"
```

### Step 5: Restart Backend
```bash
cd ~/Communication-Agent-AI/backend
nohup /usr/bin/python3 main.py > server.log 2>&1 &
```

### Step 6: Wait and Verify Backend Started
```bash
sleep 3
ps aux | grep "python3 main.py" | grep -v grep
curl http://localhost:8000/
```

### Step 7: Restart Frontend
```bash
cd ~/Communication-Agent-AI/frontend
nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 &
```

### Step 8: Verify Frontend Started
```bash
ps aux | grep "http.server 3001" | grep -v grep
curl http://localhost:3001/ | head -10
```

### Step 9: Final Verification
```bash
# Check both servers are running
ps aux | grep python3 | grep -E "main.py|http.server"

# Test backend API
curl http://localhost:8000/

# Test frontend
curl http://localhost:3001/ | head -5
```

---

## 🚀 Quick One-Liner (All Steps Combined)

If you want to do everything at once:

```bash
cd ~/Communication-Agent-AI && \
git pull origin master && \
pkill -f "python3 main.py" && \
kill $(ps aux | grep "http.server 3001" | grep -v grep | awk '{print $2}') 2>/dev/null ; \
sleep 2 && \
cd ~/Communication-Agent-AI/backend && \
nohup /usr/bin/python3 main.py > server.log 2>&1 & \
sleep 3 && \
cd ~/Communication-Agent-AI/frontend && \
nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 & \
sleep 2 && \
echo "=== Servers Status ===" && \
ps aux | grep python3 | grep -E "main.py|http.server" && \
echo "=== Backend Test ===" && \
curl http://localhost:8000/ && \
echo "" && \
echo "=== All Done! ==="
```

---

## 📋 Expected Output

### After Git Pull:
```
remote: Enumerating objects: X, done.
remote: Counting objects: 100% (X/X), done.
remote: Compressing objects: 100% (X/X), done.
remote: Total X (delta X), reused X (delta X)
Unpacking objects: 100% (X/X), done.
From https://github.com/Hlomohangcue/Communication-Agent-AI
 * branch            master     -> FETCH_HEAD
   c7d526c..4f68b68  master     -> origin/master
Updating c7d526c..4f68b68
Fast-forward
 GESTURE_FEATURE_VISUAL_GUIDE.md        | 393 ++++++++++++++++++++++++++++++++
 GESTURE_INTERPRETATION_COMPLETE.md     | 263 +++++++++++++++++++++
 GESTURE_INTERPRETATION_SUMMARY.md      | 263 +++++++++++++++++++++
 QUICK_START_GESTURE_INTERPRETATION.md  | 200 ++++++++++++++++
 backend/services/gesture_meanings.py   |   2 +
 test_gesture_interpretation.py         |  85 +++++++
 6 files changed, 1206 insertions(+)
```

### After Backend Restart:
```
ubuntu     XXXXX  X.X  X.X XXXXXX XXXXXX pts/0   Sl   XX:XX   0:XX /usr/bin/python3 main.py
{"status":"Communication Bridge AI is running","version":"1.0.0"}
```

### After Frontend Restart:
```
ubuntu     XXXXX  X.X  X.X XXXXXX XXXXXX pts/0   S    XX:XX   0:XX /usr/bin/python3 -m http.server 3001
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
```

---

## ✅ Success Indicators

You'll know everything worked when:
- ✅ Git pull shows files updated
- ✅ Backend process shows in `ps aux` output
- ✅ Backend responds with JSON status
- ✅ Frontend process shows in `ps aux` output
- ✅ Frontend responds with HTML
- ✅ No error messages in output

---

## 🔍 Troubleshooting

### If Git Pull Fails:
```bash
# Check for local changes
git status

# If you have local changes, stash them
git stash

# Try pull again
git pull origin master

# Reapply stashed changes if needed
git stash pop
```

### If Backend Won't Start:
```bash
# Check for errors in log
cd ~/Communication-Agent-AI/backend
tail -50 server.log

# Try running directly to see errors
/usr/bin/python3 main.py
```

### If Frontend Won't Start:
```bash
# Check if port is in use
lsof -i :3001

# Kill any process using port 3001
kill -9 $(lsof -t -i:3001)

# Try starting again
cd ~/Communication-Agent-AI/frontend
nohup /usr/bin/python3 -m http.server 3001 > frontend.log 2>&1 &
```

### If Servers Are Running But Not Accessible:
```bash
# Check Brev secure links are set to "Public"
# Go to: https://console.brev.dev
# Find your instance: communication-bridge-ai
# Check ports 8000 and 3001 are set to "Public"
```

---

## 🎯 What Changed in This Update

The latest pull includes:
1. ✅ Fixed missing imports in `gesture_meanings.py`
2. ✅ Added comprehensive documentation:
   - GESTURE_INTERPRETATION_COMPLETE.md
   - QUICK_START_GESTURE_INTERPRETATION.md
   - GESTURE_INTERPRETATION_SUMMARY.md
   - GESTURE_FEATURE_VISUAL_GUIDE.md
3. ✅ Added test script: `test_gesture_interpretation.py`

---

## 🌐 Access Your Updated Application

After restart, access at:
- **Frontend:** https://3001-i1jp0gsn9.brevlab.com
- **Backend:** https://8000-i1jp0gsn9.brevlab.com

---

## 📞 Need Help?

If you encounter issues:
1. Check the server logs: `tail -50 ~/Communication-Agent-AI/backend/server.log`
2. Verify processes: `ps aux | grep python3`
3. Test locally: `curl http://localhost:8000/`
4. Check Brev console for port settings

---

**Ready to pull and restart!** 🚀
