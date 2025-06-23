#!/usr/bin/env python3
"""
Reset IMDB Clone Database
This script will delete the existing database and allow you to start fresh
"""

import os
from pathlib import Path

def reset_database():
    """Delete the existing database files"""
    db_files = [
        "imdb.db",
        "imdb.db-shm", 
        "imdb.db-wal"
    ]
    
    print("🗑️  Resetting IMDB Clone Database")
    print("=" * 40)
    
    deleted_count = 0
    
    for db_file in db_files:
        if Path(db_file).exists():
            try:
                os.remove(db_file)
                print(f"✅ Deleted: {db_file}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {db_file}: {e}")
        else:
            print(f"⚠️  File not found: {db_file}")
    
    if deleted_count > 0:
        print(f"\n🎉 Database reset complete! Deleted {deleted_count} files.")
        print("You can now run 'python imdb_clone.py' to start fresh.")
    else:
        print("\n💡 No database files found to delete.")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete the existing database? (yes/no): ")
    if confirm.lower() in ['yes', 'y']:
        reset_database()
    else:
        print("Reset cancelled.")
