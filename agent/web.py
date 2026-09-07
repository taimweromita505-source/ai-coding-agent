#!/usr/bin/env python3
"""
Web Interface for Local AI Coding Agent
"""

import json
import os
import sys
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class AgentWebHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.agent = kwargs.pop('agent', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_index_html().encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                "ollama_running": self.agent.check_ollama() if self.agent else False,
                "models": self.agent.list_models() if self.agent else [],
                "workspace_files": [f.name for f in self.agent.workspace.glob("*")] if self.agent else []
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            prompt = data.get('prompt', '')
            language = data.get('language', 'python')
            
            if not prompt:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "No prompt provided"}')
                return
            
            code = self.agent.generate_code(prompt, language=language)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"code": code, "language": language}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_index_html(self):
        return """<!DOCTYPE html>
<html>
<head>
    <title>Local AI Coding Agent</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1e1e1e;
            color: #d4d4d4;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #252526;
            padding: 15px 20px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 18px; color: #569cd6; }
        .status { font-size: 12px; color: #4ec9b0; }
        .main {
            flex: 1;
            display: flex;
            padding: 20px;
            gap: 20px;
            overflow: hidden;
        }
        .panel {
            background: #252526;
            border-radius: 8px;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        .input-panel { flex: 1; }
        .output-panel { flex: 1; }
        .panel h2 {
            font-size: 14px;
            color: #569cd6;
            margin-bottom: 15px;
            text-transform: uppercase;
        }
        textarea {
            flex: 1;
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            color: #d4d4d4;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            resize: none;
        }
        .controls {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        select, button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { background: #1177bb; }
        select { background: #3e3e42; }
        .output-content {
            flex: 1;
            background: #1e1e1e;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            overflow: auto;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Local AI Coding Agent</h1>
        <div class="status" id="status">Checking...</div>
    </div>
    <div class="main">
        <div class="panel input-panel">
            <h2>Task</h2>
            <textarea id="prompt" placeholder="Describe what you want to code..."></textarea>
            <div class="controls">
                <select id="language">
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="rust">Rust</option>
                    <option value="go">Go</option>
                </select>
                <button onclick="generate()">Generate Code</button>
            </div>
        </div>
        <div class="panel output-panel">
            <h2>Generated Code</h2>
            <div class="output-content" id="output">Code will appear here...</div>
        </div>
    </div>
    <script>
        async function checkStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                document.getElementById('status').textContent = 
                    data.ollama_running ? '● Ollama Running' : '● Ollama Stopped';
            } catch (e) {
                document.getElementById('status').textContent = '● Error';
            }
        }
        async function generate() {
            const prompt = document.getElementById('prompt').value;
            const language = document.getElementById('language').value;
            const output = document.getElementById('output');
            
            if (!prompt.trim()) {
                output.textContent = 'Please enter a task.';
                return;
            }
            
            output.textContent = 'Generating...';
            
            try {
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt, language })
                });
                const data = await res.json();
                output.textContent = data.code || 'Error: ' + JSON.stringify(data);
            } catch (e) {
                output.textContent = 'Error: ' + e.message;
            }
        }
        checkStatus();
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>"""

def run_web_server(agent, port=8080):
    handler = lambda *args, **kwargs: AgentWebHandler(*args, agent=agent, **kwargs)
    server = HTTPServer(('0.0.0.0', port), handler)
    print(f"Web interface running at http://localhost:{port}")
    print(f"Network: http://<your-ip>:{port}")
    server.serve_forever()

if __name__ == "__main__":
    # Import agent module
    sys.path.insert(0, str(Path(__file__).parent))
    from agent import LocalAICodingAgent
    
    agent = LocalAICodingAgent()
    print("Starting web interface...")
    run_web_server(agent)
