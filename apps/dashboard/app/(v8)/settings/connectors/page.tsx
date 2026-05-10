import { PlugZap } from "lucide-react";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type Connector = {
  id: string;
  label: string;
  category: string;
  status: string;
  connected: boolean;
  description?: string | null;
  capabilities?: string[];
  connection_status?: string | null;
};

export default async function ConnectorsSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const payload = await v8Fetch<{ connectors: Connector[] }>(accessToken, org.id, "/connectors");
  const connectors = payload?.connectors ?? [];
  const connected = connectors.filter((connector) => connector.connected).length;
  const categories = new Set(connectors.map((connector) => connector.category));
  const apiUnavailable = payload === null;

  return (
    <SettingsShell active="Connectors">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Registry entries" value={connectors.length} sub="Data-driven connector catalog" />
        <Metric label="Connected" value={connected} sub="Backed by existing source connections" />
        <Metric label="Categories" value={categories.size} sub="Compliance, agents, SCM, SIEM, WORM" />
      </div>

      {connectors.length ? (
        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {connectors.map((connector) => (
            <article className="rounded-[8px] border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-4" key={connector.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-[color:var(--text-primary)]">{connector.label}</h2>
                  <p className="mt-1 text-[12px] text-[color:var(--text-tertiary)]">{connector.category}</p>
                </div>
                <span className={connector.connected ? "rounded-full bg-[color:var(--accent-green)]/15 px-2 py-1 text-[12px] font-semibold text-[color:var(--accent-green)]" : "rounded-full bg-[color:var(--bg-base)] px-2 py-1 text-[12px] font-semibold text-[color:var(--text-tertiary)]"}>
                  {connector.connected ? "Connected" : connector.status}
                </span>
              </div>
              {connector.description ? (
                <p className="mt-3 text-[13px] leading-6 text-[color:var(--text-secondary)]">{connector.description}</p>
              ) : null}
              {connector.capabilities?.length ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {connector.capabilities.map((capability) => (
                    <span className="rounded-full border border-[color:var(--bg-border)] px-2 py-1 text-[11px] font-semibold text-[color:var(--text-tertiary)]" key={capability}>
                      {capability}
                    </span>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </section>
      ) : apiUnavailable ? (
        <EmptyPanel detail="The connector API did not respond for this session. Refresh after sign-in, or use Analyze repo while the connector registry reloads." icon={<PlugZap className="h-5 w-5" />} title="Connector registry unavailable." />
      ) : (
        <EmptyPanel detail="No connectors are configured yet. Connect GitHub or another source to populate live connection status." icon={<PlugZap className="h-5 w-5" />} title="No connectors connected yet." />
      )}
    </SettingsShell>
  );
}
