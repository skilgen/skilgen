import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test("registry detail page", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/registry`);
  await page.screenshot({ path: "test-results/registry-list.png", fullPage: true });

  const firstCard = page.locator("article").first();
  const cardVisible = await firstCard.isVisible().catch(() => false);
  if (cardVisible) {
    await firstCard.click();
    await expect(page).toHaveURL(/\/dashboard\/registry\/.+/);
    await expect(page.getByText("SKILL.md Content")).toBeVisible();
    await page.screenshot({ path: "test-results/registry-detail.png", fullPage: true });

    const copyPathBtn = page.getByRole("button", { name: /copy path/i }).first();
    if (await copyPathBtn.isVisible().catch(() => false)) {
      await copyPathBtn.click();
      await page.screenshot({ path: "test-results/registry-detail-copied.png" });
    }
  }
});
