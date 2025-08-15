#!/usr/bin/env python3
"""
Simple test script to diagnose Chrome and ChromeDriver issues
"""

import os
import sys
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def check_chrome_installation():
    """Check if Chrome is installed"""
    print("Checking Chrome installation...")
    
    # Common Chrome installation paths
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ Chrome found at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("✗ Chrome not found in common locations")
        print("  Please install Chrome from: https://www.google.com/chrome/")
        return False
    
    return True

def check_chromedriver():
    """Check ChromeDriver installation"""
    print("\nChecking ChromeDriver...")
    
    try:
        # Try to get ChromeDriver path
        driver_path = ChromeDriverManager().install()
        print(f"✓ ChromeDriver found at: {driver_path}")
        
        # Check if the file exists and is executable
        if os.path.exists(driver_path):
            print("✓ ChromeDriver file exists")
            return True
        else:
            print("✗ ChromeDriver file not found")
            return False
            
    except Exception as e:
        print(f"✗ ChromeDriver error: {e}")
        return False

def test_selenium_setup():
    """Test Selenium setup"""
    print("\nTesting Selenium setup...")
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")  # Run headless for testing
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✓ Selenium setup successful")
        print("✓ Chrome driver created successfully")
        
        # Test a simple navigation
        driver.get("https://www.google.com")
        print("✓ Successfully navigated to Google")
        
        driver.quit()
        print("✓ Driver closed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Selenium setup failed: {e}")
        return False

def main():
    print("="*60)
    print("CHROME & CHROMEDRIVER DIAGNOSTIC TOOL")
    print("="*60)
    
    # Check Chrome installation
    chrome_ok = check_chrome_installation()
    
    # Check ChromeDriver
    driver_ok = check_chromedriver()
    
    # Test Selenium setup
    selenium_ok = test_selenium_setup()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Chrome Installation: {'✓ OK' if chrome_ok else '✗ FAILED'}")
    print(f"ChromeDriver: {'✓ OK' if driver_ok else '✗ FAILED'}")
    print(f"Selenium Setup: {'✓ OK' if selenium_ok else '✗ FAILED'}")
    
    if not chrome_ok:
        print("\nRECOMMENDATION: Install Google Chrome first")
    elif not driver_ok:
        print("\nRECOMMENDATION: ChromeDriver issue - try reinstalling webdriver-manager")
    elif not selenium_ok:
        print("\nRECOMMENDATION: Selenium configuration issue")
    else:
        print("\n✓ Everything looks good! You should be able to run the LinkedIn finder.")
    
    print("="*60)

if __name__ == "__main__":
    main()
