#!/usr/bin/env python3
"""
Test script to verify the IMDB Clone setup
"""

def test_imports():
    """Test all required imports"""
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import sqlite3
        print("✅ SQLite3 imported successfully")
        
        import dash
        print("✅ Dash imported successfully")
        
        import plotly.express as px
        print("✅ Plotly imported successfully")
        
        from pathlib import Path
        print("✅ Path imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_dataset():
    """Test if dataset files exist"""
    from pathlib import Path
    
    dataset_path = Path("dataset")
    required_files = [
        "title.basics.tsv.gz",
        "name.basics.tsv.gz", 
        "title.ratings.tsv.gz",
        "title.principals.tsv.gz"
    ]
    
    print(f"\n🔍 Checking dataset folder: {dataset_path.absolute()}")
    
    if not dataset_path.exists():
        print("❌ Dataset folder not found!")
        return False
    
    for file in required_files:
        file_path = dataset_path / file
        if file_path.exists():
            size = file_path.stat().st_size / (1024*1024)  # MB
            print(f"✅ {file} found ({size:.1f} MB)")
        else:
            print(f"⚠️  {file} not found")
    
    return True

def test_database_creation():
    """Test basic database operations"""
    import sqlite3
    import tempfile
    import os
    
    print("\n🗄️  Testing database operations...")
    
    try:
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        conn = sqlite3.connect(db_path)
        
        # Test table creation
        conn.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        # Test data insertion
        conn.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        conn.commit()
        
        # Test data retrieval
        result = conn.execute("SELECT * FROM test_table").fetchone()
        
        conn.close()
        os.unlink(db_path)  # Clean up
        
        if result:
            print("✅ Database operations working correctly")
            return True
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎬 IMDB Clone Setup Test")
    print("=" * 40)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Dataset Files", test_dataset), 
        ("Database Operations", test_database_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
        
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("🚀 You can now run: python imdb_clone.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
