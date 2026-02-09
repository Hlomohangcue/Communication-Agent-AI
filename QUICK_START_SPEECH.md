# Quick Start - Speech Recording

## 🚀 Test Speech Recording Now

### Step 1: Test Microphone (Recommended First)
```bash
# Open the test page in your browser
frontend/mic-test.html
```
This simple page will help you:
- Verify microphone access
- Test continuous recording
- Troubleshoot permission issues

### Step 2: Use in Main Dashboard
```bash
# Start backend
cd backend
python main.py

# Open dashboard
frontend/dashboard.html
```

## 🎤 How to Use Speech Mode

1. **Start Simulation** - Click "Start Simulation" button
2. **Switch to Speech** - Click "Speech" button (top of input area)
3. **Start Recording** - Click "Start Recording" button
4. **Allow Microphone** - Click "Allow" when browser asks for permission
5. **Speak Clearly** - Your words will appear in the transcript box
6. **Keep Speaking** - Recording continues until you stop it
7. **Stop Recording** - Click "Stop Recording" when done
8. **Send Message** - Click "Send Message" to send your speech

## ⚠️ Troubleshooting

### "Microphone access denied" Error

**Quick Fix:**
1. Look for 🔒 icon in browser address bar
2. Click it
3. Find "Microphone" → Change to "Allow"
4. Refresh page (F5)

**Still Not Working?**
- Try Chrome or Edge (best support)
- Make sure you're on `localhost` or `https://`
- Check browser settings: `chrome://settings/content/microphone`

### Recording Stops Immediately

**This is now fixed!** The new code:
- ✅ Automatically restarts when browser pauses
- ✅ Keeps your transcript across restarts
- ✅ Only stops when you click "Stop Recording"

### No Speech Detected

- Speak louder or closer to microphone
- Check microphone is not muted
- Test microphone in system settings
- Try the `mic-test.html` page first

## 🔧 Technical Notes

**Browser Support:**
- ✅ Chrome (recommended)
- ✅ Edge
- ✅ Safari
- ❌ Firefox (no support)

**Requirements:**
- Internet connection (uses Google's speech API)
- Microphone access permission
- HTTPS or localhost

**Limitations:**
- Browser may pause after ~60 seconds (auto-restarts)
- Requires internet (cloud-based recognition)
- English only (can be changed in code)

## 📝 What Changed?

### Before:
- Recording stopped after a few seconds
- Transcript lost on restart
- Poor error handling

### After:
- ✅ Continuous recording until you stop
- ✅ Transcript persists across restarts
- ✅ Better error messages
- ✅ Auto-restart on browser pause
- ✅ Clear permission instructions

## 🎯 Testing Checklist

Test these scenarios:
- [ ] Click "Start Recording" → microphone activates
- [ ] Speak a sentence → appears in transcript
- [ ] Pause for 3 seconds → recording continues
- [ ] Speak another sentence → adds to transcript
- [ ] Wait 10 seconds → still recording
- [ ] Click "Stop Recording" → stops
- [ ] Click "Send Message" → message sent
- [ ] Switch to Text mode → works
- [ ] Switch back to Speech → works

## 💡 Tips

1. **First Time**: Use `mic-test.html` to verify everything works
2. **Permission Issues**: Check browser address bar for 🔒 icon
3. **Best Quality**: Speak clearly, avoid background noise
4. **Long Messages**: Recording continues as long as you need
5. **Switching Modes**: Can switch between Text/Speech anytime

## 🆘 Need Help?

1. Check browser console (F12) for error messages
2. Try `mic-test.html` for isolated testing
3. Verify backend is running on port 8000
4. Check `SPEECH_RECORDING_FIX.md` for detailed info
