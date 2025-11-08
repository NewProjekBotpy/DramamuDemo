#!/usr/bin/env python3
"""
Script Import Database Dramamu
===============================
Import data dari backup SQL file ke database PostgreSQL

Usage:
    python import_database.py backup_YYYYMMDD_HHMMSS.sql
    
atau dengan DATABASE_URL custom:
    DATABASE_URL=postgresql://user:pass@host/db python import_database.py backup.sql
"""

import os
import sys
import psycopg2

def get_database_url():
    """Get DATABASE_URL dari environment variable"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL tidak ditemukan!")
        print("   Set environment variable DATABASE_URL terlebih dahulu.")
        print()
        print("   Contoh:")
        print("   export DATABASE_URL=postgresql://user:pass@host/database")
        print("   python import_database.py backup.sql")
        sys.exit(1)
    return db_url

def import_database(sql_file):
    """Import SQL file ke database"""
    if not os.path.exists(sql_file):
        print(f"❌ ERROR: File {sql_file} tidak ditemukan!")
        sys.exit(1)
    
    db_url = get_database_url()
    
    print(f"📦 Memulai import database...")
    print(f"📍 Database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    print(f"📄 SQL file: {sql_file}")
    print()
    
    # Warning
    print("⚠️  WARNING: Import akan MENGHAPUS data existing di database!")
    response = input("   Lanjutkan? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Import dibatalkan.")
        sys.exit(0)
    
    print()
    print("🔄 Importing...")
    
    try:
        # Connect ke database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Read SQL file
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute SQL
        cursor.execute(sql_content)
        conn.commit()
        
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies")
        movies_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # Summary
        print()
        print("=" * 60)
        print("✅ IMPORT BERHASIL!")
        print("=" * 60)
        print(f"👥 Users: {users_count}")
        print(f"🎬 Movies: {movies_count}")
        print()
        print("✅ Database siap digunakan!")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Pastikan DATABASE_URL benar")
        print("   2. Pastikan database schema sudah dibuat (import database_schema.sql dulu)")
        print("   3. Cek format SQL file")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_database.py <backup_file.sql>")
        print()
        print("Example:")
        print("  python import_database.py backup_20251108_123456.sql")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    import_database(sql_file)
