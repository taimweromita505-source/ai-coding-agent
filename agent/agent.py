#!/usr/bin/env python3
"""
Local AI Coding Agent
Uses Ollama to run local LLMs for coding tasks.
"""

import json
import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime

class LocalAICodingAgent:
    def __init__(self, config_path="agent/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.workspace = Path(self.config["agent"]["workspace"])
        self.logs_dir = Path(self.config["agent"]["logs"])
        self.ollama_url = self.config["agent"]["ollama"]["url"]
        self.models = self.config["agent"]["models"]
        
        # Ensure directories exist
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.logs_dir / f"agent-{datetime.now().strftime('%Y%m%d')}.log"
        
    def load_config(self):
        """Load agent configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def log(self, message):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama(self):
        """Start Ollama service if not running"""
        if self.check_ollama():
            self.log("Ollama is already running")
            return True
        
        self.log("Starting Ollama...")
        try:
            # Start Ollama in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            time.sleep(3)
            return self.check_ollama()
        except Exception as e:
            self.log(f"Failed to start Ollama: {e}")
            return False
    
    def list_models(self):
        """List available models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except:
            return []
    
    def generate_code(self, prompt, model=None, language="python"):
        """Generate code using local LLM"""
        if not model:
            model = self.models["primary"]
        
        system_prompt = f"""You are an expert coding assistant. Generate clean, efficient, and well-documented {language} code.
Follow these rules:
- Write complete, runnable code
- Include error handling where appropriate
- Add comments explaining complex logic
- Follow best practices for {language}
- Output ONLY the code, no explanations or markdown blocks"""

        full_prompt = f"{system_prompt}\n\nTask: {prompt}\n\nGenerate the {language} code:"
        
        self.log(f"Generating code with {model}...")
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config["agent"]["temperature"],
                        "num_predict": 2000
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result.get("response", "")
                # Clean up markdown code blocks if present
                code = code.strip()
                if code.startswith("```"):
                    code = code.split("\n", 1)[1]
                if code.endswith("```"):
                    code = code.rsplit("\n", 1)[0]
                return code.strip()
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error generating code: {e}"
    
    def save_code(self, filename, code, language="python"):
        """Save generated code to workspace"""
        filepath = self.workspace / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        self.log(f"Code saved to: {filepath}")
        return filepath
    
    def execute_code(self, filepath, language="python"):
        """Execute generated code and return output"""
        self.log(f"Executing: {filepath}")
        
        try:
            if language == "python":
                result = subprocess.run(
                    [sys.executable, str(filepath)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.workspace)
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            else:
                return {"success": False, "error": f"Unsupported language: {language}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Execution timed out (30s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def interactive_mode(self):
        """Run interactive coding agent"""
        print("=" * 60)
        print("  Local AI Coding Agent")
        print("=" * 60)
        print()
        
        # Check Ollama
        if not self.check_ollama():
            print("Starting Ollama service...")
            if not self.start_ollama():
                print("ERROR: Could not start Ollama. Please install it first.")
                input("Press Enter to exit...")
                return
        
        print("Ollama is running!")
        print()
        
        # List available models
        models = self.list_models()
        if models:
            print("Available models:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
            print()
        
        print(f"Primary model: {self.models['primary']}")
        print(f"Fallback model: {self.models['fallback']}")
        print()
        print("Type 'exit' or 'quit' to exit")
        print("Type 'models' to list available models")
        print("Type 'clear' to clear workspace")
        print("=" * 60)
        print()
        
        while True:
            try:
                user_input = input("Coding Task: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'models':
                    models = self.list_models()
                    print("\nAvailable models:")
                    for m in models:
                        print(f"  - {m}")
                    print()
                    continue
                
                if user_input.lower() == 'clear':
                    import shutil
                    for f in self.workspace.glob("*"):
                        if f.is_file():
                            f.unlink()
                    print("Workspace cleared.\n")
                    continue
                
                if not user_input:
                    continue
                
                # Detect language from prompt
                language = "python"
                if "javascript" in user_input.lower() or "js" in user_input.lower():
                    language = "javascript"
                elif "java" in user_input.lower():
                    language = "java"
                elif "c++" in user_input.lower() or "cpp" in user_input.lower():
                    language = "cpp"
                elif "rust" in user_input.lower():
                    language = "rust"
                elif "go" in user_input.lower():
                    language = "go"
                
                print(f"\nGenerating {language} code...")
                code = self.generate_code(user_input, language=language)
                
                if code.startswith("Error:"):
                    print(f"ERROR: {code}")
                    continue
                
                # Save code
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_{timestamp}.{language}"
                filepath = self.save_code(filename, code, language)
                
                print(f"\nCode saved to: {filepath}")
                print("\n" + "=" * 60)
                print("Generated Code:")
                print("=" * 60)
                print(code)
                print("=" * 60)
                
                # Ask if user wants to execute
                execute = input("\nExecute this code? (y/n): ").strip().lower()
                if execute == 'y':
                    result = self.execute_code(filepath, language)
                    if result["success"]:
                        print("\nOutput:")
                        print(result["stdout"])
                    else:
                        print("\nError:")
                        print(result.get("stderr", result.get("error", "Unknown error")))
                
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue

def main():
    agent = LocalAICodingAgent()
    agent.interactive_mode()

if __name__ == "__main__":
    main()
