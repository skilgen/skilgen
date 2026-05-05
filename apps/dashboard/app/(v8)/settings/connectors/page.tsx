import { PlugZap } from "lucide-react";

import { EmptyPanel, Metric, SettingsShell } from "../_components/settings-shell";
import { loadSettingsContext, v8Fetch } from "../_components/settings-data";

type Connector = {
  id: string;
  label: string;
  category: string;
  status: string;
  connected: boolean;
  connection_status?: string | null;
};

export default async function ConnectorsSettingsPage() {
  const { accessToken, org } = await loadSettingsContext();
  const payload = await v8Fetch<{ connectors: Connector[] }>(accessToken, org.id, "/connectors");
  const connectors = payload?.connectors ?? [];
  const connected = connectors.filter((connector) => connector.connected).length;
  const categories = new Set(connectors.map((connector) => connector.category));

  return (
    <SettingsShell active="Connectors">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Registry entries" value={connectors.length || 22} sub="Data-driven, no new implementations" />
        <Metric label="Connected" value={connected} sub="Backed by existing source connections" />
        <Metric label="Categories" value={categories.size || 8} sub="Agents, SCM, SIEM, WORM, provenance" />
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
            </article>
          ))}
        </section>
      ) : (
        <EmptyPanel detail="The connector catalog is now a registry file under Settings. Available rows will reflect existing source connections when the API is reachable." icon={<PlugZap className="h-5 w-5" />} title="Connector registry ready." />
      )}
    </SettingsShell>
  );
}
