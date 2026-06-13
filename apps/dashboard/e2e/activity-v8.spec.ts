import { expect, test } from "@playwright/test";
import { execFileSync, spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import path from "node:path";

const TEST_API_URL = process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999";
const FLAG_ON_URL = process.env.PLAYWRIGHT_FLAG_ON_URL;
const FLAG_OFF_URL = process.env.PLAYWRIGHT_FLAG_OFF_URL;
const FLAG_ON_PORT = process.env.PLAYWRIGHT_ACTIVITY_FLAG_ON_PORT ? Number(process.env.PLAYWRIGHT_ACTIVITY_FLAG_ON_PORT) : null;
const FLAG_OFF_PORT = process.env.PLAYWRIGHT_ACTIVITY_FLAG_OFF_PORT ? Number(process.env.PLAYWRIGHT_ACTIVITY_FLAG_OFF_PORT) : null;

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

function nextCliPath(): string {
  return path.join(dashboardCwd(), "..", "..", "node_modules", "next", "dist", "bin", "next");
}

function preferredNodePath(): string {
  if (process.env.PLAYWRIGHT_NODE_BIN) return process.env.PLAYWRIGHT_NODE_BIN;
  if (process.env.NODE_BIN) return process.env.NODE_BIN;

  const npmWrapper = path.join(process.cwd(), ".tools", "npm", "bin", "npm");
  if (fs.existsSync(npmWrapper)) {
    try {
      const selected = execFileSync(npmWrapper, ["exec", "--", "node", "-p", "process.execPath"], {
        cwd: process.cwd(),
        encoding: "utf8",
        env: {
          ...process.env,
          NEXT_TELEMETRY_DISABLED: "1",
        },
      }).trim();
      if (selected) return selected;
    } catch {
      // Fall back to the current runtime when the repo-local npm wrapper is unavailable.
    }
  }

  return process.execPath;
}

function spawnEnv(extra: NodeJS.ProcessEnv = {}): NodeJS.ProcessEnv {
  const nodeBin = preferredNodePath();
  return {
    ...process.env,
    ...extra,
    PATH: `${path.dirname(nodeBin)}${path.delimiter}${process.env.PATH || ""}`,
    NEXT_TELEMETRY_DISABLED: "1",
  };
}

async function ensureDashboardBuilt(): Promise<void> {
  const buildIdPath = path.join(dashboardCwd(), ".next", "BUILD_ID");
  if (fs.existsSync(buildIdPath)) return;

  await new Promise<void>((resolve, reject) => {
    const build = spawn("bash", ["scripts/next-build.sh"], {
      cwd: dashboardCwd(),
      env: spawnEnv(),
      stdio: "ignore",
    });
    build.once("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`next build failed with exit code ${code ?? "unknown"}`));
    });
    build.once("error", reject);
  });
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

async function reservePort(preferred?: number | null): Promise<number> {
  await new Promise<void>((resolve, reject) => {
    const probe = net.createServer();
    probe.once("error", reject);
    probe.listen(preferred ?? 0, "127.0.0.1", () => {
      probe.close((error) => {
        if (error) reject(error);
        else resolve();
      });
    });
  });

  return await new Promise<number>((resolve, reject) => {
    const server = net.createServer();
    server.once("error", reject);
    server.listen(preferred ?? 0, "127.0.0.1", () => {
      const address = server.address();
      if (!address || typeof address === "string") {
        server.close(() => reject(new Error("Failed to resolve a dashboard test port")));
        return;
      }
      const { port } = address;
      server.close((error) => {
        if (error) reject(error);
        else resolve(port);
      });
    });
  });
}

async function startDashboardServer(name: string, port: number, iaV8Default: "true" | "false", readinessPath: string): Promise<string> {
  await ensureDashboardBuilt();
  const url = `http://127.0.0.1:${port}`;
  const server = spawn(preferredNodePath(), ["--preserve-symlinks", "--preserve-symlinks-main", nextCliPath(), "start", "--hostname", "127.0.0.1", "--port", String(port)], {
    cwd: dashboardCwd(),
    env: spawnEnv({
      API_URL: TEST_API_URL,
      NEXT_PUBLIC_API_URL: TEST_API_URL,
      IA_V8_DEFAULT: iaV8Default,
      PORT: String(port),
    }),
    stdio: "ignore",
  });
  const managed = { name, process: server };
  managedServers.push(managed);
  await waitForReady(`${url}${readinessPath}`, managed);
  return url;
}

test.setTimeout(120000);
test.describe.configure({ mode: "serial" });

test.beforeAll(async ({}, testInfo) => {
  testInfo.setTimeout(120000);
  if (!flagOnBaseUrl) {
    const port = await reservePort(FLAG_ON_PORT);
    flagOnBaseUrl = await startDashboardServer("activity-ia-v8-on", port, "true", "/activity/live-feed");
  }
  if (!flagOffBaseUrl) {
    const port = await reservePort(FLAG_OFF_PORT);
    flagOffBaseUrl = await startDashboardServer("activity-ia-v8-off", port, "false", "/dashboard");
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

test("activity tabs render with IA_V8 on", async ({ page }) => {
  for (const route of ["/activity/live-feed", "/activity/sessions", "/activity/replay", "/activity/heatmap"]) {
    const response = await page.goto(`${flagOnBaseUrl}${route}`, { waitUntil: "domcontentloaded" });
    expect(response?.status(), route).toBeLessThan(400);
    await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Activity tabs" })).toBeVisible();
  }
});

test("live feed filter chips keep the enterprise route", async ({ page }) => {
  const response = await page.goto(`${flagOnBaseUrl}/activity/live-feed?agent_provider=codex&window=24h`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  const chip = page.locator('a[href*="/activity/live-feed"]').filter({ hasText: /Provider:\s*codex/i }).first();
  await expect(chip).toBeVisible();
  await expect(chip).toContainText(/Provider:\s*codex/i);
  await expect(chip).toHaveAttribute("href", /\/activity\/live-feed/);
});

test("live feed captures desktop and mobile triage layout", async ({ page }, testInfo) => {
  const response = await page.goto(`${flagOnBaseUrl}/activity/live-feed`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();
  await expect(page.locator('select[name="hours"]')).toHaveValue("168");
  await page.screenshot({ path: testInfo.outputPath("activity-live-feed-desktop.png"), fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${flagOnBaseUrl}/activity/live-feed`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("activity-live-feed-mobile.png"), fullPage: true });
});

test("replay captures desktop and mobile forensic layout", async ({ page }, testInfo) => {
  const response = await page.goto(`${flagOnBaseUrl}/activity/replay`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  await expect(page.getByRole("heading", { name: "Run review queue" })).toBeVisible();
  await expect(page.getByRole("link", { name: /Open run/i }).first()).toBeVisible();
  await page.getByRole("link", { name: /Open run/i }).first().click();
  await expect(page.getByRole("button", { name: /Acknowledge run/i })).toBeVisible();
  await expect(page.getByText("Recommended action")).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("activity-replay-desktop.png"), fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(page.url(), { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("button", { name: /Acknowledge run/i })).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("activity-replay-mobile.png"), fullPage: true });
});

test("dashboard renders Activity with IA_V8 on and legacy overview with flag off", async ({ page }) => {
  await page.goto(`${flagOnBaseUrl}/dashboard`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();

  await page.goto(`${flagOffBaseUrl}/dashboard`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
});
