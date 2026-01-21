import asyncio
import os
from playwright.async_api import async_playwright

async def render_slides(html_content: str, project_name: str, output_base_dir: str = "output"):
    """
    Renders the HTML content in a headless browser and takes screenshots of each slide.
    """
    output_dir = os.path.join(output_base_dir, project_name)
    os.makedirs(output_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # We start a context. No need for a specific viewport on the context 
        # because the elements have fixed size, but setting it helps debugging/defaults.
        context = await browser.new_context(viewport={"width": 1080, "height": 1350})
        page = await context.new_page()

        # Load the HTML content. We can use set_content method.
        await page.set_content(html_content, wait_until="networkidle")

        # Find all slide containers
        # We assume IDs are slide-1, slide-2, etc.
        # We can find them dynamically.
        locators = page.locator(".slide-container")
        count = await locators.count()
        
        print(f"Found {count} slides. Generating images...")

        for i in range(count):
            slide_index = i + 1
            # Select the slide element
            slide = locators.nth(i)
            
            # File name: 01.png, 02.png...
            filename = f"{slide_index:02d}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Take screenshot of the specific element
            await slide.screenshot(path=filepath, type="png")
            print(f"Saved: {filepath}")

        await browser.close()
