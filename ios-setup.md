# AI Coding Agent - iOS Setup Guide

## Option 1: Web App (Recommended - No App Store Needed)

1. **Start the agent on your computer:**
   ```bash
   python agent/cross-platform-launcher.py --web
   ```
   Or use the web interface:
   ```bash
   python agent/mobile-web.py
   ```

2. **Ensure both devices are on the same WiFi network**

3. **Find your computer's IP address:**
   - Windows: `ipconfig` in terminal
   - macOS/Linux: `ifconfig` in terminal
   - Look for IPv4 address (e.g., 192.168.1.100)

4. **On iPhone/iPad:**
   - Open Safari
   - Go to: `http://YOUR_IP:8080`
   - Tap the Share button
   - Select "Add to Home Screen"
   - The app will appear on your home screen

5. **Use the app:**
   - Launch from home screen
   - Works offline after first load
   - Full PWA support

## Option 2: Pythonista (Advanced)

If you have Pythonista on iOS:

1. Install Pythonista from App Store
2. Install StaSh (Shell) from Pythonista
3. In StaSh, run:
   ```bash
   pip install requests
   ```
4. Create the agent files in Pythonista
5. Note: Ollama won't run on iOS, so you'll need a remote Ollama server

## Option 3: Remote Server

Run the agent on a server/computer and access from iOS:

1. Start the web interface:
   ```bash
   python agent/mobile-web.py
   ```

2. Access from any browser on iOS:
   ```
   http://your-server-ip:8080
   ```

3. For remote access over internet:
   - Use ngrok: `ngrok http 8080`
   - Or set up port forwarding on your router

## Features on iOS

- Full PWA support
- Add to home screen
- Works offline
- Touch-optimized interface
- Responsive design
- No app store needed

## Security Notes

- The web interface binds to all interfaces (0.0.0.0)
- Ensure your firewall allows port 8080
- Use HTTPS for remote access
- Don't expose to public internet without authentication
