#!/usr/bin/env python3
"""
LinkedIn Profile Finder API - Chromium Version Startup Script

This script starts the FastAPI server for the LinkedIn Profile Finder API
using the Chromium-compatible version that runs headless.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_browser():
    """Check if Chrome or Chromium browser is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Try to create a Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("✅ Chrome/Chromium browser is available")
        return True
    except Exception as e:
        print(f"❌ Chrome/Chromium browser not found: {e}")
        print("\nTo fix this issue, please install one of the following:")
        print("\n1. Google Chrome:")
        print("   - Download from: https://www.google.com/chrome/")
        print("   - Or install via package manager:")
        print("     Ubuntu/Debian: sudo apt install google-chrome-stable")
        print("     CentOS/RHEL: sudo yum install google-chrome-stable")
        print("     macOS: brew install --cask google-chrome")
        print("\n2. Chromium (recommended for automation):")
        print("   - Ubuntu/Debian: sudo apt install chromium-browser")
        print("   - CentOS/RHEL: sudo yum install chromium")
        print("   - macOS: brew install chromium")
        print("   - Windows: Download from https://www.chromium.org/getting-involved/download-chromium")
        print("\n3. After installation, restart your terminal/command prompt")
        print("4. Run this script again")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting LinkedIn Profile Finder API (Chromium Version)...")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        return False
    
    # Check browser availability
    if not check_browser():
        return False
    
    print("\n📋 API Information:")
    print("   • API URL: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Web Interface: api/index.html")
    print("   • Browser: Chromium/Chrome (Headless Mode)")
    print("\n" + "=" * 60)
    
    # Start the server
    try:
        cmd = [
            sys.executable, "-m", "uvicorn",
            "api.main_chromium:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--log-level", "info"
        ]
        
        print("🔄 Starting server... (Press Ctrl+C to stop)")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return False
    
    return True

def open_web_interface():
    """Open the web interface in browser"""
    web_interface_path = Path("api/index.html")
    if web_interface_path.exists():
        try:
            webbrowser.open(f"file://{web_interface_path.absolute()}")
            print("🌐 Web interface opened in browser")
        except Exception as e:
            print(f"⚠️  Could not open web interface: {e}")
            print(f"   You can manually open: {web_interface_path.absolute()}")
    else:
        print("⚠️  Web interface not found at api/index.html")

def main():
    """Main function"""
    print("🔍 LinkedIn Profile Finder API - Chromium Version")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("linkedin_finder_chromium.py").exists():
        print("❌ Error: linkedin_finder_chromium.py not found in current directory")
        print("   Please run this script from the project root directory")
        return
    
    if not Path("api/main_chromium.py").exists():
        print("❌ Error: api/main_chromium.py not found")
        print("   Please make sure the API files are in the api/ directory")
        return
    
    # Ask user if they want to open web interface
    try:
        response = input("\n🌐 Open web interface in browser? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            # Start server in background and open web interface
            print("\n🔄 Starting server in background...")
            import threading
            import time
            
            def start_server():
                start_api_server()
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Open web interface
            open_web_interface()
            
            # Keep main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
        else:
            # Just start the server
            start_api_server()
    except KeyboardInterrupt:
        print("\n🛑 Cancelled by user")

if __name__ == "__main__":
    main()

