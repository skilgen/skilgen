// @ts-nocheck
import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test.setTimeout(120000);

test("add repos modal flow", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/repos`);
  await page.screenshot({ path: "test-results/repos-page-initial.png", fullPage: true });

  const addMoreRepos = page.getByRole("button", { name: /add more repos/i });
  if (await addMoreRepos.isVisible().catch(() => false)) {
    await addMoreRepos.click();
    await expect(page.getByRole("heading", { name: "Add repositories" })).toBeVisible();
    await page.screenshot({ path: "test-results/modal-open.png", fullPage: true });

    const modal = page.getByTestId("add-repos-modal");
    await page.getByText("Loading your repositories…").waitFor({ state: "detached", timeout: 5000 }).catch(() => {});

    const repoRows = modal.getByTestId("available-repo-row");
    const repoCount = await repoRows.count();
    if (repoCount > 0) {
      await repoRows.first().click();
    }

    await page.screenshot({ path: "test-results/after-connect.png", fullPage: true }).catch(() => {});

    const cancel = page.getByRole("button", { name: /cancel/i });
    if (await cancel.isVisible().catch(() => false)) {
      await cancel.click();
    }
  }
});
