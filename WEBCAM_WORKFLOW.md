# Webcam Gesture Recognition - Complete Workflow

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [📹 Webcam Button] ──► Activates Webcam Section               │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │  📹 Webcam Feed (640x480)                             │    │
│  │  ┌─────────────────────────────────────────────┐     │    │
│  │  │                                               │     │    │
│  │  │         [User performs gesture]               │     │    │
│  │  │              👍 Thumbs Up                     │     │    │
│  │  │                                               │     │    │
│  │  └─────────────────────────────────────────────┘     │    │
│  │                                                       │    │
│  │  Overlay: "👋 Detected: thumbs_up (95%)"            │    │
│  │           "📝 Emojis: 👍"                            │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Start Camera] [Stop Camera] [Capture Gesture]                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │ Message Input:  👋 👤 🆘                              │    │
│  │                 ↑  ↑  ↑                               │    │
│  │                 Auto-populated from gestures!         │    │
│  └───────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Send Message] ──► Translates to: "Hello, I need help"       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### 1. Initialization Phase

```
User Action: Click "📹 Webcam" button
    ↓
Frontend: Show webcam section
    ↓
User Action: Click "Start Camera"
    ↓
Browser: Request camera permission
    ↓
User: Allow camera access
    ↓
Frontend: Start video stream
    ↓
Frontend: Begin automatic detection (every 500ms)
```

### 2. Gesture Detection Loop

```
┌─────────────────────────────────────────────────────────┐
│  CONTINUOUS LOOP (Every 500ms)                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Capture Frame                                       │
│     video → canvas → base64                             │
│                                                         │
│  2. Send to Backend                                     │
│     POST /vision/process-frame                          │
│     {                                                   │
│       frame: "data:image/jpeg;base64,/9j/4AAQ...",     │
│       session_id: "abc-123"                             │
│     }                                                   │
│                                                         │
│  3. Backend Processing                                  │
│     ┌─────────────────────────────────┐               │
│     │ VisionService.process_frame()   │               │
│     │   ↓                              │               │
│     │ Decode base64 image              │               │
│     │   ↓                              │               │
│     │ MediaPipe Hand Detection         │               │
│     │   ↓                              │               │
│     │ Recognize Gesture                │               │
│     │   ↓                              │               │
│     │ Map to Emoji                     │               │
│     └─────────────────────────────────┘               │
│                                                         │
│  4. Response                                            │
│     {                                                   │
│       hands_detected: 1,                                │
│       gestures: [{                                      │
│         gesture: "thumbs_up",                           │
│         hand: "Right",                                  │
│         confidence: 0.95                                │
│       }],                                               │
│       emojis: ["👍"]                                    │
│     }                                                   │
│                                                         │
│  5. Update UI                                           │
│     ┌─────────────────────────────────┐               │
│     │ updateGestureDisplay(result)    │               │
│     │   ↓                              │               │
│     │ Show in overlay                  │               │
│     │   ↓                              │               │
│     │ Add emoji to input field ✨      │               │
│     │   ↓                              │               │
│     │ Flash green feedback             │               │
│     └─────────────────────────────────┘               │
│                                                         │
│  6. Repeat                                              │
│     Wait 500ms → Loop back to step 1                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. Message Sending Phase

```
User builds message with gestures:
    👋 (wave) → Input: "👋"
    👤 (me)   → Input: "👋 👤"
    🆘 (help) → Input: "👋 👤 🆘"
    
User clicks "Send Message"
    ↓
Frontend: sendMessage()
    ↓
Backend: POST /simulate/step
    {
        session_id: "abc-123",
        input_text: "👋 👤 🆘"
    }
    ↓
Coordinator: process_communication()
    ↓
Intent Agent: Analyze emojis
    ↓
Nonverbal Agent: Translate to text
    "Hello, I need help"
    ↓
Context Agent: Add context
    ↓
Response: Display in conversation
```

## Code Flow

### Frontend (app.js)

```javascript
// 1. Start webcam
startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: true })
    startGestureDetection()  // Begin 500ms loop
}

// 2. Continuous detection
startGestureDetection() {
    setInterval(() => {
        processCurrentFrame()  // Every 500ms
    }, 500)
}

// 3. Process frame
async processCurrentFrame() {
    // Capture
    canvas.drawImage(video, 0, 0)
    frameData = canvas.toDataURL('image/jpeg')
    
    // Send to backend
    response = await fetch('/vision/process-frame', {
        body: JSON.stringify({ frame: frameData })
    })
    
    result = await response.json()
    
    // Update UI
    updateGestureDisplay(result)
}

// 4. Auto-populate input ✨
updateGestureDisplay(result) {
    if (result.emojis.length > 0) {
        // Add to input field
        studentInput.value += ' ' + result.emojis.join(' ')
        
        // Visual feedback
        studentInput.style.backgroundColor = '#e6ffed'
        setTimeout(() => {
            studentInput.style.backgroundColor = ''
        }, 300)
    }
}
```

### Backend (vision_service.py)

```python
# 1. Process frame
def process_frame(frame_data: str):
    # Decode image
    image = decode_image(frame_data)
    
    # MediaPipe detection
    results = mediapipe_hands.process(image)
    
    # Recognize gestures
    gestures = []
    for hand_landmarks in results.multi_hand_landmarks:
        gesture = recognize_gesture(hand_landmarks)
        gestures.append(gesture)
    
    # Map to emojis
    emojis = [gesture_to_emoji[g] for g in gestures]
    
    return {
        "hands_detected": len(results),
        "gestures": gestures,
        "emojis": emojis
    }

# 2. Gesture recognition
def recognize_gesture(landmarks):
    # Count extended fingers
    fingers_up = count_fingers_up(landmarks)
    
    # Thumbs up: thumb up, others down
    if fingers_up["thumb"] and not any([
        fingers_up["index"],
        fingers_up["middle"],
        fingers_up["ring"],
        fingers_up["pinky"]
    ]):
        return "thumbs_up"
    
    # ... more gesture logic ...
```

## Data Flow

```
┌──────────────┐
│   Browser    │
│   Webcam     │
└──────┬───────┘
       │ Video Stream
       ↓
┌──────────────┐
│   Canvas     │
│   Element    │
└──────┬───────┘
       │ Base64 Image
       ↓
┌──────────────┐
│   Frontend   │
│   JavaScript │
└──────┬───────┘
       │ HTTP POST
       ↓
┌──────────────┐
│   FastAPI    │
│   Backend    │
└──────┬───────┘
       │ Frame Data
       ↓
┌──────────────┐
│  MediaPipe   │
│   Hands      │
└──────┬───────┘
       │ Landmarks (21 points)
       ↓
┌──────────────┐
│   Gesture    │
│ Recognition  │
└──────┬───────┘
       │ Gesture Name
       ↓
┌──────────────┐
│    Emoji     │
│   Mapping    │
└──────┬───────┘
       │ Emoji
       ↓
┌──────────────┐
│   Response   │
│     JSON     │
└──────┬───────┘
       │ HTTP Response
       ↓
┌──────────────┐
│   Frontend   │
│   Update UI  │
└──────┬───────┘
       │ Auto-populate
       ↓
┌──────────────┐
│    Input     │
│    Field     │
└──────────────┘
```

## Timing Diagram

```
Time    User Action              Frontend                Backend              UI Update
────────────────────────────────────────────────────────────────────────────────────────
0ms     Click "Start Camera"     Request camera          -                    -
100ms   Allow permission         Start video stream      -                    Show video
200ms   -                        Start detection loop    -                    -
500ms   Perform gesture          Capture frame           -                    -
550ms   -                        Send to backend         Receive frame        -
600ms   -                        -                       Process with MP      -
650ms   -                        -                       Recognize gesture    -
700ms   -                        Receive response        Send response        -
750ms   -                        Update overlay          -                    Show "👍"
800ms   -                        Add to input ✨         -                    Flash green
1000ms  -                        Capture next frame      -                    -
1050ms  -                        Send to backend         Receive frame        -
...     (Loop continues every 500ms)
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────┐
│  Error Scenarios                                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Camera Permission Denied                            │
│     ↓                                                   │
│     Show error: "Could not access webcam"               │
│     ↓                                                   │
│     Provide instructions to enable camera               │
│                                                         │
│  2. MediaPipe Not Available                             │
│     ↓                                                   │
│     Return error in response                            │
│     ↓                                                   │
│     Show in overlay: "⚠️ MediaPipe not installed"      │
│     ↓                                                   │
│     Fallback to manual emoji input                      │
│                                                         │
│  3. No Gesture Detected                                 │
│     ↓                                                   │
│     Return empty gestures array                         │
│     ↓                                                   │
│     Show: "No gestures detected"                        │
│     ↓                                                   │
│     Continue detection loop                             │
│                                                         │
│  4. Network Error                                       │
│     ↓                                                   │
│     Catch fetch error                                   │
│     ↓                                                   │
│     Log to console                                      │
│     ↓                                                   │
│     Continue detection loop (retry)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Performance Optimization

```
┌─────────────────────────────────────────────────────────┐
│  Optimization Strategies                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Frame Rate: 500ms intervals (2 FPS)                 │
│     - Balance between responsiveness and CPU usage      │
│     - Adjustable based on device performance            │
│                                                         │
│  2. Image Compression: JPEG quality 0.8                 │
│     - Reduces payload size                              │
│     - Maintains sufficient quality for detection        │
│                                                         │
│  3. Resolution: 640x480                                 │
│     - Optimal for hand detection                        │
│     - Lower bandwidth usage                             │
│                                                         │
│  4. Async Processing                                    │
│     - Non-blocking frame capture                        │
│     - UI remains responsive                             │
│                                                         │
│  5. Error Recovery                                      │
│     - Continue loop on errors                           │
│     - Automatic retry mechanism                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**This workflow enables seamless gesture-to-text communication, making the system accessible to non-verbal users through natural hand gestures.**
