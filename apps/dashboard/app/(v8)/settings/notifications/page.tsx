import { Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";
import { NotificationsPanel } from "./notifications-panel";

const fallback = {
  title: "Weekly AI Readiness Digest",
  subject: "Your Weekly AI Readiness Report",
  frequency: "weekly",
  recipients: [],
  widgets: ["memory_score", "agent_loads", "active_repos", "top_skill", "skill_gaps", "roi_multiplier"],
  layout: { columns: 2 },
};

export default async function NotificationsSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const config = await v8Fetch<typeof fallback>(accessToken, org.id, "/notifications/digest") ?? fallback;

  return (
    <SettingsShell active="Notifications">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Frequency" value={config.frequency} sub="Existing digest scheduler" />
        <Metric label="Recipients" value={config.recipients.length} sub="Configured email targets" />
        <Metric label="Widgets" value={config.widgets.length} sub="Digest modules selected" />
      </div>
      <NotificationsPanel accessToken={accessToken} initial={config} orgId={org.id} />
    </SettingsShell>
  );
}
