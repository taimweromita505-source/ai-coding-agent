# AI Coding Agent - Portable Edition

**Fully portable AI coding agent that works from a flash drive. Online when needed, offline when not.**

## Flash Drive Setup

1. Copy the entire `E:\AI-Coding-Agent` folder to your flash drive
2. Ensure the folder structure is preserved:
   ```
   AI-Coding-Agent/
   ├── agent/
   │   ├── unlimited-agent.py
   │   ├── beautiful-cli.py
   │   ├── memory.py
   │   ├── api_keys.py
   │   ├── settings_manager.py
   │   ├── config.json
   │   ├── vscode-extension/
   │   └── ...
   ├── workspace/
   ├── models/
   ├── logs/
   ├── setup.py
   ├── plugin-setup.py
   ├── START.bat
   └── README-PORTABLE.md
   ```

## Quick Start

### Windows
- Double-click `START.bat` or run:
  ```cmd
  python agent\unlimited-agent.py --web
  ```
- Open browser to `http://localhost:8080`

### macOS / Linux
```bash
python3 agent/unlimited-agent.py --web
```

## Portable Modes

The agent automatically detects connectivity:

- **ONLINE** - Internet available. Uses OpenRouter/OmniRoute if configured, falls back to local Ollama.
- **OFFLINE-LOCAL** - No internet, but Ollama running with local models.
- **OFFLINE** - No internet, no Ollama. Agent still works for file editing and command execution.

## Model Management

### Pre-download for offline use
When you have internet, download models to the flash drive:

```bash
ollama pull gpt-oss:20b
ollama pull qwen2.5-coder:latest
ollama pull deepseek-coder:1.3b
```

Models are stored in `./models/` and move with the flash drive.

### Auto-download from web UI
In the IDE:
1. Open the **Settings** panel
2. Click **Download Models**
3. Missing models are downloaded automatically

## Settings Sync

Export/import all settings, memory, and workspace:

```bash
# Export
python agent/unlimited-agent.py --stdin
> export settings

# Import
> import settings exports/ai-agent-settings-YYYYMMDD_HHMMSS.zip
```

## API Keys

Configure keys for online providers:

```bash
# In CLI
> set openrouter sk-or-v1-...
> set omniroute sk-or-v1-...
> api keys

# In web UI
Settings panel → API Keys section
```

Keys are stored in `logs/api_keys.json` and move with the flash drive.

## VS Code Extension

Package the extension:
```bash
cd agent/vscode-extension
npm install
vsce package
```

Install in VS Code:
```
code --install-extension ai-coding-agent-3.2.0.vsix
```

## Portable Tips

- **Python required**: Ensure Python 3.8+ is installed on the host machine
- **Ollama optional**: For full offline AI, install Ollama on the host
- **No hardcoded paths**: All paths are relative to the agent folder
- **Cross-platform**: Works on Windows, macOS, Linux from the same flash drive

## Troubleshooting

**"Ollama not running"**
- Install Ollama from https://ollama.ai/download
- Run `ollama serve` before starting the agent

**"Models not found"**
- Download models while online: `ollama pull <model>`
- Or use online providers via API keys

**"Portability issues"**
- Run `validate portable` in the agent to check paths

## License

MIT - Developed by Taimwe.Romita
