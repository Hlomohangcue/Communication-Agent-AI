# Quick Start - Computer Vision

## 🚀 Get Started in 3 Steps

### Step 1: Install MediaPipe (1 minute)

```bash
pip install mediapipe
```

### Step 2: Start Backend (30 seconds)

```bash
cd backend
python main.py
```

You should see:
```
✓ MediaPipe Hands initialized
✓ Gemini model initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Open Frontend (30 seconds)

Open `frontend/dashboard.html` in your browser

---

## 🎥 Using Webcam Gestures

1. **Login** (if not already logged in)
2. **Start Simulation** button
3. **Click "📹 Webcam" tab** (next to Text and Speech)
4. **Click "Start Camera"** - Allow webcam access
5. **Make a gesture:**
   - 👋 Wave (all fingers extended)
   - 👍 Thumbs up
   - ✌️ Peace sign
   - 🙋 Raise hand
6. **Watch real-time detection** in the overlay
7. **Click "Capture Gesture"** to send to AI

---

## ✅ Verify It's Working

### Test 1: Check Backend
```bash
curl http://localhost:8000/vision/gestures
```

Should return list of 10 gestures.

### Test 2: Check Frontend
- Webcam tab visible? ✅
- Camera starts? ✅
- Gestures detected? ✅
- AI responds? ✅

---

## 🎯 Quick Demo

**30-Second Demo:**
1. Start camera
2. Wave at camera → See "👋 wave" detected
3. Click "Capture Gesture"
4. AI responds: "Hello! It's great to see you today!"

**Perfect for showing off!** 🎉

---

## 🐛 Troubleshooting

### Camera won't start?
- Check browser permissions
- Use Chrome/Firefox/Edge
- Must be HTTPS or localhost

### Gestures not detected?
- Improve lighting
- Move hand closer (1-2 feet)
- Hold gesture steady

### "MediaPipe not installed"?
```bash
pip install mediapipe opencv-python
```

---

## 📊 What You Can Do

- ✅ Real-time gesture detection
- ✅ 10 different gestures
- ✅ Automatic emoji conversion
- ✅ AI responses to gestures
- ✅ Three input modes (Text, Speech, Webcam)

---

## 🎬 Ready for Demo!

Your system now has:
- Text input (emoji buttons)
- Speech input (microphone)
- **Webcam input (gesture detection)** ← NEW!
- AI responses
- SaaS authentication

**Perfect for your hackathon!** 🏆
