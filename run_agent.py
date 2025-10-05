#!/usr/bin/env python3
"""
Cricket Agent Launcher
Simple script to run the cricket agent with different options
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found")
        print("Run: python setup.py")
        return False
    
    # Check if Google API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == "your_google_api_key_here":
        print("❌ Google API key not set")
        print("Please edit .env file and add your Google API key")
        return False
    
    print("✅ Requirements met")
    return True

def run_web_interface():
    """Run the Gradio web interface"""
    print("🌐 Starting web interface...")
    try:
        subprocess.run([sys.executable, "cricket_gradio_demo.py"])
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")
    except Exception as e:
        print(f"❌ Error running web interface: {e}")

def run_command_line():
    """Run the command line interface"""
    print("💻 Starting command line interface...")
    try:
        subprocess.run([sys.executable, "cricket_agent.py"])
    except KeyboardInterrupt:
        print("\n👋 Command line interface stopped")
    except Exception as e:
        print(f"❌ Error running command line interface: {e}")

def run_mcp_server():
    """Run the MCP server only"""
    print("🔧 Starting MCP server...")
    try:
        subprocess.run([sys.executable, "cricket_mcp_server.py"])
    except KeyboardInterrupt:
        print("\n👋 MCP server stopped")
    except Exception as e:
        print(f"❌ Error running MCP server: {e}")

def run_tests():
    """Run tests"""
    print("🧪 Running tests...")
    try:
        subprocess.run([sys.executable, "test_cricket_agent.py"])
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def show_help():
    """Show help information"""
    help_text = """
🏏 Cricket Statistics Agent Launcher

Usage: python run_agent.py [option]

Options:
  web, w     - Run web interface (Gradio)
  cli, c      - Run command line interface
  mcp, m      - Run MCP server only
  test, t     - Run tests
  help, h     - Show this help

Examples:
  python run_agent.py web    # Start web interface
  python run_agent.py cli    # Start command line
  python run_agent.py test   # Run tests

Default: web interface
    """
    print(help_text)

def main():
    """Main launcher function"""
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
    else:
        option = "web"  # Default to web interface
    
    print("🏏 Cricket Statistics Agent")
    print("=" * 40)
    
    # Check requirements first
    if not check_requirements():
        sys.exit(1)
    
    # Run based on option
    if option in ["web", "w"]:
        run_web_interface()
    elif option in ["cli", "c"]:
        run_command_line()
    elif option in ["mcp", "m"]:
        run_mcp_server()
    elif option in ["test", "t"]:
        run_tests()
    elif option in ["help", "h"]:
        show_help()
    else:
        print(f"❌ Unknown option: {option}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
