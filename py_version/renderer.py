import os
from playwright.sync_api import sync_playwright

def render_slides(html_content: str, project_name: str, output_base_dir: str = "output"):
    """
    Renders the HTML content in a browser and takes screenshots of each slide (Sync version).
    """
    output_dir = os.path.join(output_base_dir, project_name)
    os.makedirs(output_dir, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser synchronously
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1080, "height": 1350})
        page = context.new_page()

        # Set content
        page.set_content(html_content, wait_until="networkidle")

        locators = page.locator(".slide-container")
        count = locators.count()
        
        print(f"Found {count} slides. Generating images...")

        for i in range(count):
            slide_index = i + 1
            slide = locators.nth(i)
            
            filename = f"{slide_index:02d}.png"
            filepath = os.path.join(output_dir, filename)
            
            # Take screenshot synchronously
            slide.screenshot(path=filepath, type="png")
            print(f"Saved: {filepath}")

        browser.close()
