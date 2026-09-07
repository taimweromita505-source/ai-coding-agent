#!/usr/bin/env python3
"""
Model Manager - Download and manage local LLM models
"""

import json
import os
import subprocess
import sys
from pathlib import Path

class ModelManager:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "agent" / "config.json"
        self.config = self.load_config()
        self.models_dir = Path(self.config["agent"]["ollama"]["models_dir"])
        
    def load_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def check_ollama(self):
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    def list_available(self):
        """List locally available models"""
        if not self.check_ollama():
            print("ERROR: Ollama is not installed or not in PATH")
            return []
        
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            models = []
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            return models
        return []
    
    def list_recommended(self):
        """List recommended coding models"""
        return [
            {"name": "deepseek-coder:1.3b", "size": "~750MB", "desc": "Fast, lightweight coding model", "recommended": True},
            {"name": "deepseek-coder:6.7b", "size": "~3.5GB", "desc": "Balanced coding model", "recommended": True},
            {"name": "codellama:7b", "size": "~3.8GB", "desc": "Best overall coding model", "recommended": True},
            {"name": "codellama:13b", "size": "~7GB", "desc": "Larger, more capable coding model", "recommended": False},
            {"name": "llama2:7b", "size": "~3.8GB", "desc": "General purpose model", "recommended": True},
            {"name": "llama2:13b", "size": "~7GB", "desc": "Larger general purpose model", "recommended": False},
            {"name": "mistral:7b", "size": "~4GB", "desc": "Good general purpose model", "recommended": True},
            {"name": "neural-chat:7b", "size": "~4GB", "desc": "Conversational model", "recommended": False},
        ]
    
    def pull_model(self, model_name):
        """Download a model"""
        print(f"\nDownloading {model_name}...")
        print("This may take a while depending on your internet speed.")
        print()
        
        try:
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                print(line, end='')
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n✓ Successfully downloaded {model_name}")
                return True
            else:
                print(f"\n✗ Failed to download {model_name}")
                return False
                
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False
    
    def remove_model(self, model_name):
        """Remove a model"""
        try:
            subprocess.run(["ollama", "rm", model_name], check=True)
            print(f"✓ Removed {model_name}")
            return True
        except Exception as e:
            print(f"✗ Failed to remove {model_name}: {e}")
            return False
    
    def interactive_mode(self):
        """Interactive model management"""
        print("=" * 60)
        print("  Model Manager")
        print("=" * 60)
        print()
        
        if not self.check_ollama():
            print("ERROR: Ollama is not installed!")
            print("Please install from: https://ollama.ai/download")
            input("Press Enter to exit...")
            return
        
        while True:
            print("\nAvailable locally:")
            local = self.list_available()
            if local:
                for m in local:
                    print(f"  ✓ {m}")
            else:
                print("  (none)")
            
            print("\nRecommended models:")
            recommended = self.list_recommended()
            for i, m in enumerate(recommended, 1):
                status = "✓" if m["name"] in local else " "
                print(f"  {status} {i}. {m['name']} ({m['size']}) - {m['desc']}")
            
            print("\nOptions:")
            print("  1-8. Download model")
            print("  d. Download all recommended")
            print("  r. Remove a model")
            print("  q. Quit")
            print()
            
            choice = input("Select option: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'd':
                for m in recommended:
                    if m["recommended"] and m["name"] not in local:
                        self.pull_model(m["name"])
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(recommended):
                    model = recommended[idx]["name"]
                    if model in local:
                        print(f"{model} is already downloaded.")
                    else:
                        self.pull_model(model)
            elif choice == 'r':
                if local:
                    print("\nWhich model to remove?")
                    for i, m in enumerate(local, 1):
                        print(f"  {i}. {m}")
                    sel = input("Enter number: ").strip()
                    if sel.isdigit():
                        idx = int(sel) - 1
                        if 0 <= idx < len(local):
                            self.remove_model(local[idx])

def main():
    manager = ModelManager()
    manager.interactive_mode()

if __name__ == "__main__":
    main()
