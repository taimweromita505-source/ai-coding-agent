# AI Coding Agent - Claude Plugin

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
- Default model: `gpt-oss:20b`
- Ollama URL: `http://localhost:11434`
- Workspace: `E:\AI-Coding-Agent\workspace`

## Models

Download models to: `E:\AI-Coding-Agent\models`

Current models:
- Primary: gpt-oss:20b
- Fallback: qwen2.5-coder:latest
- Fast: deepseek-coder:1.3b

## Requirements

- Python 3.8+
- Ollama installed
- Models downloaded locally
