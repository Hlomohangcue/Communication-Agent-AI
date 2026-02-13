# Quick Installation Guide - Computer Vision

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
pip install mediapipe opencv-python numpy
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Start Backend

```bash
cd backend
python main.py
```

You should see:
```
✓ MediaPipe Hands initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Open Frontend

Open `frontend/dashboard.html` in your browser (or use Live Server)

### Step 4: Test Webcam

1. Click the **"📹 Webcam"** tab
2. Click **"Start Camera"**
3. Allow webcam access
4. Make a gesture (wave, thumbs up, peace sign)
5. Watch the detection overlay
6. Click **"Capture Gesture"** to send to AI

---

## ✅ Verification

### Check Backend
```bash
curl http://localhost:8000/vision/gestures
```

Should return list of supported gestures.

### Check Frontend
- Webcam tab visible
- Camera starts successfully
- Gestures detected in real-time
- AI responds to captured gestures

---

## 🐛 Common Issues

### Issue: "MediaPipe not installed"
**Solution:**
```bash
pip install mediapipe opencv-python
```

### Issue: Webcam not accessible
**Solution:**
- Check browser permissions
- Use HTTPS or localhost
- Close other apps using webcam

### Issue: Gestures not detected
**Solution:**
- Improve lighting
- Move hand closer (1-2 feet)
- Hold gesture steady
- Face palm toward camera

---

## 📊 System Requirements

### Minimum:
- Python 3.8+
- Webcam
- Modern browser (Chrome, Firefox, Edge)
- 2GB RAM

### Recommended:
- Python 3.10+
- HD Webcam
- Chrome browser
- 4GB RAM
- GPU (optional, for better performance)

---

## 🎯 Testing

### Test 1: Backend API
```bash
# Check vision service status
curl http://localhost:8000/vision/gestures
```

### Test 2: Gesture Detection
1. Open dashboard
2. Switch to Webcam mode
3. Start camera
4. Try each gesture:
   - 👋 Wave (all fingers extended)
   - 👍 Thumbs up (thumb up, others closed)
   - ✌️ Peace (index + middle up)
   - 🙋 Raised hand (hand above head)
   - ✋ Stop (open palm)

### Test 3: AI Integration
1. Make a gesture
2. Click "Capture Gesture"
3. Verify AI responds appropriately

---

## 💡 Tips

### For Best Results:
1. **Lighting:** Bright, even lighting
2. **Background:** Plain, contrasting background
3. **Distance:** 1-2 feet from camera
4. **Position:** Hand at chest/face level
5. **Hold:** Keep gesture steady for 1-2 seconds

### Performance:
- Detection runs at ~2 FPS (every 500ms)
- Adjust in `app.js` if needed:
```javascript
setInterval(() => {
    processCurrentFrame();
}, 1000);  // Slower but less CPU usage
```

---

## 🎉 You're Ready!

Computer vision is now integrated and working. Try it out and prepare for your demo!

**Next:** Follow `GPU_DEPLOYMENT_COMPLETE.md` to deploy on NVIDIA GPU for even better performance.
