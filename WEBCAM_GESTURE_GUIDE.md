# Webcam Gesture Recognition Guide

## Overview

The Communication Bridge AI now supports **real-time webcam gesture recognition** that automatically populates the message input field with detected gestures, similar to speech-to-text functionality.

## How It Works

### Architecture

```
Webcam → Browser Capture → Backend Processing → MediaPipe → Gesture Detection → Emoji Output → Input Field
```

### Workflow

1. **User enables webcam** - Browser requests camera permission
2. **Continuous frame capture** - System captures frames every 500ms
3. **Hand detection** - MediaPipe identifies hand landmarks (21 points per hand)
4. **Gesture recognition** - AI recognizes specific hand gestures
5. **Emoji mapping** - Gestures are converted to emojis
6. **Auto-populate** - Emojis are automatically added to the input field
7. **Send message** - User clicks send to translate gestures to text

## Supported Gestures

| Gesture | How to Perform | Emoji | Meaning |
|---------|---------------|-------|---------|
| **Wave** | Open palm, move side to side | 👋 | Hello/Goodbye |
| **Thumbs Up** | Thumb extended up, other fingers down | 👍 | Yes/Good/Agree |
| **Thumbs Down** | Thumb pointing down | 👎 | No/Bad/Disagree |
| **Peace Sign** | Index and middle fingers up in V shape | ✌️ | Peace/Victory |
| **OK Sign** | Thumb and index finger form circle | 👌 | OK/Perfect |
| **Pointing Up** | Only index finger extended upward | ☝️ | Attention/Wait |
| **Fist** | All fingers closed | ✊ | Stop/Power |
| **Open Palm** | All fingers extended | 🖐️ | Stop/Wait |
| **Raised Hand** | Open palm raised above wrist | 🙋 | Question/Raise hand |
| **Stop** | Open palm facing forward | ✋ | Stop/Wait |

## Using Webcam Gestures

### Step 1: Enable Webcam Mode

1. Log in to your dashboard
2. Click the **📹 Webcam** button in the input mode selector
3. The webcam section will appear

### Step 2: Start Camera

1. Click **"Start Camera"** button
2. Allow camera access when prompted by your browser
3. Your webcam feed will appear
4. Automatic gesture detection begins immediately

### Step 3: Perform Gestures

1. Position your hand in front of the camera
2. Perform a gesture from the supported list
3. The system detects the gesture in real-time
4. Detected gestures appear in the overlay: `👋 Detected: wave (95%)`
5. **Emojis are automatically added to your input field**

### Step 4: Build Your Message

- Perform multiple gestures to build a sequence
- Each detected gesture adds an emoji to the input field
- Example: 👋 (wave) + 👤 (me) + 🆘 (help) = "Hello, I need help"

### Step 5: Send Message

1. Review the emojis in your input field
2. Click **"Send Message"** button
3. The system translates your gesture sequence to text
4. The verbal translation appears in the conversation

### Step 6: Stop Camera

- Click **"Stop Camera"** when done
- This saves battery and processing power

## Features

### ✅ Automatic Detection

- Gestures are detected continuously every 500ms
- No need to click "capture" for each gesture
- Real-time feedback in the overlay

### ✅ Auto-Populate Input

- Detected emojis automatically appear in the message field
- Similar to speech-to-text functionality
- Visual feedback with green highlight when gesture is added

### ✅ Confidence Scores

- Each detection shows confidence percentage
- Example: `thumbs_up (95%)`
- Higher confidence = more accurate detection

### ✅ Multi-Hand Support

- Detects gestures from both hands
- Can recognize multiple hands simultaneously
- Each hand's gesture is processed independently

## Tips for Best Results

### Camera Setup

- **Good lighting** - Ensure your face and hands are well-lit
- **Plain background** - Avoid busy backgrounds
- **Camera position** - Position camera at chest/face level
- **Distance** - Keep hands 1-2 feet from camera

### Gesture Performance

- **Clear gestures** - Make distinct, deliberate movements
- **Hold steady** - Hold gesture for 1-2 seconds
- **Face camera** - Keep palm facing the camera
- **One at a time** - Perform one gesture at a time for clarity

### Browser Compatibility

- ✅ **Chrome** - Full support
- ✅ **Edge** - Full support  
- ✅ **Safari** - Full support (macOS/iOS)
- ⚠️ **Firefox** - Limited MediaPipe support

### HTTPS Requirement

- Webcam access requires HTTPS connection
- Use Brev secure links: `https://3001-i1jp0gsn9.brevlab.com`
- Local development: Use `localhost` (automatically secure)

## Troubleshooting

### Camera Not Starting

**Problem**: "Could not access webcam" error

**Solutions**:
1. Check browser permissions (click lock icon in address bar)
2. Ensure no other app is using the camera
3. Try refreshing the page
4. Use HTTPS connection (not HTTP)

### No Gestures Detected

**Problem**: Overlay shows "No gestures detected"

**Solutions**:
1. Improve lighting conditions
2. Move hand closer to camera
3. Perform gestures more clearly
4. Check if MediaPipe is enabled (see backend logs)

### Wrong Gestures Detected

**Problem**: System detects incorrect gestures

**Solutions**:
1. Hold gesture longer (1-2 seconds)
2. Make gesture more distinct
3. Check confidence score (should be >70%)
4. Avoid partial gestures

### Emojis Not Appearing in Input

**Problem**: Gestures detected but input field not updating

**Solutions**:
1. Check browser console for errors
2. Ensure you're in "Non-Verbal to Verbal" mode
3. Verify session is active (click "Start Simulation")
4. Refresh the page and try again

## Technical Details

### Backend Processing

```python
# Vision Service (backend/services/vision_service.py)
def process_frame(frame_data):
    # Decode base64 image
    image = decode_image(frame_data)
    
    # Process with MediaPipe Hands
    results = mediapipe_hands.process(image)
    
    # Detect gestures from landmarks
    gestures = recognize_gesture(landmarks)
    
    # Map to emojis
    emojis = [gesture_to_emoji[g] for g in gestures]
    
    return {
        "hands_detected": len(results),
        "gestures": gestures,
        "emojis": emojis,
        "confidence": avg_confidence
    }
```

### Frontend Integration

```javascript
// Automatic gesture detection (frontend/app.js)
function updateGestureDisplay(result) {
    if (result.emojis.length > 0) {
        // Get input field
        const studentInput = document.getElementById('student-input');
        
        // Add emojis to input
        studentInput.value += ' ' + result.emojis.join(' ');
        
        // Visual feedback
        studentInput.style.backgroundColor = '#e6ffed';
    }
}
```

### API Endpoints

- `POST /vision/process-frame` - Process single frame, return gestures
- `POST /vision/gesture-to-text` - Full pipeline: frame → gesture → AI response
- `GET /vision/gestures` - Get list of supported gestures

## Current Status

⚠️ **MediaPipe Status**: The system currently has MediaPipe v0.10.30+ which uses a new API. The vision service is temporarily disabled until the new API is integrated.

**Workaround**: The system falls back to manual emoji input. Users can still type emojis directly into the input field.

**GPU Deployment**: When deployed on the NVIDIA GPU instance (Brev), MediaPipe will be configured with the correct version for full gesture recognition.

## Enabling MediaPipe

To enable full webcam gesture recognition on your Brev instance:

```bash
# SSH into your Brev instance
ssh ubuntu@34.6.169.63

# Install compatible MediaPipe version
pip install mediapipe==0.10.8

# Restart backend
cd ~/Communication-Agent-AI/backend
pkill -f "python3 main.py"
nohup /usr/bin/python3 main.py > server.log 2>&1 &
```

## Future Enhancements

- [ ] Custom gesture training
- [ ] Gesture sequences (combine multiple gestures)
- [ ] Facial expression recognition
- [ ] Body pose detection
- [ ] Sign language alphabet (A-Z)
- [ ] Gesture history and favorites
- [ ] Offline gesture recognition

## Related Documentation

- [Computer Vision Guide](COMPUTER_VISION_GUIDE.md)
- [Speech-to-Text Guide](SPEECH_TO_TEXT_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Quick Start Guide](QUICK_START_BIDIRECTIONAL.md)

## Support

For issues or questions:
1. Check browser console for errors
2. Review backend logs: `tail -f ~/Communication-Agent-AI/backend/server.log`
3. Test with simple gestures first (thumbs up, wave)
4. Ensure HTTPS connection is active

---

**Last Updated**: February 2026
**Version**: 1.0.0
**Status**: Beta - MediaPipe integration pending
