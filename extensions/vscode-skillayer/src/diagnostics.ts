import * as vscode from "vscode";
import type { Finding } from "./check";

export function findingsToDiagnostics(
  findings: Finding[],
  severityLevel: vscode.DiagnosticSeverity,
  document: vscode.TextDocument,
): vscode.Diagnostic[] {
  return findings
    .filter((finding) => finding.file_path && document.uri.fsPath.endsWith(finding.file_path))
    .map((finding) => {
      const line = Math.max(0, (finding.line_number ?? 1) - 1);
      const range = document.lineAt(Math.min(line, document.lineCount - 1)).range;
      const message = `[${finding.skill_name}] ${finding.message}${finding.suggestion ? ` - ${finding.suggestion}` : ""}`;
      const diagnostic = new vscode.Diagnostic(range, message, severityLevel);
      diagnostic.source = "Skillayer";
      diagnostic.code = finding.skill_name;
      return diagnostic;
    });
}
