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
      - link "IRIS ДокПоток IRIS" [ref=e7]:
        - /url: /dashboard
        - generic [ref=e8]: IRIS
        - generic [ref=e9]: ДокПоток IRIS
      - generic [ref=e10]:
        - button "Переключить тему" [ref=e11] [cursor=pointer]:
          - img [ref=e12]
        - button "Уведомления" [ref=e14] [cursor=pointer]:
          - img [ref=e15]
          - generic [ref=e18]: "3"
        - button [ref=e20] [cursor=pointer]:
          - img [ref=e22]
          - img [ref=e25]
  - main [ref=e27]:
    - generic [ref=e28]:
      - generic [ref=e29]:
        - generic [ref=e30]:
          - heading "Портфолио проектов" [level=1] [ref=e31]
          - paragraph [ref=e32]: Обзор состояния проектного портфеля на 20 апреля 2026 г.
        - generic [ref=e33]:
          - button "Аналитика" [ref=e34] [cursor=pointer]:
            - generic [ref=e35]: Аналитика
          - button "+ Добавить проект" [ref=e36] [cursor=pointer]:
            - generic [ref=e37]: + Добавить проект
      - generic [ref=e38]:
        - generic [ref=e40]:
          - generic [ref=e41]:
            - generic [ref=e42]: Всего проектов
            - generic [ref=e43]: "0"
            - generic [ref=e44]: За всё время
          - img [ref=e46]
        - generic [ref=e49]:
          - generic [ref=e50]:
            - generic [ref=e51]: Активных
            - generic [ref=e52]: "0"
            - generic [ref=e53]: В разработке
          - img [ref=e55]
        - generic [ref=e59]:
          - generic [ref=e60]:
            - generic [ref=e61]: В зоне риска
            - generic [ref=e62]: "0"
            - generic [ref=e63]: Требуют внимания
          - img [ref=e65]
        - generic [ref=e68]:
          - generic [ref=e69]:
            - generic [ref=e70]: Завершено
            - generic [ref=e71]: "0"
            - generic [ref=e72]: Успешно закрыты
          - img [ref=e74]
      - generic [ref=e77]:
        - generic [ref=e78]:
          - generic [ref=e79]:
            - generic [ref=e80]:
              - heading "Последние проекты" [level=2] [ref=e81]
              - paragraph [ref=e82]: Актуальный статус проектного портфеля
            - button "Все проекты" [ref=e83] [cursor=pointer]:
              - generic [ref=e84]: Все проекты
          - table [ref=e86]:
            - rowgroup [ref=e87]:
              - row "Проект Заказчик Прогресс SPI Риск" [ref=e88]:
                - columnheader "Проект" [ref=e89]
                - columnheader "Заказчик" [ref=e90]
                - columnheader "Прогресс" [ref=e91]
                - columnheader "SPI" [ref=e92]
                - columnheader "Риск" [ref=e93]
            - rowgroup [ref=e94]:
              - row "Модернизация НПЗ PRJ-001 Газпром 62% 0.92 Medium" [ref=e95] [cursor=pointer]:
                - cell "Модернизация НПЗ PRJ-001" [ref=e96]:
                  - generic [ref=e97]: Модернизация НПЗ
                  - generic [ref=e98]: PRJ-001
                - cell "Газпром" [ref=e99]
                - cell "62%" [ref=e100]:
                  - generic [ref=e101]: 62%
                - cell "0.92" [ref=e104]:
                  - generic [ref=e105]: "0.92"
                - cell "Medium" [ref=e106]:
                  - generic [ref=e107]: Medium
              - row "Строительство ЛЭП PRJ-002 РусГидро 83% 1.05 Low" [ref=e108] [cursor=pointer]:
                - cell "Строительство ЛЭП PRJ-002" [ref=e109]:
                  - generic [ref=e110]: Строительство ЛЭП
                  - generic [ref=e111]: PRJ-002
                - cell "РусГидро" [ref=e112]
                - cell "83%" [ref=e113]:
                  - generic [ref=e114]: 83%
                - cell "1.05" [ref=e117]:
                  - generic [ref=e118]: "1.05"
                - cell "Low" [ref=e119]:
                  - generic [ref=e120]: Low
              - row "Реконструкция котельной PRJ-003 ТГК-1 25% 0.62 High" [ref=e121] [cursor=pointer]:
                - cell "Реконструкция котельной PRJ-003" [ref=e122]:
                  - generic [ref=e123]: Реконструкция котельной
                  - generic [ref=e124]: PRJ-003
                - cell "ТГК-1" [ref=e125]
                - cell "25%" [ref=e126]:
                  - generic [ref=e127]: 25%
                - cell "0.62" [ref=e130]:
                  - generic [ref=e131]: "0.62"
                - cell "High" [ref=e132]:
                  - generic [ref=e133]: High
        - generic [ref=e134]:
          - generic [ref=e135]:
            - generic [ref=e136]:
              - generic [ref=e137]:
                - heading "Общая эффективность" [level=3] [ref=e138]
                - paragraph [ref=e139]: Средний SPI по всем проектам вырос на 4.2% за прошлую неделю.
              - generic [ref=e140]: +4.2%
            - generic [ref=e141]:
              - generic [ref=e143]:
                - generic [ref=e144]: Активные проекты
                - generic [ref=e145]: "0"
              - generic [ref=e149]:
                - generic [ref=e150]: Завершённые
                - generic [ref=e151]: "0"
              - generic [ref=e155]:
                - generic [ref=e156]: Риски
                - generic [ref=e157]: "0"
            - button "Смотреть отчет" [ref=e161] [cursor=pointer]:
              - generic [ref=e163]:
                - text: Смотреть отчет
                - img [ref=e164]
          - generic [ref=e167]:
            - generic [ref=e168]:
              - generic [ref=e169]:
                - generic [ref=e170]:
                  - img [ref=e171]
                  - text: Ежедневный квест
                - heading "Закрыть 3 задачи без просрочки" [level=3] [ref=e177]
                - paragraph [ref=e178]: Выполни план дня и получи дополнительные очки в инженерном рейтинге.
              - img [ref=e180]
            - generic [ref=e185]: Выполнено 2 из 3 шагов
            - button "Открыть задачи" [ref=e187] [cursor=pointer]:
              - generic [ref=e188]: Открыть задачи
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