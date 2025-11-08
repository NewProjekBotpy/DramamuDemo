# 🚀 Deploy ke Render - Quick Guide

## Prerequisites
✅ Secrets sudah diisi di Replit (BOT_TOKEN, BOT_USERNAME, DB_*)
✅ Supabase database sudah setup
✅ Telegram bot sudah dibuat

---

## Option 1: Deploy via GitHub (Recommended)

### Step 1: Push ke GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Connect Render ke GitHub
1. Login ke https://render.com
2. Klik **New** → **Web Service**
3. Klik **Connect GitHub**
4. Pilih repository Anda
5. Klik **Connect**

### Step 3: Configure Service
**Name:** `dramamu-backend`

**Region:** `Singapore` (atau terdekat)

**Branch:** `main`

**Root Directory:** (kosongkan atau `.`)

**Runtime:** `Python 3`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
bash start.sh
```

### Step 4: Set Environment Variables
Di tab **Environment**, tambahkan semua secrets:

| Key | Value | 
|-----|-------|
| BOT_TOKEN | [dari Replit Secrets] |
| BOT_USERNAME | [dari Replit Secrets] |
| DB_HOST | [dari Replit Secrets] |
| DB_PORT | [dari Replit Secrets] |
| DB_NAME | [dari Replit Secrets] |
| DB_USER | [dari Replit Secrets] |
| DB_PASS | [dari Replit Secrets] |
| PORT | 8000 |
| PYTHON_VERSION | 3.11.0 |

### Step 5: Deploy!
1. Klik **Create Web Service**
2. Tunggu ~5-10 menit
3. Monitor logs untuk memastikan tidak ada error

---

## Option 2: Deploy via render.yaml (Blueprint)

Jika repository Anda sudah ada file `render.yaml`, Render akan auto-detect dan setup semuanya.

1. Push code + render.yaml ke GitHub
2. Di Render, klik **New** → **Blueprint**
3. Connect repository
4. Render akan baca render.yaml dan setup otomatis
5. Tinggal isi environment variables

---

## ✅ Verification

Setelah deploy selesai, test endpoint:

**Health Check:**
```
https://dramamu-backend.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "..."
}
```

**Movies List:**
```
https://dramamu-backend.onrender.com/api/v1/movies
```

Should return:
```json
{
  "movies": [...]
}
```

---

## 🐛 Troubleshooting

### Build Failed
- Cek `requirements.txt` ada di root
- Cek Python version compatibility

### Database Connection Error
- Verify semua DB_* environment variables benar
- Test connection string di Supabase dashboard
- Pastikan Supabase tidak block IP Render

### Bot Not Responding
- Cek BOT_TOKEN benar
- Verify bot.py berjalan (check logs)
- Pastikan tidak ada error di startup

### Port Binding Error
- Pastikan start command pakai `$PORT` dari environment
- Jangan hardcode port

---

## 📊 Monitor Logs

Di Render Dashboard:
1. Klik service Anda
2. Tab **Logs**
3. Real-time logs akan muncul
4. Cari error atau warning

---

## 🔄 Auto-Deploy

Render akan auto-deploy setiap kali Anda push ke GitHub branch yang dipilih (biasanya `main`).

Untuk disable: 
- Settings → Auto-Deploy → Toggle OFF

---

## 💰 Free Tier Limits

Render Free Tier:
- ✅ 750 jam/bulan (cukup untuk 1 app 24/7)
- ✅ Automatic SSL
- ⚠️ App akan sleep setelah 15 menit tidak ada traffic
- ⚠️ Cold start ~30 detik

**Untuk production:** Upgrade ke paid plan ($7/mo) untuk always-on service.

---

## 🎉 Next Steps

Setelah backend deployed:
1. Simpan URL backend: `https://dramamu-backend.onrender.com`
2. Update URL di HTML files (Netlify deployment)
3. Test end-to-end flow
