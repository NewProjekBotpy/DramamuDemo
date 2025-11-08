# Dramamu - Telegram Bot Film dengan Mini App

## Konteks Utama Sistem (Penyaring Prompt)

### Tujuan Inti Sistem
Membangun sistem Telegram Bot film yang memungkinkan user memilih dan menonton drama melalui Mini App, dengan FastAPI sebagai proxy/perantara untuk mengirim konten ke Telegram secara tidak langsung.

### Arsitektur Kritis

**Alur Komunikasi Utama:**
```
Mini App (Netlify) → FastAPI Backend → Telegram Bot API → User
```

### Komponen Sistem

1. **Telegram Bot** (`ini yang ada di github/bot.py`)
   - Handle command `/start` dan token fallback
   - Mengirim InlineKeyboardButton dengan web_app ke Mini App
   - Menerima data dari Mini App via sendData
   - Kirim film ke user via sendMessage/sendPhoto

2. **FastAPI Backend** (`ini yang ada di github/main.py`)
   - Endpoint utama: `/api/v1/handle_movie_request`
   - Verifikasi initData Telegram (HMAC-SHA256)
   - Cek status VIP dari database
   - Proxy request ke Telegram Bot API
   - Buat fallback token jika user belum `/start`
   - Handle payment via Midtrans
   - Manage referral system

3. **Mini App HTML** (`ini nanti di deploy netlify/`)
   - `drama.html` - Daftar film dan pencarian
   - `payment.html` - Pembelian VIP via Midtrans
   - `referal.html` - Sistem referral & penarikan komisi
   - `request.html` - Request drama baru

4. **Database PostgreSQL (Supabase)**
   - Single source of truth untuk:
     - Status VIP user
     - Pending actions (fallback mechanism)
     - Payment & referral data
     - Activity logs

### Mekanisme Fallback Kritis

**Masalah:** User baru belum pernah `/start` bot → Bot tidak bisa kirim pesan (403 Forbidden)

**Solusi:**
1. Mini App kirim request ke FastAPI dengan initData
2. FastAPI coba kirim via Bot API
3. Jika gagal (403) → Buat `start_token` unik
4. Simpan di `pending_actions` table dengan expiry 15 menit
5. Return link: `https://t.me/{BOT_USERNAME}?start={TOKEN}`
6. User klik link → Bot handle `/start {TOKEN}`
7. Bot ambil data dari `pending_actions` → Kirim film
8. Setelah sekali `/start`, user bisa terima pesan selamanya

### Keamanan
- Verifikasi initData menggunakan HMAC-SHA256 (official Telegram method)
- Token fallback sekali pakai dengan expiry 5-15 menit
- Rate limiting pada semua endpoint API
- Validasi input untuk mencegah injection

### Dependensi Utama
```
fastapi, uvicorn, psycopg2-binary, python-telegram-bot
midtransclient, slowapi, pydantic
```

### URL Backend Production
- Backend API: `https://dramamu-api.onrender.com`
- Mini App: `https://dramamuid.netlify.app`
- Bot Username: `@dramamu_bot`

### Risiko Arsitektural
1. **Database Dependency** - Jika Supabase down, semua flow terputus (VIP check, pending actions)
2. **Duplikasi Logic** - bot.py dan main.py duplicate initData validation & DB access (risk divergence)
3. **Race Condition** - Dua jalur akses DB (bot & backend) tanpa koordinasi transaksi
4. **API Availability** - Sangat bergantung pada Telegram Bot API availability

### Environment Variables Required
```
BOT_TOKEN - Token bot Telegram
BOT_USERNAME - Username bot
DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS - PostgreSQL connection
MIDTRANS_SERVER_KEY, MIDTRANS_CLIENT_KEY - Payment gateway
ADMIN_ID - ID admin Telegram
```

### Status Development
- Backend: Ada di `ini yang ada di github/`
- Frontend: Ada di `ini nanti di deploy netlify/`
- Database: Supabase (PostgreSQL)
- Payment: Midtrans Sandbox mode
- Deployment: Backend → Render/Replit, Frontend → Netlify

---

## Prinsip Development

Saat bekerja dengan sistem ini, fokus pada:
1. **Alur komunikasi** Mini App → FastAPI → Bot harus selalu berfungsi
2. **Mekanisme fallback** dengan start_token adalah fitur kritis
3. **Verifikasi initData** wajib dilakukan di semua endpoint yang menerima data dari Mini App
4. **Supabase sebagai single source of truth** untuk semua state management
5. **Error handling comprehensive** untuk semua API calls

Jangan fokus pada:
- Hardcoded URL (akan diganti saat deployment)
- Environment variables kosong (akan diisi saat setup)
- Struktur folder (akan dirapikan setelah sistem stabil)
