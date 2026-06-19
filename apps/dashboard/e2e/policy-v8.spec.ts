import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_FLAG_ON_URL || "http://127.0.0.1:4311";

const policyTabs = [
  { path: "/policy/rules", label: "Rules" },
  { path: "/policy/violations", label: "Violations" },
  { path: "/policy/approvals", label: "Approvals" },
  { path: "/policy/quarantine", label: "Quarantine" },
];

test.use({ viewport: { width: 1440, height: 1000 } });

for (const tab of policyTabs) {
  test(`policy ${tab.label} tab renders`, async ({ page }) => {
    const response = await page.goto(`${BASE_URL}${tab.path}`, { waitUntil: "domcontentloaded" });

    expect(response?.status(), tab.path).toBeLessThan(400);
    await expect(page.getByRole("heading", { name: "Agent Governance Rules" })).toBeVisible();
    await expect(page.getByRole("link", { name: tab.label })).toBeVisible();
  });
}
