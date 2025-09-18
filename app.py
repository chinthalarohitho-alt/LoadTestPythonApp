import streamlit as st
import json 
    
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)
    
st.set_page_config(layout="centered")

st.title("Provide JSON")
json_data = st.text_area("Paste your JSON here", height="content")  # Add height="content"

example_json = {
    "name": "John Doe",
    "age": 30,
    "skills": ["Python", "Streamlit"],
    "contact": {"email": "john@example.com"}
}


if st.button("Submit JSON"):
    try:
        parsed = json.loads(json_data)
        st.session_state["json_data"] = json_data
        st.switch_page("pages/LoadingPage.py")
    except json.JSONDecodeError as e:
        lines = json_data.splitlines()
        error_line = e.lineno
        error_content = lines[error_line - 1] if 0 < error_line <= len(lines) else "(No content found)"
        st.error(f"Invalid JSON at line {error_line}: {error_content}\n{e.msg}")
        st.info("Your JSON should look like this:\n")
        st.json(example_json)
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.info("Your JSON should look like this:\n")
        st.json(example_json)
        
        