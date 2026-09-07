#!/usr/bin/env python3
"""
Plugin setup for AI Coding Agent
Auto-detects OS and installs as a global CLI plugin / IDE integration
"""

import os
import sys
import json
import shutil
import platform
import subprocess
import tempfile
import zipfile
from pathlib import Path

INSTALL_DIR = Path(__file__).parent.absolute()
AGENT_DIR = INSTALL_DIR / "agent"
sys.path.insert(0, str(AGENT_DIR))

from os_utils import OSDetector


def detect_os():
    os_type = OSDetector.get_os()
    python = OSDetector.get_python_executable()
    home = OSDetector.get_home()
    print(f"[+] OS detected: {os_type}")
    print(f"[+] Python: {python}")
    print(f"[+] Home: {home}")
    return os_type, python, home


def ensure_dirs():
    for d in [INSTALL_DIR / "workspace", INSTALL_DIR / "logs", INSTALL_DIR / "models"]:
        d.mkdir(exist_ok=True)


def install_cli_plugin(os_type, python, home):
    plugin_name = "ai-agent"
    launcher = AGENT_DIR / "unlimited-agent.py"

    if os_type == "windows":
        scripts_dir = home / "AppData" / "Local" / "Programs" / "Python" / "Scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        bat_path = scripts_dir / f"{plugin_name}.bat"
        bat = f'''@echo off
"{python}" "{launcher}" %*
'''
        bat_path.write_text(bat)
        print(f"[+] CLI plugin installed: {bat_path}")

        user_path = home / "AppData" / "Local" / "Microsoft" / "WindowsApps"
        if user_path.exists():
            exe_path = user_path / f"{plugin_name}.exe"
            exe = f'''@echo off
"{python}" "{launcher}" %*
'''
            exe_path.write_text(exe)
            print(f"[+] CLI plugin installed: {exe_path}")

    else:
        bin_dir = home / ".local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)

        script_path = bin_dir / plugin_name
        script = f'''#!/bin/sh
"{python}" "{launcher}" "$@"
'''
        script_path.write_text(script)
        script_path.chmod(0o755)
        print(f"[+] CLI plugin installed: {script_path}")

        shell_rc = None
        if os_type == "macos":
            shell_rc = home / ".zshrc"
            if not shell_rc.exists():
                shell_rc = home / ".bash_profile"
        else:
            shell_rc = home / ".bashrc"
            if not shell_rc.exists():
                shell_rc = home / ".bash_profile"

        if shell_rc and shell_rc.exists():
            export_line = f'\nexport PATH="{bin_dir}:$PATH"\n'
            content = shell_rc.read_text()
            if str(bin_dir) not in content:
                shell_rc.write_text(content + export_line)
                print(f"[+] PATH updated in: {shell_rc}")

    return plugin_name


def install_vscode_extension(os_type, python):
    ext_dir = AGENT_DIR / "vscode-extension"
    ext_dir.mkdir(exist_ok=True)

    package_json = {
        "name": "ai-coding-agent",
        "displayName": "AI Coding Agent",
        "description": "Unlimited AI Coding Agent - No Restrictions",
        "version": "3.0.0",
        "publisher": "ai-coding-agent",
        "engines": {"vscode": "^1.75.0"},
        "categories": ["Machine Learning", "Snippets", "Other"],
        "activationEvents": ["onCommand:aiAgent.start", "onView:aiAgent.sidebar"],
        "main": "./out/extension.js",
        "contributes": {
            "commands": [
                {"command": "aiAgent.start", "title": "Start AI Agent"},
                {"command": "aiAgent.chat", "title": "AI Agent Chat"},
                {"command": "aiAgent.explain", "title": "Explain Code"}
            ],
            "viewsContainers": {
                "activitybar": [
                    {
                        "id": "aiAgent.sidebar",
                        "title": "AI Agent",
                        "icon": "resources/icon.svg"
                    }
                ]
            },
            "views": {
                "aiAgent.sidebar": [
                    {"id": "aiAgent.chatView", "name": "Chat"}
                ]
            }
        },
        "scripts": {
            "vscode:prepublish": "python -m tsc -p ./",
            "compile": "python -m tsc -watch -p ./"
        }
    }

    (ext_dir / "package.json").write_text(json.dumps(package_json, indent=2))

    tsconfig = {
        "compilerOptions": {
            "module": "commonjs",
            "outDir": "out",
            "lib": ["es2020"],
            "sourceMap": True,
            "rootDir": "src",
            "strict": True
        },
        "include": ["src"]
    }
    (ext_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

    src_dir = ext_dir / "src"
    src_dir.mkdir(exist_ok=True)

    extension_js = '''
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Coding Agent is now active');

    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(robot) AI Agent';
    statusBar.tooltip = 'Click to open AI Agent';
    statusBar.command = 'aiAgent.chat';
    statusBar.show();

    const provider = vscode.TreeDataProvider.create((item) => {
        return vscode.window.createTreeItem('AI Agent Ready', vscode.TreeItemCollapsibleState.None);
    });

    const treeView = vscode.window.createTreeView('aiAgent.chatView', {
        treeDataProvider: provider,
        showCollapseAll: false
    });

    context.subscriptions.push(
        vscode.commands.registerCommand('aiAgent.start', () => {
            vscode.window.showInformationMessage('AI Coding Agent: Starting...');
        }),
        vscode.commands.registerCommand('aiAgent.chat', async () => {
            const prompt = await vscode.window.showInputBox({ prompt: 'Ask AI Agent' });
            if (prompt) {
                vscode.window.showInformationMessage(`AI: ${prompt}`);
            }
        }),
        vscode.window.registerTreeDataProvider('aiAgent.chatView', provider),
        statusBar,
        treeView
    );
}

export function deactivate() {
    console.log('AI Coding Agent deactivated');
}
'''
    (src_dir / "extension.ts").write_text(extension_js)

    vscodeignore = ext_dir / ".vscodeignore"
    vscodeignore.write_text("vscode-extension/**\n.gitignore\n*.log\nnode_modules\nout/test/**\n")

    print(f"[+] VS Code extension scaffolded: {ext_dir}")
    print(f"    To package: cd {ext_dir} && vsce package")


def install_claude_plugin(os_type, python):
    plugin_dir = AGENT_DIR / "claude-plugin"
    plugin_dir.mkdir(exist_ok=True)

    plugin_json = {
        "name": "ai-coding-agent",
        "version": "3.0.0",
        "description": "Unlimited AI Coding Agent plugin",
        "author": {
            "name": "AI Coding Agent",
            "email": "agent@example.com"
        },
        "homepage": "https://github.com/ai-coding-agent",
        "repository": {
            "type": "git",
            "url": "https://github.com/ai-coding-agent/claude-plugin"
        },
        "license": "MIT",
        "keywords": ["ai", "coding", "agent", "claude"],
        "claude": {
            "api": {
                "endpoint": "http://localhost:11434/api/generate",
                "models": ["gpt-oss:20b", "qwen2.5-coder:latest", "deepseek-coder:1.3b"]
            },
            "permissions": {
                "filesystem": {"read": True, "write": True},
                "shell": {"execute": True},
                "network": {"outbound": True}
            }
        },
        "commands": [
            {
                "name": "ai-agent:chat",
                "description": "Chat with AI Coding Agent",
                "handler": "python unlimited-agent.py"
            },
            {
                "name": "ai-agent:web",
                "description": "Start web interface",
                "handler": "python unlimited-agent.py --web"
            },
            {
                "name": "ai-agent:setup",
                "description": "Run setup wizard",
                "handler": "python setup.py"
            }
        ],
        "activation": {
            "hooks": ["onCommand", "onFileSave", "onError"],
            "auto_start": True
        },
        "config": {
            "default_model": "gpt-oss:20b",
            "fallback_model": "qwen2.5-coder:latest",
            "fast_model": "deepseek-coder:1.3b",
            "ollama_url": "http://localhost:11434",
            "workspace": str(INSTALL_DIR / "workspace"),
            "models_dir": str(INSTALL_DIR / "models"),
            "max_iterations": 10,
            "temperature": 0.7
        }
    }

    (plugin_dir / "plugin.json").write_text(json.dumps(plugin_json, indent=2))

    readme = f'''# AI Coding Agent - Claude Plugin

Auto-generated plugin for Claude Code / compatible environments.

## Installation

1. Copy this folder to your plugins directory
2. Restart Claude Code
3. The agent will auto-start

## Commands

- `ai-agent:chat` - Open chat with AI agent
- `ai-agent:web` - Start web interface on port 8080
- `ai-agent:setup` - Run setup wizard

## Configuration

Edit `plugin.json` to change:
- Default model: `{plugin_json["config"]["default_model"]}`
- Ollama URL: `{plugin_json["config"]["ollama_url"]}`
- Workspace: `{plugin_json["config"]["workspace"]}`

## Models

Download models to: `{INSTALL_DIR / "models"}`

Current models:
- Primary: gpt-oss:20b
- Fallback: qwen2.5-coder:latest
- Fast: deepseek-coder:1.3b

## Requirements

- Python 3.8+
- Ollama installed
- Models downloaded locally
'''
    (plugin_dir / "README.md").write_text(readme)

    print(f"[+] Claude plugin scaffolded: {plugin_dir}")


def main():
    print("=" * 80)
    print("  AI CODING AGENT - PLUGIN AUTO-SETUP")
    print("=" * 80)

    ensure_dirs()
    os_type, python, home = detect_os()

    print("\n[1/3] Installing CLI plugin...")
    install_cli_plugin(os_type, python, home)

    print("\n[2/3] Scaffolding VS Code extension...")
    install_vscode_extension(os_type, python)

    print("\n[3/3] Scaffolding Claude plugin...")
    install_claude_plugin(os_type, python)

    print("\n" + "=" * 80)
    print("  PLUGIN SETUP COMPLETE")
    print("=" * 80)
    print(f"\nInstallation: {INSTALL_DIR}")
    print(f"Agent code: {AGENT_DIR}")
    print(f"\nNext steps:")
    print(f"  1. Restart your terminal or source shell config")
    print(f"  2. Run: ai-agent --help")
    print(f"  3. For VS Code: see {AGENT_DIR / 'vscode-extension'}")
    print(f"  4. For Claude: see {AGENT_DIR / 'claude-plugin'}")
    print(f"\nTo launch:")
    print(f"  python {AGENT_DIR / 'unlimited-agent.py'} --web")
    print(f"  python {AGENT_DIR / 'beautiful-cli.py'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
