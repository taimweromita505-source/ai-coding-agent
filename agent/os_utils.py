#!/usr/bin/env python3
"""
Cross-platform utilities for AI Coding Agent
"""

import os
import sys
import platform
from pathlib import Path

class OSDetector:
    @staticmethod
    def get_os():
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            # Detect Android/Termux
            if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
                return 'android'
            return 'linux'
        else:
            return 'unknown'
    
    @staticmethod
    def get_home():
        return Path.home()
    
    @staticmethod
    def get_app_dir():
        """Get the agent installation directory"""
        # If running from installed location
        if sys.platform == 'win32':
            # Check if we're in Program Files or AppData
            script_dir = Path(__file__).parent.absolute()
            if 'Program Files' in str(script_dir) or 'AppData' in str(script_dir):
                return script_dir
        
        # Otherwise use the directory where the script is located
        return Path(__file__).parent.absolute()
    
    @staticmethod
    def get_startup_dir():
        """Get the startup directory for auto-start"""
        os_type = OSDetector.get_os()
        home = OSDetector.get_home()
        
        if os_type == 'windows':
            # Windows Startup folder
            return home / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
        elif os_type == 'macos':
            # macOS LaunchAgents
            return home / 'Library' / 'LaunchAgents'
        elif os_type == 'linux':
            # Linux autostart
            return home / '.config' / 'autostart'
        else:
            return None
    
    @staticmethod
    def get_python_executable():
        """Get the Python executable path"""
        if sys.platform == 'win32':
            # Try to find Python in common locations
            import shutil
            python = shutil.which('python')
            if python:
                return python
            python = shutil.which('python3')
            if python:
                return python
            # Default locations
            possible_paths = [
                Path(sys.executable),
                Path.home() / 'AppData' / 'Local' / 'Programs' / 'Python' / 'Python314' / 'python.exe',
                Path.home() / 'AppData' / 'Local' / 'Programs' / 'Python' / 'Python313' / 'python.exe',
                Path.home() / 'AppData' / 'Local' / 'Programs' / 'Python' / 'Python312' / 'python.exe',
                Path('/usr/bin/python3'),
                Path('/usr/local/bin/python3'),
            ]
            for path in possible_paths:
                if path.exists():
                    return str(path)
            return 'python'
        else:
            return 'python3'
    
    @staticmethod
    def get_ollama_command():
        """Get the Ollama command"""
        import shutil
        ollama = shutil.which('ollama')
        if ollama:
            return ollama
        
        if sys.platform == 'win32':
            possible_paths = [
                Path.home() / 'AppData' / 'Local' / 'Programs' / 'Ollama' / 'ollama.exe',
                Path('C:/Program Files/Ollama/ollama.exe'),
                Path('C:/Program Files (x86)/Ollama/ollama.exe'),
            ]
            for path in possible_paths:
                if path.exists():
                    return str(path)
        else:
            possible_paths = [
                Path('/usr/local/bin/ollama'),
                Path('/usr/bin/ollama'),
                Path.home() / 'bin' / 'ollama',
            ]
            for path in possible_paths:
                if path.exists():
                    return str(path)
        
        return 'ollama'
