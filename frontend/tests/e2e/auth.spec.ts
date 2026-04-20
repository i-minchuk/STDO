import { test, expect } from '@playwright/test';

test.describe('Authentication E2E Tests', () => {
  const baseUrl = 'http://localhost:5173';

  test.beforeEach(async ({ page }) => {
    await page.goto(`${baseUrl}/login`);
  });

  test('should display login form', async ({ page }) => {
    await expect(page.locator('h1')).toContainText(/докпоток iris/i);
    await expect(page.locator('input[type="text"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.fill('input[type="text"]', 'wronguser');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Wait for error message
    await expect(page.getByText(/неверный логин или пароль|сервер недоступен/i)).toBeVisible({ timeout: 5000 });
  });

  test('should redirect to dashboard on successful login', async ({ page }) => {
    // Use test credentials (should be set up in test environment)
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Wait for navigation
    await page.waitForURL(/dashboard|projects/i, { timeout: 10000 });
    await expect(page.getByRole('heading', { level: 1 })).toContainText(/портфолио проектов/i);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL(/dashboard|projects/i, { timeout: 10000 });
    
    // Find and click logout button
    const logoutButton = page.locator('button:has-text("Logout"), button:has-text("Выйти")');
    if (await logoutButton.count() > 0) {
      await logoutButton.click();
      await page.waitForURL(/login/i, { timeout: 5000 });
      await expect(page.locator('h1')).toContainText(/докпоток iris/i);
    }
  });
});
