#!/usr/bin/env python3
"""
Script Export Database Dramamu
==============================
Export semua data dari database PostgreSQL ke file SQL
Bisa digunakan untuk backup atau migrasi ke platform lain (Railway, Render, dll)

Usage:
    python export_database.py
    
Output:
    - backup_YYYYMMDD_HHMMSS.sql
"""

import os
import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

def get_database_url():
    """Get DATABASE_URL dari environment variable"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ ERROR: DATABASE_URL tidak ditemukan!")
        print("   Set environment variable DATABASE_URL terlebih dahulu.")
        sys.exit(1)
    return db_url

def export_database():
    """Export database ke file SQL"""
    db_url = get_database_url()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.sql"
    
    print(f"📦 Memulai export database...")
    print(f"📍 Database: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    print(f"📄 Output file: {filename}")
    print()
    
    try:
        # Connect ke database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buka file untuk write
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("-- ================================================\n")
            f.write("-- DRAMAMU DATABASE BACKUP\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- ================================================\n\n")
            f.write("-- Disable triggers during import\n")
            f.write("SET session_replication_role = 'replica';\n\n")
            
            # List of tables in correct order (respect foreign keys)
            tables = [
                'users',
                'movies',
                'intermediary_queue',
                'pending_actions',
                'payments',
                'activity_logs',
                'requests',
                'withdrawal_requests'
            ]
            
            total_rows = 0
            
            for table in tables:
                print(f"📊 Exporting table: {table}")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()['count']
                total_rows += count
                
                if count == 0:
                    print(f"   ⚠️  Table '{table}' kosong, skip.")
                    f.write(f"-- Table {table}: 0 rows (skipped)\n\n")
                    continue
                
                print(f"   ✅ {count} rows")
                
                # Get all data
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                # Write table comment
                f.write(f"-- ================================================\n")
                f.write(f"-- TABLE: {table} ({count} rows)\n")
                f.write(f"-- ================================================\n\n")
                
                # Truncate table before insert (untuk clean import)
                f.write(f"TRUNCATE TABLE {table} CASCADE;\n\n")
                
                # Generate INSERT statements
                for row in rows:
                    columns = list(row.keys())
                    values = []
                    
                    for col in columns:
                        val = row[col]
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        elif isinstance(val, bool):
                            values.append('TRUE' if val else 'FALSE')
                        elif isinstance(val, datetime):
                            values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                        elif isinstance(val, dict):
                            # For JSONB columns
                            import json
                            json_str = json.dumps(val).replace("'", "''")
                            values.append(f"'{json_str}'::jsonb")
                        else:
                            # String - escape single quotes
                            escaped = str(val).replace("'", "''")
                            values.append(f"'{escaped}'")
                    
                    cols_str = ', '.join(columns)
                    vals_str = ', '.join(values)
                    
                    f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str});\n")
                
                f.write("\n\n")
            
            # Re-enable triggers
            f.write("-- Re-enable triggers\n")
            f.write("SET session_replication_role = 'origin';\n\n")
            
            # Update sequences
            f.write("-- Update sequences to max ID\n")
            for table in tables:
                # Check if table has id column
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = 'id'
                """)
                if cursor.fetchone():
                    f.write(f"SELECT setval('{table}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM {table}));\n")
            
            f.write("\n-- BACKUP COMPLETE\n")
        
        cursor.close()
        conn.close()
        
        # Summary
        print()
        print("=" * 60)
        print("✅ EXPORT BERHASIL!")
        print("=" * 60)
        print(f"📄 File: {filename}")
        print(f"📊 Total rows exported: {total_rows}")
        print()
        print("📋 Next Steps:")
        print("   1. Upload file ini ke platform baru (Railway/Render)")
        print("   2. Import dengan: psql $DATABASE_URL < " + filename)
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    export_database()
