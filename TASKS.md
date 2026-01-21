# Project Tasks & Roadmap

## Phase 1: Python MVP (Active)
- [x] Core Logic (JSON -> HTML with Jinja2)
- [x] Rendering Engine (Playwright Screenshot)
- [x] CLI Tool (main.py)
- [x] Streamlit UI (app.py) implementation
- [x] Refactor folder structure (move python files to `py_version` folder)
- [ ] Verify Streamlit app works after refactor

## Phase 2: Go Implementation (Learning Goal)
- [ ] Initialize Go module in `go_version/`
- [ ] Implement CLI in Go (rendering logic port)
- [ ] Integrate `pongo2` or similar to reuse existing Jinja2 templates
- [ ] Benchmark performance against Python version

## Phase 3: Laravel Implementation (SaaS Goal)
- [ ] Setup Laravel project
- [ ] Create simple web interface (Blade templates)
- [ ] Implement Job Queue for rendering (using the Go or Python CLI as a worker)
- [ ] User authentication and project saving
