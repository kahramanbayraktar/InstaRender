import argparse
import json
import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from renderer import render_slides

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_template(data):
    # Setup Jinja2 environment
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('base.html')
    
    # Render with data
    # The JSON structure has 'project_name' and 'slides'.
    # We pass these directly to the template.
    return template.render(**data)

async def main():
    parser = argparse.ArgumentParser(description="Instagram Carousel Generator")
    parser.add_argument("json_file", help="Path to the input JSON file", nargs='?', default="data/sample.json")
    
    args = parser.parse_args()
    
    print(f"Reading configuration from: {args.json_file}")
    
    try:
        data = load_json(args.json_file)
    except FileNotFoundError:
        print(f"Error: File {args.json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args.json_file}.")
        return

    print(f"Project: {data.get('project_name', 'Unknown')}")
    print("Rendering HTML template...")
    
    html_content = render_template(data)
    
    print("Starting Playwright renderer...")
    await render_slides(html_content, data.get('project_name', 'default_project'))
    
    print("Done! Check the output directory.")

if __name__ == "__main__":
    asyncio.run(main())
