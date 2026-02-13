# Quick Start: SaaS Authentication System

## 🚀 Get Started in 3 Steps

### Step 1: Install New Dependencies
```bash
cd backend
pip install bcrypt==4.1.2 PyJWT==2.8.0
```

### Step 2: Start the Backend
```bash
python main.py
```

The database will automatically create new tables for users, credits, and subscriptions.

### Step 3: Open the Login Page
Open `frontend/login.html` in your browser or use Live Server.

## 📝 Create Your First Account

1. Click the **"Sign Up"** tab
2. Enter your details:
   - Full Name: `John Doe`
   - Email: `john@example.com`
   - Password: `password123` (min 8 characters)
   - Confirm Password: `password123`
3. Check "I agree to Terms"
4. Click **"Create Account"**
5. You'll get **100 free credits** automatically! 🎁

## 🔐 Login

1. Enter your email and password
2. Check "Remember me" to stay logged in
3. Click **"Login"**
4. You'll be redirected to the dashboard

## 💳 How Credits Work

### Free Plan (Default)
- **100 free messages** when you sign up
- **1 credit = 1 message**
- Credits deduct automatically when you send messages
- Perfect for trying out the system!

### Pro Plan ($19/month)
- **Unlimited messages** - no credit deductions
- Advanced AI features
- Unlimited conversation history
- Priority support

## 🎯 Using the System

1. **Login** at `frontend/login.html`
2. **Dashboard** opens automatically
3. **User Account** section shows:
   - Your name
   - Your role (Student/Teacher)
   - Settings and Help buttons
4. **Send messages** - credits deduct automatically (free plan only)
5. **Check credits** - displayed in user account section

## 🔄 Testing the System

### Test Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Response includes:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid-here",
    "email": "test@example.com",
    "name": "Test User",
    "plan": "free",
    "credits": 100
  }
}
```

### Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Database Tables Created

The system automatically creates these tables:

1. **users** - User accounts and credits
2. **sessions** - Communication sessions (linked to users)
3. **messages** - All messages sent
4. **credit_usage** - Credit usage history
5. **subscriptions** - Subscription plans
6. **agent_logs** - AI agent decision logs
7. **gestures** - Gesture library
8. **phrases** - Common phrases
9. **gesture_sequences** - Translation history

## 🎨 Features

### Login Page
- ✅ Modern, responsive design
- ✅ Tab-based login/signup
- ✅ Password validation
- ✅ Remember me option
- ✅ Social login ready (Google)
- ✅ Features sidebar with pricing
- ✅ Freemium badge

### Dashboard
- ✅ User account section
- ✅ Dynamic role display
- ✅ Credit tracking
- ✅ Settings and help buttons
- ✅ All existing features

### Backend
- ✅ JWT authentication
- ✅ Bcrypt password hashing
- ✅ Credit management
- ✅ Plan management
- ✅ Usage tracking
- ✅ Protected endpoints

## 🔒 Security

- **Passwords**: Hashed with bcrypt + salt
- **Tokens**: JWT with 7-day expiration
- **API**: Bearer token authentication
- **Validation**: Email format, password strength
- **Protection**: All simulation endpoints require auth

## 🐛 Troubleshooting

### "Module not found: bcrypt"
```bash
pip install bcrypt==4.1.2
```

### "Module not found: jwt"
```bash
pip install PyJWT==2.8.0
```

### "401 Unauthorized"
- Check if you're logged in
- Verify token is being sent
- Token might be expired (7 days)

### "402 Insufficient credits"
- Free plan users ran out of credits
- Upgrade to Pro plan for unlimited messages
- Or wait for monthly reset (future feature)

### Database errors
```bash
# Delete old database and restart
rm backend/communication_bridge.db
python backend/main.py
```

## 📈 Next Steps

1. **Customize**: Update branding, colors, logos
2. **Payment**: Integrate Stripe for Pro plan
3. **Email**: Add email verification
4. **Reset**: Implement password reset
5. **Admin**: Create admin dashboard
6. **Analytics**: Add usage analytics
7. **Mobile**: Create mobile app
8. **API**: Expose public API

## 💡 Tips

- **Free Trial**: Every new user gets 100 free credits
- **Testing**: Use different emails for testing
- **Development**: Use `remember me` to stay logged in
- **Production**: Change JWT_SECRET_KEY in .env
- **Monitoring**: Check backend logs for errors

## 🎉 You're Ready!

Your SaaS authentication system is now live! Users can:
1. Sign up and get 100 free credits
2. Login securely with JWT
3. Use the communication system
4. Track their credit usage
5. Upgrade to Pro for unlimited access

Happy coding! 🚀
