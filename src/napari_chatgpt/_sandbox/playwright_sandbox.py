import asyncio

from playwright.async_api import Playwright, async_playwright


async def run(playwright: Playwright) -> None:
    # Launch the headed browser instance (headless=False)
    # To see the process of playwright scraping
    # chromium.launch - opens a Chromium browser
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()  # Creates a new browser context
    page = await context.new_page()  # Open new page
    await page.goto("https://scrapeme.live/shop/")  # Go to the chosen website

    # You scraping functions go here

    # Turn off the browser and context once you have finished
    await context.close()
    await browser.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
