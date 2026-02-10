# Quick Start - Bidirectional Communication

## 🚀 Get Started in 3 Minutes!

### Step 1: Start the Backend
```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Open the Dashboard
Open in your browser:
```
frontend/dashboard.html
```

### Step 3: Start a Session
Click the **"Start Session"** button

### Step 4: Choose Your Mode

#### Option A: Non-Verbal → Verbal (Original)
- Non-verbal user sends gestures
- Verbal user receives text
- Same as before, but with more gestures!

#### Option B: Verbal → Non-Verbal (NEW!)
1. Click **"Verbal → Non-Verbal"** button
2. Type a message in the verbal user panel
3. Click **"Send to Non-Verbal User"**
4. See it translated to gestures!

#### Option C: Bidirectional (NEW!)
1. Click **"Bidirectional"** button
2. Both users can communicate:
   - Left panel: Non-verbal user (gestures)
   - Right panel: Verbal user (text)
3. Messages translate in both directions!

## 🎯 Try These Examples

### Example 1: Simple Greeting
**Verbal user types:** "Good morning"
**Non-verbal user sees:** 👋 ☀️

### Example 2: Ask for Help
**Verbal user types:** "Can you help me?"
**Non-verbal user sees:** ❓ 🆘 👤

### Example 3: Express Need
**Non-verbal user selects:** 👤 🚻
**Verbal user sees:** "I need to go to the bathroom"

### Example 4: Use Quick Phrases
1. Click a phrase button (e.g., "Thank you")
2. It auto-fills the input
3. Click send
4. See the translation!

## 🎨 Features to Explore

### Gesture Palette
- Click any emoji to add it to your message
- 80+ gestures organized by category
- Hover to see descriptions

### Phrase Library
- Pre-built common phrases
- Categories: Greetings, Questions, Needs, Responses, Classroom
- One-click selection

### Real-Time Translation
- Text automatically converts to gestures
- Gestures automatically convert to text
- See both formats simultaneously

## 📊 What's Different?

### Before (Original System)
```
Non-Verbal User → Gestures → AI → Text → Verbal User
```

### Now (Bidirectional System)
```
Non-Verbal User ←→ Gestures ←→ AI ←→ Text ←→ Verbal User
```

Both directions work!

## 🔧 Troubleshooting

### Backend Not Starting?
```bash
# Make sure you're in the backend folder
cd backend

# Check if port 8000 is available
# If not, change port in main.py
python main.py
```

### Gestures Not Showing?
- Refresh the page
- Check browser console (F12)
- Verify backend is running

### Translation Not Working?
- Check your `.env` file has `GEMINI_API_KEY`
- Verify API key is valid
- Check backend console for errors

## 📝 Quick Reference

### Keyboard Shortcuts
- **Ctrl+Enter**: Send message (in text mode)
- **F5**: Refresh page
- **F12**: Open developer console

### Common Gestures
- 👋 = Hello/Goodbye
- 👍 = Yes/Good
- 👎 = No/Bad
- ❓ = Question/What
- 🆘 = Help
- 🚻 = Bathroom
- 💧 = Water/Thirsty
- 🍎 = Food/Hungry
- 😊 = Happy
- 📚 = Book/Study

### API Endpoints
- `POST /translate/text-to-gesture` - Translate text to gestures
- `GET /gestures` - Get all gestures
- `GET /phrases` - Get common phrases
- `POST /phrases/custom` - Add custom phrase

## 🎓 Next Steps

1. **Explore all gesture categories**
   - Basic, Questions, Needs, Emotions, Classroom

2. **Try complex sentences**
   - "Can you help me with my math homework?"
   - "I don't understand this question"
   - "I'm hungry and need a break"

3. **Test bidirectional mode**
   - Send messages from both sides
   - See real-time translation
   - Experience true two-way communication

4. **Create custom phrases**
   - Use the API to add your own
   - Build a personalized phrase library

5. **Check the documentation**
   - `BIDIRECTIONAL_FEATURES.md` - Full feature guide
   - `ENHANCEMENT_PLAN.md` - Technical details
   - `README.md` - Project overview

## 💡 Tips

1. **Start Simple**: Try basic phrases first
2. **Use Quick Phrases**: Faster than typing
3. **Combine Gestures**: Create your own sequences
4. **Check Translation Method**: See how AI interpreted your text
5. **Save Favorites**: Note which phrases work best

## 🎉 You're Ready!

You now have a fully bidirectional communication system with:
- ✅ 80+ ASL-inspired gestures
- ✅ Common phrase library
- ✅ AI-powered text-to-gesture translation
- ✅ Gesture-to-text translation
- ✅ Real-time bidirectional communication
- ✅ Multiple communication modes

Start communicating! 🌉
