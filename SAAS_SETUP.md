# SaaS Authentication & Freemium System

## Overview
Communication Bridge AI now includes a complete SaaS authentication system with freemium credits and subscription plans.

## Features Implemented

### 1. Authentication System
- **User Registration**: Email/password signup with validation
- **User Login**: Secure JWT-based authentication
- **Password Security**: Bcrypt hashing for password storage
- **Token Management**: 7-day JWT tokens with automatic expiration
- **Session Persistence**: Remember me functionality

### 2. Freemium Credit System
- **Free Plan**: 100 free messages/month
- **Credit Tracking**: Real-time credit usage monitoring
- **Credit Deduction**: Automatic deduction per message sent
- **Credit History**: Full audit trail of credit usage

### 3. Subscription Plans

#### Free Plan
- 100 messages/month
- Basic ASL translation
- 7-day conversation history
- Community support

#### Pro Plan ($19/month)
- Unlimited messages
- Advanced AI features
- Unlimited conversation history
- Priority support
- No credit deductions

### 4. Database Schema

#### Users Table
```sql
- id (TEXT PRIMARY KEY)
- email (TEXT UNIQUE)
- name (TEXT)
- password_hash (TEXT)
- plan (TEXT) - 'free' or 'pro'
- credits (INTEGER) - default 100
- created_at (TEXT)
- last_login (TEXT)
- is_active (BOOLEAN)
```

#### Credit Usage Table
```sql
- id (INTEGER PRIMARY KEY)
- user_id (TEXT)
- session_id (TEXT)
- credits_used (INTEGER)
- action_type (TEXT)
- created_at (TEXT)
```

#### Subscriptions Table
```sql
- id (INTEGER PRIMARY KEY)
- user_id (TEXT)
- plan (TEXT)
- status (TEXT)
- started_at (TEXT)
- expires_at (TEXT)
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Login and get token
- `GET /auth/verify` - Verify token validity
- `GET /auth/me` - Get current user info
- `GET /auth/credits` - Get remaining credits

### Protected Endpoints
All simulation endpoints now require authentication:
- `POST /simulate/start` - Requires Bearer token
- `POST /simulate/step` - Requires Bearer token, uses 1 credit (free plan only)

## Frontend Files

### Login Page (`frontend/login.html`)
- Modern, responsive design
- Tab-based login/signup interface
- Features sidebar with pricing
- Social login placeholder (Google)
- Freemium badge highlighting free trial

### Authentication Styles (`frontend/auth-styles.css`)
- Gradient background
- Card-based layout
- Responsive design (mobile-friendly)
- Smooth animations
- Notification system

### Authentication Logic (`frontend/auth.js`)
- Form validation
- API integration
- Token storage (localStorage/sessionStorage)
- Auto-redirect if already logged in
- Error handling with notifications

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `bcrypt==4.1.2` - Password hashing
- `PyJWT==2.8.0` - JWT token generation

### 2. Environment Variables
Add to `.env`:
```
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Initialize Database
The database will auto-initialize with new tables on first run:
```bash
python main.py
```

### 4. Access the System
1. Open `frontend/login.html` in browser
2. Create an account (gets 100 free credits)
3. Login and access dashboard
4. Credits deduct automatically per message

## User Flow

### New User
1. Visit login page
2. Click "Sign Up" tab
3. Enter name, email, password
4. Account created with 100 free credits
5. Redirected to login
6. Login and access dashboard

### Returning User
1. Visit login page
2. Enter email and password
3. Check "Remember me" for persistent login
4. Access dashboard
5. Credits displayed in user account section

### Credit Usage
1. Free plan users: 1 credit per message
2. Pro plan users: Unlimited messages
3. When credits reach 0: Upgrade prompt
4. Credits reset monthly (future feature)

## Security Features

### Password Security
- Bcrypt hashing with salt
- Minimum 8 characters required
- Password confirmation on signup

### Token Security
- JWT with 7-day expiration
- Secure secret key
- Bearer token authentication
- Automatic token verification

### API Security
- All simulation endpoints protected
- User authentication required
- Credit validation before processing
- Proper error messages (no info leakage)

## Future Enhancements

### Payment Integration
- Stripe integration for Pro plan
- Automatic credit refills
- Monthly subscription billing
- Invoice generation

### Credit Management
- Monthly credit reset for free users
- Credit purchase options
- Bulk credit packages
- Referral bonuses

### User Dashboard
- Credit usage analytics
- Billing history
- Plan upgrade/downgrade
- Account settings

### Admin Panel
- User management
- Credit allocation
- Usage analytics
- System monitoring

## Testing

### Test User Creation
```bash
# Using curl
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Deployment Considerations

### Production Checklist
- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Enable HTTPS only
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting
- [ ] Set up database backups
- [ ] Enable logging and monitoring
- [ ] Add email verification
- [ ] Implement password reset
- [ ] Add 2FA option
- [ ] Set up payment gateway

### Environment Variables
```
JWT_SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-db-url>
STRIPE_SECRET_KEY=<stripe-key>
STRIPE_WEBHOOK_SECRET=<webhook-secret>
EMAIL_SERVICE_KEY=<email-api-key>
```

## Support

For issues or questions:
- Check logs in backend console
- Verify database initialization
- Ensure all dependencies installed
- Check API endpoint responses
- Review browser console for frontend errors

## License
Proprietary - Communication Bridge AI SaaS Platform
