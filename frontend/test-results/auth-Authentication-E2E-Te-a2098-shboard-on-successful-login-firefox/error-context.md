# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auth.spec.ts >> Authentication E2E Tests >> should redirect to dashboard on successful login
- Location: tests\e2e\auth.spec.ts:26:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: locator('h1, h2')
Expected pattern: /dashboard|projects/i
Error: strict mode violation: locator('h1, h2') resolved to 2 elements:
    1) <h1 class="text-3xl font-semibold tracking-tight">Портфолио проектов</h1> aka getByRole('heading', { name: 'Портфолио проектов' })
    2) <h2 class="text-base font-semibold tracking-tight">Последние проекты</h2> aka getByRole('heading', { name: 'Последние проекты' })

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for locator('h1, h2')
    2 × locator resolved to <h1 class="text-2xl font-bold text-gray-900">ДокПоток IRIS</h1>
      - unexpected value "ДокПоток IRIS"

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - link "IRIS ДокПоток IRIS" [ref=e7] [cursor=pointer]:
          - /url: /dashboard
          - generic [ref=e8]: IRIS
          - generic [ref=e9]: ДокПоток IRIS
        - navigation "Главная навигация" [ref=e10]:
          - link "Руководители" [ref=e11] [cursor=pointer]:
            - /url: /dashboard
          - link "Инженерные группы" [ref=e12] [cursor=pointer]:
            - /url: /projects
          - link "Производство" [ref=e13] [cursor=pointer]:
            - /url: /production
          - link "Документооборот" [ref=e14] [cursor=pointer]:
            - /url: /documents
          - link "Согласования" [ref=e15] [cursor=pointer]:
            - /url: /approvals
          - link "Аудит и контроль" [ref=e16] [cursor=pointer]:
            - /url: /audit
      - generic [ref=e17]:
        - button "Переключить тему" [ref=e18] [cursor=pointer]:
          - img [ref=e19]
        - button "Уведомления" [ref=e21] [cursor=pointer]:
          - img [ref=e22]
          - generic [ref=e25]: "3"
        - button "Администратор" [ref=e27] [cursor=pointer]:
          - img [ref=e29]
          - generic [ref=e32]: Администратор
          - img [ref=e33]
  - main [ref=e35]:
    - generic [ref=e36]:
      - generic [ref=e37]:
        - generic [ref=e38]:
          - heading "Портфолио проектов" [level=1] [ref=e39]
          - paragraph [ref=e40]: Обзор состояния проектного портфеля на 20 апреля 2026 г.
        - generic [ref=e41]:
          - button "Аналитика" [ref=e42] [cursor=pointer]:
            - generic [ref=e43]: Аналитика
          - button "+ Добавить проект" [ref=e44] [cursor=pointer]:
            - generic [ref=e45]: + Добавить проект
      - generic [ref=e46]:
        - generic [ref=e48]:
          - generic [ref=e49]:
            - generic [ref=e50]: Всего проектов
            - generic [ref=e51]: "0"
            - generic [ref=e52]: За всё время
          - img [ref=e54]
        - generic [ref=e57]:
          - generic [ref=e58]:
            - generic [ref=e59]: Активных
            - generic [ref=e60]: "0"
            - generic [ref=e61]: В разработке
          - img [ref=e63]
        - generic [ref=e67]:
          - generic [ref=e68]:
            - generic [ref=e69]: В зоне риска
            - generic [ref=e70]: "0"
            - generic [ref=e71]: Требуют внимания
          - img [ref=e73]
        - generic [ref=e78]:
          - generic [ref=e79]:
            - generic [ref=e80]: Завершено
            - generic [ref=e81]: "0"
            - generic [ref=e82]: Успешно закрыты
          - img [ref=e84]
      - generic [ref=e87]:
        - generic [ref=e88]:
          - generic [ref=e89]:
            - generic [ref=e90]:
              - heading "Последние проекты" [level=2] [ref=e91]
              - paragraph [ref=e92]: Актуальный статус проектного портфеля
            - button "Все проекты" [ref=e93] [cursor=pointer]:
              - generic [ref=e94]: Все проекты
          - table [ref=e96]:
            - rowgroup [ref=e97]:
              - row "Проект Заказчик Прогресс SPI Риск" [ref=e98]:
                - columnheader "Проект" [ref=e99]
                - columnheader "Заказчик" [ref=e100]
                - columnheader "Прогресс" [ref=e101]
                - columnheader "SPI" [ref=e102]
                - columnheader "Риск" [ref=e103]
            - rowgroup [ref=e104]:
              - row "Модернизация НПЗ PRJ-001 Газпром 62% 0.92 Medium" [ref=e105] [cursor=pointer]:
                - cell "Модернизация НПЗ PRJ-001" [ref=e106]:
                  - generic [ref=e107]: Модернизация НПЗ
                  - generic [ref=e108]: PRJ-001
                - cell "Газпром" [ref=e109]
                - cell "62%" [ref=e110]:
                  - generic [ref=e111]: 62%
                - cell "0.92" [ref=e114]:
                  - generic [ref=e115]: "0.92"
                - cell "Medium" [ref=e116]:
                  - generic [ref=e117]: Medium
              - row "Строительство ЛЭП PRJ-002 РусГидро 83% 1.05 Low" [ref=e118] [cursor=pointer]:
                - cell "Строительство ЛЭП PRJ-002" [ref=e119]:
                  - generic [ref=e120]: Строительство ЛЭП
                  - generic [ref=e121]: PRJ-002
                - cell "РусГидро" [ref=e122]
                - cell "83%" [ref=e123]:
                  - generic [ref=e124]: 83%
                - cell "1.05" [ref=e127]:
                  - generic [ref=e128]: "1.05"
                - cell "Low" [ref=e129]:
                  - generic [ref=e130]: Low
              - row "Реконструкция котельной PRJ-003 ТГК-1 25% 0.62 High" [ref=e131] [cursor=pointer]:
                - cell "Реконструкция котельной PRJ-003" [ref=e132]:
                  - generic [ref=e133]: Реконструкция котельной
                  - generic [ref=e134]: PRJ-003
                - cell "ТГК-1" [ref=e135]
                - cell "25%" [ref=e136]:
                  - generic [ref=e137]: 25%
                - cell "0.62" [ref=e140]:
                  - generic [ref=e141]: "0.62"
                - cell "High" [ref=e142]:
                  - generic [ref=e143]: High
        - generic [ref=e144]:
          - generic [ref=e145]:
            - generic [ref=e146]:
              - generic [ref=e147]:
                - heading "Общая эффективность" [level=3] [ref=e148]
                - paragraph [ref=e149]: Средний SPI по всем проектам вырос на 4.2% за прошлую неделю.
              - generic [ref=e150]: +4.2%
            - generic [ref=e151]:
              - generic [ref=e153]:
                - generic [ref=e154]: Активные проекты
                - generic [ref=e155]: "0"
              - generic [ref=e158]:
                - generic [ref=e159]: Завершённые
                - generic [ref=e160]: "0"
              - generic [ref=e163]:
                - generic [ref=e164]: Риски
                - generic [ref=e165]: "0"
            - button "Смотреть отчет" [ref=e168] [cursor=pointer]:
              - generic [ref=e170]:
                - text: Смотреть отчет
                - img [ref=e171]
          - generic [ref=e174]:
            - generic [ref=e175]:
              - generic [ref=e176]:
                - generic [ref=e177]:
                  - img [ref=e178]
                  - text: Ежедневный квест
                - heading "Закрыть 3 задачи без просрочки" [level=3] [ref=e185]
                - paragraph [ref=e186]: Выполни план дня и получи дополнительные очки в инженерном рейтинге.
              - img [ref=e188]
            - generic [ref=e193]: Выполнено 2 из 3 шагов
            - button "Открыть задачи" [ref=e195] [cursor=pointer]:
              - generic [ref=e196]: Открыть задачи
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
  11 |     await expect(page.locator('h1')).toContainText(/login|войти/i);
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
> 34 |     await expect(page.locator('h1, h2')).toContainText(/dashboard|projects/i);
     |                                          ^ Error: expect(locator).toContainText(expected) failed
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