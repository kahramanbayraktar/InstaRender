import streamlit as st
import json
import os
import subprocess
import sys
from main import DATA_DIR, OUTPUT_DIR
from converter import parse_markdown

# Page Config
st.set_page_config(
    page_title="InstaRender",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark/Modern Look
st.markdown("""
    <style>
    .stApp {
        background-color: #0f0f0f;
    }
    .stTextInput > div > div > input {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333;
    }
    .stTextArea > div > div > textarea {
        background-color: #1a1a1a;
        color: #a0a0a0;
        font-family: 'Consolas', 'Monaco', monospace;
        border: 1px solid #333;
    }
    .stButton > button {
        background-color: #ff8c00;
        color: white;
        border: none;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }
    .stButton > button:hover {
        background-color: #e67e00;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Oswald', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("📸 InstaRender")
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        st.info("Paste your Markdown script in the editor.")
        st.write("---")
        st.caption("the.root.logic")

    # Layout: 2 Columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Markdown Editor")
        
        # Default placeholder (empty for clean start)
        md_input = st.text_area(
            "Paste your script here:",
            height=600,
            key="md_editor",
            placeholder="### SLIDE 1 (Cover)\nHeader: ...\n..."
        )

    with col2:
        st.subheader("🖼️ Preview & Output")
        
        # ONE BUTTON TO RULE THEM ALL
        if st.button("🚀 GENERATE CAROUSEL"):
            if not md_input.strip():
                st.warning("Please enter some markdown text first.")
            else:
                status_text = st.empty()
                progress = st.progress(0)
                
                try:
                    # 1. Convert Markdown to JSON in memory
                    status_text.text("Parsing Markdown...")
                    progress.progress(10)
                    
                    json_data = parse_markdown(md_input)
                    project_name = json_data.get("project_name", "untitled_project")
                    
                    # 2. Save JSON to temp file
                    status_text.text(f"Saving Logic for '{project_name}'...")
                    progress.progress(30)
                    
                    temp_json_path = os.path.join(DATA_DIR, "_temp_render.json")
                    with open(temp_json_path, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
                    # 3. Call Renderer (Subprocess)
                    status_text.text("Rendering Visuals (Playwright)...")
                    progress.progress(50)
                    
                    python_exe = sys.executable
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    main_py_path = os.path.join(current_dir, "main.py")
                    
                    result = subprocess.run(
                        [python_exe, main_py_path, temp_json_path],
                        capture_output=True,
                        text=True,
                        cwd=current_dir
                    )
                    
                    progress.progress(100)
                    
                    if result.returncode == 0:
                        status_text.success(f"DONE! Visuals for '{project_name}' generated.")
                        
                        # 4. Show Gallery
                        st.write("### Result")
                        final_output_path = os.path.join(OUTPUT_DIR, project_name)
                        if os.path.exists(final_output_path):
                            files = sorted([f for f in os.listdir(final_output_path) if f.endswith('.png')])
                            grid_cols = st.columns(2)
                            for i, file in enumerate(files):
                                file_path = os.path.join(final_output_path, file)
                                with grid_cols[i % 2]:
                                    st.image(file_path, caption=file, use_container_width=True)
                        
                        # Show Debug Info (Optional)
                        with st.expander("Show Generated JSON"):
                            st.json(json_data)
                            
                    else:
                        st.error(f"Render Error: {result.stderr}")
                        
                except Exception as e:
                    st.error(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
