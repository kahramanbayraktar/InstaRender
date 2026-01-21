import streamlit as st
import json
import os
import subprocess
import sys
from main import DATA_DIR, OUTPUT_DIR

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
    st.markdown("Instagram Carousel Generator - Python Version")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Load default sample if available
        default_json_path = os.path.join(DATA_DIR, "sample.json")
        default_json = ""
        try:
            with open(default_json_path, "r", encoding="utf-8") as f:
                default_json = f.read()
        except FileNotFoundError:
            default_json = '{"project_name": "demo", "slides": []}'

        st.info("Edit the JSON configuration to customize your slides.")
        st.write("---")
        st.caption("the.root.logic")

    # Layout: 2 Columns (Editor vs Preview)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Content Editor (JSON)")
        json_input = st.text_area(
            "Slide Logic:",
            value=default_json,
            height=600
        )

    with col2:
        st.subheader("🖼️ Preview & Output")
        
        # Parse JSON
        try:
            data = json.loads(json_input)
            project_name = data.get("project_name", "untitled_project")
        except json.JSONDecodeError:
            project_name = "error"
            st.error("Invalid JSON format!")
        
        if st.button("🚀 Render Carousel Images") and project_name != "error":
            status_text = st.empty()
            
            try:
                # 1. Save current JSON to a temporary file
                temp_json_path = os.path.join(DATA_DIR, "_temp_render.json")
                with open(temp_json_path, "w", encoding="utf-8") as f:
                    f.write(json_input)
                
                status_text.info("Rendering in progress (External Process)...")
                
                # 2. Call main.py as a separate process
                python_exe = sys.executable
                current_dir = os.path.dirname(os.path.abspath(__file__))
                main_py_path = os.path.join(current_dir, "main.py")
                
                result = subprocess.run(
                    [python_exe, main_py_path, temp_json_path],
                    capture_output=True,
                    text=True,
                    cwd=current_dir
                )
                
                if result.returncode == 0:
                    status_text.success(f"Generated slides in 'output/{project_name}'!")
                    
                    # 3. Show Gallery
                    st.write("### Result")
                    final_output_path = os.path.join(OUTPUT_DIR, project_name)
                    if os.path.exists(final_output_path):
                        files = sorted([f for f in os.listdir(final_output_path) if f.endswith('.png')])
                        grid_cols = st.columns(2)
                        for i, file in enumerate(files):
                            file_path = os.path.join(final_output_path, file)
                            with grid_cols[i % 2]:
                                st.image(file_path, caption=file, use_container_width=True)
                else:
                    st.error(f"Render Error: {result.stderr}")
                    
            except Exception as e:
                st.error(f"UI Error: {e}")

if __name__ == "__main__":
    main()
