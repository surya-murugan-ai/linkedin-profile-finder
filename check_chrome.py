#!/usr/bin/env python3
"""
Chrome Installation Checker for Windows

This script checks if Chrome or Chromium is installed on Windows and shows the installation paths.
"""

import os
import platform
import subprocess

def check_chrome_installation():
    """Check for Chrome/Chromium installation on Windows"""
    print("🔍 Chrome/Chromium Installation Checker")
    print("=" * 50)
    
    if platform.system() != "Windows":
        print("This script is designed for Windows systems.")
        return
    
    # Common Windows Chrome/Chromium installation paths
    windows_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
        r"C:\Program Files\Chromium\Application\chrome.exe",
        r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Chromium\Application\chrome.exe".format(os.getenv('USERNAME', '')),
    ]
    
    found_browsers = []
    
    print("Checking for Chrome/Chromium installations...")
    print("-" * 30)
    
    for path in windows_paths:
        if os.path.exists(path):
            print(f"✅ Found: {path}")
            found_browsers.append(path)
            
            # Try to get version
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.stdout:
                    version = result.stdout.strip()
                    print(f"   Version: {version}")
            except:
                print("   Version: Could not determine")
        else:
            print(f"❌ Not found: {path}")
    
    print("\n" + "=" * 50)
    
    if found_browsers:
        print("🎉 Chrome/Chromium is installed!")
        print(f"Found {len(found_browsers)} installation(s):")
        for browser in found_browsers:
            print(f"  • {browser}")
        print("\nYou should be able to run the LinkedIn finder now.")
    else:
        print("❌ No Chrome/Chromium installation found!")
        print("\nTo install Chrome:")
        print("1. Download from: https://www.google.com/chrome/")
        print("2. Run the installer")
        print("3. Restart your terminal/command prompt")
        print("4. Run this script again")
        
        print("\nTo install Chromium:")
        print("1. Download from: https://www.chromium.org/getting-involved/download-chromium")
        print("2. Extract to C:\\Program Files\\Chromium\\")
        print("3. Restart your terminal/command prompt")
        print("4. Run this script again")

if __name__ == "__main__":
    check_chrome_installation()

