import { expect, test } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import path from "node:path";

const TEST_API_URL = process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999";
const FLAG_OFF_URL = process.env.PLAYWRIGHT_FLAG_OFF_URL;
const FLAG_ON_URL = process.env.PLAYWRIGHT_FLAG_ON_URL;
const FLAG_OFF_PORT = Number(process.env.PLAYWRIGHT_FLAG_OFF_PORT || 4310);
const FLAG_ON_PORT = Number(process.env.PLAYWRIGHT_FLAG_ON_PORT || 4311);

const legacyRoutes = [
  "/dashboard",
  "/dashboard/repos",
  "/dashboard/skills",
  "/dashboard/agent-prs",
  "/dashboard/review",
  "/dashboard/agent-scorecard",
  "/dashboard/ai-readiness",
  "/dashboard/connect",
  "/dashboard/settings",
  "/dashboard/my-code-today",
  "/dashboard/leaderboard",
  "/dashboard/analytics",
  "/dashboard/eval",
  "/dashboard/heatmap",
  "/dashboard/intelligence",
  "/dashboard/skillql",
  "/dashboard/eval/gaps",
  "/dashboard/debt",
  "/dashboard/knowledge-risk",
  "/dashboard/red-flags",
  "/dashboard/eval/ab-tests",
  "/dashboard/registry",
  "/dashboard/sessions",
  "/dashboard/digest",
  "/dashboard/autopilot",
  "/dashboard/sources",
  "/dashboard/sla",
  "/dashboard/half-life",
  "/dashboard/registry/dependency-graph",
  "/dashboard/teams",
  "/dashboard/audit",
];

const legacySidebarItems = [
  "Overview",
  "My Code Today",
  "PR Inbox",
  "Leaderboard",
  "Skills",
  "Registry",
  "Repos",
  "Agent Scorecard",
  "Agent Performance",
  "Heatmap",
  "Intelligence",
  "AI Readiness",
  "SkillQL",
  "Skill Gaps",
  "Skill Debt",
  "Knowledge Risk",
  "Red Flags",
  "A/B Tests",
  "Code Review",
  "Sessions",
  "Digest",
  "Autopilot",
  "Sources",
  "Coverage SLA",
  "Half-life",
  "Dependency Graph",
  "Connect Agent",
  "Teams",
  "Audit",
  "Settings",
];

const v8Surfaces = [
  { label: "Activity", path: "/activity", heading: "Activity", placeholder: false },
  { label: "Policy", path: "/policy", heading: "Agent Governance Rules", placeholder: false },
  { label: "Audit", path: "/audit", heading: "Audit", placeholder: false },
  { label: "Skills", path: "/skills", heading: "Skills", placeholder: false },
  { label: "Insights", path: "/insights", heading: "Insights", placeholder: false },
  { label: "Settings", path: "/settings", heading: "Settings", placeholder: false },
];

const v8SkillsTabs = [
  { label: "Registry", path: "/skills/registry" },
  { label: "Score", path: "/skills/score" },
  { label: "Drift", path: "/skills/drift" },
  { label: "Provenance", path: "/skills/provenance" },
  { label: "SkillQL", path: "/skills/skillql" },
  { label: "Repos", path: "/skills/repos" },
];

test.setTimeout(120000);
test.use({ viewport: { width: 1440, height: 1000 } });
test.describe.configure({ mode: "serial" });

type ManagedServer = {
  name: string;
  process: ChildProcess;
};

let flagOffBaseUrl = FLAG_OFF_URL || "";
let flagOnBaseUrl = FLAG_ON_URL || "";
const managedServers: ManagedServer[] = [];

function dashboardCwd(): string {
  return process.cwd().endsWith(`${path.sep}apps${path.sep}dashboard`)
    ? process.cwd()
    : path.join(process.cwd(), "apps", "dashboard");
}

async function waitForReady(url: string, server: ManagedServer): Promise<void> {
  const deadline = Date.now() + 60_000;
  let lastError = "";

  while (Date.now() < deadline) {
    if (server.process.exitCode !== null) {
      throw new Error(`${server.name} exited before it was ready. ${lastError}`);
    }

    try {
      const response = await fetch(url);
      if (response.status < 500) return;
      lastError = `Last status: ${response.status}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  throw new Error(`${server.name} did not become ready at ${url}. ${lastError}`);
}

async function startDashboardServer(name: string, port: number, iaV8Default: "true" | "false"): Promise<string> {
  const url = `http://127.0.0.1:${port}`;
  const server = spawn("npx", ["next", "start", "--hostname", "127.0.0.1", "--port", String(port)], {
    cwd: dashboardCwd(),
    env: {
      ...process.env,
      API_URL: TEST_API_URL,
      NEXT_PUBLIC_API_URL: TEST_API_URL,
      IA_V8_DEFAULT: iaV8Default,
      NEXT_TELEMETRY_DISABLED: "1",
      PORT: String(port),
    },
    stdio: "ignore",
  });

  const managedServer = { name, process: server };
  managedServers.push(managedServer);

  await waitForReady(url, managedServer);
  return url;
}

test.beforeAll(async () => {
  if (!flagOffBaseUrl) {
    flagOffBaseUrl = await startDashboardServer("ia-v8-off", FLAG_OFF_PORT, "false");
  }
  if (!flagOnBaseUrl) {
    flagOnBaseUrl = await startDashboardServer("ia-v8-on", FLAG_ON_PORT, "true");
  }
});

test.afterAll(async () => {
  await Promise.all(
    managedServers.map(
      (server) =>
        new Promise<void>((resolve) => {
          if (server.process.exitCode !== null) {
            resolve();
            return;
          }
          server.process.once("exit", () => resolve());
          server.process.kill("SIGTERM");
          setTimeout(() => {
            if (server.process.exitCode === null) server.process.kill("SIGKILL");
            resolve();
          }, 2_000).unref();
        }),
    ),
  );
});

test("legacy sidebar renders and v7 routes are valid", async ({ page }) => {
  for (const route of legacyRoutes) {
    const response = await page.goto(`${flagOffBaseUrl}${route}`, { timeout: 15000, waitUntil: "commit" });
    expect(response?.status(), route).toBeLessThan(400);
  }

  await page.goto(`${flagOffBaseUrl}/dashboard`, { waitUntil: "domcontentloaded" });
  await expect(page.locator("aside")).toBeVisible();
  for (const label of legacySidebarItems) {
    await expect(page.locator("aside").getByText(label, { exact: true })).toBeVisible();
  }
  await page.screenshot({ path: "test-results/ia-v8-flag-off-v7-sidebar.png", fullPage: true });
});

test("v8 sidebar and placeholders render", async ({ page }) => {
  for (const surface of v8Surfaces) {
    const response = await page.goto(`${flagOnBaseUrl}${surface.path}`, { waitUntil: "domcontentloaded" });
    expect(response?.status(), surface.path).toBeLessThan(400);
    await expect(page.locator("aside").getByText(surface.label, { exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: surface.heading })).toBeVisible();
    if (surface.placeholder) {
      await expect(page.getByText("Coming soon — v8 surface")).toBeVisible();
    }
    await page.screenshot({ path: `test-results/ia-v8-${surface.label.toLowerCase()}.png`, fullPage: true });
  }

  const links = page.locator("aside nav a");
  await expect(links).toHaveCount(6);
});

test("v8 skills tabs render as routes", async ({ page }) => {
  const landing = await page.goto(`${flagOnBaseUrl}/skills`, { waitUntil: "domcontentloaded" });
  expect(landing?.status(), "/skills").toBeLessThan(400);
  await expect(page).toHaveURL(/\/skills\/registry$/);

  for (const tab of v8SkillsTabs) {
    const response = await page.goto(`${flagOnBaseUrl}${tab.path}`, { waitUntil: "domcontentloaded" });
    expect(response?.status(), tab.path).toBeLessThan(400);
    await expect(page.getByRole("heading", { name: "Skills" })).toBeVisible();
    await expect(page.getByRole("link", { name: tab.label })).toBeVisible();
    await page.screenshot({ path: `test-results/ia-v8-skills-${tab.label.toLowerCase()}.png`, fullPage: true });
  }
});

test("missing tenant override falls back to env default", async ({ page }) => {
  const response = await page.goto(`${flagOnBaseUrl}/activity`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);
  await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();
});

test("settings rbac create, binding, admin audit nav, and notifications config render", async ({ page }) => {
  await page.goto(`${flagOnBaseUrl}/settings/rbac`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();
  await expect(page.getByRole("link", { name: /RBAC/i })).toBeVisible();

  await page.getByLabel("Role name").fill("Payments approver");
  await page.getByRole("button", { name: "Create role" }).click();
  await expect(page.getByText("Payments approver")).toBeVisible();

  await page.getByLabel("Principal").fill("payments-reviewer@example.com");
  await page.getByLabel("Scope expression").fill("repo:payments/*");
  await page.getByRole("button", { name: "Add binding" }).click();
  await expect(page.getByText("payments-reviewer@example.com")).toBeVisible();
  await expect(page.getByText("repo:payments/*", { exact: true })).toBeVisible();

  await page.getByRole("link", { name: /Admin audit/i }).click();
  await expect(page).toHaveURL(/\/settings\/admin-audit/);
  await expect(page.getByText("No admin audit events yet.")).toBeVisible();

  await page.getByRole("link", { name: /Notifications/i }).click();
  await expect(page).toHaveURL(/\/settings\/notifications/);
  await page.getByLabel("Title").fill("Weekly Governance Digest");
  await page.getByLabel("Recipients").fill("platform@example.com");
  await page.getByRole("button", { name: "Save config" }).click();
  await expect(page.getByText(/Notification config/)).toBeVisible();
});
