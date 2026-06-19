import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test("skill debt page", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/debt`);
  await expect(page.getByRole("heading", { name: /skill health score/i })).toBeVisible();
  await page.screenshot({ path: "test-results/skill-debt-page.png", fullPage: true });
  await expect(page.getByText(/Higher is better/i)).toBeVisible();

  const tabScreens: Array<[RegExp, string]> = [
    [/coverage gaps/i, "test-results/skill-debt-gaps.png"],
    [/stale skills/i, "test-results/skill-debt-stale.png"],
    [/low score/i, "test-results/skill-debt-low.png"],
    [/never loaded/i, "test-results/skill-debt-never.png"],
  ];

  for (const [name, path] of tabScreens) {
    const tab = page.getByRole("button", { name });
    if (await tab.isVisible().catch(() => false)) {
      await tab.click();
      await page.screenshot({ path, fullPage: true });
    }
  }
});
