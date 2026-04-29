import * as vscode from "vscode";
import { getConfig, isConfigured } from "./config";
import { checkDiff, diffCurrentFile, getStagedDiff } from "./check";
import { findingsToDiagnostics } from "./diagnostics";

const collection = vscode.languages.createDiagnosticCollection("skillayer");
let statusBar: vscode.StatusBarItem;

function toSeverity(value: string): vscode.DiagnosticSeverity {
  if (value === "Error") return vscode.DiagnosticSeverity.Error;
  if (value === "Information") return vscode.DiagnosticSeverity.Information;
  return vscode.DiagnosticSeverity.Warning;
}

export function activate(context: vscode.ExtensionContext) {
  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  statusBar.text = "$(shield) Skillayer";
  statusBar.tooltip = "Click to run skill check";
  statusBar.command = "skillayer.checkFile";
  statusBar.show();
  context.subscriptions.push(statusBar, collection);

  context.subscriptions.push(
    vscode.commands.registerCommand("skillayer.checkFile", checkCurrentFile),
    vscode.commands.registerCommand("skillayer.checkStaged", checkStaged),
    vscode.commands.registerCommand("skillayer.clearDiagnostics", () => collection.clear()),
  );

  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(async (document) => {
      if (getConfig().checkOnSave) await checkDocument(document);
    }),
  );
}

async function checkDocument(document: vscode.TextDocument) {
  if (!isConfigured()) {
    vscode.window.showWarningMessage("Skillayer: Set skillayer.apiKey and skillayer.repoId in settings.");
    return;
  }
  const { apiKey, repoId, apiUrl, violationSeverity, warningSeverity } = getConfig();
  statusBar.text = "$(sync~spin) Skillayer checking...";
  try {
    const diff = await diffCurrentFile(document.uri.fsPath, document.getText());
    const result = await checkDiff(diff, apiUrl, repoId, apiKey);
    const diagnostics = [
      ...findingsToDiagnostics(result.violations, toSeverity(violationSeverity), document),
      ...findingsToDiagnostics(result.warnings, toSeverity(warningSeverity), document),
    ];
    collection.set(document.uri, diagnostics);
    statusBar.text = diagnostics.length > 0 ? `$(warning) Skillayer: ${diagnostics.length} issue${diagnostics.length > 1 ? "s" : ""}` : "$(check) Skillayer: clean";
  } catch (error) {
    statusBar.text = "$(error) Skillayer error";
    vscode.window.showErrorMessage(`Skillayer check failed: ${error}`);
  }
}

async function checkCurrentFile() {
  const editor = vscode.window.activeTextEditor;
  if (!editor) return;
  await checkDocument(editor.document);
}

async function checkStaged() {
  if (!isConfigured()) {
    vscode.window.showWarningMessage("Skillayer: Set skillayer.apiKey and skillayer.repoId in settings.");
    return;
  }
  const { apiKey, repoId, apiUrl } = getConfig();
  statusBar.text = "$(sync~spin) Skillayer checking staged...";
  try {
    const diff = await getStagedDiff();
    if (!diff.trim()) {
      vscode.window.showInformationMessage("Skillayer: No staged changes to check.");
      statusBar.text = "$(shield) Skillayer";
      return;
    }
    const result = await checkDiff(diff, apiUrl, repoId, apiKey);
    const total = result.violations.length + result.warnings.length;
    statusBar.text = total > 0 ? `$(warning) Skillayer: ${total} issue${total > 1 ? "s" : ""}` : "$(check) Skillayer: staged clean";
    vscode.window.showInformationMessage(
      `Skillayer staged check: ${result.violations.length} violations, ${result.warnings.length} warnings - risk tier: ${result.risk_tier}`,
    );
  } catch (error) {
    statusBar.text = "$(error) Skillayer error";
    vscode.window.showErrorMessage(`Skillayer staged check failed: ${error}`);
  }
}

export function deactivate() {
  collection.dispose();
}
