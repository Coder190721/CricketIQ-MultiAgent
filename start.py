#!/usr/bin/env python3
"""
CricketIQ Quick Start Script
"""

import os
import sys
import subprocess

def check_env():
    """Check if environment is properly set up"""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("📝 Please run: python setup.py")
        return False
    
    # Check if GOOGLE_API_KEY is set
    with open(".env", "r") as f:
        content = f.read()
        if "your_google_api_key_here" in content:
            print("❌ Please set your Google API key in .env file")
            return False
    
    return True

def start_cricket_iq():
    """Start CricketIQ application"""
    print("🏏 Starting CricketIQ...")
    print("=" * 30)
    
    if not check_env():
        return False
    
    try:
        print("🚀 Launching CricketIQ Gradio app...")
        subprocess.run([sys.executable, "cricket_adk_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 CricketIQ stopped by user")
    except Exception as e:
        print(f"❌ Error starting CricketIQ: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_cricket_iq()
