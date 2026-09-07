
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
