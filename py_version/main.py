import argparse
import json
import os
import sys
import asyncio

# WINDOWS FIX: Playwright/Asyncio NotImplementedError
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from jinja2 import Environment, FileSystemLoader
from renderer import render_slides

# Base paths
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(LOCAL_DIR)

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates') # Back to common
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_template(data):
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('base.html')
    return template.render(**data)

def main():
    default_json = os.path.join(DATA_DIR, 'sample.json')
    
    parser = argparse.ArgumentParser(description="Instagram Carousel Generator")
    parser.add_argument("json_file", help="Path to the input JSON file", nargs='?', default=default_json)
    
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
    render_slides(html_content, data.get('project_name', 'default_project'), OUTPUT_DIR)
    
    print("Done! Check the output directory.")

if __name__ == "__main__":
    main()
