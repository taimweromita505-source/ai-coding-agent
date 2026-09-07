#!/usr/bin/env python3
"""
API Key Manager for AI Coding Agent
Securely manages API keys for different model providers
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict

INSTALL_DIR = Path(__file__).parent.parent.absolute()
KEYS_FILE = INSTALL_DIR / "logs" / "api_keys.json"


class APIKeyManager:
    """Manages API keys for different providers"""
    
    def __init__(self):
        self.keys: Dict[str, str] = self._load_keys()
    
    def _load_keys(self) -> Dict[str, str]:
        try:
            if KEYS_FILE.exists():
                return json.loads(KEYS_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
        return {}
    
    def _save_keys(self):
        try:
            KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
            KEYS_FILE.write_text(json.dumps(self.keys, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            print(f"Warning: Failed to save API keys: {e}")
    
    def get_key(self, provider: str) -> Optional[str]:
        env_var = f"{provider.upper()}_API_KEY"
        key = os.environ.get(env_var)
        if key:
            return key
        return self.keys.get(provider)
    
    def set_key(self, provider: str, key: str):
        if not key or not key.strip():
            if provider in self.keys:
                del self.keys[provider]
                self._save_keys()
            return
        self.keys[provider] = key.strip()
        self._save_keys()
    
    def remove_key(self, provider: str):
        if provider in self.keys:
            del self.keys[provider]
            self._save_keys()
    
    def list_keys(self) -> Dict[str, str]:
        result = {}
        for provider in ["openai", "anthropic", "google", "ollama", "openrouter", "omniroute"]:
            key = self.get_key(provider)
            if key:
                masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                result[provider] = masked
            else:
                result[provider] = None
        return result
    
    def has_key(self, provider: str) -> bool:
        key = self.get_key(provider)
        return bool(key and key.strip())
    
    def get_provider_info(self, provider: str, config: dict) -> Optional[dict]:
        info = config.get("providers", {}).get(provider)
        if not info:
            return None
        
        api_key = self.get_key(provider)
        if not api_key and provider != "ollama":
            return None
        
        return {
            "url": info.get("url"),
            "api_key": api_key,
            "models_dir": info.get("models_dir")
        }
