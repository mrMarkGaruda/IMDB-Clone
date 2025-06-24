#!/usr/bin/env python3
"""
Simple launcher for the IMDB Clone application
Run this file to start the complete application
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🎬 IMDB Clone & Analytics Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("dataset").exists():
        print("❌ Error: 'dataset' folder not found!")
        print("Please make sure you're running this from the IMDB-Clone directory")
        print("and that the dataset folder contains the IMDB TSV.GZ files")
        return
    
    # Check if main script exists
    if not Path("imdb_clone.py").exists():
        print("❌ Error: 'imdb_clone.py' not found!")
        return
    
    print("✅ Files found, starting application...")
    print("📊 This will create a database and start the web interface")
    print("🌐 Once ready, open: http://localhost:8050")
    print()
    
    try:
        # Run the main application
        subprocess.run([sys.executable, "imdb_clone.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
