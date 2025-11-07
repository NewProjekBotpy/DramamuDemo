import psycopg2
import time
import os
import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qs
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import midtransclient
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database config
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Telegram config
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Midtrans config
MIDTRANS_SERVER_KEY = os.environ.get("MIDTRANS_SERVER_KEY")
MIDTRANS_CLIENT_KEY = os.environ.get("MIDTRANS_CLIENT_KEY")

# Initialize Midtrans
midtrans_client = None
if MIDTRANS_SERVER_KEY and MIDTRANS_CLIENT_KEY:
    midtrans_client = midtransclient.Snap(
        is_production=False,
        server_key=MIDTRANS_SERVER_KEY,
        client_key=MIDTRANS_CLIENT_KEY
    )

# FastAPI app
app = FastAPI(title="Dramamu API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dramamuid.netlify.app",
        "https://*.netlify.app",
        "http://localhost:*",
        "https://telegram.org"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database context manager
@contextmanager
def get_db_connection():
    conn = None
    try:
        if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS]):
            raise Exception("Database configuration incomplete")
        
        conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASS}'"
        conn = psycopg2.connect(conn_string)
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        if conn:
            conn.close()

# Validate Telegram WebApp data
def validate_telegram_init_data(init_data: str) -> dict:
    """Validate Telegram WebApp initData"""
    try:
        if not init_data or not BOT_TOKEN:
            return None
        
        parsed_data = parse_qs(init_data)
        hash_value = parsed_data.get('hash', [None])[0]
        
        if not hash_value:
            return None
        
        # Create data-check-string
        data_check_arr = []
        for key, values in sorted(parsed_data.items()):
            if key != 'hash':
                data_check_arr.append(f"{key}={values[0]}")
        
        data_check_string = '\n'.join(data_check_arr)
        
        # Calculate secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if calculated_hash != hash_value:
            logger.warning("Telegram initData validation failed: hash mismatch")
            return None
        
        # Parse user data
        user_data = parsed_data.get('user', [None])[0]
        if user_data:
            return json.loads(user_data)
        
        return None
    except Exception as e:
        logger.error(f"Error validating Telegram data: {e}")
        return None

# Pydantic models
class PaymentRequest(BaseModel):
    telegram_id: int
    paket_id: int
    gross_amount: int
    nama_paket: str

class MovieRequest(BaseModel):
    chat_id: int
    movie_id: int
    title: str
    poster_url: str
    init_data: str

# Health check
@app.get("/")
async def root():
    return {"message": "Dramamu API", "status": "running"}

@app.get("/health")
async def health_check():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Get all movies
@app.get("/api/v1/movies")
async def get_all_movies():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, title, description, poster_url, video_link FROM movies ORDER BY id DESC;")
            movies_raw = cur.fetchall()
            cur.close()
            
            movies_list = []
            for movie in movies_raw:
                movies_list.append({
                    "id": movie[0],
                    "title": movie[1],
                    "description": movie[2],
                    "poster_url": movie[3],
                    "video_link": movie[4]
                })
            
            return {"movies": movies_list}
    except Exception as e:
        logger.error(f"Error fetching movies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get user status
@app.get("/api/v1/user_status/{telegram_id}")
async def get_user_status(telegram_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT is_vip FROM users WHERE telegram_id = %s;", (telegram_id,))
            user = cur.fetchone()
            cur.close()
            
            if user:
                return {"telegram_id": telegram_id, "is_vip": user[0]}
            else:
                return {"telegram_id": telegram_id, "is_vip": False, "status": "user_not_found"}
    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get referral stats
@app.get("/api/v1/referral_stats/{telegram_id}")
async def get_referral_stats(telegram_id: int):
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT referral_code, commission_balance, total_referrals FROM users WHERE telegram_id = %s;",
                (telegram_id,)
            )
            user_stats = cur.fetchone()
            cur.close()
            
            if user_stats:
                return {
                    "referral_code": user_stats[0] or "KODE_UNIK",
                    "commission_balance": user_stats[1] or 0,
                    "total_referrals": user_stats[2] or 0
                }
            else:
                return {"referral_code": "KODE_UNIK", "commission_balance": 0, "total_referrals": 0}
    except Exception as e:
        logger.error(f"Error fetching referral stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Handle movie request from WebApp
@app.post("/api/v1/handle_movie_request")
async def handle_movie_request(request: MovieRequest):
    """
    Handle movie request from Telegram WebApp.
    Validates initData, checks VIP status, sends video via bot.
    """
    try:
        # Validate Telegram initData
        user = validate_telegram_init_data(request.init_data)
        if not user:
            logger.warning(f"Invalid initData for chat_id: {request.chat_id}")
            # Continue anyway for development, but log warning
        
        # Verify user matches chat_id
        if user and user.get('id') != request.chat_id:
            raise HTTPException(status_code=403, detail="User ID mismatch")
        
        # Check VIP status
        is_vip = False
        movie_data = None
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Check VIP status
            cur.execute("SELECT is_vip FROM users WHERE telegram_id = %s;", (request.chat_id,))
            user_row = cur.fetchone()
            
            if user_row:
                is_vip = user_row[0]
            else:
                # Create user if not exists
                cur.execute(
                    "INSERT INTO users (telegram_id, is_vip) VALUES (%s, %s) ON CONFLICT (telegram_id) DO NOTHING",
                    (request.chat_id, False)
                )
                conn.commit()
            
            # Get movie details
            cur.execute("SELECT title, video_link FROM movies WHERE id = %s;", (request.movie_id,))
            movie_row = cur.fetchone()
            
            if movie_row:
                movie_data = {"title": movie_row[0], "video_link": movie_row[1]}
            
            cur.close()
        
        if not movie_data:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # If not VIP, return upgrade required
        if not is_vip:
            return {
                "status": "vip_required",
                "message": "Upgrade ke VIP untuk menonton film ini",
                "movie_title": movie_data["title"]
            }
        
        # Send video via bot
        if not BOT_TOKEN:
            raise HTTPException(status_code=500, detail="Bot token not configured")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Send video
                response = await client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                    json={
                        "chat_id": request.chat_id,
                        "video": movie_data["video_link"],
                        "caption": f"🎥 <b>{movie_data['title']}</b>",
                        "parse_mode": "HTML"
                    }
                )
                
                result = response.json()
                
                if result.get("ok"):
                    return {
                        "status": "success",
                        "message": "Film berhasil dikirim ke chat Telegram Anda!",
                        "movie_title": movie_data["title"]
                    }
                else:
                    # If send video fails, send as text with link
                    text_response = await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": request.chat_id,
                            "text": f"🎬 <b>{movie_data['title']}</b>\n\n{movie_data['video_link']}",
                            "parse_mode": "HTML"
                        }
                    )
                    
                    if text_response.json().get("ok"):
                        return {
                            "status": "success",
                            "message": "Link film dikirim ke chat Telegram Anda!",
                            "movie_title": movie_data["title"]
                        }
                    else:
                        raise Exception("Failed to send message")
        
        except Exception as bot_error:
            logger.error(f"Error sending via bot: {bot_error}")
            # Return deep link as fallback
            bot_username = "dramamu_bot"  # Change this to your bot username
            deep_link = f"https://t.me/{bot_username}?start=movie_{request.movie_id}"
            
            return {
                "status": "need_start",
                "message": "Silakan start bot terlebih dahulu",
                "link": deep_link
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling movie request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Create payment
@app.post("/api/v1/create_payment")
async def create_payment_link(request: PaymentRequest):
    try:
        if not midtrans_client:
            raise HTTPException(status_code=500, detail="Payment gateway not configured")
        
        order_id = f"DRAMAMU-{request.telegram_id}-{int(time.time())}"
        
        transaction_details = {
            "order_id": order_id,
            "gross_amount": request.gross_amount,
        }
        
        customer_details = {
            "first_name": "User",
            "last_name": str(request.telegram_id),
            "email": f"{request.telegram_id}@dramamu.com",
            "phone": "08123456789",
        }
        
        item_details = [
            {
                "id": f"VIP-{request.paket_id}",
                "price": request.gross_amount,
                "quantity": 1,
                "name": request.nama_paket,
            }
        ]
        
        transaction_data = {
            "transaction_details": transaction_details,
            "customer_details": customer_details,
            "item_details": item_details,
        }
        
        snap_response = midtrans_client.create_transaction(transaction_data)
        snap_token = snap_response['token']
        
        return {"snap_token": snap_token, "order_id": order_id}
    
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
