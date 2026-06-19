import { expect, test } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import fs from "node:fs";
import { createServer, type IncomingMessage, type Server, type ServerResponse } from "node:http";
import path from "node:path";

const PREVIEW_PORT = Number(process.env.PLAYWRIGHT_AUTH_ENTRY_PORT || 4331);
const CONFIGURED_PORT = Number(process.env.PLAYWRIGHT_AUTH_ENTRY_CONFIGURED_PORT || 4332);
const PROVIDED_PREVIEW_BASE_URL = process.env.PLAYWRIGHT_AUTH_ENTRY_URL;
const PROVIDED_CONFIGURED_BASE_URL = process.env.PLAYWRIGHT_AUTH_ENTRY_CONFIGURED_URL;

type ManagedServer = {
  name: string;
  process: ChildProcess;
};

let previewBaseUrl = PROVIDED_PREVIEW_BASE_URL || "";
let configuredBaseUrl = PROVIDED_CONFIGURED_BASE_URL || "";
const managedServers: ManagedServer[] = [];
let workosStub: { port: number; server: Server; calls: Array<{ path: string; body: unknown }> } | null = null;

function dashboardCwd(): string {
  return process.cwd().endsWith(`${path.sep}apps${path.sep}dashboard`)
    ? process.cwd()
    : path.join(process.cwd(), "apps", "dashboard");
}

function nextCliPath(): string {
  return path.join(dashboardCwd(), "..", "..", "node_modules", "next", "dist", "bin", "next");
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
  if (fs.existsSync(buildIdPath) && (PROVIDED_PREVIEW_BASE_URL || PROVIDED_CONFIGURED_BASE_URL)) return;

  await new Promise<void>((resolve, reject) => {
    const build = spawn(process.execPath, [nextCliPath(), "build"], {
      cwd: dashboardCwd(),
      env: {
        ...process.env,
        FF_SELF_SERVE_AUTH: "true",
        IA_V8_DEFAULT: "true",
        NEXT_PUBLIC_API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
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
  const url = `http://127.0.0.1:${PREVIEW_PORT}`;
  const server = spawn(process.execPath, [nextCliPath(), "start", "--hostname", "127.0.0.1", "--port", String(PREVIEW_PORT)], {
    cwd: dashboardCwd(),
    env: {
      ...process.env,
      API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
      FF_SELF_SERVE_AUTH: "true",
      IA_V8_DEFAULT: "true",
      NEXT_PUBLIC_API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
      NEXT_TELEMETRY_DISABLED: "1",
      PORT: String(PREVIEW_PORT),
      WORKOS_API_KEY: "",
      WORKOS_CLIENT_ID: "",
      WORKOS_COOKIE_PASSWORD: "",
      WORKOS_REDIRECT_URI: "",
    },
    stdio: "ignore",
  });
  const managed = { name: "auth-entry-preview", process: server };
  managedServers.push(managed);
  await waitForReady(url, managed);
  return url;
}

test.setTimeout(120_000);
test.describe.configure({ mode: "serial" });

test.beforeAll(async ({}, testInfo) => {
  testInfo.setTimeout(120_000);
  if (!previewBaseUrl) previewBaseUrl = await startDashboardServer();
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

  if (workosStub) {
    await new Promise<void>((resolve) => workosStub?.server.close(() => resolve()));
    workosStub = null;
  }
});

test("public landing routes developers to sign in", async ({ page }) => {
  const response = await page.goto(previewBaseUrl, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  await expect(page.getByRole("heading", { name: /Skillayer connects every coding agent/i })).toBeVisible();
  await expect(page.getByRole("navigation").getByRole("link", { name: /^Sign in$/ })).toBeVisible();
  await page.screenshot({ path: "test-results/auth-entry-landing-desktop.png", fullPage: true });

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(previewBaseUrl, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("navigation").getByRole("link", { name: /^Sign in$/ })).toBeVisible();
  await page.screenshot({ path: "test-results/auth-entry-landing-mobile.png", fullPage: true });
});

test("sign-in page exposes enterprise auth choices", async ({ page }) => {
  const response = await page.goto(`${previewBaseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);

  await expect(page.getByRole("heading", { name: /Sign in to connect local agents/i })).toBeVisible();
  await expect(page.getByText("Sign in with work account")).toBeVisible();
  await expect(page.getByText("Email magic link")).toBeVisible();
  await expect(page.getByPlaceholder("you@company.com")).toBeVisible();
  await expect(page.getByText("Sign in with GitHub")).toBeVisible();
  await page.screenshot({ path: "test-results/auth-entry-sign-in-desktop.png", fullPage: true });
});

test("magic-link form routes corporate email to Connect in local preview", async ({ page }) => {
  await page.goto(`${previewBaseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  await page.getByPlaceholder("you@company.com").fill("dev@acme.test");
  await page.getByRole("button", { name: /^Send$/ }).click();

  await expect(page).toHaveURL(/\/settings\/connectors\?auth=magic-link-preview&email=dev%40acme\.test$/);
  await expect(page.getByRole("heading", { name: /^Settings$/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: /Agent compliance setup/i })).toBeVisible();
});

test("magic-link form rejects personal email domains", async ({ page }) => {
  await page.goto(`${previewBaseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  await page.getByPlaceholder("you@company.com").fill("dev@gmail.com");
  await page.getByRole("button", { name: /^Send$/ }).click();

  await expect(page).toHaveURL(/\/sign-in\?error=personal-email&email=dev%40gmail\.com$/);
  await expect(page.getByText(/Use a work email/i)).toBeVisible();
});

test("sso route falls back to local preview when WorkOS is not configured", async ({ page }) => {
  const response = await page.goto(`${previewBaseUrl}/api/auth/sso`, { waitUntil: "domcontentloaded" });
  expect(response?.status()).toBeLessThan(400);
  await expect(page).toHaveURL(/\/activity$/);
});

function readJsonBody(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve) => {
    let buffer = "";
    req.on("data", (chunk) => {
      buffer += String(chunk);
    });
    req.on("end", () => {
      if (!buffer) {
        resolve(null);
        return;
      }
      try {
        resolve(JSON.parse(buffer));
      } catch {
        resolve(buffer);
      }
    });
  });
}

function json(res: ServerResponse, status: number, payload: unknown) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json");
  res.end(JSON.stringify(payload));
}

async function startWorkOSStubServer(): Promise<{ port: number; server: Server; calls: Array<{ path: string; body: unknown }> }> {
  const calls: Array<{ path: string; body: unknown }> = [];
  const server = createServer(async (req, res) => {
    const url = new URL(req.url || "/", "http://127.0.0.1");
    const body = await readJsonBody(req);
    calls.push({ path: url.pathname, body });

    if (req.method === "POST" && url.pathname === "/passwordless/sessions") {
      json(res, 200, {
        id: "psess_test_123",
        email: typeof body === "object" && body && "email" in body ? (body as any).email : "unknown@example.com",
        expires_at: new Date(Date.now() + 15 * 60_000).toISOString(),
        link: "https://workos.stub/magic-link",
        object: "passwordless_session",
      });
      return;
    }

    if (req.method === "POST" && url.pathname === "/passwordless/sessions/psess_test_123/send") {
      json(res, 200, { sent: true });
      return;
    }

    json(res, 404, { error: "not_found", path: url.pathname });
  });

  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  const port = typeof address === "object" && address ? address.port : 0;
  return { port, server, calls };
}

async function startConfiguredDashboardServer(): Promise<string> {
  workosStub = await startWorkOSStubServer();
  await ensureDashboardBuilt();
  const url = `http://127.0.0.1:${CONFIGURED_PORT}`;
  const server = spawn(process.execPath, [nextCliPath(), "start", "--hostname", "127.0.0.1", "--port", String(CONFIGURED_PORT)], {
    cwd: dashboardCwd(),
    env: {
      ...process.env,
      API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
      FF_SELF_SERVE_AUTH: "true",
      IA_V8_DEFAULT: "true",
      NEXT_PUBLIC_API_URL: process.env.PLAYWRIGHT_TEST_API_URL || "http://127.0.0.1:59999",
      NEXT_TELEMETRY_DISABLED: "1",
      PORT: String(CONFIGURED_PORT),
      WORKOS_API_KEY: "sk_test_stub",
      WORKOS_CLIENT_ID: "client_stub",
      WORKOS_COOKIE_PASSWORD: "x".repeat(32),
      WORKOS_REDIRECT_URI: `http://127.0.0.1:${CONFIGURED_PORT}/callback`,
      WORKOS_API_HOSTNAME: "127.0.0.1",
      WORKOS_API_PORT: String(workosStub.port),
      WORKOS_API_HTTPS: "false",
    },
    stdio: "ignore",
  });
  const managed = { name: "auth-entry-configured", process: server };
  managedServers.push(managed);
  await waitForReady(url, managed);
  return url;
}

test("magic-link form hits WorkOS session send when configured (stubbed)", async ({ page }) => {
  if (!configuredBaseUrl) configuredBaseUrl = await startConfiguredDashboardServer();

  await page.goto(`${configuredBaseUrl}/sign-in`, { waitUntil: "domcontentloaded" });
  await page.getByPlaceholder("you@company.com").fill("dev@acme.test");
  await page.getByRole("button", { name: /^Send$/ }).click();

  await expect(page).toHaveURL(/\/sign-in\?sent=magic-link&email=dev%40acme\.test$/);
  await expect(page.getByText(/Check .*dev@acme\.test.* for a Skillayer sign-in link/i)).toBeVisible();

  const calls = workosStub?.calls ?? [];
  expect(calls.some((call) => call.path === "/passwordless/sessions")).toBeTruthy();
  expect(calls.some((call) => call.path === "/passwordless/sessions/psess_test_123/send")).toBeTruthy();
});

test("sso route returns a WorkOS redirect when configured", async ({ request }) => {
  if (!configuredBaseUrl) configuredBaseUrl = await startConfiguredDashboardServer();

  const response = await request.get(`${configuredBaseUrl}/api/auth/sso`, { maxRedirects: 0 });
  expect(response.status()).toBeGreaterThanOrEqual(300);
  expect(response.status()).toBeLessThan(400);
  const location = response.headers()["location"] || "";
  expect(location).toMatch(/workos/i);
});
