import { expect, test } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const PORT = Number(process.env.PLAYWRIGHT_AUTH_ENTRY_PORT || 4331);
const PROVIDED_BASE_URL = process.env.PLAYWRIGHT_AUTH_ENTRY_URL;

type ManagedServer = {
  process: ChildProcess;
};

let baseUrl = PROVIDED_BASE_URL || "";
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
      throw new Error(`dashboard exited before auth-entry smoke was ready. ${lastError}`);
    }

    try {
      const response = await fetch(url);
      if (response.status < 500) return;
      lastError = `status ${response.status}`;
    } catch (error) {
      lastError = error instanceof Error ? error.message : String(error);
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  throw new Error(`dashboard did not become ready at ${url}. ${lastError}`);
}

async function ensureDashboardBuilt(): Promise<void> {
  const buildIdPath = path.join(dashboardCwd(), ".next", "BUILD_ID");
  if (fs.existsSync(buildIdPath)) return;

  await new Promise<void>((resolve, reject) => {
    const build = spawn("npx", ["next", "build"], {
      cwd: dashboardCwd(),
      env: {
        ...process.env,
        NEXT_TELEMETRY_DISABLED: "1",
      },
      stdio: "ignore",
    });
    build.once("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`next build failed with exit code ${code ?? "unknown"}`));
    });
    build.once("error", reject);
  });
}

async function startDashboardServer(): Promise<string> {
  await ensureDashboardBuilt();
  const url = `http://127.0.0.1:${PORT}`;
  const server = spawn("npx", ["next", "start", "--hostname", "127.0.0.1", "--port", String(PORT)], {
    cwd: dashboardCwd(),
    env: {
      ...process.env,
      API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
      IA_V8_DEFAULT: "true",
      NEXT_PUBLIC_API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
      NEXT_TELEMETRY_DISABLED: "1",
      PORT: String(PORT),
      WORKOS_API_KEY: "",
      WORKOS_CLIENT_ID: "",
      WORKOS_COOKIE_PASSWORD: "",
      WORKOS_REDIRECT_URI: "",
    },
    stdio: "ignore",
  });
  const managed = { process: server };
  managedServers.push(managed);
  await waitForReady(url, managed);
  return url;
}

test.setTimeout(90_000);
test.describe.configure({ mode: "serial" });

test.beforeAll(
  async () => {
  if (!baseUrl) baseUrl = await startDashboardServer();
  },
  { timeout: 120_000 },
);

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

test("public landing routes developers to sign in", async ({ page }) => {
  const response = await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  await expect(page.getByRole("heading", { name: /Skillayer connects every coding agent/i })).toBeVisible();
  await expect(page.getByRole("navigation").getByRole("link", { name: /^Sign in$/ })).toBeVisible();
  await page.screenshot({ path: "test-results/auth-entry-landing-desktop.png", fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("navigation").getByRole("link", { name: /^Sign in$/ })).toBeVisible();
  await page.screenshot({ path: "test-results/auth-entry-landing-mobile.png", fullPage: true });
});

test("sign-in page exposes enterprise auth choices", async ({ page }) => {
  const response = await page.goto(`${baseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  await expect(page.getByRole("heading", { name: /Sign in to connect local agents/i })).toBeVisible();
  await expect(page.getByText("Sign in with work account")).toBeVisible();
  await expect(page.getByText("Email magic link")).toBeVisible();
  await expect(page.getByPlaceholder("you@company.com")).toBeVisible();
  await expect(page.getByText("Sign in with GitHub")).toBeVisible();
  await page.screenshot({ path: "test-results/auth-entry-sign-in-desktop.png", fullPage: true });
});

test("magic-link form routes corporate email to Connect in local preview", async ({ page }) => {
  await page.goto(`${baseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  await page.getByPlaceholder("you@company.com").fill("dev@acme.test");
  await page.getByRole("button", { name: /^Send$/ }).click();

  await expect(page).toHaveURL(/\/settings\/connectors\?auth=magic-link-preview&email=dev%40acme\.test$/);
});

test("magic-link form rejects personal email domains", async ({ page }) => {
  await page.goto(`${baseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  await page.getByPlaceholder("you@company.com").fill("dev@gmail.com");
  await page.getByRole("button", { name: /^Send$/ }).click();

  await expect(page).toHaveURL(/\/sign-in\?error=personal-email&email=dev%40gmail\.com$/);
  await expect(page.getByText(/Use a work email/i)).toBeVisible();
});

test("sso route falls back to local preview when WorkOS is not configured", async ({ page }) => {
  const response = await page.goto(`${baseUrl}/api/auth/sso`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);
  await expect(page).toHaveURL(/\/activity$/);
});
