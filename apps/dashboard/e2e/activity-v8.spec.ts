import { expect, test } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import path from "node:path";

const TEST_API_URL = process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999";
const FLAG_ON_URL = process.env.PLAYWRIGHT_FLAG_ON_URL;
const FLAG_OFF_URL = process.env.PLAYWRIGHT_FLAG_OFF_URL;
const FLAG_ON_PORT = Number(process.env.PLAYWRIGHT_ACTIVITY_FLAG_ON_PORT || 4321);
const FLAG_OFF_PORT = Number(process.env.PLAYWRIGHT_ACTIVITY_FLAG_OFF_PORT || 4322);

type ManagedServer = {
  name: string;
  process: ChildProcess;
};

let flagOnBaseUrl = FLAG_ON_URL || "";
let flagOffBaseUrl = FLAG_OFF_URL || "";
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
    if (server.process.exitCode !== null) throw new Error(`${server.name} exited before ready. ${lastError}`);
    try {
      const response = await fetch(url);
      if (response.status < 500) return;
      lastError = `status ${response.status}`;
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
  const managed = { name, process: server };
  managedServers.push(managed);
  await waitForReady(url, managed);
  return url;
}

test.setTimeout(120000);
test.describe.configure({ mode: "serial" });

test.beforeAll(async () => {
  if (!flagOnBaseUrl) flagOnBaseUrl = await startDashboardServer("activity-ia-v8-on", FLAG_ON_PORT, "true");
  if (!flagOffBaseUrl) flagOffBaseUrl = await startDashboardServer("activity-ia-v8-off", FLAG_OFF_PORT, "false");
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

test("activity tabs render with IA_V8 on", async ({ page }) => {
  for (const route of ["/activity/live-feed", "/activity/sessions", "/activity/replay", "/activity/heatmap"]) {
    const response = await page.goto(`${flagOnBaseUrl}${route}`, { waitUntil: "domcontentloaded" });
    expect(response?.status(), route).toBeLessThan(400);
    await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Activity tabs" })).toBeVisible();
  }
});

test("dashboard renders Activity with IA_V8 on and legacy overview with flag off", async ({ page }) => {
  await page.goto(`${flagOnBaseUrl}/dashboard`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();

  await page.goto(`${flagOffBaseUrl}/dashboard`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
});
