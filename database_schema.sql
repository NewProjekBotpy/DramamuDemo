-- =====================================================
-- DATABASE SCHEMA UNTUK DRAMAMU BOT
-- Database: PostgreSQL (Replit Built-in)
-- =====================================================

-- 1. TABEL USERS (Data user dan status VIP)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_vip BOOLEAN DEFAULT FALSE,
    vip_expires_at TIMESTAMPTZ,
    referral_code VARCHAR(50) UNIQUE,
    referred_by BIGINT REFERENCES users(telegram_id),
    commission_balance DECIMAL(15, 2) DEFAULT 0,
    total_referrals INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code);

-- 2. TABEL MOVIES (Data film/drama)
CREATE TABLE IF NOT EXISTS movies (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    poster_url TEXT,
    video_link TEXT NOT NULL,
    genre VARCHAR(100),
    year INT,
    rating DECIMAL(3, 1),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
CREATE INDEX IF NOT EXISTS idx_movies_active ON movies(active);

-- 3. TABEL INTERMEDIARY_QUEUE (Pelantara - Menahan data film sampai bot menerima /start)
CREATE TABLE IF NOT EXISTS intermediary_queue (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    movie_id BIGINT REFERENCES movies(id),
    start_token VARCHAR(255) UNIQUE NOT NULL,
    movie_data JSONB,
    status VARCHAR(50) DEFAULT 'waiting_start',
    start_link TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sent_to_bot_at TIMESTAMPTZ,
    bot_received_start_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_intermediary_telegram_id ON intermediary_queue(telegram_id);
CREATE INDEX IF NOT EXISTS idx_intermediary_token ON intermediary_queue(start_token);
CREATE INDEX IF NOT EXISTS idx_intermediary_status ON intermediary_queue(status);
CREATE INDEX IF NOT EXISTS idx_intermediary_expires ON intermediary_queue(expires_at);

-- 4. TABEL PENDING_ACTIONS (Legacy - untuk backward compatibility)
CREATE TABLE IF NOT EXISTS pending_actions (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    movie_id BIGINT REFERENCES movies(id),
    start_token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pending_telegram_id ON pending_actions(telegram_id);
CREATE INDEX IF NOT EXISTS idx_pending_token ON pending_actions(start_token);
CREATE INDEX IF NOT EXISTS idx_pending_expires ON pending_actions(expires_at);

-- 5. TABEL PAYMENTS (Log pembayaran VIP)
CREATE TABLE IF NOT EXISTS payments (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    order_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    package_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(100),
    midtrans_transaction_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_telegram_id ON payments(telegram_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);

-- 6. TABEL ACTIVITY_LOGS (Log aktivitas user)
CREATE TABLE IF NOT EXISTS activity_logs (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    movie_id BIGINT REFERENCES movies(id),
    status VARCHAR(50),
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_telegram_id ON activity_logs(telegram_id);
CREATE INDEX IF NOT EXISTS idx_logs_action ON activity_logs(action);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON activity_logs(created_at);

-- 7. TABEL REQUESTS (Request drama dari user)
CREATE TABLE IF NOT EXISTS requests (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    judul VARCHAR(500) NOT NULL,
    aplikasi VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_requests_telegram_id ON requests(telegram_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);

-- 8. TABEL WITHDRAWAL_REQUESTS (Request penarikan komisi referral)
CREATE TABLE IF NOT EXISTS withdrawal_requests (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    method VARCHAR(100) NOT NULL,
    account_number VARCHAR(255) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_withdrawals_telegram_id ON withdrawal_requests(telegram_id);
CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON withdrawal_requests(status);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Function untuk auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_movies_updated_at ON movies;
CREATE TRIGGER update_movies_updated_at BEFORE UPDATE ON movies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA (untuk testing)
-- =====================================================

INSERT INTO movies (title, description, poster_url, video_link, genre, year, rating, active) VALUES
('Drama Test 1', 'Ini adalah drama test pertama untuk development', 'https://via.placeholder.com/300x450/333333/FFFFFF?text=Drama+1', 'https://example.com/drama1', 'Romance', 2024, 8.5, true),
('Drama Test 2', 'Ini adalah drama test kedua untuk development', 'https://via.placeholder.com/300x450/333333/FFFFFF?text=Drama+2', 'https://example.com/drama2', 'Action', 2024, 7.8, true),
('Drama Test 3', 'Ini adalah drama test ketiga untuk development', 'https://via.placeholder.com/300x450/333333/FFFFFF?text=Drama+3', 'https://example.com/drama3', 'Comedy', 2024, 9.0, true),
('My Demon', 'Drama Korea tentang setan yang kehilangan kekuatannya', 'https://via.placeholder.com/300x450/ff0000/FFFFFF?text=My+Demon', 'https://example.com/mydemon', 'Fantasy, Romance', 2024, 9.2, true),
('Marry My Husband', 'Drama tentang time travel dan balas dendam', 'https://via.placeholder.com/300x450/0000ff/FFFFFF?text=Marry+My+Husband', 'https://example.com/marrymyhusband', 'Romance, Thriller', 2024, 8.8, true)
ON CONFLICT DO NOTHING;

-- =====================================================
-- NOTES
-- =====================================================
-- Schema ini sudah terintegrasi dengan Replit Database
-- Environment variables otomatis tersedia:
--   DATABASE_URL, PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
-- =====================================================
