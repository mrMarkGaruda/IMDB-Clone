#!/usr/bin/env python3
"""
🚀 ULTRA-FAST LAUNCH SCRIPT
One-click setup and launch for the optimized IMDB Clone
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("🎬" + "="*60 + "🎬")
    print("   🚀 ULTRA-OPTIMIZED IMDB CLONE LAUNCHER")
    print("   ⚡ Lightning-fast database operations")
    print("   📊 Real-time analytics and insights") 
    print("   🔍 Advanced search capabilities")
    print("🎬" + "="*60 + "🎬")
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask', 'pandas', 'plotly', 'matplotlib', 'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        subprocess.run([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages, check=True)
        
        print("✅ All dependencies installed!")
    else:
        print("✅ All dependencies satisfied!")
    
    print()

def check_database():
    """Check if database exists and has data"""
    print("🗄️ Checking database...")
    
    db_path = Path("imdb.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        print("🚀 Would you like to import data now? This will take 5-10 minutes.")
        choice = input("Import data? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes']:
            return import_data()
        else:
            print("❌ Cannot run without database. Please import data first.")
            return False
    
    # Check if database has data
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        
        # Check table counts
        tables = ['title_basics', 'name_basics', 'title_ratings']
        total_rows = 0
        
        for table in tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"  📊 {table}: {count:,} rows")
                total_rows += count
            except:
                print(f"  ⚠️ {table}: Table not found or empty")
        
        conn.close()
        
        if total_rows > 100000:  # Reasonable threshold
            print(f"✅ Database ready with {total_rows:,} total rows!")
            return True
        else:
            print("⚠️ Database seems incomplete. Consider re-importing data.")
            return True  # Still allow to run
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def import_data():
    """Import data using the turbo importer"""
    print("🚀 Starting turbo data import...")
    
    # Check if dataset folder exists
    dataset_path = Path("dataset")
    if not dataset_path.exists():
        print("❌ Dataset folder not found!")
        print("Please download IMDB datasets and place them in the 'dataset' folder:")
        print("  - title.basics.tsv.gz")
        print("  - name.basics.tsv.gz") 
        print("  - title.ratings.tsv.gz")
        print("  - title.principals.tsv.gz")
        print("  - title.crew.tsv.gz")
        print("  - title.episode.tsv.gz")
        print("  - title.akas.tsv.gz")
        return False
    
    # Check for required files
    required_files = [
        "title.basics.tsv.gz",
        "name.basics.tsv.gz",
        "title.ratings.tsv.gz"
    ]
    
    missing_files = []
    for file in required_files:
        if not (dataset_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("📁 Dataset files found!")
    print("⏱️ Import will take 5-10 minutes depending on your system...")
    
    try:
        # Use turbo importer if available
        if Path("turbo_importer.py").exists():
            print("🚀 Using turbo importer (parallel processing)...")
            subprocess.run([sys.executable, "turbo_importer.py"], check=True)
        else:
            print("📦 Using standard importer...")
            subprocess.run([sys.executable, "imdb_clone_fixed.py"], check=True)
        
        print("✅ Data import completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def launch_application():
    """Launch the optimized application"""
    print("🚀 Launching IMDB Clone application...")
    
    # Choose the best available app file
    app_choices = [
        ("optimized_app.py", "Ultra-optimized version"),
        ("app.py", "Standard version"),
        ("imdb_clone_fixed.py", "Fallback version")
    ]
    
    app_file = None
    for filename, description in app_choices:
        if Path(filename).exists():
            app_file = filename
            print(f"📱 Using: {filename} ({description})")
            break
    
    if not app_file:
        print("❌ No application file found!")
        return False
    
    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:5000")
    print("⚡ Application will start in 3 seconds...")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    time.sleep(3)
    
    try:
        subprocess.run([sys.executable, app_file], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def main():
    """Main launcher function"""
    print_banner()
    
    # Step 1: Check dependencies
    try:
        check_dependencies()
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return
    
    # Step 2: Check database
    try:
        if not check_database():
            print("❌ Database setup failed. Cannot continue.")
            return
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return
    
    # Step 3: Launch application  
    try:
        launch_application()
    except Exception as e:
        print(f"❌ Application launch failed: {e}")
    
    print("\n👋 Thanks for using the IMDB Clone!")

if __name__ == "__main__":
    main()
