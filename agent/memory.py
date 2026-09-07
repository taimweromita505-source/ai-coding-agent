#!/usr/bin/env python3
"""
Memory and auto-learning module for AI Coding Agent
Provides persistent memory, pattern learning, and context awareness
"""

import json
import os
import sys
import re
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Optional, Dict, List, Any


class MemoryStore:
    """Persistent memory storage with automatic pruning"""
    
    def __init__(self, install_dir: Path):
        self.memory_dir = install_dir / "logs" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.memory_dir / "history.json"
        self.learned_file = self.memory_dir / "learned.json"
        self.profile_file = self.memory_dir / "profile.json"
        self.cache_file = self.memory_dir / "cache.json"
        
        self.history: List[Dict] = self._load_json(self.history_file, [])
        self.learned: Dict[str, Any] = self._load_json(self.learned_file, {
            "commands": {},
            "languages": {},
            "files": {},
            "models": {},
            "patterns": [],
            "errors": [],
            "preferences": {}
        })
        self.profile: Dict[str, Any] = self._load_json(self.profile_file, {
            "total_sessions": 0,
            "total_interactions": 0,
            "total_code_executions": 0,
            "total_commands": 0,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "favorite_model": None,
            "favorite_language": None,
            "common_commands": [],
            "common_files": []
        })
        self._dirty = False
        self._flush_counter = 0
        self._flush_interval = 3
    
    def _load_json(self, path: Path, default):
        try:
            if path.exists():
                return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
        return default
    
    def _save_json(self, path: Path, data):
        self._dirty = True
    
    def flush(self):
        if not self._dirty:
            return
        try:
            self._write_json(self.history_file, self.history)
            self._write_json(self.learned_file, self.learned)
            self._write_json(self.profile_file, self.profile)
            self._dirty = False
            self._flush_counter = 0
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to flush memory: {e}\n")
    def maybe_flush(self):
        self._flush_counter += 1
        if self._flush_counter >= self._flush_interval:
            self._flush_counter = 0
            self.flush()
    
    def _write_json(self, path: Path, data):
        try:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to save memory to {path}: {e}\n")
    
    def add_interaction(self, user_input: str, ai_response: str, metadata: Optional[Dict] = None):
        """Record a conversation turn"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "ai": ai_response,
            "metadata": metadata or {}
        }
        self.history.append(entry)
        
        # Keep last 1000 interactions in memory
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self.profile["total_interactions"] += 1
        self.profile["last_seen"] = datetime.now().isoformat()
        
        self._save_json(self.history_file, self.history)
        self._save_json(self.profile_file, self.profile)
    
    def add_execution(self, lang: str, code: str, success: bool, output: str):
        """Record a code execution outcome"""
        self.profile["total_code_executions"] += 1
        
        # Learn language preference
        self.learned["languages"][lang] = self.learned["languages"].get(lang, {
            "count": 0, "success": 0, "failure": 0
        })
        self.learned["languages"][lang]["count"] += 1
        if success:
            self.learned["languages"][lang]["success"] += 1
        else:
            self.learned["languages"][lang]["failure"] += 1
        
        # Learn error patterns
        if not success:
            error_key = self._extract_error_pattern(output)
            if error_key:
                self.learned["errors"].append({
                    "timestamp": datetime.now().isoformat(),
                    "language": lang,
                    "pattern": error_key,
                    "output": output[:500]
                })
                # Keep only last 100 errors
                if len(self.learned["errors"]) > 100:
                    self.learned["errors"] = self.learned["errors"][-100:]
        
        self._save_json(self.learned_file, self.learned)
        self._save_json(self.profile_file, self.profile)
    
    def add_command(self, cmd: str, success: bool, output: str):
        """Record a shell command execution"""
        self.profile["total_commands"] += 1
        
        # Normalize command (remove arguments for learning)
        base_cmd = cmd.strip().split()[0] if cmd.strip() else ""
        if base_cmd:
            self.learned["commands"][base_cmd] = self.learned["commands"].get(base_cmd, {
                "count": 0, "success": 0, "failure": 0
            })
            self.learned["commands"][base_cmd]["count"] += 1
            if success:
                self.learned["commands"][base_cmd]["success"] += 1
            else:
                self.learned["commands"][base_cmd]["failure"] += 1
        
        self._save_json(self.learned_file, self.learned)
        self._save_json(self.profile_file, self.profile)
    
    def add_file_operation(self, operation: str, filename: str, success: bool):
        """Record file operations"""
        self.learned["files"][filename] = self.learned["files"].get(filename, {
            "count": 0, "read": 0, "write": 0, "success": 0
        })
        self.learned["files"][filename]["count"] += 1
        self.learned["files"][filename][operation] = self.learned["files"][filename].get(operation, 0) + 1
        if success:
            self.learned["files"][filename]["success"] += 1
        
        self._save_json(self.learned_file, self.learned)
    
    def record_model_usage(self, model: str, task_type: str, success: bool, latency: float):
        """Record model performance for different task types"""
        if model not in self.learned["models"]:
            self.learned["models"][model] = {}
        
        if task_type not in self.learned["models"][model]:
            self.learned["models"][model][task_type] = {
                "count": 0, "success": 0, "total_latency": 0.0
            }
        
        entry = self.learned["models"][model][task_type]
        entry["count"] += 1
        entry["total_latency"] += latency
        if success:
            entry["success"] += 1
        
        self._save_json(self.learned_file, self.learned)
    
    def start_session(self):
        """Mark a new session start"""
        self.profile["total_sessions"] += 1
        self._save_json(self.profile_file, self.profile)
    
    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.history[-limit:] if self.history else []
    
    def get_learned_context(self) -> str:
        """Generate a context string from learned patterns for system prompt injection"""
        parts = []
        
        # Favorite model
        if self.profile.get("favorite_model"):
            parts.append(f"User often prefers model: {self.profile['favorite_model']}")
        
        # Favorite language
        if self.profile.get("favorite_language"):
            parts.append(f"User frequently works with: {self.profile['favorite_language']}")
        
        # Top languages
        if self.learned.get("languages"):
            top_langs = sorted(self.learned["languages"].items(), 
                             key=lambda x: x[1]["count"], reverse=True)[:3]
            langs = ", ".join([l[0] for l in top_langs])
            parts.append(f"Common languages: {langs}")
        
        # Top commands
        if self.learned.get("commands"):
            top_cmds = sorted(self.learned["commands"].items(),
                            key=lambda x: x[1]["count"], reverse=True)[:5]
            cmds = ", ".join([c[0] for c in top_cmds])
            parts.append(f"Frequent commands: {cmds}")
        
        # Common files
        if self.learned.get("files"):
            top_files = sorted(self.learned["files"].items(),
                             key=lambda x: x[1]["count"], reverse=True)[:5]
            files = ", ".join([f[0] for f in top_files])
            parts.append(f"Common files: {files}")
        
        # Known error patterns to avoid
        if self.learned.get("errors"):
            recent_errors = [e["pattern"] for e in self.learned["errors"][-5:]]
            if recent_errors:
                parts.append(f"Recent errors to watch for: {', '.join(recent_errors)}")
        
        # Model performance hints
        if self.learned.get("models"):
            best_models = []
            for model, tasks in self.learned["models"].items():
                for task, stats in tasks.items():
                    if stats["count"] >= 3 and stats["success"] / stats["count"] > 0.8:
                        avg_latency = stats["total_latency"] / stats["count"]
                        best_models.append((model, task, avg_latency))
            
            if best_models:
                best_models.sort(key=lambda x: x[2])
                parts.append(f"Fast reliable models: {', '.join([m[0] for m in best_models[:3]])}")
        
        return "\n".join(parts) if parts else ""
    
    def get_summary(self) -> str:
        """Get a summary of learned knowledge"""
        lines = [
            f"Total sessions: {self.profile['total_sessions']}",
            f"Total interactions: {self.profile['total_interactions']}",
            f"Code executions: {self.profile['total_code_executions']}",
            f"Commands run: {self.profile['total_commands']}",
            f"Languages used: {len(self.learned.get('languages', {}))}",
            f"Files accessed: {len(self.learned.get('files', {}))}",
        ]
        return "\n".join(lines)
    
    def _extract_error_pattern(self, output: str) -> Optional[str]:
        """Extract a simplified error pattern for learning"""
        patterns = [
            r"(SyntaxError: .+?)(?:\n|$)",
            r"(NameError: .+?)(?:\n|$)",
            r"(TypeError: .+?)(?:\n|$)",
            r"(ImportError: .+?)(?:\n|$)",
            r"(ModuleNotFoundError: .+?)(?:\n|$)",
            r"(FileNotFoundError: .+?)(?:\n|$)",
            r"(PermissionError: .+?)(?:\n|$)",
            r"(IndexError: .+?)(?:\n|$)",
            r"(KeyError: .+?)(?:\n|$)",
            r"(AttributeError: .+?)(?:\n|$)",
            r"(ValueError: .+?)(?:\n|$)",
            r"(RuntimeError: .+?)(?:\n|$)",
            r"(error: .+?)(?:\n|$)",
            r"(fatal: .+?)(?:\n|$)",
            r"(exception: .+?)(?:\n|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:200]
        
        # Generic fallback
        lines = output.strip().split('\n')
        if lines:
            return lines[-1][:200]
        return None
    
    def export_knowledge(self) -> Dict[str, Any]:
        """Export all learned knowledge for inspection"""
        return {
            "profile": self.profile,
            "learned": self.learned,
            "recent_history": self.get_recent_history(20)
        }
    
    def clear_memory(self):
        """Clear all memory (use with caution)"""
        self.history = []
        self.learned = {
            "commands": {},
            "languages": {},
            "files": {},
            "models": {},
            "patterns": [],
            "errors": [],
            "preferences": {}
        }
        self.profile = {
            "total_sessions": 0,
            "total_interactions": 0,
            "total_code_executions": 0,
            "total_commands": 0,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "favorite_model": None,
            "favorite_language": None,
            "common_commands": [],
            "common_files": []
        }
        
        for f in [self.history_file, self.learned_file, self.profile_file]:
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass
    
    def get_suggestions(self) -> List[str]:
        """Generate proactive suggestions based on learned patterns"""
        suggestions = []
        
        # Suggest frequently used files
        if self.learned.get("files"):
            top_files = sorted(self.learned["files"].items(),
                             key=lambda x: x[1]["count"], reverse=True)[:3]
            for fname, stats in top_files:
                if stats["count"] > 5:
                    suggestions.append(f"Read {fname} (frequently accessed)")
        
        # Suggest successful commands
        if self.learned.get("commands"):
            successful_cmds = [(cmd, stats) for cmd, stats in self.learned["commands"].items()
                             if stats["success"] / stats["count"] > 0.8 and stats["count"] > 3]
            if successful_cmds:
                suggestions.append(f"Try running: {successful_cmds[0][0]}")
        
        # Suggest language-specific tasks
        if self.learned.get("languages"):
            top_lang = max(self.learned["languages"].items(), 
                          key=lambda x: x[1]["success"], default=None)
            if top_lang and top_lang[1]["success"] > 5:
                suggestions.append(f"Write more {top_lang[0]} code (high success rate)")
        
        return suggestions[:3]


class AutoLearner:
    """Active learning component that improves agent behavior over time"""
    
    def __init__(self, memory: MemoryStore):
        self.memory = memory
    
    def build_system_prompt(self, base_prompt: str) -> str:
        """Enhance system prompt with learned context"""
        learned_context = self.memory.get_learned_context()
        
        if not learned_context:
            return base_prompt
        
        learning_section = f"""
=== LEARNED CONTEXT ===
{learned_context}
=== END LEARNED CONTEXT ===

Use this context to provide personalized, faster responses.
"""
        return base_prompt + "\n\n" + learning_section
    
    def get_recommended_model(self, task_type: str = "general") -> str:
        """Recommend the best model for a task based on past performance"""
        models = self.memory.learned.get("models", {})
        
        best_model = None
        best_score = -1
        
        for model, tasks in models.items():
            if task_type in tasks:
                stats = tasks[task_type]
                if stats["count"] >= 2:
                    success_rate = stats["success"] / stats["count"]
                    avg_latency = stats["total_latency"] / stats["count"]
                    # Score: prioritize success rate, then lower latency
                    score = success_rate * 100 - avg_latency * 0.1
                    if score > best_score:
                        best_score = score
                        best_model = model
        
        return best_model
    
    def get_fast_fallback(self) -> str:
        """Get the fastest reliable fallback model"""
        models = self.memory.learned.get("models", {})
        
        fast_model = None
        min_latency = float('inf')
        
        for model, tasks in models.items():
            for task, stats in tasks.items():
                if stats["count"] >= 2 and stats["success"] / stats["count"] > 0.7:
                    avg_latency = stats["total_latency"] / stats["count"]
                    if avg_latency < min_latency:
                        min_latency = avg_latency
                        fast_model = model
        
        return fast_model
    
    def compress_history(self, history: List[Dict]) -> str:
        """Compress old history into a summary to save context"""
        if not history:
            return ""
        
        # Group by date
        by_date = defaultdict(list)
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                date_key = dt.strftime("%Y-%m-%d")
                by_date[date_key].append(entry)
            except Exception:
                continue
        
        # Create summary
        summary_parts = []
        for date in sorted(by_date.keys())[-5:]:  # Last 5 days
            entries = by_date[date]
            user_msgs = [e["user"][:50] for e in entries if e.get("user")]
            summary_parts.append(f"{date}: {len(entries)} interactions")
            if user_msgs:
                summary_parts.append(f"  Topics: {', '.join(user_msgs[:3])}")
        
        return "\n".join(summary_parts) if summary_parts else ""


class ContextManager:
    """Manages conversation context for the agent"""
    
    def __init__(self, memory: MemoryStore, max_context_length: int = 4000):
        self.memory = memory
        self.max_context_length = max_context_length
        self.current_context: List[Dict] = []
    
    def add_turn(self, user_input: str, ai_response: str):
        """Add a turn to current context"""
        self.current_context.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        self.current_context.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim context if too long
        self._trim_context()
    
    def _trim_context(self):
        """Trim context to stay within limits"""
        total_chars = sum(len(str(c.get("content", ""))) for c in self.current_context)
        
        while total_chars > self.max_context_length and len(self.current_context) > 2:
            # Remove oldest non-system turn
            if self.current_context[0]["role"] != "system":
                removed = self.current_context.pop(0)
                total_chars -= len(str(removed.get("content", "")))
            else:
                break
    
    def get_context_prompt(self) -> str:
        """Build context prompt from current conversation"""
        if not self.current_context:
            return ""
        
        parts = []
        for turn in self.current_context[-10:]:  # Last 10 turns
            role = turn["role"].capitalize()
            content = turn.get("content", "")[:500]
            parts.append(f"{role}: {content}")
        
        return "\n".join(parts)
    
    def clear_context(self):
        """Clear current context"""
        self.current_context = []
