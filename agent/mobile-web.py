#!/usr/bin/env python3
"""
Mobile-friendly web interface for AI Coding Agent
Works on Android, iPhone, and desktop browsers
"""

import json
import os
import sys
import subprocess
import requests
import time
import re
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

INSTALL_DIR = Path(__file__).parent.parent.absolute()
AGENT_DIR = Path(__file__).parent.absolute()
WORKSPACE = INSTALL_DIR / "workspace"
LOGS = INSTALL_DIR / "logs"
OLLAMA_URL = "http://localhost:11434"

WORKSPACE.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)

class MobileWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.agent = kwargs.pop('agent', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_mobile_html().encode())
        elif self.path == '/manifest.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            with open(AGENT_DIR / 'manifest.json', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/sw.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(self.get_service_worker().encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                "ollama_running": self.agent.check_ollama() if self.agent else False,
                "models": self.agent.list_models() if self.agent else [],
                "current_model": self.agent.current_model if self.agent else None,
                "workspace_files": self.agent.list_files() if self.agent else []
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length))
            prompt = data.get('message', '')
            model = data.get('model', '')
            
            if prompt:
                if model:
                    self.agent.current_model = model
                response = self.agent.process(prompt)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"response": response}).encode())
            else:
                self.send_error(400)
        else:
            self.send_error(404)
    
    def get_mobile_html(self):
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0a0a0a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>AI Coding Agent</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0a0a0a;
            color: #fff;
            height: 100vh;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 15px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 18px;
            background: linear-gradient(45deg, #00ff00, #00ffff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .status {
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 12px;
            background: #333;
        }
        .status.online { background: #0a0; color: #fff; }
        .status.offline { background: #a00; color: #fff; }
        .main {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 60px);
        }
        .output {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            font-size: 14px;
            line-height: 1.6;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            border-left: 3px solid #4fc3f7;
        }
        .ai-message {
            background: linear-gradient(135deg, #1a3a1a 0%, #2d5a2d 100%);
            border-left: 3px solid #00ff00;
        }
        .message-header {
            font-size: 11px;
            opacity: 0.7;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .message-content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .code-block {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 6px;
            padding: 10px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
        }
        .input-area {
            background: #1a1a1a;
            border-top: 1px solid #333;
            padding: 10px;
        }
        .input-row {
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
        }
        select, button, input {
            background: #2a2a2a;
            color: #fff;
            border: 1px solid #444;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
        }
        button {
            background: linear-gradient(135deg, #00aa00 0%, #00cc00 100%);
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
        }
        button:active { opacity: 0.8; }
        textarea {
            flex: 1;
            background: #2a2a2a;
            border: 1px solid #444;
            border-radius: 6px;
            color: #fff;
            padding: 12px;
            font-size: 14px;
            resize: none;
            font-family: inherit;
        }
        textarea:focus { outline: none; border-color: #00ff00; }
        .quick-actions {
            display: flex;
            gap: 6px;
            overflow-x: auto;
            padding-bottom: 8px;
        }
        .quick-btn {
            background: #333;
            border: 1px solid #444;
            color: #fff;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            cursor: pointer;
            white-space: nowrap;
        }
        .quick-btn:active { background: #444; }
        .typing-indicator {
            display: none;
            padding: 10px;
            color: #888;
            font-style: italic;
        }
        .typing-indicator.active { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Agent</h1>
        <div class="status" id="status">Connecting...</div>
    </div>
    <div class="main">
        <div class="output" id="output">
            <div class="message ai-message">
                <div class="message-header">AI Agent</div>
                <div class="message-content">Welcome! I'm your unlimited AI coding agent. No restrictions, full access. How can I help you today?</div>
            </div>
        </div>
        <div class="typing-indicator" id="typing">AI is thinking...</div>
        <div class="input-area">
            <div class="quick-actions">
                <button class="quick-btn" onclick="quickAction('Write a Python web scraper')">Scraper</button>
                <button class="quick-btn" onclick="quickAction('Create a REST API')">API</button>
                <button class="quick-btn" onclick="quickAction('Write a React component')">React</button>
                <button class="quick-btn" onclick="quickAction('Debug this code')">Debug</button>
                <button class="quick-btn" onclick="quickAction('Explain this code')">Explain</button>
            </div>
            <div class="input-row">
                <select id="model">
                    <option value="">Auto</option>
                </select>
                <button onclick="sendMessage()">Send</button>
            </div>
            <textarea id="input" placeholder="Ask me anything...&#10;&#10;Examples:&#10;- Write a Python web server&#10;- Create a React app&#10;- Debug my code&#10;- Explain async/await" rows="3"></textarea>
        </div>
    </div>
    <script>
        const output = document.getElementById('output');
        const input = document.getElementById('input');
        const status = document.getElementById('status');
        const typing = document.getElementById('typing');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user-message' : 'ai-message');
            div.innerHTML = '<div class=\"message-header\">' + (isUser ? 'You' : 'AI Agent') + '</div>' +
                           '<div class=\"message-content\">' + escapeHtml(text) + '</div>';
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function checkStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                status.textContent = data.ollama_running ? '● Online' : '● Offline';
                status.className = 'status ' + (data.ollama_running ? 'online' : 'offline');
                
                const modelSelect = document.getElementById('model');
                modelSelect.innerHTML = '<option value="">Auto</option>' +
                    data.models.map(m => '<option value=\"' + m + '\">' + m + '</option>').join('');
            } catch (e) {
                status.textContent = '● Error';
                status.className = 'status offline';
            }
        }
        
        async function sendMessage() {
            const message = input.value.trim();
            const model = document.getElementById('model').value;
            
            if (!message) return;
            
            addMessage(message, true);
            input.value = '';
            typing.classList.add('active');
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message, model })
                });
                const data = await res.json();
                addMessage(data.response || 'Error: ' + JSON.stringify(data), false);
            } catch (e) {
                addMessage('Error: ' + e.message, false);
            } finally {
                typing.classList.remove('active');
            }
        }
        
        function quickAction(text) {
            input.value = text;
            sendMessage();
        }
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        checkStatus();
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>"""
    
    def get_service_worker(self):
        return """const CACHE_NAME = 'ai-agent-v1';
const urlsToCache = ['/', '/index.html'];

self.addEventListener('install', (e) => {
    e.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache)));
});

self.addEventListener('fetch', (e) => {
    e.respondWith(caches.match(e.request).then((response) => response || fetch(e.request)));
});"""

def run_mobile_server(agent, port=8080):
    handler = lambda *args, **kwargs: MobileWebHandler(*args, agent=agent, **kwargs)
    server = HTTPServer(('0.0.0.0', port), handler)
    print(f"Mobile web interface: http://localhost:{port}")
    print(f"Network access: http://<your-ip>:{port}")
    print(f"PWA enabled - add to home screen")
    server.serve_forever()

if __name__ == "__main__":
    sys.path.insert(0, str(AGENT_DIR))
    from unlimited_agent import Agent
    
    agent = Agent()
    print("Starting mobile web interface...")
    run_mobile_server(agent)
