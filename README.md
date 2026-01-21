# Instagram Carousel Generator

A Python tool to generate high-quality Instagram carousel images from JSON input using Playwright and HTML/CSS templates.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**
   This is critical for the renderer to work.
   ```bash
   playwright install
   ```

## Usage

Run the tool with the sample data:
```bash
python main.py
```

Run with your own JSON file:
```bash
python main.py path/to/your/input.json
```

## Input Format (JSON)

See `data/sample.json` for an example. Key fields:
- `project_name`: Used for the output folder name.
- `slides`: Array of slide objects.
  - `type`: `cover`, `content`, `mechanism`, or `dictionary`.
  - Content fields vary by type (`title`, `subtitle`, `body`, `steps`, `terms`).

## Output

Images are saved in `output/{project_name}/` as `01.png`, `02.png`, etc.
