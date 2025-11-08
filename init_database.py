#!/usr/bin/env python3
"""
Database Initialization Script
Membuat semua table yang diperlukan untuk Dramamu Bot
"""

import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL tidak tersedia!")
    print("💡 Pastikan Replit database sudah di-provision")
    exit(1)

print("🔌 Connecting to database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("✅ Connected to database successfully!")
    print("📝 Creating tables...")
    
    # Read schema file
    with open('database_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Execute schema
    cur.execute(schema_sql)
    conn.commit()
    
    print("✅ All tables created successfully!")
    
    # Verify tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    print(f"\n📊 Total {len(tables)} tables created:")
    for table in tables:
        print(f"   ✓ {table[0]}")
    
    # Check sample data
    cur.execute("SELECT COUNT(*) FROM movies;")
    result = cur.fetchone()
    movie_count = result[0] if result else 0
    print(f"\n🎬 Sample movies inserted: {movie_count}")
    
    cur.close()
    conn.close()
    
    print("\n✅ Database initialization complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
