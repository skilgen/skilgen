import { expect, test } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import path from "node:path";

const TEST_API_URL = process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999";
const INSIGHTS_URL = process.env.PLAYWRIGHT_INSIGHTS_URL;
const INSIGHTS_PORT = Number(process.env.PLAYWRIGHT_INSIGHTS_PORT || 4312);

const tabs = [
  { path: "/insights", label: "Fleet KPIs" },
  { path: "/insights/fleet-kpis", label: "Fleet KPIs" },
  { path: "/insights/risky-agents", label: "Risky agents" },
  { path: "/insights/risky-repos", label: "Risky repos" },
  { path: "/insights/coverage-sla", label: "Coverage SLA" },
];

test.setTimeout(120000);
test.use({ viewport: { width: 1440, height: 1000 } });
test.describe.configure({ mode: "serial" });

let baseUrl = INSIGHTS_URL || "";
let managedServer: ChildProcess | null = null;

function dashboardCwd(): string {
  return process.cwd().endsWith(`${path.sep}apps${path.sep}dashboard`)
    ? process.cwd()
    : path.join(process.cwd(), "apps", "dashboard");
}

async function waitForReady(url: string): Promise<void> {
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    if (managedServer?.exitCode !== null) {
      throw new Error("Insights dashboard server exited before it was ready.");
    }
    try {
      const response = await fetch(url);
      if (response.status < 500) return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }
  throw new Error(`Insights dashboard server did not become ready at ${url}.`);
}

test.beforeAll(async () => {
  if (baseUrl) return;
  baseUrl = `http://127.0.0.1:${INSIGHTS_PORT}`;
  managedServer = spawn("npx", ["next", "start", "--hostname", "127.0.0.1", "--port", String(INSIGHTS_PORT)], {
    cwd: dashboardCwd(),
    env: {
      ...process.env,
      API_URL: TEST_API_URL,
      NEXT_PUBLIC_API_URL: TEST_API_URL,
      IA_V8_DEFAULT: "true",
      NEXT_TELEMETRY_DISABLED: "1",
      PORT: String(INSIGHTS_PORT),
    },
    stdio: "ignore",
  });
  await waitForReady(baseUrl);
});

test.afterAll(async () => {
  if (!managedServer || managedServer.exitCode !== null) return;
  await new Promise<void>((resolve) => {
    managedServer?.once("exit", () => resolve());
    managedServer?.kill("SIGTERM");
    setTimeout(() => {
      if (managedServer?.exitCode === null) managedServer.kill("SIGKILL");
      resolve();
    }, 2_000).unref();
  });
});

for (const tab of tabs) {
  test(`Insights tab renders: ${tab.path}`, async ({ page }) => {
    const response = await page.goto(`${baseUrl}${tab.path}`, { waitUntil: "domcontentloaded" });
    expect(response?.status(), tab.path).toBeLessThan(400);
    await expect(page.getByRole("heading", { name: "Insights" })).toBeVisible();
    await expect(page.getByRole("link", { name: tab.label })).toBeVisible();
    await page.screenshot({ path: `test-results/insights-v8-${tab.label.toLowerCase().replaceAll(" ", "-")}.png`, fullPage: true });
  });
}
