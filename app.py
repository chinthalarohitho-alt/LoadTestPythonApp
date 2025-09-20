import streamlit as st
import json
from streamlit_elements import elements, mui
import streamlit.components.v1 as components
import time
from datetime import datetime

st.set_page_config(page_title="Provide JSON", layout="centered")

# ================== STYLES ==================
st.markdown("""
<style>
/* Animation */

.stTextArea textarea::placeholder {
    color: #1976d2;  /* placeholder color */
    opacity: 0;
    transform: translateY(-10px);
    transition: all 0.6s ease-in-out;
    font-weight: 500;
}

/* Animate when textarea is empty */
.stTextArea textarea:hover::placeholder,
.stTextArea textarea:not(:placeholder-shown)::placeholder {
    opacity: 0.5;  /* partially visible on focus/typing */
    transform: translateY(0);
}

/* Optional: smooth fade-in when page loads */
.stTextArea textarea::placeholder {
    animation: placeholderFade 1s ease forwards;
}

@keyframes placeholderFade {
    0% {
        opacity: 0;
        transform: translateY(-10px);
    }
    50% {
        opacity: 0.3;
        transform: translateY(-5px);
    }
    100% {
        opacity: 0.5;
        transform: translateY(0);
    }
}


@keyframes fadeDownIn {
    0% {
        opacity: 0;
        transform: translateY(-40px);
    }
    50% {
        opacity: 0.5;
        transform: translateY(-15px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
.fade-down-animate {
    animation: fadeDownInSmooth 0.8s ease-out both;
    transition: all 0.5s ease-out;
}

/* Textarea hover & focus */
.stTextArea:hover textarea,
.stTextArea:focus-within textarea {
    transform: translateY(-2px) scale(1.01);
    min-height: 200px !important;
    box-shadow: 0 6px 20px 4px rgba(33,150,243,0.25) !important;
    background: #f0f4ff !important;
    transition: all 0.35s ease-in-out;
    cursor: text;
}

/* Textarea default */
.stTextArea textarea {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.82rem;
    border-radius: 19px;
    border: 2px solid #e2e8f0;
    background: #f4f7fc !important;
    min-height: 120px !important;
    max-height: 400px;
    width: 100% !important;
    resize: vertical !important;
    box-shadow: 0 1px 12px 1px rgba(33,150,243,0.06) !important;
    padding: 0.72rem 1rem !important;
    transition: all 0.3s ease;
    cursor: text;
}

/* Main container */
.main-container, .main-container.has-content {
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0 !important;
    margin: 28vh auto 0 auto !important;
    width: 98vw !important;
    transition: all 0.55s cubic-bezier(.45,1.24,.54,1.01);
}
.main-container.has-content {
    margin: 2vh auto 0 auto !important;
}
.main-container .block {
    border-radius: 36px;
    max-width: 100% !important;
}

/* Typography & Alerts */
.material-alert-success {
    background: #e4f8e5;
    border-left: 7px solid #69d36a;
    color: #185a1e;
    font-weight: 500;
    border-radius: 15px;
    margin: 1.1rem 0 1.21rem 0;
    padding: 0.72rem 1.14rem;
}
.material-alert-error {
    background: #fff2ef;
    border-left: 7px solid #f44336;
    color: #9c1c20;
    font-weight: 600;
    border-radius: 15px;
    margin: 1.1rem 0 1.16rem 0;
    padding: 0.74rem 1.13rem;
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
    word-break: break-word;
}
.material-alert-error code {
    width: 100% !important;
    max-width: 100%;
    display: block !important;
    box-sizing: border-box !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    font-size: 1.05rem;
}
.material-alert-info {
    background: #f0f3fb;
    border-left: 6px solid #1976d2;
    color: #3949ab;
    font-weight: 500;
    border-radius: 14px;
    margin: 0.37rem 0 1.07rem 0;
    padding: 0.63rem 1.2rem;
}
</style>
<link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ================== FUNCTIONS ==================
def calc_height(s, minheight=120, maxheight=600):
    lines = len(s.splitlines()) if s else 1
    return min(maxheight, max(minheight, 32 * lines + 20))

example_json = {
  "baseUrl": "https://httpbin.org",
  "stages": [
    { "duration": "10s", "target": 100 },
    { "duration": "50s", "target": 100 }
  ],
  "thresholds": {
    "http_req_duration": ["p(95)<800"],
    "checks": ["rate>0.98"]
  },
  "tags": { "env": "demo", "service": "httpbin" },
  "sleep": 0.2
}

json_path = "./Core/config/"

if "json_str" not in st.session_state:
    st.session_state["json_str"] = ""

# ================== MAIN WRAPPER ==================
main_class = "main-container has-content" if st.session_state["json_str"].strip() else "main-container"
st.markdown(f'<div class="{main_class}"><div class="block">', unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown('<div id="top-card"></div>', unsafe_allow_html=True)

with elements("material-header-card"):
    mui.Grid(
        container=True,
        spacing=3,
        sx={"marginBottom": 3},
        children=[
            mui.Grid(
                item=True,
                xs=12,
                children=mui.Paper(
                    elevation=8,
                    sx={
                        "borderRadius": "28px",
                        "padding": "14px 1px",
                        "background": "#fff",
                        "boxShadow": "0 4px 12px 4px rgba(33,150,243,0.13)",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "width": "32%",
                        "margin": "0 auto"
                    },
                    children=[
                        mui.Typography(
                            "Load Test",
                            variant="h5",
                            sx={
                                "color": "#1976d2",
                                "fontWeight": 700,
                                "fontSize": "1.5rem",
                                "fontFamily": "'Roboto','Arial',sans-serif",
                                "textAlign": "center",
                                "width": "100%"
                            }
                        )
                    ]
                )
            ),
            mui.Grid(
                item=True,
                xs=23,
                children=mui.Paper(
                    elevation=8,
                    sx={
                        "borderRadius": "28px",
                        "padding": "14px 1px",
                        "background": "#fff",
                        "boxShadow": "0 4px 12px 4px rgba(33,150,243,0.13)",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "width": "18%",
                        "margin": "0 auto"
                    },
                    children=[
                        mui.Typography(
                            "powered by QA",
                            variant="h5",
                            sx={
                                "color": "#1976d2",
                                "fontWeight": 500,
                                "fontSize": "0.8rem",
                                "fontFamily": "'Roboto','Arial',sans-serif",
                                "textAlign": "center",
                                "width": "100%"
                            }
                        )
                    ]
                )
            )
        ]
    )

# ================== TEXTAREA ==================
json_str = st.text_area(
    label="Paste JSON here",
    value=st.session_state["json_str"],
    key="json_str",
    height=calc_height(st.session_state["json_str"]),
    placeholder="Provide JSON here",   # <-- This adds the placeholder inside
    label_visibility="collapsed"
)

# ================== VALIDATION ==================
is_valid = False
error_line = None

if not json_str.strip():
    st.markdown('', unsafe_allow_html=True)
else:
    try:
        json.loads(json_str)
        is_valid = True
    except json.JSONDecodeError as e:
        error_line = e.lineno
        lines = json_str.splitlines()
        above_line = lines[error_line - 2] if error_line > 1 else ""
        error_line_content = lines[error_line - 1] if 0 < error_line <= len(lines) else "(No content)"
        below_line = lines[error_line] if error_line < len(lines) else ""
        context_html = ""
        if above_line:
            context_html += f'<code style="background:#f3f6fa;padding:0.17rem 0.4rem;border-radius:7px;display:block;margin-bottom:2px;">{above_line}</code>'
        context_html += f'<code style="background:#fff3f5;padding:0.19rem 0.4rem;border-radius:7px;display:block;margin-bottom:2px;border-left:5px solid #f44336;">{error_line_content}</code>'
        if below_line:
            context_html += f'<code style="background:#f3f6fa;padding:0.17rem 0.4rem;border-radius:7px;display:block;margin-bottom:2px;">{below_line}</code>'
        st.markdown(f'<div class="material-alert-error fade-down-animate">Invalid JSON at line <b>{error_line}</b>:<br>{context_html}<br><b>{e.msg}</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="material-alert-info fade-down-animate">Example JSON:</div>', unsafe_allow_html=True)
        st.code(json.dumps(example_json, indent=2), language="json")

# ================== SUCCESS ==================
if json_str.strip() and is_valid:
    status_placeholder = st.markdown(
        '<div class="material-alert-success fade-down-animate">JSON is valid!</div>',
        unsafe_allow_html=True
    )
    

    if st.button("Submit JSON", disabled=not is_valid):
        # Parse JSON
        parsed_json = json.loads(json_str)

        # Create filename based on current datetime
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
        full_path = f"{json_path}{filename}"

        # Write JSON to file with pretty formatting
        with open(full_path, "w") as f:
            json.dump(parsed_json, f, indent=2)

        # Also write to sample_config.json in the same path
        sample_path = f"{json_path}sample_config.json"
        with open(sample_path, "w") as f:
         json.dump(parsed_json, f, indent=2)
    
        # Optional: show next message before switching
        status_placeholder.markdown(
            '<div class="material-alert-info fade-down-animate">Lets move to console</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.5)

        # Switch to the next page
        st.switch_page("pages/LoadingPage.py")


st.markdown("</div></div>", unsafe_allow_html=True)  # close block + main-container
