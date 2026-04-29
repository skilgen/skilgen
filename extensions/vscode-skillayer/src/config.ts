import * as vscode from "vscode";

export function getConfig() {
  const cfg = vscode.workspace.getConfiguration("skillayer");
  return {
    apiKey: cfg.get<string>("apiKey") || "",
    repoId: cfg.get<string>("repoId") || "",
    apiUrl: cfg.get<string>("apiUrl") || "https://api.skillayer.com",
    checkOnSave: cfg.get<boolean>("checkOnSave") || false,
    violationSeverity: cfg.get<string>("severity.violations") || "Error",
    warningSeverity: cfg.get<string>("severity.warnings") || "Warning",
  };
}

export function isConfigured(): boolean {
  const { apiKey, repoId } = getConfig();
  return apiKey.length > 0 && repoId.length > 0;
}
