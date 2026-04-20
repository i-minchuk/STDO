# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication E2E Tests >> should display login form
- Location: tests\e2e\auth.spec.ts:10:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('h1')
Expected pattern: /login|войти/i
Received string:  "ДокПоток IRIS"
Timeout: 5000ms

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for locator('h1')
    6 × locator resolved to <h1 class="text-2xl font-bold text-gray-900">ДокПоток IRIS</h1>
      - unexpected value "ДокПоток IRIS"

```

# Page snapshot

```yaml
- generic [ref=e4]:
  - generic [ref=e5]:
    - img [ref=e6]
    - heading "ДокПоток IRIS" [level=1] [ref=e9]
  - paragraph [ref=e10]: Система учёта технической документации
  - generic [ref=e11]:
    - generic [ref=e12]:
      - generic [ref=e13]: Логин
      - textbox "admin" [ref=e14]
    - generic [ref=e15]:
      - generic [ref=e16]: Пароль
      - textbox "••••••" [ref=e17]
    - button "Войти" [ref=e18] [cursor=pointer]
  - generic [ref=e19]:
    - button "Демо-режим (без сервера)" [ref=e20] [cursor=pointer]
    - paragraph [ref=e21]: Демо-режим работает на моковых данных без подключения к бэкенду
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Authentication E2E Tests', () => {
  4  |   const baseUrl = 'http://localhost:5173';
  5  | 
  6  |   test.beforeEach(async ({ page }) => {
  7  |     await page.goto(baseUrl);
  8  |   });
  9  | 
  10 |   test('should display login form', async ({ page }) => {
> 11 |     await expect(page.locator('h1')).toContainText(/login|войти/i);
     |                                      ^ Error: expect(locator).toContainText(expected) failed
  12 |     await expect(page.locator('input[type="text"]')).toBeVisible();
  13 |     await expect(page.locator('input[type="password"]')).toBeVisible();
  14 |     await expect(page.locator('button[type="submit"]')).toBeVisible();
  15 |   });
  16 | 
  17 |   test('should show error on invalid credentials', async ({ page }) => {
  18 |     await page.fill('input[type="text"]', 'wronguser');
  19 |     await page.fill('input[type="password"]', 'wrongpassword');
  20 |     await page.click('button[type="submit"]');
  21 |     
  22 |     // Wait for error message
  23 |     await expect(page.locator('text=Invalid credentials')).toBeVisible({ timeout: 5000 });
  24 |   });
  25 | 
  26 |   test('should redirect to dashboard on successful login', async ({ page }) => {
  27 |     // Use test credentials (should be set up in test environment)
  28 |     await page.fill('input[type="text"]', 'admin');
  29 |     await page.fill('input[type="password"]', 'admin123');
  30 |     await page.click('button[type="submit"]');
  31 |     
  32 |     // Wait for navigation
  33 |     await page.waitForURL(/dashboard|projects/i, { timeout: 10000 });
  34 |     await expect(page.locator('h1, h2')).toContainText(/dashboard|projects/i);
  35 |   });
  36 | 
  37 |   test('should logout successfully', async ({ page }) => {
  38 |     // Login first
  39 |     await page.fill('input[type="text"]', 'admin');
  40 |     await page.fill('input[type="password"]', 'admin123');
  41 |     await page.click('button[type="submit"]');
  42 |     await page.waitForURL(/dashboard|projects/i, { timeout: 10000 });
  43 |     
  44 |     // Find and click logout button
  45 |     const logoutButton = page.locator('button:has-text("Logout"), button:has-text("Выйти")');
  46 |     if (await logoutButton.count() > 0) {
  47 |       await logoutButton.click();
  48 |       await page.waitForURL(/login/i, { timeout: 5000 });
  49 |       await expect(page.locator('h1')).toContainText(/login|войти/i);
  50 |     }
  51 |   });
  52 | });
  53 | 
```