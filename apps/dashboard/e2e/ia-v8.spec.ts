import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";
const IA_V8_DEFAULT = (process.env.IA_V8_DEFAULT || "").toLowerCase();
const isDefaultOn = ["1", "true", "yes", "on"].includes(IA_V8_DEFAULT);

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
  { label: "Activity", path: "/activity" },
  { label: "Policy", path: "/policy" },
  { label: "Audit", path: "/audit" },
  { label: "Skills", path: "/skills" },
  { label: "Insights", path: "/insights" },
  { label: "Settings", path: "/settings" },
];

test.setTimeout(120000);
test.use({ viewport: { width: 1440, height: 1000 } });

test.describe("IA_V8 flag off", () => {
  test.skip(isDefaultOn, "Run this smoke with IA_V8_DEFAULT unset or false.");

  test("legacy sidebar renders and v7 routes are valid", async ({ page }) => {
    for (const route of legacyRoutes) {
      const response = await page.goto(`${BASE_URL}${route}`, { timeout: 15000, waitUntil: "commit" });
      expect(response?.status(), route).toBeLessThan(400);
    }

    await page.goto(`${BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" });
    await expect(page.locator("aside")).toBeVisible();
    for (const label of legacySidebarItems) {
      await expect(page.locator("aside").getByText(label, { exact: true })).toBeVisible();
    }
    await page.screenshot({ path: "test-results/ia-v8-flag-off-v7-sidebar.png", fullPage: true });
  });
});

test.describe("IA_V8 flag on", () => {
  test.skip(!isDefaultOn, "Run this smoke with IA_V8_DEFAULT=true.");

  test("v8 sidebar and placeholders render", async ({ page }) => {
    for (const surface of v8Surfaces) {
      const response = await page.goto(`${BASE_URL}${surface.path}`, { waitUntil: "domcontentloaded" });
      expect(response?.status(), surface.path).toBeLessThan(400);
      await expect(page.locator("aside").getByText(surface.label, { exact: true })).toBeVisible();
      await expect(page.getByRole("heading", { name: surface.label })).toBeVisible();
      await expect(page.getByText("Coming soon — v8 surface")).toBeVisible();
      await page.screenshot({ path: `test-results/ia-v8-${surface.label.toLowerCase()}.png`, fullPage: true });
    }

    const links = page.locator("aside nav a");
    await expect(links).toHaveCount(6);
  });

  test("missing tenant override falls back to env default", async ({ page }) => {
    const response = await page.goto(`${BASE_URL}/activity`, { waitUntil: "domcontentloaded" });
    expect(response?.status()).toBeLessThan(400);
    await expect(page.getByRole("heading", { name: "Activity" })).toBeVisible();
  });
});
