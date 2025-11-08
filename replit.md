# Dramamu - Drama Streaming Bot

## Overview
Dramamu adalah Telegram bot untuk streaming drama dengan sistem VIP membership dan referral program. Project ini terdiri dari:
- **Backend (FastAPI)**: API server untuk manage movies, users, payments
- **Bot (Telegram)**: Telegram bot untuk interaksi dengan user
- **WebApp (Static HTML)**: Frontend untuk browse dan request movies

## Recent Changes (Nov 8, 2025)
- ✅ Fixed requirements.txt duplicates - clean version pinning
- ✅ Added Netlify deployment configuration (netlify.toml)
- ✅ Updated .env.example with Supabase instructions
- ✅ Created DEPLOYMENT_GUIDE.md for Netlify + Supabase setup
- ✅ Backend fully compatible with Supabase PostgreSQL

## Previous Changes (Nov 7, 2025)
- ✅ Fixed dependency mismatch (pyTelegramBotAPI → python-telegram-bot)
- ✅ Added missing `/api/v1/handle_movie_request` endpoint with security validation
- ✅ Improved error handling with context managers
- ✅ Added mandatory Telegram initData validation (HMAC-SHA256)
- ✅ Reorganized file structure (backend/, bot/, static/)
- ✅ Fixed CORS configuration
- ✅ Better logging and error handling

## Project Architecture

### Directory Structure
```
.
├── backend/
│   └── main.py          # FastAPI server
├── bot/
│   └── app.py           # Telegram bot
├── static/
│   └── drama.html       # WebApp frontend
├── poster.jpg           # Bot welcome image
├── requirements.txt     # Python dependencies
├── start.sh            # Start script untuk dev
└── replit.md           # This file
```

### Tech Stack
- **Backend**: FastAPI (hosted on Replit)
- **Database**: Supabase PostgreSQL
- **Bot**: python-telegram-bot v20 (hosted on Replit)
- **Frontend**: Vanilla JS, Tailwind CSS, Telegram WebApp SDK (deployed to Netlify)
- **Payment**: Midtrans

### Key Features
1. **Movie Browsing**: Users can browse movies via WebApp
2. **VIP System**: Only VIP users can watch full movies
3. **Payment Integration**: Midtrans for VIP subscriptions
4. **Referral Program**: Users earn commission from referrals
5. **Request System**: Users can request new movies

## Deployment Architecture

```
User
  │
  ├─────────────────┬────────────────────┐
  │                 │                    │
  v                 v                    v
Telegram Bot    WebApp              Backend API
(Replit)       (Netlify)            (Replit)
  │                 │                    │
  └─────────────────┴────────────────────┘
                    │
                    v
              Database (Supabase)
```

## Environment Variables Required
```
# Telegram
BOT_TOKEN=              # From @BotFather
ADMIN_ID=               # Your Telegram ID

# Database (Supabase)
DB_HOST=                # db.xxxxx.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=                # From Supabase dashboard

# WebApp (Netlify)
WEBAPP_URL=             # https://yourapp.netlify.app

# Payment (Midtrans)
MIDTRANS_SERVER_KEY=    # From Midtrans dashboard
MIDTRANS_CLIENT_KEY=    # From Midtrans dashboard
```

**📖 See DEPLOYMENT_GUIDE.md for step-by-step setup!**

## API Endpoints

### Public Endpoints
- `GET /` - Health check
- `GET /health` - Database health check
- `GET /api/v1/movies` - Get all movies
- `GET /api/v1/user_status/{telegram_id}` - Check VIP status
- `GET /api/v1/referral_stats/{telegram_id}` - Get referral stats

### Protected Endpoints
- `POST /api/v1/handle_movie_request` - Handle movie request from WebApp
- `POST /api/v1/create_payment` - Create Midtrans payment

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    is_vip BOOLEAN DEFAULT FALSE,
    referral_code VARCHAR(50),
    commission_balance DECIMAL(10,2) DEFAULT 0,
    total_referrals INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Movies Table
```sql
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    poster_url VARCHAR(500),
    video_link VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Development Notes

### Running Locally
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run: `./start.sh` or run services separately:
   - Backend: `cd backend && uvicorn main:app --reload --port 5000`
   - Bot: `cd bot && python app.py`

### WebApp Integration
- Frontend hosted di Netlify: https://dramamuid.netlify.app
- Uses Telegram WebApp SDK for authentication
- Communicates with backend via REST API
- Validates initData for security

### Bot Commands
- `/start` - Show main menu with WebApp buttons

### WebApp Actions
- `watch` - Request to watch a movie (sends via bot)
- `request_drama` - Request new drama
- `withdraw_referral` - Withdraw referral commission

## Security Features
1. Telegram initData validation using HMAC-SHA256
2. Context managers for database connections
3. Proper error handling and logging
4. CORS restricted to specific origins
5. Environment-based configuration

## Deployment Steps

### Quick Start:
1. **Setup Supabase**: Create project, run SQL schema (see DEPLOYMENT_GUIDE.md)
2. **Deploy to Netlify**: Drag & drop `static/` folder or connect GitHub
3. **Configure Replit Secrets**: Add all environment variables from .env.example
4. **Update CORS**: Add your Netlify URL to backend/main.py
5. **Restart Backend**: Restart workflow to apply changes
6. **Test**: Start bot → Browse Drama → Request movie

### Detailed Guide:
See **DEPLOYMENT_GUIDE.md** for complete instructions!

## Known Issues & TODO
- [ ] Add rate limiting (slowapi already installed)
- [ ] Implement Midtrans webhook for auto VIP activation
- [ ] Add database migrations (Alembic)
- [ ] Improve caching for movie data
- [ ] Add admin panel
- [ ] Better error messages for users

## User Preferences
- Uses Indonesian language for user-facing messages
- Casual, friendly tone ("bre", emoji usage)
- Clean, modern UI design
