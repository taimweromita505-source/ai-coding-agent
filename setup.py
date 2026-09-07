#!/usr/bin/env python3
"""
Universal setup script for AI Coding Agent
Works on Windows, macOS, Linux, Android (Termux), and iOS (Web)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Determine installation directory
if getattr(sys, 'frozen', False):
    INSTALL_DIR = Path(sys.executable).parent
else:
    INSTALL_DIR = Path(__file__).parent.absolute()

sys.path.insert(0, str(INSTALL_DIR))

from os_utils import OSDetector

def print_banner():
    print("=" * 80)
    print("                                                                        ")
    print("   ###   ###  #####  #   #  #####  #   #  #####  #   #  #   #  ###   ###     ")
    print("   #  # #   # #   # ## ## #   #  ## ## #   #  ##  # #   # #   # #  # #   #    ")
    print("   #  # #     #   # # # # #   #  # # # #   #  # # # #   # #   # #  # #       ")
    print("   ###  #     #####  #  #  #####  #  #  #####  #  ## #   # ##### ###   ###     ")
    print("   # #  #     #   #     # #   #     #  #   # #   ## #   #     # # #       #    ")
    print("   #  #  ###  #   #     # #   #     #  #   # #    #  ###      # #  #  ###      ")
    print("                                                                        ")
    print("              UNLIMITED AI CODING AGENT - Universal Setup              ")
    print("              No Restrictions. Full Access.                            ")
    print("                                                                        ")
    print("=" * 80)

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Error: Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_ollama():
    ollama_cmd = OSDetector.get_ollama_command()
    try:
        result = subprocess.run([ollama_cmd, '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"Ollama - OK")
            return True
    except:
        pass
    
    print("Ollama - Not found")
    print("  Please install from: https://ollama.ai/download")
    return False

def install_dependencies():
    print("\nInstalling dependencies...")
    requirements = INSTALL_DIR / 'agent' / 'requirements.txt'
    requirements_cli = INSTALL_DIR / 'agent' / 'requirements-cli.txt'
    
    python = OSDetector.get_python_executable()
    
    if requirements.exists():
        print(f"  Installing {requirements.name}...")
        subprocess.run([python, '-m', 'pip', 'install', '-r', str(requirements)], 
                      capture_output=True)
    
    if requirements_cli.exists():
        print(f"  Installing {requirements_cli.name}...")
        subprocess.run([python, '-m', 'pip', 'install', '-r', str(requirements_cli)], 
                      capture_output=True)
    
    print("  Dependencies installed")

def setup_directories():
    dirs = [
        INSTALL_DIR / 'workspace',
        INSTALL_DIR / 'logs',
        INSTALL_DIR / 'models',
    ]
    
    for d in dirs:
        d.mkdir(exist_ok=True)
        print(f"  Created: {d}")

def setup_autostart():
    os_type = OSDetector.get_os()
    print(f"\nAuto-start setup for {os_type}...")
    
    launcher = INSTALL_DIR / 'agent' / 'cross-platform-launcher.py'
    python = OSDetector.get_python_executable()
    startup_dir = OSDetector.get_startup_dir()
    
    if not startup_dir:
        print("  Unsupported OS for auto-start")
        return
    
    try:
        if os_type == 'windows':
            vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "{python} \"{launcher}\"", 0, False'''
            vbs_path = startup_dir / 'AI-Coding-Agent.vbs'
            with open(vbs_path, 'w') as f:
                f.write(vbs_content)
            print(f"  Auto-start enabled: {vbs_path}")
            
        elif os_type == 'macos':
            plist_path = startup_dir / 'com.aicodingagent.plist'
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aicodingagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python}</string>
        <string>{launcher}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{INSTALL_DIR}/logs/autostart.log</string>
    <key>StandardErrorPath</key>
    <string>{INSTALL_DIR}/logs/autostart.log</string>
</dict>
</plist>'''
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            subprocess.run(['launchctl', 'load', str(plist_path)], check=True)
            print(f"  Auto-start enabled: {plist_path}")
            
        elif os_type == 'linux':
            desktop_path = startup_dir / 'ai-coding-agent.desktop'
            desktop_content = f'''[Desktop Entry]
Type=Application
Name=AI Coding Agent
Exec={python} {launcher}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
'''
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            os.chmod(desktop_path, 0o755)
            print(f"  Auto-start enabled: {desktop_path}")
    except Exception as e:
        print(f"  Auto-start setup failed: {e}")

def create_launchers():
    os_type = OSDetector.get_os()
    python = OSDetector.get_python_executable()
    launcher = INSTALL_DIR / 'agent' / 'cross-platform-launcher.py'
    
    if os_type == 'windows':
        bat_content = f'''@echo off
cd /d "{INSTALL_DIR}"
"{python}" "{launcher}"
pause
'''
        bat_path = INSTALL_DIR / 'START.bat'
        with open(bat_path, 'w') as f:
            f.write(bat_content)
        print(f"  Created: {bat_path}")
        
    elif os_type in ['macos', 'linux']:
        sh_content = f'''#!/bin/bash
cd "{INSTALL_DIR}"
"{python}" "{launcher}"
'''
        sh_path = INSTALL_DIR / 'start.sh'
        with open(sh_path, 'w') as f:
            f.write(sh_content)
        os.chmod(sh_path, 0o755)
        print(f"  Created: {sh_path}")

def main():
    print_banner()
    
    os_type = OSDetector.get_os()
    python = OSDetector.get_python_executable()
    print(f"\nOS: {os_type}")
    print(f"Python: {python}")
    print(f"Installation: {INSTALL_DIR}\n")
    
    if not check_python():
        sys.exit(1)
    
    ollama_installed = check_ollama()
    
    print("\nSetup:")
    setup_directories()
    install_dependencies()
    create_launchers()
    
    if ollama_installed and os_type not in ['android', 'ios']:
        autostart = input("\nEnable auto-start on boot? (Y/n): ").strip().lower()
        if autostart in ['', 'y', 'yes']:
            setup_autostart()
    
    print("\nPlugin setup:")
    plugin_setup = INSTALL_DIR / 'plugin-setup.py'
    if plugin_setup.exists():
        try:
            subprocess.run([python, str(plugin_setup)], check=True)
        except Exception as e:
            print(f"  Plugin setup failed: {e}")
    else:
        print(f"  Plugin setup script not found: {plugin_setup}")
    
    print("\n" + "=" * 80)
    print("Setup complete!")
    print("=" * 80)
    print(f"\nInstallation: {INSTALL_DIR}")
    print(f"Workspace: {INSTALL_DIR / 'workspace'}")
    print(f"Logs: {INSTALL_DIR / 'logs'}")
    print(f"Models: {INSTALL_DIR / 'models'}")
    
    print("\nTo start the agent:")
    if os_type == 'windows':
        print(f"  {INSTALL_DIR / 'START.bat'}")
    elif os_type == 'android':
        print(f"  cd ~/ai-coding-agent && python agent/beautiful-cli.py")
    else:
        print(f"  {INSTALL_DIR / 'start.sh'}")
    
    print("\nTo access from mobile:")
    print(f"  python agent/mobile-web.py")
    print(f"  Then open http://localhost:8080 on your phone")
    
    print("\nFeatures:")
    print("  - No restrictions, full access")
    print("  - Code generation in any language")
    print("  - Code execution")
    print("  - Shell command execution")
    print("  - File operations")
    print("  - Beautiful CLI interface")
    print("  - Web interface for mobile")
    print("  - PWA support (install on home screen)")
    print("  - Auto-start on boot")
    print("  - Cross-platform (Windows, macOS, Linux, Android, iOS)")
    
    print("\n" + "=" * 80)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
