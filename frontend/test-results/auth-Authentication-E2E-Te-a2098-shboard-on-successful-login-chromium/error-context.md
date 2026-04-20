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
        - generic [ref=e76]:
          - generic [ref=e77]:
            - generic [ref=e78]: Завершено
            - generic [ref=e79]: "0"
            - generic [ref=e80]: Успешно закрыты
          - img [ref=e82]
      - generic [ref=e85]:
        - generic [ref=e86]:
          - generic [ref=e87]:
            - generic [ref=e88]:
              - heading "Последние проекты" [level=2] [ref=e89]
              - paragraph [ref=e90]: Актуальный статус проектного портфеля
            - button "Все проекты" [ref=e91] [cursor=pointer]:
              - generic [ref=e92]: Все проекты
          - table [ref=e94]:
            - rowgroup [ref=e95]:
              - row "Проект Заказчик Прогресс SPI Риск" [ref=e96]:
                - columnheader "Проект" [ref=e97]
                - columnheader "Заказчик" [ref=e98]
                - columnheader "Прогресс" [ref=e99]
                - columnheader "SPI" [ref=e100]
                - columnheader "Риск" [ref=e101]
            - rowgroup [ref=e102]:
              - row "Модернизация НПЗ PRJ-001 Газпром 62% 0.92 Medium" [ref=e103] [cursor=pointer]:
                - cell "Модернизация НПЗ PRJ-001" [ref=e104]:
                  - generic [ref=e105]: Модернизация НПЗ
                  - generic [ref=e106]: PRJ-001
                - cell "Газпром" [ref=e107]
                - cell "62%" [ref=e108]:
                  - generic [ref=e109]: 62%
                - cell "0.92" [ref=e112]:
                  - generic [ref=e113]: "0.92"
                - cell "Medium" [ref=e114]:
                  - generic [ref=e115]: Medium
              - row "Строительство ЛЭП PRJ-002 РусГидро 83% 1.05 Low" [ref=e116] [cursor=pointer]:
                - cell "Строительство ЛЭП PRJ-002" [ref=e117]:
                  - generic [ref=e118]: Строительство ЛЭП
                  - generic [ref=e119]: PRJ-002
                - cell "РусГидро" [ref=e120]
                - cell "83%" [ref=e121]:
                  - generic [ref=e122]: 83%
                - cell "1.05" [ref=e125]:
                  - generic [ref=e126]: "1.05"
                - cell "Low" [ref=e127]:
                  - generic [ref=e128]: Low
              - row "Реконструкция котельной PRJ-003 ТГК-1 25% 0.62 High" [ref=e129] [cursor=pointer]:
                - cell "Реконструкция котельной PRJ-003" [ref=e130]:
                  - generic [ref=e131]: Реконструкция котельной
                  - generic [ref=e132]: PRJ-003
                - cell "ТГК-1" [ref=e133]
                - cell "25%" [ref=e134]:
                  - generic [ref=e135]: 25%
                - cell "0.62" [ref=e138]:
                  - generic [ref=e139]: "0.62"
                - cell "High" [ref=e140]:
                  - generic [ref=e141]: High
        - generic [ref=e142]:
          - generic [ref=e143]:
            - generic [ref=e144]:
              - generic [ref=e145]:
                - heading "Общая эффективность" [level=3] [ref=e146]
                - paragraph [ref=e147]: Средний SPI по всем проектам вырос на 4.2% за прошлую неделю.
              - generic [ref=e148]: +4.2%
            - generic [ref=e149]:
              - generic [ref=e151]:
                - generic [ref=e152]: Активные проекты
                - generic [ref=e153]: "0"
              - generic [ref=e157]:
                - generic [ref=e158]: Завершённые
                - generic [ref=e159]: "0"
              - generic [ref=e163]:
                - generic [ref=e164]: Риски
                - generic [ref=e165]: "0"
            - button "Смотреть отчет" [ref=e169] [cursor=pointer]:
              - generic [ref=e171]:
                - text: Смотреть отчет
                - img [ref=e172]
          - generic [ref=e175]:
            - generic [ref=e176]:
              - generic [ref=e177]:
                - generic [ref=e178]:
                  - img [ref=e179]
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