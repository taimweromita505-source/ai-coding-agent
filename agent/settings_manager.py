#!/usr/bin/env python3
"""
Portable settings manager for AI Coding Agent
Handles export/import of all agent state
"""

import json
import os
import sys
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, Dict, List

INSTALL_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = INSTALL_DIR / "data"
EXPORTS_DIR = INSTALL_DIR / "exports"


class SettingsManager:
    """Manages portable settings and data sync"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.exports_dir = EXPORTS_DIR
        self.data_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
    
    def export_settings(self, include_models: bool = False) -> Optional[Path]:
        try:
            timestamp = Path().resolve().cwd()  # dummy to get path operations
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = self.exports_dir / f"ai-agent-settings-{ts}.zip"
            
            with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Export config
                config_path = INSTALL_DIR / "agent" / "config.json"
                if config_path.exists():
                    zf.write(config_path, "agent/config.json")
                
                # Export memory
                memory_dir = INSTALL_DIR / "logs" / "memory"
                if memory_dir.exists():
                    for f in memory_dir.glob("*.json"):
                        zf.write(f, f"logs/memory/{f.name}")
                
                # Export API keys
                keys_path = INSTALL_DIR / "logs" / "api_keys.json"
                if keys_path.exists():
                    zf.write(keys_path, "logs/api_keys.json")
                
                # Export workspace
                workspace = INSTALL_DIR / "workspace"
                if workspace.exists():
                    for f in workspace.glob("*"):
                        if f.is_file():
                            zf.write(f, f"workspace/{f.name}")
                
                # Optionally export models (usually too large)
                if include_models:
                    models_dir = INSTALL_DIR / "models"
                    if models_dir.exists():
                        for f in models_dir.glob("*"):
                            if f.is_file():
                                zf.write(f, f"models/{f.name}")
            
            return export_file
        except Exception as e:
            print(f"Export failed: {e}")
            return None
    
    def import_settings(self, zip_path: Path) -> bool:
        try:
            if not zip_path.exists():
                return False
            
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Import config
                if "agent/config.json" in zf.namelist():
                    target = INSTALL_DIR / "agent" / "config.json"
                    target.write_bytes(zf.read("agent/config.json"))
                
                # Import memory
                for name in zf.namelist():
                    if name.startswith("logs/memory/"):
                        target = INSTALL_DIR / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(zf.read(name))
                
                # Import API keys
                if "logs/api_keys.json" in zf.namelist():
                    target = INSTALL_DIR / "logs" / "api_keys.json"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read("logs/api_keys.json"))
                
                # Import workspace
                for name in zf.namelist():
                    if name.startswith("workspace/"):
                        target = INSTALL_DIR / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(zf.read(name))
            
            return True
        except Exception as e:
            print(f"Import failed: {e}")
            return False
    
    def list_exports(self) -> List[Dict[str, any]]:
        exports = []
        if self.exports_dir.exists():
            for f in sorted(self.exports_dir.glob("*.zip")):
                exports.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "path": str(f)
                })
        return exports
    
    def get_portable_paths(self) -> Dict[str, Path]:
        return {
            "install": INSTALL_DIR,
            "data": self.data_dir,
            "logs": INSTALL_DIR / "logs",
            "workspace": INSTALL_DIR / "workspace",
            "models": INSTALL_DIR / "models",
            "exports": self.exports_dir
        }
    
    def validate_portable(self) -> List[str]:
        issues = []
        paths = self.get_portable_paths()
        for name, path in paths.items():
            if not path.exists():
                issues.append(f"Missing: {name} -> {path}")
        return issues
