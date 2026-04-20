# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: documents.spec.ts >> Documents E2E Tests >> should display documents list
- Location: tests\e2e\documents.spec.ts:20:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('h1, h2')
Expected pattern: /documents|документы/i
Received string:  "ДокПоток IRIS"
Timeout: 5000ms

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for locator('h1, h2')
    5 × locator resolved to <h1 class="text-2xl font-bold text-gray-900">ДокПоток IRIS</h1>
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
  3  | test.describe('Documents E2E Tests', () => {
  4  |   const baseUrl = 'http://localhost:5173';
  5  | 
  6  |   test.beforeEach(async ({ context }) => {
  7  |     const token = process.env.TEST_ACCESS_TOKEN;
  8  |     if (token) {
  9  |       await context.addCookies([
  10 |         {
  11 |           name: 'access_token',
  12 |           value: token,
  13 |           domain: 'localhost',
  14 |           path: '/',
  15 |         },
  16 |       ]);
  17 |     }
  18 |   });
  19 | 
  20 |   test('should display documents list', async ({ page }) => {
  21 |     await page.goto(`${baseUrl}/documents`);
> 22 |     await expect(page.locator('h1, h2')).toContainText(/documents|документы/i);
     |                                          ^ Error: expect(locator).toContainText(expected) failed
  23 |     await expect(page.locator('table, .documents-list')).toBeVisible({ timeout: 10000 });
  24 |   });
  25 | 
  26 |   test('should search documents', async ({ page }) => {
  27 |     await page.goto(`${baseUrl}/documents`);
  28 |     
  29 |     const searchInput = page.locator('input[type="search"], input[placeholder*="search"], input[placeholder*="поиск"]');
  30 |     if (await searchInput.count() > 0) {
  31 |       await searchInput.fill('SPEC');
  32 |       await page.waitForTimeout(500);
  33 |       
  34 |       // Check if results are filtered
  35 |       await expect(page.locator('[data-testid="document-item"]')).toBeVisible();
  36 |     }
  37 |   });
  38 | 
  39 |   test('should filter documents by status', async ({ page }) => {
  40 |     await page.goto(`${baseUrl}/documents`);
  41 |     
  42 |     const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]');
  43 |     if (await statusFilter.count() > 0) {
  44 |       await statusFilter.selectOption('in_work');
  45 |       await page.waitForTimeout(500);
  46 |       
  47 |       // Verify filtered results show in_work status
  48 |       const documents = page.locator('[data-testid="document-item"]');
  49 |       if (await documents.count() > 0) {
  50 |         await expect(documents.first()).toBeVisible();
  51 |       }
  52 |     }
  53 |   });
  54 | 
  55 |   test('should navigate to document detail', async ({ page }) => {
  56 |     await page.goto(`${baseUrl}/documents`);
  57 |     
  58 |     const documentLink = page.locator('a[href*="/documents/"]').first();
  59 |     if (await documentLink.count() > 0) {
  60 |       await documentLink.click();
  61 |       await page.waitForURL(/\/documents\/\d+/i);
  62 |       await expect(page.locator('h1, h2')).toBeVisible();
  63 |     }
  64 |   });
  65 | 
  66 |   test('should display document revisions', async ({ page }) => {
  67 |     await page.goto(`${baseUrl}/documents/1`);
  68 |     
  69 |     // Check revisions section
  70 |     const revisionsSection = page.locator('.revisions, [data-testid="revisions-list"]');
  71 |     if (await revisionsSection.count() > 0) {
  72 |       await expect(revisionsSection).toBeVisible();
  73 |     }
  74 |   });
  75 | });
  76 | 
```