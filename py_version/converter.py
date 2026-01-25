import re
import json
import argparse

def parse_markdown(md_content):
    """
    Parses a specific simplified text format into InstaRender JSON.
    Format is Header: Value line based.
    """
    lines = md_content.splitlines()
    slides = []
    project_name = "untitled_project"
    account_handle = "@the.root.logic" # Default
    
    # 1. Global Metadata (Project Name, Brand)
    # We look at valid lines until the first SLIDE
    header_buffer = []
    
    # Pre-scan for project name clues before first slide or generic content
    for line in lines:
        if line.upper().startswith("SLIDE"):
            break
        header_buffer.append(line)
        
    for line in header_buffer:
        line = line.strip()
        if not line: continue
        if line.startswith("# ") or line.startswith("Project:"):
            val = line.split(":", 1)[-1].strip() if ":" in line else line.replace("#", "").strip()
            project_name = val.lower().replace(" ", "_")
        if "Brand" in line:
            account_handle = line.split(":", 1)[-1].strip()

    # 2. Slide Parsing
    # We will buffer lines between "SLIDE X" markers
    
    slide_pattern = re.compile(r"^SLIDE \d+\s*\((.+)\)", re.IGNORECASE)
    
    current_slide_lines = []
    
    def process_buffer(buffer):
        if not buffer: return None
        
        # Detect type from first line: SLIDE 1 (The Cover)
        header_line = buffer[0].strip()
        type_match = slide_pattern.match(header_line)
        
        slide_type = "content" # default
        if type_match:
            raw_type = type_match.group(1).lower()
            if "cover" in raw_type: slide_type = "cover"
            elif "quote" in raw_type: slide_type = "quote"
            elif "resource" in raw_type or "kaynak" in raw_type: slide_type = "resources"
            elif "dictionary" in raw_type or "sözlük" in raw_type or "knowledge" in raw_type: slide_type = "dictionary"
            elif "mechanism" in raw_type: slide_type = "mechanism"
        
        slide_data = {"type": slide_type}
        
        # Parse Key-Values
        # Keys: Header, SubHeader, Text, Author, Visual Prompt, Ref
        current_key = None
        current_text_buffer = [] 
        
        key_map = {
            "header": "title",
            "subheader": "subtitle",
            "text": "body",
            "author": "author",
            "visual prompt": "visual",
            "ref": "ref"
        }
        
        # Helper to flush text buffer to the last active key
        def flush_text(s_data, key, txt_list):
            if not key or not txt_list: return
            
            full_text = "\n".join(txt_list).strip()
            if not full_text: return

            # Special handling for Lists inside Text
            # If text contains lines starting with "- ", convert to HTML list
            if "- " in full_text and (slide_type == "content" or slide_type == "cover"):
                # Basic markdown list to HTML conversion
                html_lines = []
                in_list = False
                for t_line in txt_list:
                    t_line = t_line.strip()
                    if t_line.startswith("- ") or t_line.startswith("• "):
                        if not in_list: 
                            html_lines.append('<ul class="list-disc pl-8 space-y-4 mt-4 text-4xl">')
                            in_list = True
                        content = t_line[2:]
                        # Bold parsing: **text** -> <strong>text</strong>
                        content = re.sub(r"\*\*(.+?)\*\*", r"<strong class='text-white'>\1</strong>", content)
                        html_lines.append(f"<li class='text-gray-300'>{content}</li>")
                    else:
                        if in_list: 
                            html_lines.append("</ul>")
                            in_list = False
                        
                        # Bold parsing for regular lines
                        t_line = re.sub(r"\*\*(.+?)\*\*", r"<strong class='text-accent'>\1</strong>", t_line)
                        html_lines.append(f"<p class='mb-4'>{t_line}</p>")
                
                if in_list: html_lines.append("</ul>")
                s_data[key] = "".join(html_lines)
            
            elif key == "body":
                # Regular body text with bold support
                # Convert newlines to breaks for regular paragraphs
                processed_lines = []
                for t_line in txt_list:
                    if not t_line.strip(): continue
                    # Bold parsing
                    t_line = re.sub(r"\*\*(.+?)\*\*", r"<strong class='text-accent'>\1</strong>", t_line)
                    
                    # Sentence Splitting: Replace (. ? !) followed by space with active line break
                    # We use a negative lookbehind to avoid splitting like "Dr." or "Mr." if possible, but keeping it simple for now
                    # This allows "Sentence 1. Sentence 2." -> "Sentence 1.<br>Sentence 2."
                    t_line = re.sub(r'([.?!])\s+', r'\1<br>', t_line)
                    
                    processed_lines.append(t_line)
                s_data[key] = "<br><br>".join(processed_lines)
                
            elif key == "ref":
                # Refs are appended to body usually, or separate field
                # Format: (1) Blah -> [1] Blah
                # Remove parens if they exist strictly, but mainly formatting the container
                formatted_ref = full_text.replace("(", "[").replace(")", "]")
                ref_html = f"<div class='mt-12 pt-6 border-t border-gray-800 text-secondary text-3xl font-light'>{formatted_ref}</div>"
                if "body" in s_data:
                    s_data["body"] += ref_html
                else:
                    s_data["body"] = ref_html
            
            else:
                # Title, Subtitle etc.
                s_data[key] = full_text

        
        # Specific Logic for Dictionary & Resources which are list-based
        if slide_type == "dictionary":
            terms = []
            for l in buffer[1:]:
                l = l.strip()
                if not l: continue
                # - **Term:** Def
                m = re.match(r"^-\s*\*\*(.+?):\*\*\s*(.*)", l)
                if m:
                    terms.append({"key": m.group(1), "definition": m.group(2)})
            if terms: slide_data["terms"] = terms
            # Also capture Header if exists
            for l in buffer[1:]:
                if l.startswith("Header:"): slide_data["title"] = l.split(":",1)[1].strip()

        elif slide_type == "resources":
            items = []
            for l in buffer[1:]:
                l = l.strip()
                if not l: continue
                # [1] ... or - ...
                if l.startswith("[") or l.startswith("-") or l[0].isdigit():
                    clean = re.sub(r"^[-*]\s*", "", l)
                    items.append(clean)
            if items: slide_data["resource_items"] = items
            # Capture Header
            for l in buffer[1:]:
                if l.startswith("Header:"): slide_data["title"] = l.split(":",1)[1].strip()
        
        else:
            # Standard Parsing for Content, Cover, Quote
            for line in buffer[1:]:
                line = line.strip()
                if not line: continue
                
                # Check if line starts with a known key
                is_key_line = False
                lower_line = line.lower()
                
                for k in key_map:
                    if lower_line.startswith(k + ":"):
                        # Flush previous
                        flush_text(slide_data, current_key, current_text_buffer)
                        
                        # Start new
                        current_key = key_map[k]
                        current_text_buffer = []
                        val = line.split(":", 1)[1].strip()
                        if val: current_text_buffer.append(val)
                        is_key_line = True
                        break
                
                if not is_key_line:
                    # Append to current buffer
                    if current_key:
                        current_text_buffer.append(line)
            
            # Flush final buffer
            flush_text(slide_data, current_key, current_text_buffer)

        # Post-process: specific key mappings per type
        if slide_type == "quote" and "body" in slide_data:
            slide_data["quote"] = slide_data["body"]
            
        return slide_data

    # Main Loop
    current_buffer = []
    
    for line in lines:
        if line.upper().startswith("SLIDE "):
            if current_buffer:
                s = process_buffer(current_buffer)
                if s: slides.append(s)
            current_buffer = [line]
        else:
            if current_buffer: 
                current_buffer.append(line)
    
    # Last one
    if current_buffer:
        s = process_buffer(current_buffer)
        if s: slides.append(s)
        
    return {
        "project_name": project_name,
        "account_handle": account_handle,
        "slides": slides
    }

if __name__ == "__main__":
    import sys
    # Quick test
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            print(json.dumps(parse_markdown(f.read()), indent=2, ensure_ascii=False))
