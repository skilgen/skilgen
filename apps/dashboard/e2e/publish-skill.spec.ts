import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test("publish skill modal", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/repos`);
  await page.screenshot({ path: "test-results/repos-for-publish.png", fullPage: true });

  const firstRepoRow = page.locator("tbody tr").first();
  if (await firstRepoRow.isVisible().catch(() => false)) {
    await firstRepoRow.click();
    await page.waitForURL(/\/dashboard\/repos\/.+/);
    await page.screenshot({ path: "test-results/repo-detail-for-publish.png", fullPage: true });

    const firstSkillLink = page.locator("a[href*='/skills/']").first();
    if (await firstSkillLink.isVisible().catch(() => false)) {
      await firstSkillLink.click();
      await page.waitForURL(/\/skills\/.+/);
      await page.screenshot({ path: "test-results/skill-detail-before-publish.png", fullPage: true });

      const publishBtn = page.getByRole("button", { name: /publish/i });
      if (await publishBtn.isVisible().catch(() => false)) {
        await publishBtn.click();
        await expect(page.getByRole("heading", { name: /publish to registry/i })).toBeVisible();
        await page.screenshot({ path: "test-results/publish-modal-open.png", fullPage: true });

        await page.getByLabel(/skill name/i).fill("Test Skill");
        await page.getByPlaceholder(/describe what this skill/i).fill("This skill covers the core patterns used in this domain.");
        await page.screenshot({ path: "test-results/publish-modal-filled.png", fullPage: true });
      }
    }
  }
});
