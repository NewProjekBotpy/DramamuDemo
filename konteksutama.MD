‎prbaiki sistem, sistem Telegram Bot ini untuk layanan film, yang menggunakan InlineKeyboardButton untuk membuka Mini App (web_app), dengan komunikasi perantara melalui server FastAPI yang terhubung ke Supabase sebagai database utama.
‎Mini App dihosting di Netlify, dibangun dengan HTML, CSS, dan JavaScript. Backend menggunakan FastAPI (Python), database menggunakan Supabase (PostgreSQL), dan Bot Telegram dibuat dengan Telebot (PyTelegramBotAPI) yang terhubung ke server FastAPI melalui endpoint API.
‎
‎User menekan InlineKeyboardButton di bawah pesan bot Telegram untuk membuka Mini App. Mini App menggunakan Telegram.WebApp.initData untuk autentikasi dan mengambil user.id dari Telegram. Ketika user memilih film, Mini App mengirim request POST ke server FastAPI:
‎
‎{ "chat_id": <Telegram user.id>, "movie_id": "<MOVIE_ID>", "title": "<TITLE>", "poster_url": "<POSTER_URL>", "init_data": "<Telegram initData>" } 
‎
‎Server FastAPI memverifikasi init_data menggunakan metode validasi resmi Telegram (HMAC_SHA256). Server menyimpan aktivitas di Supabase (tabel logs, pending_actions, users, dll), lalu mencoba meneruskan data ke Telegram Bot API dengan sendMessage atau sendPhoto. Jika berhasil, pesan berisi teks atau gambar film dan tombol “Tonton Sekarang” terkirim ke user. Jika gagal (403 Forbidden), server membuat token unik sementara (start_token) dan mengembalikan respon:
‎
‎{ "status": "need_start", "link": "https://t.me/<BOT_USERNAME>?start=<TOKEN>" } 
‎
‎Mini App menampilkan tombol “Buka di Telegram untuk lanjut” menggunakan link tersebut. Saat user klik tombol itu dan menekan Start, bot menerima /start , memanggil endpoint /api/v1/pending/ di FastAPI, lalu mengirim data film ke user. Setelah user pernah menekan Start satu kali, izin kirim pesan berlaku permanen dan semua klik berikutnya berhasil otomatis tanpa fallback.
‎
‎Semua request dari Mini App diverifikasi via initData Telegram. Token fallback bersifat sekali pakai dan kadaluarsa 5–15 menit. Server FastAPI menggunakan Supabase sebagai penyimpanan terpusat (stateful) dan mencatat semua aktivitas serta error untuk analitik. Mini App menampilkan fallback otomatis tanpa reload manual.
‎
‎Tujuan akhir: membangun sistem Telegram Bot film dengan InlineKeyboardButton + Mini App yang berkomunikasi via server FastAPI dan Supabase, agar Mini App bisa mengirim data ke Telegram secara tidak langsung (proxy logic), dengan keamanan, stabilitas, dan pengalaman pengguna yang lancar.
‎