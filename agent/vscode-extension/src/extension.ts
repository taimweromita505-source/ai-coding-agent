import * as vscode from 'vscode';

let statusBar: vscode.StatusBarItem;
let chatPanel: vscode.WebviewPanel | undefined;
let treeDataProvider: AgentTreeDataProvider;

export function activate(context: vscode.ExtensionContext) {
    statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(robot) AI Agent';
    statusBar.tooltip = 'AI Coding Agent - Click to open chat';
    statusBar.command = 'aiAgent.chat';
    statusBar.show();

    treeDataProvider = new AgentTreeDataProvider();
    const treeView = vscode.window.createTreeView('aiAgent.chatView', {
        treeDataProvider: treeDataProvider
    });

    context.subscriptions.push(
        vscode.commands.registerCommand('aiAgent.start', () => {
            vscode.window.showInformationMessage('AI Coding Agent: Starting...');
            statusBar.text = '$(sync~spin) AI Agent';
        }),
        vscode.commands.registerCommand('aiAgent.chat', () => {
            openChatPanel(context.extensionUri);
        }),
        vscode.commands.registerCommand('aiAgent.explain', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const selection = editor.selection;
                const text = editor.document.getText(selection);
                if (text) {
                    explainCode(text, editor.document.languageId);
                } else {
                    vscode.window.showWarningMessage('Select code to explain');
                }
            }
        }),
        vscode.commands.registerCommand('aiAgent.runAgentic', async () => {
            const task = await vscode.window.showInputBox({ 
                prompt: 'Describe the task for agentic execution',
                placeHolder: 'Build a simple Python calculator...'
            });
            if (task) {
                vscode.window.showInformationMessage(`Agentic task: ${task}`);
            }
        }),
        vscode.window.registerTreeDataProvider('aiAgent.chatView', treeDataProvider),
        statusBar,
        treeView
    );

    treeDataProvider.refresh();
}

function openChatPanel(extensionUri: vscode.Uri) {
    if (chatPanel) {
        chatPanel.reveal();
        return;
    }

    chatPanel = vscode.window.createWebviewPanel(
        'aiAgent.chat',
        'AI Agent Chat',
        vscode.ViewColumn.Beside,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    chatPanel.webview.html = getChatHtml(extensionUri);

    chatPanel.onDidDispose(() => {
        chatPanel = undefined;
    });

    chatPanel.webview.onDidReceiveMessage(async message => {
        if (message.command === 'chat') {
            const response = await sendToAgent(message.text);
            chatPanel?.webview.postMessage({ command: 'response', text: response });
        }
    });
}

async function sendToAgent(text: string): Promise<string> {
    const config = vscode.workspace.getConfiguration('aiAgent');
    const ollamaUrl = config.get<string>('ollamaUrl', 'http://localhost:11434');
    
    try {
        const response = await fetch(`${ollamaUrl}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: config.get('primaryModel', 'gpt-oss:20b'),
                prompt: text,
                stream: false
            })
        });
        const data = await response.json();
        return data.response || 'No response';
    } catch (error) {
        return `Error: ${error}`;
    }
}

async function explainCode(code: string, language: string) {
    const prompt = `Explain this ${language} code:\n\`\`\`${language}\n${code}\n\`\`\``;
    const response = await sendToAgent(prompt);
    vscode.window.showInformationMessage(response);
}

function getChatHtml(extensionUri: vscode.Uri): string {
    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: var(--vscode-font-family); padding: 10px; }
        .chat { display: flex; flex-direction: column; gap: 8px; }
        .user { text-align: right; color: var(--vscode-terminal-ansiBlue); }
        .ai { text-align: left; color: var(--vscode-terminal-ansiGreen); }
        .input { display: flex; gap: 8px; }
        input { flex: 1; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); padding: 6px; }
        button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 6px 12px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat" id="chat"></div>
    <div class="input">
        <input id="msg" placeholder="Ask AI Agent..." onkeydown="if(event.key==='Enter') send()">
        <button onclick="send()">Send</button>
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        function send() {
            const input = document.getElementById('msg');
            const text = input.value.trim();
            if (!text) return;
            append('user', text);
            input.value = '';
            vscode.postMessage({ command: 'chat', text });
        }
        window.addEventListener('message', event => {
            if (event.data.command === 'response') {
                append('ai', event.data.text);
            }
        });
        function append(role, text) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = role;
            div.textContent = text;
            chat.appendChild(div);
        }
    </script>
</body>
</html>`;
}

class AgentTreeDataProvider implements vscode.TreeDataProvider<AgentTreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<AgentTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: AgentTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: AgentTreeItem): Thenable<AgentTreeItem[]> {
        if (!element) {
            return Promise.resolve([
                new AgentTreeItem('AI Agent Ready', vscode.TreeItemCollapsibleState.None),
                new AgentTreeItem('Models: gpt-oss:20b, qwen2.5-coder, deepseek-coder', vscode.TreeItemCollapsibleState.None)
            ]);
        }
        return Promise.resolve([]);
    }
}

class AgentTreeItem extends vscode.TreeItem {
    constructor(label: string, collapsibleState: vscode.TreeItemCollapsibleState) {
        super(label, collapsibleState);
        this.tooltip = label;
        this.contextValue = 'agentItem';
    }
}

export function deactivate() {
    if (statusBar) {
        statusBar.dispose();
    }
    if (chatPanel) {
        chatPanel.dispose();
    }
}
