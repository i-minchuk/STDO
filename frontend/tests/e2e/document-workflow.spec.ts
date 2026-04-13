import { test, expect, Page } from '@playwright/test';

/**
 * E2E Test: Документный Флоу (Happy Path)
 * 
 * Покрывает весь жизненный цикл документа:
 * 1. Создание проекта
 * 2. Создание документа
 * 3. Создание ревизии
 * 4. Утверждение ревизии
 * 5. Проверка актуального состояния
 */

test.describe('Document Workflow E2E', () => {
  const baseUrl = 'http://localhost:5173';
  let testProjectId: number;
  let testDocumentId: number;

  // --- Setup: Login ---
  test.beforeAll(async ({ context, page }) => {
    const token = process.env.TEST_ACCESS_TOKEN || 'test-token';
    
    await context.addCookies([
      {
        name: 'access_token',
        value: token,
        domain: 'localhost',
        path: '/',
      },
    ]);

    // Navigate to login if needed
    await page.goto(`${baseUrl}/login`);
    const isLoggedIn = await page.locator('[data-testid="user-menu"], .user-menu').count() > 0;
    
    if (!isLoggedIn) {
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(`${baseUrl}/dashboard`);
    }
  });

  // --- Step 1: Create Project ---
  test('Step 1: Should create a new project', async ({ page }) => {
    await page.goto(`${baseUrl}/dashboard`);
    
    // Click "Create Project" button
    await page.click('button:has-text("Создать проект"), button:has-text("Create Project")');
    
    // Fill project form
    await page.fill('input[name="code"], input[placeholder*="код"]', 'E2E-TEST-001');
    await page.fill('input[name="name"], input[placeholder*="название"]', 'E2E Test Project');
    await page.fill('input[name="customer"], input[placeholder*="заказчик"]', 'Test Customer');
    
    // Submit
    await page.click('button[type="submit"]:has-text("Создать"), button[type="submit"]:has-text("Create")');
    
    // Verify redirect to project detail
    await page.waitForURL(/\/projects\/\d+/i);
    testProjectId = Number(page.url().split('/').pop());
    expect(testProjectId).toBeGreaterThan(0);
    
    // Verify project info
    await expect(page.locator('h1, h2')).toContainText('E2E-TEST-001');
  });

  // --- Step 2: Create Document ---
  test('Step 2: Should create a new document in project', async ({ page }) => {
    // Navigate to project documents
    await page.goto(`${baseUrl}/projects/${testProjectId}`);
    
    // Click "Add Document" button
    await page.click('button:has-text("Добавить документ"), button:has-text("Add Document")');
    
    // Fill document form
    await page.fill('input[name="code"], input[placeholder*="код"]', 'E2E-DOC-001');
    await page.fill('input[name="title"], input[placeholder*="название"]', 'E2E Test Document');
    
    // Select discipline
    const disciplineSelect = page.locator('select[name="discipline"]');
    if (await disciplineSelect.count() > 0) {
      await disciplineSelect.selectOption('КМ');
    }
    
    // Submit
    await page.click('button[type="submit"]:has-text("Создать"), button[type="submit"]:has-text("Create")');
    
    // Verify redirect to document detail
    await page.waitForURL(/\/documents\/\d+/i);
    testDocumentId = Number(page.url().split('/').pop());
    expect(testDocumentId).toBeGreaterThan(0);
    
    // Verify document info
    await expect(page.locator('h1, h2')).toContainText('E2E-DOC-001');
  });

  // --- Step 3: Create Revision ---
  test('Step 3: Should create a new revision', async ({ page }) => {
    await page.goto(`${baseUrl}/documents/${testDocumentId}`);
    
    // Click "Create Revision" button
    await page.click('button:has-text("Создать ревизию"), button:has-text("Create Revision")');
    
    // Wait for modal/dialog
    const modal = page.locator('[role="dialog"], .modal, [data-testid="modal"]');
    await expect(modal).toBeVisible({ timeout: 5000 });
    
    // Fill revision form
    await page.fill('input[name="revision_index"], input[placeholder*="индекс"]', 'A.1');
    await page.fill('textarea[name="change_log"], textarea[placeholder*="изменения"]', 'Initial revision');
    
    // Submit
    await page.click('button:has-text("Создать"), button:has-text("Create")');
    
    // Wait for modal close
    await expect(modal).not.toBeVisible({ timeout: 5000 });
    
    // Verify revision was added to table
    await expect(page.locator('table')).toContainText('A.1');
  });

  // --- Step 4: Approve Revision ---
  test('Step 4: Should approve revision', async ({ page }) => {
    await page.goto(`${baseUrl}/documents/${testDocumentId}`);
    
    // Navigate to Revisions tab if not already there
    const revisionsTab = page.locator('button:has-text("Ревизии"), button:has-text("Revisions")');
    if (await revisionsTab.count() > 0) {
      await revisionsTab.click();
    }
    
    // Find approve button for the first revision
    const approveButton = page.locator('button:has-text("Утвердить"), button:has-text("Approve")').first();
    
    if (await approveButton.count() > 0) {
      await approveButton.click();
      
      // Confirm if dialog appears
      const confirmDialog = page.locator('[role="dialog"]');
      if (await confirmDialog.count() > 0) {
        await confirmDialog.click('button:has-text("Подтвердить"), button:has-text("Confirm")');
      }
    }
    
    // Verify status changed to approved
    await page.waitForTimeout(1000); // Wait for API call
    
    const approvedBadge = page.locator('span:has-text("Утверждён"), span:has-text("Approved")');
    await expect(approvedBadge).toBeVisible();
  });

  // --- Step 5: Verify Current State ---
  test('Step 5: Should verify document is approved', async ({ page }) => {
    await page.goto(`${baseUrl}/documents/${testDocumentId}`);
    
    // Check status badge
    const statusBadge = page.locator('[data-testid="status-badge"], .status-badge');
    if (await statusBadge.count() > 0) {
      await expect(statusBadge).toContainText(/утверждён|approved/i);
    }
    
    // Check current revision
    const currentRevision = page.locator('[data-testid="current-revision"]');
    if (await currentRevision.count() > 0) {
      await expect(currentRevision).toBeVisible();
    }
    
    // Verify document is in approved state
    const documentRow = page.locator('tr:has-text("E2E-DOC-001")');
    if (await documentRow.count() > 0) {
      await expect(documentRow).toContainText(/утверждён|approved/i);
    }
  });

  // --- Cleanup: Delete Test Data ---
  test.afterAll(async ({ page }) => {
    // Note: In real scenario, you would delete test data via API
    // For now, we just log the test IDs
    console.log(`Test data created: Project ${testProjectId}, Document ${testDocumentId}`);
    console.log('Manual cleanup may be required');
  });
});
