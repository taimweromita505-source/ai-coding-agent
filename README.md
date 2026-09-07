# UNLIMITED AI CODING AGENT - Universal Edition

## Works on: Windows, macOS, Linux, Android, iPhone

## Quick Start

### Desktop (Windows/macOS/Linux)
```bash
# Setup
python setup.py

# Run
START.bat          # Windows
./start.sh         # macOS/Linux
```

### Android
1. Install **Termux** from F-Droid
2. Open Termux and run:
   ```bash
   pkg update -y && pkg upgrade -y
   pkg install -y python python-dev git curl wget
   curl -fsSL https://ollama.ai/install.sh | sh
   ```
3. Copy the `ai-coding-agent` folder to your device
4. Run:
   ```bash
   cd ~/ai-coding-agent
   python agent/beautiful-cli.py
   ```

### iPhone/iPad
1. Start the web interface on your computer:
   ```bash
   python agent/mobile-web.py
   ```
2. Find your computer's IP: `python agent/network-access.py`
3. On iPhone, open Safari and go to `http://YOUR_IP:8080`
4. Tap Share → "Add to Home Screen"
5. Use like a native app

## Auto-Start

### Windows
```bash
python agent/cross-platform-launcher.py --install-autostart
```

### macOS
```bash
python3 agent/cross-platform-launcher.py --install-autostart
```

### Linux
```bash
python3 agent/cross-platform-launcher.py --install-autostart
```

### Android (Termux)
Add to `~/.bashrc`:
```bash
echo 'ollama serve &' >> ~/.bashrc
```

### iPhone
- Use PWA auto-launch (iOS 16.4+)
- Or use Shortcuts app to automate

## Access Methods

### 1. Desktop CLI
- Beautiful terminal interface
- Full keyboard support
- Syntax highlighting

### 2. Web Interface
- Mobile-friendly responsive design
- PWA support (add to home screen)
- Works on any device with browser

### 3. Mobile Web
- Touch-optimized UI
- Quick action buttons
- Offline support

## Mobile Features

- **PWA**: Install on home screen, works offline
- **Responsive**: Adapts to any screen size
- **Touch-friendly**: Large buttons, easy input
- **Quick actions**: One-tap common tasks
- **Offline mode**: Works without internet (after first load)

## Directory Structure

```
AI-Coding-Agent/
├── agent/
│   ├── beautiful-cli.py         # Desktop CLI
│   ├── mobile-web.py            # Mobile web interface
│   ├── cross-platform-launcher.py # Universal launcher
│   ├── network-access.py        # Network helper
│   ├── os-utils.py              # OS detection
│   ├── unlimited-agent.py       # Core agent
│   ├── config.json              # Configuration
│   └── manifest.json            # PWA manifest
├── workspace/                   # Generated files
├── logs/                       # Logs
├── models/                     # Ollama models
├── setup.py                    # Universal setup
├── universal-launcher.bat      # Windows launcher
├── start.sh                    # macOS/Linux launcher
├── android-setup.sh            # Android setup
├── ios-setup.md                # iOS instructions
└── README.md                   # This file
```

## Commands

All platforms support:
- `help` - Show help
- `clear` - Clear screen
- `history` - Show history
- `models` - List models
- `switch <model>` - Switch model
- `files` - List files
- `read <file>` - Read file
- `save <file> ```content``` - Save file
- `execute ```language\ncode``` - Execute code
- `command: <cmd>` - Run command
- `profile` - System info
- `exit` - Exit

## Models

Download models:
```bash
# Windows
$env:OLLAMA_MODELS = "E:\AI-Coding-Agent\models"
ollama pull codellama:7b

# macOS/Linux
export OLLAMA_MODELS="./models"
ollama pull codellama:7b

# Android (Termux)
export OLLAMA_MODELS="$HOME/ai-coding-agent/models"
ollama pull codellama:7b
```

## Network Access

To access from other devices:

1. Start web interface:
   ```bash
   python agent/mobile-web.py
   ```

2. Get your IP:
   ```bash
   python agent/network-access.py
   ```

3. Access from any device:
   ```
   http://YOUR_IP:8080
   ```

## PWA Installation

### Android (Chrome)
1. Open `http://YOUR_IP:8080`
2. Tap menu (3 dots)
3. "Add to Home Screen"
4. Launch from home screen

### iPhone (Safari)
1. Open `http://YOUR_IP:8080`
2. Tap Share button
3. "Add to Home Screen"
4. Launch from home screen

## No Restrictions

- No credit limits
- No usage caps
- No rate limits
- Full system access
- Unlimited requests
- Works offline

## System Requirements

### Desktop
- **OS**: Windows 10+, macOS 10.14+, Linux
- **Python**: 3.8+
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB+ for models

### Android
- **OS**: Android 7.0+
- **RAM**: 8GB recommended
- **Storage**: 10GB+ free
- **Termux**: Required

### iPhone/iPad
- **iOS**: 14.0+
- **Browser**: Safari or Chrome
- **Network**: Same WiFi as host computer

## Troubleshooting

### Can't connect from mobile
- Ensure same WiFi network
- Check firewall allows port 8080
- Try `http://localhost:8080` on host

### Ollama not starting
- Install from https://ollama.ai/download
- Check if port 11434 is available

### Models too large
- Use `deepseek-coder:1.3b` for mobile
- Store models on external storage (Android)

## Support

- Desktop: Full support
- Android: Termux support
- iOS: Web/PWA support only
