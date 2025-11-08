# 🚀 PANDUAN DEPLOYMENT DRAMAMU BOT

Panduan lengkap untuk deploy sistem Dramamu ke production menggunakan Netlify, Render, dan Supabase.

---

## 📋 PERSIAPAN

Pastikan Anda memiliki akun di:
- ✅ [Supabase](https://supabase.com) - Database PostgreSQL
- ✅ [Render](https://render.com) - Backend FastAPI
- ✅ [Netlify](https://netlify.com) - Frontend Mini App
- ✅ Telegram (untuk buat bot via BotFather)
- ✅ [Midtrans](https://midtrans.com) - Payment gateway (optional untuk testing bisa pakai sandbox)

---

## 1️⃣ SETUP SUPABASE DATABASE

### Step 1: Create Project
1. Login ke https://supabase.com
2. Klik **New Project**
3. Isi:
   - **Name**: `dramamu-db` (atau nama lain)
   - **Database Password**: Buat password kuat (SIMPAN INI!)
   - **Region**: Pilih terdekat dengan user Anda
4. Klik **Create new project**
5. Tunggu ~2 menit sampai project ready

### Step 2: Run SQL Schema
1. Di dashboard Supabase, klik **SQL Editor** di sidebar
2. Klik **New query**
3. Copy-paste isi file `supabase_schema.sql` dari repo ini
4. Klik **Run** untuk execute
5. Pastikan semua tables berhasil dibuat (cek di **Table Editor**)

### Step 3: Get Database Credentials
1. Klik **Settings** → **Database**
2. Scroll ke **Connection string** → Pilih **URI**
3. Copy connection string, contoh:
   ```
   postgresql://postgres.xxxx:password@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
   ```
4. Parse untuk dapat credentials:
   - **DB_HOST**: `aws-0-ap-southeast-1.pooler.supabase.com`
   - **DB_PORT**: `6543`
   - **DB_NAME**: `postgres`
   - **DB_USER**: `postgres.xxxx`
   - **DB_PASS**: `[your-password]`

### Step 4: Enable Row Level Security (RLS) - OPTIONAL
Untuk security tambahan, bisa enable RLS di Table Editor untuk masing-masing table. Tapi untuk bot internal, bisa skip dulu.

✅ **Supabase Setup Selesai!**

---

## 2️⃣ SETUP TELEGRAM BOT

### Step 1: Create Bot
1. Buka Telegram, cari **@BotFather**
2. Kirim command `/newbot`
3. Ikuti instruksi:
   - **Bot name**: Dramamu (atau nama lain)
   - **Bot username**: `dramamu_bot` (harus unique, akhiran `_bot`)
4. Simpan **BOT_TOKEN** yang diberikan (contoh: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Step 2: Configure Bot
Kirim command ke BotFather:
```
/setdescription
[pilih bot Anda]
Nonton semua drama favorit cuma segelas kopi ☕
```

```
/setabouttext
[pilih bot Anda]
Bot streaming drama terlengkap dengan sistem VIP dan referral
```

```
/setcommands
[pilih bot Anda]
start - Mulai menggunakan bot
help - Bantuan penggunaan
```

### Step 3: Enable Mini App (Penting!)
```
/setmenubutton
[pilih bot Anda]
[Pilih: Configure menu button]
```
Tunggu sampai setup Netlify selesai untuk set URL Mini App.

✅ **Bot Setup Selesai!** Simpan BOT_TOKEN dan BOT_USERNAME.

---

## 3️⃣ SETUP MIDTRANS PAYMENT

### Step 1: Register
1. Daftar di https://midtrans.com
2. Pilih **Sandbox** untuk testing (gratis)
3. Verifikasi email

### Step 2: Get API Keys
1. Login ke Dashboard Midtrans
2. Klik **Settings** → **Access Keys**
3. Simpan:
   - **Server Key** (`MIDTRANS_SERVER_KEY`)
   - **Client Key** (`MIDTRANS_CLIENT_KEY`)

### Step 3: Test Mode
Untuk development, gunakan **Sandbox mode**. Saat production, switch ke **Production mode**.

✅ **Midtrans Setup Selesai!**

---

## 4️⃣ DEPLOY BACKEND KE RENDER

### Step 1: Push Code ke GitHub
Pastikan folder `ini yang ada di github/` sudah di push ke GitHub repo Anda.

### Step 2: Buat Web Service di Render
1. Login ke https://render.com
2. Klik **New** → **Web Service**
3. Connect GitHub repo Anda
4. Isi konfigurasi:
   - **Name**: `dramamu-api`
   - **Region**: Singapore atau terdekat
   - **Branch**: `main`
   - **Root Directory**: `ini yang ada di github` (atau `.` jika struktur berbeda)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py & uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables
Di **Environment** tab, tambahkan:
```
BOT_TOKEN=[dari BotFather]
BOT_USERNAME=dramamu_bot
DB_HOST=[dari Supabase]
DB_PORT=[dari Supabase, biasanya 6543]
DB_NAME=postgres
DB_USER=[dari Supabase]
DB_PASS=[dari Supabase]
MIDTRANS_SERVER_KEY=[dari Midtrans]
MIDTRANS_CLIENT_KEY=[dari Midtrans]
ADMIN_ID=[Telegram ID admin]
PORT=8000
```

### Step 4: Deploy
1. Klik **Create Web Service**
2. Tunggu ~5-10 menit untuk build & deploy
3. Cek logs, pastikan tidak ada error
4. Simpan URL backend Anda, contoh: `https://dramamu-api.onrender.com`

### Step 5: Test Endpoint
Buka browser, test:
```
https://dramamu-api.onrender.com/health
```
Harus return:
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "..."
}
```

✅ **Backend Deployed!**

---

## 5️⃣ DEPLOY FRONTEND KE NETLIFY

### Step 1: Update Backend URL
Sebelum deploy, update semua hardcoded URL di HTML files:

**File yang perlu diubah:**
- `drama.html` line 206, 308
- `payment.html` line 83
- `referal.html` line 100

Ganti `https://dramamu-api.onrender.com` dengan URL backend Render Anda.

### Step 2: Deploy ke Netlify
**Opsi A - Drag & Drop (Paling Mudah):**
1. Login ke https://netlify.com
2. Drag folder `ini nanti di deploy netlify/` ke Netlify dashboard
3. Selesai! Netlify akan auto-deploy

**Opsi B - GitHub (Recommended):**
1. Push folder `ini nanti di deploy netlify/` ke GitHub repo
2. Login Netlify → **New site from Git**
3. Connect GitHub repo
4. Set:
   - **Base directory**: `ini nanti di deploy netlify`
   - **Build command**: (kosongkan)
   - **Publish directory**: `.` atau `ini nanti di deploy netlify`
5. Deploy

### Step 3: Custom Domain (Optional)
1. Di Netlify dashboard, klik **Domain settings**
2. Tambahkan custom domain jika punya
3. Atau pakai subdomain gratis Netlify: `dramamu.netlify.app`

### Step 4: Simpan URL
Simpan URL Mini App Anda, contoh: `https://dramamuid.netlify.app`

✅ **Frontend Deployed!**

---

## 6️⃣ CONNECT SEMUA KOMPONEN

### Step 1: Update Bot Menu Button
Kembali ke BotFather di Telegram:
```
/setmenubutton
[pilih bot Anda]
[Pilih: Edit menu button URL]
[Paste URL Netlify]: https://dramamuid.netlify.app/drama.html
```

### Step 2: Set Bot Commands
```
/mybots
[pilih bot Anda]
[Edit Bot]
[Edit Commands]
```
Paste:
```
start - Mulai menggunakan bot
```

### Step 3: Test Bot
1. Buka bot Anda di Telegram
2. Kirim `/start`
3. Klik tombol **CARI JUDUL**
4. Mini App harus terbuka dengan daftar film

✅ **Semua Komponen Terkoneksi!**

---

## 7️⃣ TESTING END-TO-END

### Test Scenario 1: User Baru (Fallback Mechanism)
1. Buka bot dengan akun Telegram yang **baru pertama kali**
2. **JANGAN** kirim `/start` dulu
3. Dari akun lain, buka bot → klik tombol CARI JUDUL
4. Pilih film
5. System harus return **fallback link**
6. Klik link tersebut
7. Film harus terkirim

### Test Scenario 2: User Existing
1. User yang sudah pernah `/start`
2. Klik film
3. Film harus langsung terkirim tanpa fallback

### Test Scenario 3: VIP Check
1. User non-VIP klik film
2. Harus muncul notif "Perlu VIP"
3. User bisa klik "Upgrade VIP"

### Test Scenario 4: Payment
1. Klik **BELI VIP**
2. Pilih paket
3. Midtrans popup harus muncul
4. Test dengan kartu sandbox Midtrans:
   - **Card Number**: `4811 1111 1111 1114`
   - **CVV**: `123`
   - **Exp**: `01/25`

### Test Scenario 5: Referral
1. Klik **CARI CUAN**
2. Copy referral link
3. Buka dengan akun lain
4. System harus tracking referral

---

## 🔧 TROUBLESHOOTING

### Backend Error di Render
**Cek Logs:**
```
Dashboard → Logs → View latest logs
```

**Common Issues:**
- ❌ Database connection failed → Cek DB credentials
- ❌ Module not found → Pastikan requirements.txt complete
- ❌ Port binding error → Pastikan `PORT=$PORT` di start command

### Mini App Tidak Terhubung ke Backend
**Cek:**
1. URL backend di HTML files sudah benar?
2. CORS enabled di FastAPI? (sudah ada di main.py)
3. Backend endpoint `/api/v1/movies` bisa diakses?

### Bot Tidak Kirim Film
**Cek:**
1. BOT_TOKEN benar?
2. Database connection working?
3. Pending actions table ada data?

### Payment Tidak Jalan
**Cek:**
1. Midtrans keys benar? (Server Key di backend, Client Key di HTML)
2. Mode sandbox atau production match?
3. Snap.js loaded di payment.html?

---

## 📊 MONITORING

### Supabase
- Dashboard → **Table Editor** → Lihat data real-time
- **SQL Editor** → Query untuk analytics

### Render
- **Metrics** tab → CPU, Memory usage
- **Logs** → Real-time logs backend

### Netlify
- **Analytics** → Visitor stats
- **Functions** → Jika pakai serverless functions

---

## 🎉 SELESAI!

Sistem Dramamu sekarang sudah live di production!

**URLs Penting:**
- 🤖 Bot: `https://t.me/dramamu_bot`
- 🎬 Mini App: `https://dramamuid.netlify.app`
- 🔧 Backend API: `https://dramamu-api.onrender.com`
- 💾 Database: Supabase Dashboard

**Next Steps:**
1. Tambah film ke database via Supabase
2. Monitor logs untuk debugging
3. Setup analytics (optional)
4. Marketing & user acquisition!

---

## 📞 SUPPORT

Jika ada masalah:
1. Cek logs di Render
2. Cek database di Supabase
3. Test endpoint via Postman/curl
4. Debug dengan console.log di HTML files

Good luck! 🚀
