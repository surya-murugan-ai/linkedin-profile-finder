#!/usr/bin/env python3
"""
Quick Start Script for LinkedIn Profile Finder API

This script will:
1. Check if dependencies are installed
2. Install missing dependencies if needed
3. Start the API server
4. Open the documentation in browser
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Check if requirements file exists
        requirements_file = Path("../api_requirements.txt")
        if not requirements_file.exists():
            print("❌ api_requirements.txt not found")
            return False
        
        # Install dependencies
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_chrome():
    """Check if Chrome is available"""
    print("\n🌐 Checking Chrome browser...")
    
    try:
        # Try to import selenium and check Chrome
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # This will download ChromeDriver if needed
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        driver.quit()
        
        print("✅ Chrome and ChromeDriver are ready")
        return True
        
    except Exception as e:
        print(f"❌ Chrome setup failed: {e}")
        print("💡 Please install Google Chrome browser")
        return False

def start_api():
    """Start the API server"""
    print("\n🚀 Starting LinkedIn Profile Finder API...")
    
    try:
        # Start the API in a subprocess
        process = subprocess.Popen([
            sys.executable, "start.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ API server started successfully")
            print("📊 API Documentation: http://localhost:8000/docs")
            print("🔍 Health Check: http://localhost:8000/api/health")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start API server")
            print(f"Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return None

def open_documentation():
    """Open API documentation in browser"""
    print("\n📚 Opening API documentation...")
    
    try:
        # Wait a bit more for the server to be fully ready
        time.sleep(2)
        
        # Open documentation in default browser
        webbrowser.open("http://localhost:8000/docs")
        print("✅ Documentation opened in browser")
        
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("💡 Please manually open: http://localhost:8000/docs")

def main():
    """Main quick start function"""
    print("🚀 LinkedIn Profile Finder API - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n💡 Try running: pip install -r api_requirements.txt")
        return
    
    # Check Chrome
    if not check_chrome():
        print("\n💡 Please install Google Chrome and try again")
        return
    
    # Start API
    api_process = start_api()
    if not api_process:
        return
    
    # Open documentation
    open_documentation()
    
    print("\n" + "=" * 50)
    print("🎉 LinkedIn Profile Finder API is ready!")
    print("\n📋 Next steps:")
    print("1. View API documentation: http://localhost:8000/docs")
    print("2. Test the API: python test_api.py")
    print("3. Try the example client: python example_client.py")
    print("4. Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Keep the process running
        api_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping API server...")
        api_process.terminate()
        api_process.wait()
        print("✅ API server stopped")

if __name__ == "__main__":
    main()

