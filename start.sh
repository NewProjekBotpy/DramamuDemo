#!/bin/bash

# Start script untuk menjalankan Bot dan FastAPI backend bersamaan di Render
# Script ini akan menjalankan keduanya secara parallel

echo "🚀 Starting Dramamu Backend System..."

# Set working directory ke folder yang berisi main.py dan bot.py
cd "Ini backup/ini yang ada di github" || exit 1

echo "✅ Current directory: $(pwd)"
echo "📝 Files in directory:"
ls -la

echo "🤖 Starting Telegram Bot in background..."
python bot.py &
BOT_PID=$!
echo "   Bot PID: $BOT_PID"

# Wait a moment for bot to initialize
sleep 2

echo "🔥 Starting FastAPI Backend..."
# Render menyediakan PORT via environment variable
# Default ke 8000 jika tidak ada
PORT=${PORT:-8000}
echo "   Listening on port: $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT &
API_PID=$!
echo "   API PID: $API_PID"

echo ""
echo "✅ Both services started successfully!"
echo "🤖 Telegram Bot: Running (PID: $BOT_PID)"
echo "🔥 FastAPI Backend: http://0.0.0.0:$PORT (PID: $API_PID)"
echo ""
echo "Waiting for processes..."

# Wait for both processes
wait $BOT_PID $API_PID
