import { test, expect } from "@playwright/test"
import AxeBuilder from "@axe-core/playwright"

test("filters, customer cohorts, order pages and export work together", async ({
  page,
  isMobile,
}) => {
  await page.goto("/")
  await expect(page.getByTestId("revenue")).toContainText("168,944")
  if (isMobile) await page.getByRole("button", { name: "Filters", exact: true }).click()
  await page.getByRole("combobox", { name: "Country", exact: true }).click()
  await page.getByRole("option", { name: "Germany", exact: true }).click()
  if (isMobile)
    await page.getByRole("dialog").getByRole("button", { name: "Close", exact: true }).click()
  await expect(page.getByTestId("revenue")).not.toContainText("168,944")
  await page.getByRole("tab", { name: "Customers", exact: true }).click()
  await expect(page.getByRole("heading", { name: "A reason to return", exact: true })).toBeVisible()
  await expect(page.locator(".cohort-table tbody tr")).toHaveCount(12)
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa"]).analyze())
      .violations,
  ).toEqual([])
  await page.getByRole("tab", { name: "Orders", exact: true }).click()
  const first = await page.locator("tbody tr").first().innerText()
  await page.getByRole("button", { name: "Next orders", exact: true }).click()
  await expect(page.locator("tbody tr").first()).not.toHaveText(first)
  const download = page.waitForEvent("download")
  await page.getByRole("link", { name: "Export data", exact: true }).click()
  expect((await download).suggestedFilename()).toBe("selected_order_lines.csv")
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= screen.width)).toBe(true)
})
