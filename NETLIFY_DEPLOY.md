# 🌐 Deploy ke Netlify - Quick Guide

## Deploy Mini App HTML ke Netlify

---

## Prerequisites
✅ Backend sudah deployed di Render
✅ Punya URL backend (contoh: `https://dramamu-backend.onrender.com`)

---

## Option 1: Drag & Drop (Paling Mudah - 2 menit)

### Step 1: Prepare Folder
1. Buka folder `Ini backup/ini nanti di deploy netlify/`
2. Pastikan berisi semua file HTML:
   - drama.html
   - index.html
   - payment.html
   - referal.html
   - request.html

### Step 2: Update Backend URL
**PENTING!** Sebelum deploy, ganti URL backend di files:

**File `drama.html`:**
- Line 206: `https://dramamu-api.onrender.com` → URL Render Anda
- Line 308: `https://dramamu-api.onrender.com` → URL Render Anda

**File `payment.html`:**
- Line 83: `https://dramamu-api.onrender.com` → URL Render Anda

**File `referal.html`:**
- Line 100: `https://dramamu-api.onrender.com` → URL Render Anda

### Step 3: Deploy
1. Login ke https://netlify.com
2. Klik **Sites** di sidebar
3. **Drag & drop** folder `ini nanti di deploy netlify` ke area drop zone
4. Tunggu ~30 detik
5. Selesai! ✅

### Step 4: Get URL
Netlify akan berikan URL random seperti:
```
https://charming-cupcake-abc123.netlify.app
```

Atau custom nama:
```
https://dramamuid.netlify.app
```

---

## Option 2: Deploy via GitHub (Auto-deploy)

### Step 1: Push ke GitHub
Pastikan folder `ini nanti di deploy netlify/` ada di repo.

### Step 2: Connect ke Netlify
1. Login Netlify
2. Klik **Add new site** → **Import an existing project**
3. Choose **GitHub**
4. Pilih repository Anda

### Step 3: Configure Build Settings
**Base directory:**
```
Ini backup/ini nanti di deploy netlify
```

**Build command:** (kosongkan, tidak perlu build)

**Publish directory:** 
```
.
```
atau
```
Ini backup/ini nanti di deploy netlify
```

### Step 4: Deploy
1. Klik **Deploy site**
2. Tunggu ~1 menit
3. Done!

---

## 🎨 Custom Domain (Optional)

Untuk ganti URL jadi custom:

### Option A: Netlify Subdomain
1. Site settings → **Domain management**
2. **Options** → **Edit site name**
3. Ubah jadi: `dramamuid` (atau nama lain)
4. Save → URL jadi `dramamuid.netlify.app`

### Option B: Custom Domain
1. Beli domain (Namecheap, GoDaddy, dll)
2. Netlify: **Add custom domain**
3. Follow instructions untuk update DNS
4. SSL otomatis enabled oleh Netlify

---

## 🔧 Environment Variables (Tidak perlu untuk HTML static)

Karena ini pure HTML/JS, tidak perlu environment variables. Semua config sudah hardcoded di HTML files (backend URL, dll).

---

## ✅ Verification

Setelah deploy, test:

1. **Buka URL Netlify** di browser
2. Pastikan halaman load tanpa error
3. Buka **Developer Console** (F12)
4. Cek tidak ada error 404 atau CORS

**Test dengan Telegram:**
1. Buka bot Anda di Telegram
2. Bukan via browser, tapi via Telegram Mini App
3. Cek apakah bisa load film

---

## 🐛 Troubleshooting

### 404 Not Found
- Pastikan `index.html` ada di root folder publish
- Atau set custom redirect di `netlify.toml`

### CORS Error
- Backend sudah allow CORS? (sudah ada di main.py)
- Cek Network tab di browser console

### Tidak Load Film
- Cek backend URL benar di HTML files
- Test backend endpoint langsung via browser
- Cek Render backend masih running

### Telegram WebApp Error
- Pastikan buka via Telegram, bukan browser biasa
- Telegram.WebApp.initData hanya ada di Telegram app

---

## 📱 Test di Telegram

### Set Menu Button di Bot
Setelah deploy Netlify, update menu button bot:

1. Buka Telegram → **@BotFather**
2. Kirim command:
```
/setmenubutton
```
3. Pilih bot Anda
4. Pilih **Edit menu button URL**
5. Paste URL Netlify + path:
```
https://dramamuid.netlify.app/drama.html
```

### Set Bot Commands
```
/mybots
→ Pilih bot Anda
→ Edit Bot
→ Edit Commands
→ Paste:
start - Mulai menggunakan bot
```

---

## 🔄 Auto-Deploy

Jika deploy via GitHub, Netlify akan auto-deploy setiap push ke branch.

**Workflow:**
1. Edit HTML files
2. Push ke GitHub
3. Netlify auto-build & deploy (~1 menit)
4. Done!

---

## 💰 Free Tier

Netlify Free tier:
- ✅ 100 GB bandwidth/bulan
- ✅ Unlimited sites
- ✅ Free SSL (HTTPS)
- ✅ CDN global
- ✅ Instant cache invalidation

Untuk Mini App simple, free tier lebih dari cukup!

---

## 🎉 Next Steps

Setelah Netlify deployed:
1. ✅ Update bot menu button dengan URL Netlify
2. ✅ Test via Telegram (buka bot → klik menu)
3. ✅ Test pilih film → harus terkirim ke chat
4. ✅ Test fallback mechanism (user baru)

Sistem sudah production ready! 🚀
