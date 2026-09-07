#!/usr/bin/env python3
"""
Universal Auto-Start for AI Coding Agent
Works on Windows, macOS, Linux, Android
Detects USB drive and launches the agent automatically
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def get_os():
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
            return 'android'
        return 'linux'
    return 'unknown'

def find_usb_drive():
    """Find the AI-Coding-Agent folder on any removable drive"""
    os_type = get_os()
    
    if os_type == 'windows':
        # Check all drive letters A-Z
        import string
        for drive in string.ascii_uppercase:
            path = Path(f"{drive}:\\AI-Coding-Agent")
            if path.exists() and (path / "agent" / "beautiful-cli.py").exists():
                return path
        # Also check with backslash
        for drive in string.ascii_uppercase:
            path = Path(f"{drive}:/AI-Coding-Agent")
            if path.exists() and (path / "agent" / "beautiful-cli.py").exists():
                return path
    
    elif os_type == 'macos':
        # Check /Volumes for mounted drives
        volumes = Path("/Volumes")
        if volumes.exists():
            for volume in volumes.iterdir():
                if volume.is_dir():
                    path = volume / "AI-Coding-Agent"
                    if path.exists() and (path / "agent" / "beautiful-cli.py").exists():
                        return path
        # Also check common mount points
        for mount in [Path("/media"), Path("/mnt")]:
            if mount.exists():
                for user_dir in mount.iterdir():
                    if user_dir.is_dir():
                        for drive in user_dir.iterdir():
                            if drive.is_dir():
                                path = drive / "AI-Coding-Agent"
                                if path.exists() and (path / "agent" / "beautiful-cli.py").exists():
                                    return path
    
    elif os_type in ['linux', 'android']:
        # Check /media and /mnt
        for mount in [Path("/media"), Path("/mnt")]:
            if mount.exists():
                for user_dir in mount.iterdir():
                    if user_dir.is_dir():
                        for drive in user_dir.iterdir():
                            if drive.is_dir():
                                path = drive / "AI-Coding-Agent"
                                if path.exists() and (path / "agent" / "beautiful-cli.py").exists():
                                    return path
        
        # Check /run/media for some distros
        run_media = Path("/run/media")
        if run_media.exists():
            for user_dir in run_media.iterdir():
                if user_dir.is_dir():
                    for drive in user_dir.iterdir():
                        if drive.is_dir():
                            path = drive / "AI-Coding-Agent"
                            if path.exists() and (path / "agent" / "beautiful-cli.py").exists():
                                return path
    
    return None

def start_ollama():
    """Start Ollama if not running"""
    os_type = get_os()
    ollama_url = "http://localhost:11434"
    
    # Check if already running
    try:
        import requests
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            print("[OK] Ollama is already running")
            return True
    except:
        pass
    
    print("[*] Starting Ollama...")
    
    try:
        if os_type == 'windows':
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        # Wait for Ollama to start
        for i in range(10):
            try:
                import requests
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    print("[OK] Ollama started successfully")
                    return True
            except:
                time.sleep(1)
        
        print("[WARNING] Ollama may not have started properly")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to start Ollama: {e}")
        return False

def launch_agent(agent_path):
    """Launch the Beautiful CLI"""
    os_type = get_os()
    agent_dir = agent_path / "agent"
    cli_script = agent_dir / "beautiful-cli.py"
    
    if not cli_script.exists():
        print(f"[ERROR] CLI not found: {cli_script}")
        return False
    
    # Set environment
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = str(agent_path / "models")
    env["PYTHONUNBUFFERED"] = "1"
    
    # Find Python executable
    if os_type == 'windows':
        python_cmd = sys.executable
    else:
        python_cmd = sys.executable if sys.executable else "python3"
    
    try:
        if os_type == 'windows':
            # On Windows, run in a new console window
            subprocess.Popen(
                [python_cmd, str(cli_script)],
                cwd=str(agent_dir),
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # On macOS/Linux, run in a new terminal
            subprocess.Popen(
                [python_cmd, str(cli_script)],
                cwd=str(agent_dir),
                env=env,
                start_new_session=True
            )
        return True
    except Exception as e:
        print(f"[ERROR] Failed to launch agent: {e}")
        return False

def install_autostart(os_type):
    """Install auto-start for the current OS"""
    home = Path.home()
    
    if os_type == 'windows':
        startup_dir = home / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        vbs_path = startup_dir / 'AI-Coding-Agent-USB.vbs'
        
        vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python \"{Path(__file__).parent / 'universal-autostart.py'}\"", 0, False'''
        
        try:
            vbs_path.parent.mkdir(parents=True, exist_ok=True)
            with open(vbs_path, 'w') as f:
                f.write(vbs_content)
            print(f"[OK] Auto-start installed: {vbs_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install auto-start: {e}")
            return False
    
    elif os_type == 'macos':
        plist_path = home / 'Library' / 'LaunchAgents' / 'com.aicodingagent.plist'
        python_path = sys.executable
        script_path = Path(__file__).absolute()
        
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aicodingagent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{home}/Library/Logs/AI-Coding-Agent.log</string>
    <key>StandardErrorPath</key>
    <string>{home}/Library/Logs/AI-Coding-Agent.log</string>
</dict>
</plist>'''
        
        try:
            plist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            print(f"[OK] Auto-start installed: {plist_path}")
            subprocess.run(['launchctl', 'load', str(plist_path)], check=True)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install auto-start: {e}")
            return False
    
    elif os_type in ['linux', 'android']:
        desktop_path = home / '.config' / 'autostart' / 'ai-coding-agent.desktop'
        python_path = sys.executable
        script_path = Path(__file__).absolute()
        
        desktop_content = f'''[Desktop Entry]
Type=Application
Name=AI Coding Agent
Exec={python_path} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
Comment=Unlimited AI Coding Agent from USB
'''
        
        try:
            desktop_path.parent.mkdir(parents=True, exist_ok=True)
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            os.chmod(desktop_path, 0o755)
            print(f"[OK] Auto-start installed: {desktop_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install auto-start: {e}")
            return False
    
    else:
        print(f"[ERROR] Unsupported OS: {os_type}")
        return False

def remove_autostart(os_type):
    """Remove auto-start for the current OS"""
    home = Path.home()
    
    try:
        if os_type == 'windows':
            vbs_path = home / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup' / 'AI-Coding-Agent-USB.vbs'
            if vbs_path.exists():
                vbs_path.unlink()
                print("[OK] Auto-start removed")
            else:
                print("[INFO] Auto-start not found")
        
        elif os_type == 'macos':
            plist_path = home / 'Library' / 'LaunchAgents' / 'com.aicodingagent.plist'
            if plist_path.exists():
                subprocess.run(['launchctl', 'unload', str(plist_path)], check=True)
                plist_path.unlink()
                print("[OK] Auto-start removed")
            else:
                print("[INFO] Auto-start not found")
        
        elif os_type in ['linux', 'android']:
            desktop_path = home / '.config' / 'autostart' / 'ai-coding-agent.desktop'
            if desktop_path.exists():
                desktop_path.unlink()
                print("[OK] Auto-start removed")
            else:
                print("[INFO] Auto-start not found")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to remove auto-start: {e}")
        return False

def main():
    os_type = get_os()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install-autostart':
            print("Installing auto-start...")
            if install_autostart(os_type):
                print("\n[SUCCESS] Auto-start installed!")
                print("  The agent will start automatically when you log in.")
                if os_type == 'windows':
                    print("  Or run: AI-Coding-Agent-USB.vbs")
                elif os_type == 'macos':
                    print("  Or run: open ~/Library/LaunchAgents/com.aicodingagent.plist")
                elif os_type in ['linux', 'android']:
                    print("  Or run: ~/.config/autostart/ai-coding-agent.desktop")
            else:
                print("\n[FAILED] Could not install auto-start")
            input("\nPress Enter to exit...")
            return
        
        if sys.argv[1] == '--remove-autostart':
            print("Removing auto-start...")
            if remove_autostart(os_type):
                print("\n[SUCCESS] Auto-start removed!")
            else:
                print("\n[FAILED] Could not remove auto-start")
            input("\nPress Enter to exit...")
            return
    
    # Normal launch mode
    print("=" * 60)
    print("  UNLIMITED AI CODING AGENT - Universal Auto-Start")
    print("=" * 60)
    print()
    
    print(f"[INFO] OS: {os_type}")
    
    # Find USB drive
    print("[*] Searching for AI-Coding-Agent USB drive...")
    agent_path = find_usb_drive()
    
    if not agent_path:
        print("[ERROR] USB drive not found!")
        print("  Please insert the USB drive and try again.")
        input("Press Enter to exit...")
        return False
    
    print(f"[OK] Found agent at: {agent_path}")
    
    # Start Ollama
    start_ollama()
    
    # Small delay to ensure Ollama is ready
    time.sleep(2)
    
    # Launch agent
    print("[*] Launching AI Agent...")
    if launch_agent(agent_path):
        print("[OK] AI Agent launched successfully!")
        print("  Check your screen for the agent window.")
    else:
        print("[ERROR] Failed to launch agent")
        input("Press Enter to exit...")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
