import * as vscode from "vscode";

export interface Finding {
  file_path: string;
  line_number: number | null;
  severity: string;
  skill_name: string;
  message: string;
  suggestion?: string;
}

export interface CheckResult {
  violations: Finding[];
  warnings: Finding[];
  skills_checked: number;
  risk_tier: string;
}

export async function checkDiff(diff: string, apiUrl: string, repoId: string, apiKey: string): Promise<CheckResult> {
  const response = await fetch(`${apiUrl}/repos/${repoId}/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
    body: JSON.stringify({ diff }),
  });
  if (!response.ok) throw new Error(`Skillayer API error: ${response.status}`);
  return response.json() as Promise<CheckResult>;
}

export async function diffCurrentFile(filePath: string, content: string): Promise<string> {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  const displayPath = workspaceRoot && filePath.startsWith(workspaceRoot)
    ? filePath.slice(workspaceRoot.length + 1)
    : filePath;
  const lines = content.split("\n");
  const header = `--- a/${displayPath}\n+++ b/${displayPath}\n@@ -0,0 +1,${lines.length} @@\n`;
  return header + lines.map((line) => `+${line}`).join("\n");
}

export async function getStagedDiff(): Promise<string> {
  const { exec } = await import("child_process");
  const { promisify } = await import("util");
  const execAsync = promisify(exec);
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
  const { stdout } = await execAsync("git diff --cached", { cwd: workspaceRoot });
  return stdout;
}
