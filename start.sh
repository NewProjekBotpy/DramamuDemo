#!/bin/bash

# Start Dramamu services

echo "🚀 Starting Dramamu services..."

# Start FastAPI backend in background
echo "📡 Starting FastAPI backend on port 5000..."
cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
cd ../bot && python app.py &
BOT_PID=$!

echo "✅ Services started!"
echo "   - Backend PID: $BACKEND_PID"
echo "   - Bot PID: $BOT_PID"

# Wait for both processes
wait $BACKEND_PID $BOT_PID
