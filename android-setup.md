# AI Coding Agent - Android Setup Guide

## Option 1: Termux (Recommended - Full Linux Environment)

### Prerequisites
- Android 7.0+ (API level 24+)
- At least 4GB RAM (8GB recommended)
- 10GB free storage

### Installation Steps

1. **Install Termux:**
   - Download from F-Droid: https://f-droid.org/en/packages/com.termux/
   - Or from Play Store (if available)

2. **Open Termux and run:**
   ```bash
   pkg update -y && pkg upgrade -y
   pkg install -y python python-dev git curl wget
   pip install requests
   ```

3. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

4. **Download the agent:**
   ```bash
   cd ~
   mkdir ai-coding-agent && cd ai-coding-agent
   mkdir -p agent workspace logs models
   ```

5. **Transfer files from Windows:**
   - Copy the `agent` folder contents to `~/ai-coding-agent/agent/`
   - Or download directly in Termux

6. **Run the agent:**
   ```bash
   python agent/beautiful-cli.py
   ```

## Option 2: Web Interface (Easiest)

1. **Start the agent on your computer:**
   ```bash
   python agent/cross-platform-launcher.py --web
   ```

2. **Find your computer's IP address**

3. **On Android, open Chrome/Firefox:**
   ```
   http://YOUR_IP:8080
   ```

4. **Add to home screen:**
   - Chrome: Menu → "Add to Home screen"
   - Firefox: Menu → "Install"

5. **Use like a native app:**
   - Full screen
   - Works offline
   - Touch optimized

## Option 3: PWA (Progressive Web App)

The web interface is a full PWA:
- Installable on Android home screen
- Works offline
- No Play Store needed
- Auto-updates

## Performance Tips for Android

1. **Use lightweight models:**
   - `deepseek-coder:1.3b` (776 MB) - Fast
   - `qwen2.5-coder:latest` (4.7 GB) - Better quality

2. **Close other apps** for more RAM

3. **Use cooling** if device gets hot

4. **Keep device plugged in** for long sessions

## Termux Auto-Start

To start Ollama automatically in Termux:

1. Edit `~/.bashrc`:
   ```bash
   echo 'ollama serve &' >> ~/.bashrc
   ```

2. Or create a service:
   ```bash
   termux-wake-lock
   ollama serve &
   ```

## Troubleshooting

### Ollama not starting
```bash
# Check if installed
ollama --version

# Reinstall if needed
curl -fsSL https://ollama.ai/install.sh | sh
```

### Out of memory
- Use smaller models: `deepseek-coder:1.3b`
- Close other apps
- Reduce threads in config

### Network issues
- Ensure phone and computer are on same WiFi
- Check firewall allows port 8080
- Try `http://localhost:8080` on same device

## No Root Required

Everything works without root access:
- Termux runs in user space
- Web interface needs no installation
- PWA works in any browser
