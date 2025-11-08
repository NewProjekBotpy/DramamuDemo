-- =====================================================
-- SUPABASE DATABASE SCHEMA UNTUK DRAMAMU BOT
-- =====================================================
-- Jalankan script ini di Supabase SQL Editor
-- untuk membuat semua tables yang dibutuhkan
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

-- Index untuk performa
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_referral_code ON users(referral_code);

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

-- Index untuk search
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_active ON movies(active);

-- 3. TABEL PENDING_ACTIONS (Fallback mechanism untuk user yang belum /start)
CREATE TABLE IF NOT EXISTS pending_actions (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    movie_id BIGINT REFERENCES movies(id),
    start_token VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processed, expired
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Index untuk performa
CREATE INDEX idx_pending_telegram_id ON pending_actions(telegram_id);
CREATE INDEX idx_pending_token ON pending_actions(start_token);
CREATE INDEX idx_pending_expires ON pending_actions(expires_at);

-- 4. TABEL PAYMENTS (Log pembayaran VIP)
CREATE TABLE IF NOT EXISTS payments (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    order_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    package_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- pending, success, failed, expired
    payment_method VARCHAR(100),
    midtrans_transaction_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index untuk query
CREATE INDEX idx_payments_telegram_id ON payments(telegram_id);
CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_status ON payments(status);

-- 5. TABEL ACTIVITY_LOGS (Log aktivitas user)
CREATE TABLE IF NOT EXISTS activity_logs (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL, -- watch, request, payment, referral, etc
    movie_id BIGINT REFERENCES movies(id),
    status VARCHAR(50), -- success, failed
    error_message TEXT,
    metadata JSONB, -- Data tambahan dalam format JSON
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index untuk analytics
CREATE INDEX idx_logs_telegram_id ON activity_logs(telegram_id);
CREATE INDEX idx_logs_action ON activity_logs(action);
CREATE INDEX idx_logs_created_at ON activity_logs(created_at);

-- 6. TABEL REQUESTS (Request drama dari user)
CREATE TABLE IF NOT EXISTS requests (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    judul VARCHAR(500) NOT NULL,
    aplikasi VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, rejected
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Index
CREATE INDEX idx_requests_telegram_id ON requests(telegram_id);
CREATE INDEX idx_requests_status ON requests(status);

-- 7. TABEL WITHDRAWAL_REQUESTS (Request penarikan komisi referral)
CREATE TABLE IF NOT EXISTS withdrawal_requests (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    method VARCHAR(100) NOT NULL, -- BCA, DANA, OVO, etc
    account_number VARCHAR(255) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, completed
    admin_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Index
CREATE INDEX idx_withdrawals_telegram_id ON withdrawal_requests(telegram_id);
CREATE INDEX idx_withdrawals_status ON withdrawal_requests(status);

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

-- Trigger untuk users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger untuk movies table
CREATE TRIGGER update_movies_updated_at BEFORE UPDATE ON movies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger untuk payments table
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- SAMPLE DATA (OPTIONAL - untuk testing)
-- =====================================================

-- Insert sample movies
INSERT INTO movies (title, description, poster_url, video_link, genre, year, rating, active) VALUES
('Drama Test 1', 'Ini adalah drama test pertama untuk development', 'https://via.placeholder.com/300x450/333333/FFFFFF?text=Drama+1', 'https://example.com/drama1', 'Romance', 2024, 8.5, true),
('Drama Test 2', 'Ini adalah drama test kedua untuk development', 'https://via.placeholder.com/300x450/333333/FFFFFF?text=Drama+2', 'https://example.com/drama2', 'Action', 2024, 7.8, true),
('Drama Test 3', 'Ini adalah drama test ketiga untuk development', 'https://via.placeholder.com/300x450/333333/FFFFFF?text=Drama+3', 'https://example.com/drama3', 'Comedy', 2024, 9.0, true)
ON CONFLICT DO NOTHING;

-- =====================================================
-- NOTES
-- =====================================================
-- 1. Setelah run script ini, catat connection string dari Supabase
-- 2. Format: postgresql://postgres:[password]@[host]:[port]/postgres
-- 3. Simpan sebagai environment variables:
--    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
-- =====================================================
