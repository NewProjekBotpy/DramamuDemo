import logging
import psycopg2
import json
import os
from contextlib import contextmanager
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger("dramamu-bot")

# Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_URL = os.environ.get("WEBAPP_URL", "https://dramamuid.netlify.app")
URL_CARI_JUDUL = f"{BASE_URL}/drama.html"
URL_BELI_VIP = f"{BASE_URL}/payment.html"
URL_PROFILE = f"{BASE_URL}/profile.html"
URL_REQUEST = f"{BASE_URL}/request.html"
URL_REFERRAL = f"{BASE_URL}/referal.html"

# Database config
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Database context manager
@contextmanager
def get_db_connection():
    conn = None
    try:
        if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS]):
            logger.error("Database configuration incomplete")
            yield None
            return
        
        conn_string = f"dbname='{DB_NAME}' user='{DB_USER}' host='{DB_HOST}' port='{DB_PORT}' password='{DB_PASS}'"
        conn = psycopg2.connect(conn_string)
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        yield None
    finally:
        if conn:
            conn.close()

# Check VIP status
def check_vip_status(telegram_id: int) -> bool:
    try:
        with get_db_connection() as conn:
            if not conn:
                return False
            
            cur = conn.cursor()
            cur.execute("SELECT is_vip FROM users WHERE telegram_id = %s;", (telegram_id,))
            user = cur.fetchone()
            
            if user and user[0] is True:
                cur.close()
                return True
            elif not user:
                # Create user if not exists
                cur.execute(
                    "INSERT INTO users (telegram_id, is_vip) VALUES (%s, %s) ON CONFLICT (telegram_id) DO NOTHING",
                    (telegram_id, False),
                )
                conn.commit()
            
            cur.close()
            return False
    except Exception as e:
        logger.error(f"Error checking VIP status: {e}")
        return False

# Get movie details
def get_movie_details(movie_id: int) -> dict:
    try:
        with get_db_connection() as conn:
            if not conn:
                return None
            
            cur = conn.cursor()
            cur.execute("SELECT title, video_link FROM movies WHERE id = %s;", (movie_id,))
            row = cur.fetchone()
            cur.close()
            
            if row:
                return {"title": row[0], "video_link": row[1]}
            return None
    except Exception as e:
        logger.error(f"Error getting movie details: {e}")
        return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⭐️ GRUP DRAMA MU OFFICIAL ⭐️", url="https://t.me/dramamuofficial")],
        [
            InlineKeyboardButton("🎬 CARI JUDUL", web_app=WebAppInfo(url=URL_CARI_JUDUL)),
            InlineKeyboardButton("💰 CARI CUAN", web_app=WebAppInfo(url=URL_REFERRAL)),
        ],
        [
            InlineKeyboardButton("💎 BELI VIP", web_app=WebAppInfo(url=URL_BELI_VIP)),
            InlineKeyboardButton("📝 REQ DRAMA", web_app=WebAppInfo(url=URL_REQUEST)),
        ],
        [InlineKeyboardButton("💬 HUBUNGI KAMI", url="https://t.me/kot_dik")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        "🎬 <b>Selamat datang di Dramamu</b>\n\n"
        "Nonton semua drama favorit cuma segelas kopi ☕\n"
        "Pilih menu di bawah!"
    )
    
    try:
        if os.path.exists("poster.jpg"):
            with open("poster.jpg", "rb") as img:
                await update.message.reply_photo(
                    photo=img, 
                    caption=caption, 
                    reply_markup=reply_markup, 
                    parse_mode=ParseMode.HTML
                )
        else:
            await update.message.reply_text(
                caption, 
                reply_markup=reply_markup, 
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.error(f"Error sending /start message: {e}")
        await update.message.reply_text(
            "Halo! Pilih menu di bawah 👇", 
            reply_markup=reply_markup
        )

# Handle WebApp data
async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user_id = update.effective_user.id if update.effective_user else None
    
    # Check if message contains web_app_data
    if not message or not getattr(message, "web_app_data", None):
        return
    
    data_str = message.web_app_data.data
    if not data_str:
        logger.warning("Empty WebApp data received")
        return
    
    logger.info(f"WebApp data received from {user_id}: {data_str[:100]}...")
    
    # Parse JSON data
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from WebApp: {e}")
        await context.bot.send_message(
            chat_id=user_id, 
            text="Data dari WebApp tidak valid."
        )
        return
    
    action = data.get("action")
    
    # Handle watch action
    if action == "watch":
        movie_id = int(data.get("movie_id", 0))
        if not movie_id:
            await context.bot.send_message(chat_id=user_id, text="Film tidak valid.")
            return
        
        # Check VIP status
        if check_vip_status(user_id):
            movie = get_movie_details(movie_id)
            if not movie:
                await context.bot.send_message(
                    chat_id=user_id, 
                    text="Film tidak ditemukan."
                )
                return
            
            # Try to send video
            try:
                await context.bot.send_video(
                    chat_id=user_id,
                    video=movie["video_link"],
                    caption=f"🎥 <b>{movie['title']}</b>",
                    parse_mode=ParseMode.HTML,
                )
            except Exception as e:
                logger.error(f"Failed to send video: {e}")
                # Fallback: send as text with link
                await context.bot.send_message(
                    chat_id=user_id, 
                    text=f"🎬 <b>{movie['title']}</b>\n\n{movie['video_link']}",
                    parse_mode=ParseMode.HTML
                )
        else:
            # User not VIP
            keyboard = [[InlineKeyboardButton("💎 Upgrade VIP", web_app=WebAppInfo(url=URL_BELI_VIP))]]
            await context.bot.send_message(
                chat_id=user_id,
                text="🚫 Anda belum VIP.\n\nUpgrade ke VIP untuk menonton semua drama!",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
    
    # Handle request drama action
    elif action == "request_drama":
        judul = data.get("judul", "-")
        apk = data.get("apk", "-")
        logger.info(f"Drama request from {user_id}: {judul} from {apk}")
        await context.bot.send_message(
            chat_id=user_id, 
            text=f"✅ Request untuk '{judul}' telah diterima!\n\nKami akan review dan upload sesegera mungkin."
        )
    
    # Handle withdrawal action
    elif action == "withdraw_referral":
        jumlah = data.get("jumlah")
        metode = data.get("metode")
        nomor = data.get("nomor_rekening")
        nama = data.get("nama_pemilik")
        
        logger.info(f"Withdrawal request from {user_id}: Rp{jumlah} via {metode}")
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Request penarikan Rp {jumlah:,} diterima.\n\nDiproses dalam 1x24 jam ke rekening:\n{metode} - {nama}\n{nomor}",
        )
    
    # Unknown action
    else:
        logger.warning(f"Unknown action from WebApp: {action}")
        await context.bot.send_message(
            chat_id=user_id, 
            text="⚠️ Aksi tidak dikenali."
        )

# Handle text messages (AI agent placeholder)
async def ai_agent_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text or getattr(msg, "web_app_data", None):
        return
    
    user_msg = msg.text
    logger.info(f"Text message from {update.effective_user.id}: {user_msg}")
    
    # Simple response for now
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"Halo! Gunakan menu /start untuk melihat pilihan yang tersedia."
    )

# Global error handler
async def global_error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error occurred: {context.error}", exc_info=context.error)
    
    # Notify admin if configured
    admin_id = os.environ.get("ADMIN_ID")
    if admin_id:
        try:
            await context.bot.send_message(
                chat_id=int(admin_id), 
                text=f"⚠️ Bot error: {context.error}"
            )
        except Exception:
            pass

# Main function
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return
    
    logger.info("🚀 Dramamu Bot starting...")
    
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    
    # WebApp data handler (highest priority)
    app.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data), 
        group=-1
    )
    
    # Text message handler (lower priority)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ai_agent_handler), 
        group=1
    )
    
    # Error handler
    app.add_error_handler(global_error_handler)
    
    # Start polling
    logger.info("✅ Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
