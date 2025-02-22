import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:8000/');
  await page.getByRole('link', { name: 'Waerboom' }).click();
  await page.getByRole('link', { name: 'name Gastronomisch buffet op' }).getByRole('button').click();
  await page.locator('.mt-3 > .p-4').first().click();
  await page.getByRole('listitem').filter({ hasText: 'x Gastronomisch buffet prijzen (17-...): €97.00 = €' }).locator('#amount').click();
  await page.getByRole('listitem').filter({ hasText: 'x Gastronomisch buffet prijzen (17-...): €97.00 = €' }).locator('#amount').fill('3');
  await page.getByRole('textbox', { name: 'your-email@address.com' }).fill('pieter@hotmail.com');
  await page.getByRole('button', { name: 'REQUEST RESERVATION' }).click();
  await expect(page.getByRole('dialog')).toContainText('reservation requested');
});
