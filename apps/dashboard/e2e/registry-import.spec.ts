import { expect, test } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://127.0.0.1:3000";

test("import skill file modal", async ({ page }) => {
  await page.goto(`${BASE_URL}/dashboard/registry`);
  await page.screenshot({ path: "test-results/registry-before-import.png", fullPage: true });

  const importBtn = page.getByRole("button", { name: /import from file/i });
  if (await importBtn.isVisible().catch(() => false)) {
    await importBtn.click();
    await expect(page.getByRole("heading", { name: /import existing skill file/i })).toBeVisible();
    await page.screenshot({ path: "test-results/import-modal-step1.png", fullPage: true });

    await page.getByPlaceholder(/paste your file content/i).fill(
      "# Payments Domain\n\nThis skill covers the payments processing pipeline.\n\n## Key Patterns\n- Use idempotency keys on all POST requests\n- Retry with exponential backoff",
    );
    await page.getByRole("button", { name: /next/i }).click();
    await page.screenshot({ path: "test-results/import-modal-step2.png", fullPage: true });

    const nameField = page.getByLabel(/name/i).first();
    if (await nameField.isVisible().catch(() => false)) {
      await nameField.fill("Payments Domain");
    }
    const domainField = page.getByLabel(/domain/i);
    if (await domainField.isVisible().catch(() => false)) {
      await domainField.fill("payments");
    }
    await page.screenshot({ path: "test-results/import-modal-filled.png", fullPage: true });
  }
});
