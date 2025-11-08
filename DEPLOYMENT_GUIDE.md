# 🚀 Deployment Guide - Netlify + Supabase

## Overview
Project Dramamu menggunakan:
- **Netlify** untuk deploy WebApp (mini app)
- **Supabase** untuk database PostgreSQL
- **Replit** untuk backend API (FastAPI)

---

## 1️⃣ Setup Supabase Database

### Step 1: Buat Project Supabase
1. Buka https://supabase.com dan buat account
2. Create new project
3. Pilih region terdekat (Singapore recommended)
4. Save password Anda!

### Step 2: Buat Tables
Buka SQL Editor di Supabase dan jalankan:

```sql
-- Users table
CREATE TABLE users (
    telegram_id BIGINT PRIMARY KEY,
    is_vip BOOLEAN DEFAULT FALSE,
    referral_code VARCHAR(50),
    commission_balance DECIMAL(10,2) DEFAULT 0,
    total_referrals INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Movies table
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    poster_url VARCHAR(500),
    video_link VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_movies_id ON movies(id);
```

### Step 3: Get Connection Details
1. Buka **Project Settings** → **Database**
2. Copy **Connection String** (format URI)
3. Formatnya seperti:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
   ```

### Step 4: Set Environment Variables di Replit
Update Secrets di Replit dengan data dari Supabase:

```bash
DB_HOST=db.[PROJECT].supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=[YOUR_PASSWORD]
```

**✅ Database sudah siap!** Backend Anda sudah compatible dengan Supabase karena keduanya PostgreSQL.

---

## 2️⃣ Deploy WebApp ke Netlify

### Step 1: Prepare Static Files
Semua file WebApp ada di folder `static/`:
```
static/
└── drama.html    # Main WebApp
```

### Step 2: Update WEBAPP_URL
Setelah deploy ke Netlify, Anda akan dapat URL seperti:
```
https://dramamu.netlify.app
```

Update di Replit Secrets:
```bash
WEBAPP_URL=https://dramamu.netlify.app
```

### Step 3: Deploy ke Netlify

**Option A: Manual Deploy (Tercepat)**
1. Buka https://netlify.com dan login
2. Drag & drop folder `static/` ke Netlify dashboard
3. Done! Netlify akan kasih URL otomatis

**Option B: GitHub Auto-Deploy (Recommended)**
1. Push code ke GitHub repository
2. Di Netlify: **New site from Git** → Pilih repo
3. Build settings:
   - **Build command**: (kosongkan)
   - **Publish directory**: `static`
4. Deploy!

### Step 4: Update CORS di Backend
Setelah dapat Netlify URL, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dramamu.netlify.app",  # Ganti dengan URL Netlify Anda
        "https://web.telegram.org",
        "http://localhost:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart backend workflow** di Replit setelah update!

---

## 3️⃣ Update Telegram Bot WebApp URL

Setelah deploy ke Netlify, update bot button:

### Edit bot/app.py
```python
# Ganti WEBAPP_URL dengan URL Netlify Anda
WEBAPP_URL = "https://dramamu.netlify.app/drama.html"
```

Atau set via environment variable:
```bash
WEBAPP_URL=https://dramamu.netlify.app/drama.html
```

---

## 4️⃣ Test Integration

### Test Flow:
1. ✅ Start Telegram bot: `/start`
2. ✅ Klik button "Browse Drama"
3. ✅ WebApp terbuka dari Netlify
4. ✅ WebApp fetch movies dari Replit API
5. ✅ Request movie → backend validate → kirim via bot

### Troubleshooting:
- **CORS error**: Update `allow_origins` di backend
- **Database error**: Cek Supabase credentials di Secrets
- **WebApp blank**: Cek console browser (F12)
- **Bot tidak kirim video**: Cek BOT_TOKEN di Secrets

---

## 5️⃣ Environment Variables Lengkap

Semua yang perlu di-set di **Replit Secrets**:

```bash
# Bot
BOT_TOKEN=123456:ABC-DEF...              # Dari @BotFather
ADMIN_ID=123456789                       # Telegram ID admin

# Database (Supabase)
DB_HOST=db.xxxxx.supabase.co            # Dari Supabase settings
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=your_supabase_password

# WebApp (Netlify)
WEBAPP_URL=https://dramamu.netlify.app  # URL dari Netlify

# Payment (Midtrans)
MIDTRANS_SERVER_KEY=SB-Mid-server-xxx   # Dari Midtrans dashboard
MIDTRANS_CLIENT_KEY=SB-Mid-client-xxx

# Session
SESSION_SECRET=random_string_here        # Sudah ada
```

---

## 6️⃣ Deployment Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ├──────────────────┐
       │                  │
       v                  v
┌──────────────┐   ┌──────────────┐
│ Telegram Bot │   │   WebApp     │
│   (Replit)   │   │  (Netlify)   │
└──────┬───────┘   └──────┬───────┘
       │                  │
       │                  │
       v                  v
┌─────────────────────────────────┐
│      Backend API (Replit)       │
│   FastAPI + Uvicorn :5000       │
└────────────┬────────────────────┘
             │
             v
┌────────────────────────┐
│  Database (Supabase)   │
│    PostgreSQL          │
└────────────────────────┘
```

---

## 🎯 Next Steps

1. ✅ Setup Supabase database dan copy credentials
2. ✅ Deploy WebApp ke Netlify
3. ✅ Update environment variables di Replit
4. ✅ Update CORS dengan Netlify URL
5. ✅ Restart backend workflow
6. ✅ Test end-to-end flow
7. 🚀 Go live!

---

## 💡 Tips

- **Supabase Free Tier**: 500MB database, 2GB bandwidth/month
- **Netlify Free Tier**: 100GB bandwidth, auto SSL
- **Replit Deployment**: Bisa pakai Autoscale untuk production
- **Monitoring**: Cek Supabase dashboard untuk database usage

**Good luck! 🎬🍿**
