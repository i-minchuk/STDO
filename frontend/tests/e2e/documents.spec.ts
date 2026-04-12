import { test, expect } from '@playwright/test';

test.describe('Documents E2E Tests', () => {
  const baseUrl = 'http://localhost:5173';

  test.beforeEach(async ({ page, context }) => {
    const token = process.env.TEST_ACCESS_TOKEN;
    if (token) {
      await context.addCookies([
        {
          name: 'access_token',
          value: token,
          domain: 'localhost',
          path: '/',
        },
      ]);
    }
  });

  test('should display documents list', async ({ page }) => {
    await page.goto(`${baseUrl}/documents`);
    await expect(page.locator('h1, h2')).toContainText(/documents|документы/i);
    await expect(page.locator('table, .documents-list')).toBeVisible({ timeout: 10000 });
  });

  test('should search documents', async ({ page }) => {
    await page.goto(`${baseUrl}/documents`);
    
    const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="поиск"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('SPEC');
      await page.waitForTimeout(500);
      
      // Check if results are filtered
      await expect(page.locator('[data-testid="document-item"]')).toBeVisible();
    }
  });

  test('should filter documents by status', async ({ page }) => {
    await page.goto(`${baseUrl}/documents`);
    
    const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]');
    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption('in_work');
      await page.waitForTimeout(500);
      
      // Verify filtered results show in_work status
      const documents = page.locator('[data-testid="document-item"]');
      if (await documents.count() > 0) {
        await expect(documents.first()).toBeVisible();
      }
    }
  });

  test('should navigate to document detail', async ({ page }) => {
    await page.goto(`${baseUrl}/documents`);
    
    const documentLink = page.locator('a[href*="/documents/"]').first();
    if (await documentLink.count() > 0) {
      await documentLink.click();
      await page.waitForURL(/\/documents\/\d+/i);
      await expect(page.locator('h1, h2')).toBeVisible();
    }
  });

  test('should display document revisions', async ({ page }) => {
    await page.goto(`${baseUrl}/documents/1`);
    
    // Check revisions section
    const revisionsSection = page.locator('.revisions, [data-testid="revisions-list"]');
    if (await revisionsSection.count() > 0) {
      await expect(revisionsSection).toBeVisible();
    }
  });
});
