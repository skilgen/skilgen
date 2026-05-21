import { Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";
import { RiskPolicyPanel } from "./risk-policy-panel";

type AgentRiskPolicy = {
  critical_threshold: number;
  high_threshold: number;
  medium_threshold: number;
  critical_requires_danger_signal: boolean;
  full_access_score_floor: number;
  dangerous_command_score_floor: number;
  sensitive_path_score_floor: number;
  unknown_external_score_floor: number;
  unapproved_mcp_score_floor: number;
  dangerous_command_patterns: string[];
  sensitive_path_patterns: string[];
  approved_external_domains: string[];
  approved_mcp_tools: string[];
  updated_at?: string | null;
};

const fallback: AgentRiskPolicy = {
  critical_threshold: 90,
  high_threshold: 70,
  medium_threshold: 35,
  critical_requires_danger_signal: true,
  full_access_score_floor: 75,
  dangerous_command_score_floor: 90,
  sensitive_path_score_floor: 90,
  unknown_external_score_floor: 90,
  unapproved_mcp_score_floor: 90,
  dangerous_command_patterns: ["rm -rf", "sudo ", "git push --force", "terraform destroy", "cat .env"],
  sensitive_path_patterns: ["**/.env", "**/*secret*", "**/auth/**", "**/billing/**", "**/.github/workflows/**"],
  approved_external_domains: ["api.github.com", "api.openai.com", "api.anthropic.com"],
  approved_mcp_tools: ["js", "mcp__codex_apps__github", "mcp__computer_use__", "mcp__node_repl__"],
};

export default async function RiskPolicySettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const policy = (await v8Fetch<AgentRiskPolicy>(accessToken, org.id, "/risk-policy")) ?? fallback;

  return (
    <SettingsShell active="Risk policy">
      <div className="grid gap-4 md:grid-cols-4">
        <Metric label="Critical" value={policy.critical_threshold} sub="Requires danger signal by default" />
        <Metric label="High" value={policy.high_threshold} sub="Review queue threshold" />
        <Metric label="Full access" value={policy.full_access_score_floor} sub="Granted access floor" />
        <Metric label="Signals" value={4} sub="Commands, paths, APIs, MCP" />
      </div>

      <RiskPolicyPanel accessToken={accessToken} initial={policy} orgId={org.id} />
    </SettingsShell>
  );
}
