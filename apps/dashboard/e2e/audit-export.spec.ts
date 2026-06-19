import { expect, test } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import path from "node:path";

const PORT = Number(process.env.PLAYWRIGHT_AUDIT_PORT || 4322);
const BASE_URL = process.env.PLAYWRIGHT_AUDIT_URL || `http://127.0.0.1:${PORT}`;
let server: ChildProcess | null = null;

function dashboardCwd(): string {
  return process.cwd().endsWith(`${path.sep}apps${path.sep}dashboard`) ? process.cwd() : path.join(process.cwd(), "apps", "dashboard");
}

test.beforeAll(async () => {
  if (process.env.PLAYWRIGHT_AUDIT_URL) return;
  server = spawn("npx", ["next", "dev", "--hostname", "127.0.0.1", "--port", String(PORT)], {
    cwd: dashboardCwd(),
    env: {
      ...process.env,
      API_URL: "http://127.0.0.1:59999",
      NEXT_PUBLIC_API_URL: "http://127.0.0.1:59999",
      IA_V8_DEFAULT: "true",
      NEXT_TELEMETRY_DISABLED: "1",
    },
    stdio: "ignore",
  });
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    if (server.exitCode !== null) throw new Error("audit export dev server exited");
    try {
      const response = await fetch(BASE_URL);
      if (response.status < 500) return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }
  throw new Error("audit export dev server did not become ready");
});

test.afterAll(async () => {
  if (!server || server.exitCode !== null) return;
  await new Promise<void>((resolve) => {
    server?.once("exit", () => resolve());
    server?.kill("SIGTERM");
    setTimeout(() => {
      if (server?.exitCode === null) server.kill("SIGKILL");
      resolve();
    }, 2_000).unref();
  });
});

test("v8 audit export flow posts selected format", async ({ page }) => {
  await page.route("**/orgs/bootstrap", async (route) => {
    await route.fulfill({ json: { id: "org_1", name: "Acme", plan: "enterprise" } });
  });
  await page.route("**/v8/orgs/*/flags/ia-v8", async (route) => {
    await route.fulfill({ json: { IA_V8: true } });
  });
  await page.route("**/v8/orgs/*/audit/exports", async (route) => {
    expect(route.request().method()).toBe("POST");
    const body = route.request().postDataJSON();
    expect(body.format).toBe("json");
    await route.fulfill({ json: { format: "json", event_count: 1, content_type: "application/json", body: [{ id: "evt_1" }], destination: null, audit_event_logged: true } });
  });

  await page.goto(`${BASE_URL}/audit/exports`);
  await page.getByRole("combobox").selectOption("json");
  await page.getByRole("button", { name: "Export" }).click();
  await expect(page.getByText('"audit_event_logged": true')).toBeVisible();
});
