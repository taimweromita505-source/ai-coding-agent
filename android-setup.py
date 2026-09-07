#!/usr/bin/env python3
"""
Android setup helper - generates Termux setup script
"""

import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("  AI Coding Agent - Android Setup")
    print("=" * 60)
    print()
    print("This will generate an Android setup script for Termux.")
    print()
    
    # Read the Android setup script
    android_script = Path(__file__).parent / "android-setup.sh"
    
    if not android_script.exists():
        print("Error: android-setup.sh not found")
        sys.exit(1)
    
    print("Setup instructions:")
    print()
    print("1. Install Termux from F-Droid:")
    print("   https://f-droid.org/en/packages/com.termux/")
    print()
    print("2. Transfer this folder to your Android device")
    print()
    print("3. In Termux, run:")
    print(f"   bash {android_script}")
    print()
    print("4. After setup, start the agent:")
    print("   cd ~/ai-coding-agent")
    print("   python agent/beautiful-cli.py")
    print()
    print("=" * 60)
    
    # Generate standalone script
    output = Path.home() / "ai-coding-agent-setup.sh"
    with open(android_script, 'r') as f:
        content = f.read()
    
    with open(output, 'w') as f:
        f.write(content)
    
    print(f"Setup script saved to: {output}")
    print()
    print("Transfer this file to your Android device and run in Termux.")

if __name__ == "__main__":
    main()
