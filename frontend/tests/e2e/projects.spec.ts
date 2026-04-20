import { test, expect } from '@playwright/test';

test.describe('Projects E2E Tests', () => {
  const baseUrl = 'http://localhost:5173';

  test.beforeEach(async ({ page, context }) => {
    // Set auth token from environment or login
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
    await page.goto(baseUrl);
  });

  test('should display projects list', async ({ page }) => {
    await page.goto(`${baseUrl}/projects`);
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/проекты/i);
    await expect(page.locator('table, .projects-list, [data-testid="projects-list"]')).toBeVisible({ timeout: 10000 });
  });

  test('should filter projects by status', async ({ page }) => {
    await page.goto(`${baseUrl}/projects`);
    
    const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]');
    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
      await expect(page.locator('table')).toBeVisible();
    }
  });

  test('should paginate projects', async ({ page }) => {
    await page.goto(`${baseUrl}/projects?limit=10&offset=0`);
    
    // Check pagination controls
    const pagination = page.locator('.pagination, [data-testid="pagination"]');
    if (await pagination.count() > 0) {
      await expect(pagination).toBeVisible();
      
      // Click next page
      const nextPage = pagination.locator('button:has-text("Next"), button:has-text("Далее")');
      if (await nextPage.count() > 0) {
        await nextPage.click();
        await page.waitForURL(/offset=10/i);
      }
    }
  });

  test('should navigate to project detail', async ({ page }) => {
    await page.goto(`${baseUrl}/projects`);
    
    // Click on first project
    const projectLink = page.locator('[data-testid="project-link"], a[href*="/projects/"]').first();
    if (await projectLink.count() > 0) {
      await projectLink.click();
      await page.waitForURL(/\/projects\/\d+/i);
      await expect(page.locator('h1, h2')).toBeVisible();
    }
  });
});
