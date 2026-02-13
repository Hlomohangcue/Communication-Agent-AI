# Quick Greeting Test Guide

Test all greeting responses in your browser.

---

## 🚀 Quick Start

1. **Start Backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Open Frontend:**
   - Open `frontend/login.html` in browser
   - Login or create account
   - Go to dashboard

---

## ✅ Test Checklist

### Non-Verbal to Verbal Mode

#### Test 1: Emoji Buttons - DIFFERENTIATION TEST
- [ ] Click "Start Simulation"
- [ ] Click **🙋 Hello/Hi** button
  - Expected: "Hello! It's great to see you today!"
  - ✅ Should be GENERIC hello (not time-specific)
- [ ] Click **☀️🙋 Good Morning** button
  - Expected: "Good morning! I hope you're ready for a great day!"
  - ✅ Should mention "MORNING" and "great day"
- [ ] Click **🌤️🙋 Good Afternoon** button
  - Expected: "Good afternoon! How has your day been so far?"
  - ✅ Should mention "AFTERNOON" and ask about day
- [ ] Click **🌙🙋 Good Night** button
  - Expected: "Good night! Sleep well and see you tomorrow!"
  - ✅ Should mention "NIGHT" and "sleep"
- [ ] Click **👋✌️ Goodbye** button
  - Expected: "Goodbye! Have a wonderful rest of your day!"
  - ✅ Should say "GOODBYE" (not hello)

**IMPORTANT:** Each greeting should give a DIFFERENT, contextually appropriate response!

#### Test 2: Text Input (lowercase)
- [ ] Type "hello" in text area → Click Send
  - Expected: "Hello! It's great to see you today!"
- [ ] Type "hi" → Click Send
  - Expected: "Hello! It's great to see you today!"
- [ ] Type "good morning" → Click Send
  - Expected: "Good morning! I hope you're ready for a great day!"
- [ ] Type "good afternoon" → Click Send
  - Expected: "Good afternoon! How has your day been so far?"
- [ ] Type "good evening" → Click Send
  - Expected: "Good evening! How has your day been?"
- [ ] Type "good night" → Click Send
  - Expected: "Good night! Sleep well and see you tomorrow!"
- [ ] Type "goodbye" → Click Send
  - Expected: "Goodbye! Have a wonderful rest of your day!"

#### Test 3: Text Input (capitalized)
- [ ] Type "Hello" → Click Send
  - Expected: "Hello! It's great to see you today!"
- [ ] Type "Good Morning" → Click Send
  - Expected: "Good morning! I hope you're ready for a great day!"
- [ ] Type "Good Afternoon" → Click Send
  - Expected: "Good afternoon! How has your day been so far?"

### Verbal to Non-Verbal Mode

#### Test 4: Phrase Translation
- [ ] Click **"🗣️ → 👤 Verbal to Non-Verbal"** button
- [ ] Type or select "Hello"
  - Expected translation: 🙋
- [ ] Type or select "Good morning"
  - Expected translation: ☀️🙋
- [ ] Type or select "Good afternoon"
  - Expected translation: 🌤️🙋
- [ ] Type or select "Good night"
  - Expected translation: 🌙🙋
- [ ] Type or select "Goodbye"
  - Expected translation: 👋✌️

---

## 📊 Expected Results

### All Tests Should Show:

✅ Correct greeting response for each input
✅ Response appears in conversation history
✅ No console errors (press F12 to check)
✅ Conversation history persists when switching modes
✅ Credits decrease for free users (if applicable)

---

## 🐛 If Something Doesn't Work

### Backend Issues
```bash
# Check backend logs
cd backend
python main.py
# Look for errors in console
```

### Frontend Issues
```bash
# Open browser console (F12)
# Check for JavaScript errors
# Look at Network tab for failed API calls
```

### Common Issues

**Issue:** "Hello" gives wrong response
- **Fix:** Make sure you pulled latest code
- **Check:** `backend/agents/speech_agent.py` has text greeting detection

**Issue:** Emojis don't display correctly
- **Fix:** Make sure browser supports UTF-8
- **Try:** Chrome, Firefox, or Edge (latest versions)

**Issue:** API connection error
- **Fix:** Make sure backend is running on port 8000
- **Check:** `http://localhost:8000/` in browser

---

## 🎯 Quick Visual Test

### Expected Conversation Flow

```
You: 🙋
AI: Hello! It's great to see you today!

You: ☀️🙋
AI: Good morning! I hope you're ready for a great day!

You: good afternoon
AI: Good afternoon! How has your day been so far?

You: goodbye
AI: Goodbye! Have a wonderful rest of your day!
```

---

## ✅ Success Criteria

Your greeting system is working correctly if:

- ✅ All emoji buttons trigger correct responses
- ✅ All text greetings trigger correct responses
- ✅ Case doesn't matter (hello = Hello = HELLO)
- ✅ Responses are contextually appropriate
- ✅ Conversation history shows all messages
- ✅ Mode switching preserves conversation
- ✅ No errors in browser console

---

## 📝 Test Results Template

```
Date: _______________
Browser: _______________
Backend Version: _______________

Emoji Buttons:
[ ] 🙋 Hello/Hi - PASS / FAIL
[ ] ☀️🙋 Good Morning - PASS / FAIL
[ ] 🌤️🙋 Good Afternoon - PASS / FAIL
[ ] 🌙🙋 Good Night - PASS / FAIL
[ ] 👋✌️ Goodbye - PASS / FAIL

Text Input (lowercase):
[ ] hello - PASS / FAIL
[ ] good morning - PASS / FAIL
[ ] good afternoon - PASS / FAIL
[ ] goodbye - PASS / FAIL

Text Input (capitalized):
[ ] Hello - PASS / FAIL
[ ] Good Morning - PASS / FAIL

Translation (Verbal to Non-Verbal):
[ ] Hello → 🙋 - PASS / FAIL
[ ] Good morning → ☀️🙋 - PASS / FAIL

Overall Result: PASS / FAIL
Notes: _______________
```

---

## 🎉 All Tests Passed?

Congratulations! Your greeting system is working perfectly!

Next steps:
1. Test other features (questions, needs, emotions)
2. Deploy to production (see VULTR_DEPLOYMENT_COMPLETE.md)
3. Share with users and gather feedback

---

**Need help?** Check `GREETING_FIX_COMPLETE.md` for detailed information.
