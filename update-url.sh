#!/bin/bash

# ============================================
# SCRIPT AUTO-UPDATE URL DEVELOPMENT
# ============================================
# Script ini otomatis update URL backend di config.js
# Jalankan setiap kali URL Replit berubah

echo "🔄 Updating Backend URL in Frontend Config..."

# Dapatkan URL development saat ini dari REPLIT_DEV_DOMAIN
if [ -n "$REPLIT_DEV_DOMAIN" ]; then
    CURRENT_URL="https://$REPLIT_DEV_DOMAIN"
elif [ -n "$REPLIT_DOMAINS" ]; then
    # Fallback ke REPLIT_DOMAINS jika REPLIT_DEV_DOMAIN tidak ada
    CURRENT_URL="https://$REPLIT_DOMAINS"
else
    echo "❌ ERROR: REPLIT_DEV_DOMAIN atau REPLIT_DOMAINS tidak ditemukan!"
    echo "   Pastikan script ini dijalankan di Replit environment."
    exit 1
fi

if [ -z "$CURRENT_URL" ] || [ "$CURRENT_URL" = "https://" ]; then
    echo "❌ ERROR: Gagal mendapatkan URL Replit!"
    exit 1
fi

echo "📍 Current URL: $CURRENT_URL"

# File config yang akan diupdate
CONFIG_FILE="ini nanti di deploy netlify/config.js"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ ERROR: File $CONFIG_FILE tidak ditemukan!"
    exit 1
fi

# Backup config lama
cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
echo "💾 Backup created: $CONFIG_FILE.backup"

# Update URL di config.js
# Cari baris yang ada BACKEND_URL dan replace dengan URL baru
sed -i.tmp "s|const BACKEND_URL = 'https://.*';|const BACKEND_URL = '$CURRENT_URL';|g" "$CONFIG_FILE"
rm -f "$CONFIG_FILE.tmp"

echo "✅ Config.js updated successfully!"
echo ""
echo "📋 Next Steps:"
echo "   1. Upload folder 'ini nanti di deploy netlify' ke Netlify"
echo "   2. Atau commit & push ke GitHub (jika deploy via Git)"
echo ""
echo "🔗 Backend URL: $CURRENT_URL"
echo "🔍 Test: $CURRENT_URL/health"
echo ""

# Test backend
echo "🧪 Testing backend health..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$CURRENT_URL/health" 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Backend is healthy! (HTTP $HTTP_CODE)"
else
    echo "⚠️  Backend returned HTTP $HTTP_CODE (expected 200)"
    echo "   Make sure backend is running (check workflow 'backend')"
fi

echo ""
echo "Done! 🎉"
