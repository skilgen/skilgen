import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test("heatmap page", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/heatmap`);
  await expect(page.getByRole("heading", { name: /heatmap/i })).toBeVisible();
  await page.screenshot({ path: "test-results/heatmap-full.png", fullPage: true });

  const noAgentUsage = page.getByText(/no agent usage recorded yet/i);
  if (await noAgentUsage.isVisible().catch(() => false)) {
    await page.screenshot({ path: "test-results/heatmap-empty-org.png", fullPage: true });
    return;
  }

  const deadCallout = page.getByText(/haven't been loaded in 30/i);
  if (await deadCallout.isVisible().catch(() => false)) {
    await page.screenshot({ path: "test-results/heatmap-dead-callout.png" });
  }

  const deadFilter = page.getByRole("button", { name: /dead skills/i });
  if (await deadFilter.isVisible().catch(() => false)) {
    await deadFilter.click();
    await page.screenshot({ path: "test-results/heatmap-dead-filter.png", fullPage: true });
  }

  const searchInput = page.getByPlaceholder(/search/i);
  if (await searchInput.isVisible().catch(() => false)) {
    await searchInput.fill("test");
    await page.screenshot({ path: "test-results/heatmap-search.png", fullPage: true });
  }
});
