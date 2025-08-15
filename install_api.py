#!/usr/bin/env python3
"""
Simple installation script for LinkedIn Profile Finder API
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install dependencies one by one"""
    print("🚀 Installing LinkedIn Profile Finder API Dependencies")
    print("=" * 60)
    
    # List of packages to install (in order)
    packages = [
        "fastapi==0.95.2",
        "uvicorn==0.22.0", 
        "selenium==4.15.0",
        "webdriver-manager==4.0.0",
        "pydantic==1.10.13",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
        else:
            print(f"⚠️  Skipping remaining packages due to error with {package}")
            break
    
    print("\n" + "=" * 60)
    print(f"📊 Installation Summary: {success_count}/{total_packages} packages installed")
    
    if success_count == total_packages:
        print("🎉 All dependencies installed successfully!")
        print("\n📋 Next steps:")
        print("1. cd api")
        print("2. python start.py")
        print("3. Open http://localhost:8000/docs in your browser")
    else:
        print("❌ Some packages failed to install. Please check the errors above.")
        print("\n💡 Alternative: Try installing manually:")
        print("pip install fastapi==0.95.2 uvicorn==0.22.0 selenium==4.15.0 webdriver-manager==4.0.0 pydantic==1.10.13 python-multipart==0.0.6 python-dotenv==1.0.0 requests==2.31.0")

if __name__ == "__main__":
    main()

