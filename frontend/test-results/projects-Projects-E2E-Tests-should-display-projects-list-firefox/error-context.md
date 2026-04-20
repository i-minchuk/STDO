# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: projects.spec.ts >> Projects E2E Tests >> should display projects list
- Location: tests\e2e\projects.spec.ts:22:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('h1, h2')
Expected pattern: /projects|проекты/i
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
    - heading "ДокПоток IRIS" [level=1] [ref=e12]
  - paragraph [ref=e13]: Система учёта технической документации
  - generic [ref=e14]:
    - generic [ref=e15]:
      - generic [ref=e16]: Логин
      - textbox "admin" [ref=e17]
    - generic [ref=e18]:
      - generic [ref=e19]: Пароль
      - textbox "••••••" [ref=e20]
    - button "Войти" [ref=e21] [cursor=pointer]
  - generic [ref=e22]:
    - button "Демо-режим (без сервера)" [ref=e23] [cursor=pointer]
    - paragraph [ref=e24]: Демо-режим работает на моковых данных без подключения к бэкенду
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Projects E2E Tests', () => {
  4  |   const baseUrl = 'http://localhost:5173';
  5  | 
  6  |   test.beforeEach(async ({ page, context }) => {
  7  |     // Set auth token from environment or login
  8  |     const token = process.env.TEST_ACCESS_TOKEN;
  9  |     if (token) {
  10 |       await context.addCookies([
  11 |         {
  12 |           name: 'access_token',
  13 |           value: token,
  14 |           domain: 'localhost',
  15 |           path: '/',
  16 |         },
  17 |       ]);
  18 |     }
  19 |     await page.goto(baseUrl);
  20 |   });
  21 | 
  22 |   test('should display projects list', async ({ page }) => {
  23 |     await page.goto(`${baseUrl}/projects`);
> 24 |     await expect(page.locator('h1, h2')).toContainText(/projects|проекты/i);
     |                                          ^ Error: expect(locator).toContainText(expected) failed
  25 |     
  26 |     // Check if projects table or list is visible
  27 |     await expect(page.locator('table, .projects-list, [data-testid="projects-list"]')).toBeVisible({ timeout: 10000 });
  28 |   });
  29 | 
  30 |   test('should filter projects by status', async ({ page }) => {
  31 |     await page.goto(`${baseUrl}/projects`);
  32 |     
  33 |     const statusFilter = page.locator('select[name="status"], [data-testid="status-filter"]');
  34 |     if (await statusFilter.count() > 0) {
  35 |       await statusFilter.selectOption('active');
  36 |       await page.waitForTimeout(1000);
  37 |       
  38 |       // Verify filtered results
  39 |       const projects = page.locator('[data-testid="project-item"]');
  40 |       await expect(projects.first()).toBeVisible();
  41 |     }
  42 |   });
  43 | 
  44 |   test('should paginate projects', async ({ page }) => {
  45 |     await page.goto(`${baseUrl}/projects?limit=10&offset=0`);
  46 |     
  47 |     // Check pagination controls
  48 |     const pagination = page.locator('.pagination, [data-testid="pagination"]');
  49 |     if (await pagination.count() > 0) {
  50 |       await expect(pagination).toBeVisible();
  51 |       
  52 |       // Click next page
  53 |       const nextPage = pagination.locator('button:has-text("Next"), button:has-text("Далее")');
  54 |       if (await nextPage.count() > 0) {
  55 |         await nextPage.click();
  56 |         await page.waitForURL(/offset=10/i);
  57 |       }
  58 |     }
  59 |   });
  60 | 
  61 |   test('should navigate to project detail', async ({ page }) => {
  62 |     await page.goto(`${baseUrl}/projects`);
  63 |     
  64 |     // Click on first project
  65 |     const projectLink = page.locator('[data-testid="project-link"], a[href*="/projects/"]').first();
  66 |     if (await projectLink.count() > 0) {
  67 |       await projectLink.click();
  68 |       await page.waitForURL(/\/projects\/\d+/i);
  69 |       await expect(page.locator('h1, h2')).toBeVisible();
  70 |     }
  71 |   });
  72 | });
  73 | 
```