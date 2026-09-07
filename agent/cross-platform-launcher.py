#!/usr/bin/env python3
"""
Cross-platform launcher for AI Coding Agent
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

# Add agent directory to path
AGENT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(AGENT_DIR))

from os_utils import OSDetector

def main():
    os_type = OSDetector.get_os()
    python = OSDetector.get_python_executable()
    
    print(f"OS: {os_type}")
    print(f"Python: {python}")
    print(f"Agent dir: {AGENT_DIR}")
    
    # Check if we should install auto-start
    if len(sys.argv) > 1 and sys.argv[1] == '--install-autostart':
        install_autostart(os_type)
        return
    
    # Check if we should remove auto-start
    if len(sys.argv) > 1 and sys.argv[1] == '--remove-autostart':
        remove_autostart(os_type)
        return
    
    # Start Ollama
    start_ollama(os_type)
    
    # Launch the beautiful CLI
    beautiful_cli = AGENT_DIR / 'beautiful-cli.py'
    if not beautiful_cli.exists():
        print(f"Error: {beautiful_cli} not found")
        sys.exit(1)
    
    try:
        subprocess.run([python, str(beautiful_cli)], check=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def start_ollama(os_type):
    """Start Ollama if not running"""
    import requests
    
    ollama_url = "http://localhost:11434"
    
    # Check if Ollama is running
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            print("Ollama is already running")
            return True
    except:
        pass
    
    # Start Ollama
    ollama_cmd = OSDetector.get_ollama_command()
    print(f"Starting Ollama...")
    
    try:
        if os_type == 'windows':
            subprocess.Popen(
                [ollama_cmd, 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                [ollama_cmd, 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        # Wait for Ollama to start
        time.sleep(3)
        
        # Verify
        for i in range(10):
            try:
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    print("Ollama started successfully")
                    return True
            except:
                time.sleep(1)
        
        print("Warning: Ollama may not have started properly")
        return False
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False

def install_autostart(os_type):
    """Install auto-start for the current OS"""
    startup_dir = OSDetector.get_startup_dir()
    if not startup_dir:
        print("Unsupported OS for auto-start")
        return False
    
    python = OSDetector.get_python_executable()
    launcher = AGENT_DIR / 'cross-platform-launcher.py'
    
    try:
        if os_type == 'windows':
            # Create a VBScript that runs the launcher hidden
            vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "{python} \"{launcher}\"", 0, False'''
            vbs_path = startup_dir / 'AI-Coding-Agent.vbs'
            with open(vbs_path, 'w') as f:
                f.write(vbs_content)
            print(f"Auto-start installed: {vbs_path}")
            
        elif os_type == 'macos':
            # Create LaunchAgent plist
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
    <string>{AGENT_DIR}/logs/autostart.log</string>
    <key>StandardErrorPath</key>
    <string>{AGENT_DIR}/logs/autostart.log</string>
</dict>
</plist>'''
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            print(f"Auto-start installed: {plist_path}")
            # Load the launch agent
            subprocess.run(['launchctl', 'load', str(plist_path)], check=True)
            
        elif os_type == 'linux':
            # Create .desktop file
            desktop_path = startup_dir / 'ai-coding-agent.desktop'
            desktop_content = f'''[Desktop Entry]
Type=Application
Name=AI Coding Agent
Exec={python} {launcher}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
Comment=Unlimited AI Coding Agent
'''
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            # Make it executable
            os.chmod(desktop_path, 0o755)
            print(f"Auto-start installed: {desktop_path}")
        
        return True
    except Exception as e:
        print(f"Failed to install auto-start: {e}")
        return False

def remove_autostart(os_type):
    """Remove auto-start for the current OS"""
    startup_dir = OSDetector.get_startup_dir()
    if not startup_dir:
        print("Unsupported OS for auto-start")
        return False
    
    try:
        if os_type == 'windows':
            autostart_file = startup_dir / 'AI-Coding-Agent.vbs'
            if autostart_file.exists():
                autostart_file.unlink()
                print("Auto-start removed")
            else:
                print("Auto-start not found")
                
        elif os_type == 'macos':
            plist_path = startup_dir / 'com.aicodingagent.plist'
            if plist_path.exists():
                subprocess.run(['launchctl', 'unload', str(plist_path)], check=True)
                plist_path.unlink()
                print("Auto-start removed")
            else:
                print("Auto-start not found")
                
        elif os_type == 'linux':
            desktop_path = startup_dir / 'ai-coding-agent.desktop'
            if desktop_path.exists():
                desktop_path.unlink()
                print("Auto-start removed")
            else:
                print("Auto-start not found")
        
        return True
    except Exception as e:
        print(f"Failed to remove auto-start: {e}")
        return False

if __name__ == "__main__":
    main()
