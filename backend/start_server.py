#!/usr/bin/env python
"""
Script to start Django server with proper error handling
"""
import os
import sys
import subprocess
import time
import requests

def check_server_status():
    """Check if Django server is running"""
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        return True
    except:
        return False

def main():
    print("🚀 DJANGO SERVER STARTER")
    print("=" * 30)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Check if server is already running
    if check_server_status():
        print("✅ Django server is already running on http://localhost:8000")
        return
    
    print("🔍 Checking Django setup...")
    
    # Check if manage.py exists
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found in current directory")
        return
    
    # Check if virtual environment is activated
    venv_path = os.path.join(backend_dir, 'venv')
    if os.path.exists(venv_path):
        print("📁 Virtual environment found")
        
        # Activate virtual environment
        if sys.platform == "win32":
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:
            python_exe = os.path.join(venv_path, 'bin', 'python')
        
        if not os.path.exists(python_exe):
            print("⚠️  Virtual environment Python not found, using system Python")
            python_exe = sys.executable
    else:
        print("⚠️  No virtual environment found, using system Python")
        python_exe = sys.executable
    
    print(f"🐍 Using Python: {python_exe}")
    
    # Try to run migrations first
    print("\n🔄 Running migrations...")
    try:
        result = subprocess.run([python_exe, 'manage.py', 'migrate'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Migrations completed successfully")
        else:
            print(f"⚠️  Migration warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Migration error: {e}")
    
    # Start the server
    print("\n🚀 Starting Django server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start server in foreground
        subprocess.run([python_exe, 'manage.py', 'runserver', '8000'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()