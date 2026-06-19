import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test("skill diff flow", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/repos`);
  const firstRepoRow = page.locator("tbody tr").first();
  if (!(await firstRepoRow.isVisible().catch(() => false))) {
    await page.screenshot({ path: "test-results/skill-diff-no-repos.png", fullPage: true });
    await expect(page.getByRole("heading", { name: "Repositories", exact: true })).toBeVisible();
    return;
  }
  await firstRepoRow.click();
  await page.waitForURL(/\/dashboard\/repos\/.+/);

  const firstSkillLink = page.locator("a[href*='/skills/']").first();
  if (!(await firstSkillLink.isVisible().catch(() => false))) {
    await page.screenshot({ path: "test-results/skill-diff-no-skills.png", fullPage: true });
    await expect(page).toHaveURL(/\/dashboard\/repos\/.+/);
    return;
  }

  await firstSkillLink.click();
  await page.waitForURL(/\/skills\/.+/);
  await page.screenshot({ path: "test-results/skill-detail-with-diff-links.png", fullPage: true });

  const diffLink = page.getByRole("link", { name: /view diff/i }).first();
  if (!(await diffLink.isVisible().catch(() => false))) {
    await expect(page.getByText(/no previous version/i)).toBeVisible();
    return;
  }

  await diffLink.click();
  await expect(page.getByRole("heading", { name: /skill diff/i })).toBeVisible();
  await page.screenshot({ path: "test-results/skill-diff-page.png", fullPage: true });
  await expect(page.getByText(/first version|SKILL.md changes/i)).toBeVisible();
});
