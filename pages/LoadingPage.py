import streamlit as st
import time
import subprocess

st.set_page_config(layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
body {
    background: linear-gradient(135deg,#f5f6fc 0,#ffffff 100%)!important;
    font-family: 'Roboto', Arial, sans-serif;
}
.main .block-container {
    background: #fff;
    border-radius: 32px;
    box-shadow: 0 4px 36px 4px rgba(33,150,243,0.12);
    max-width: 850px;
    padding: 1.6rem 2.2rem 0.7rem 2.2rem;
}
@keyframes terminalOpen {
    from { transform: translateY(100px); opacity: 0; }
    to   { transform: translateY(0);   opacity: 1; }
}
#logbox {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100vw;
    height: 74vh;
    overflow-y: auto;
    background: #101114 !important;
    color: #f8ffe5;
    font-family: 'Roboto Mono', 'monospace', monospace;
    font-size: 1.13rem;
    border-radius: 20px 20px 0 0;
    border-top: 3.5px solid #1976d2;
    box-shadow: 0 -8px 22px 1px rgba(25,118,210,0.10);
    z-index: 1000;
    padding: 1.4rem 2rem 1.2rem 2.1rem;
    animation: terminalOpen 0.65s cubic-bezier(.5,1.5,.55,1.1);
    margin: 0;
}
.material-title {
    color: #1976d2;
    font-family: 'Roboto', Arial, sans-serif;
    font-size: 2.02rem;
    font-weight: 700;
    margin-bottom: 1.2rem;
    text-align: left;
    letter-spacing: 0.01em;
}
.material-btn {
    border-radius: 26px !important;
    background: #1976d2 !important;
    color: #fff !important;
    font-weight: 700;
    font-size: 1.22rem !important;
    box-shadow: 0 2px 9px 1px rgba(33,150,243,0.10) !important;
    padding: 0.67rem 2.8rem !important;
    border: none;
    transition: background 0.13s;
    min-width: 100px !important;
    width: 100% !important;
}
.material-btn:hover {
    background: #1553a1 !important;
}
/* Force all st.button to be wide! */
[data-testid="stButton"] button {
    border-radius: 26px !important;
    background: #101114 !important;
    color: #fff !important;
    font-weight: 500;
    font-size: 0.7rem !important;
    box-shadow: 0 2px 9px 1px rgba(33,150,243,0.10) !important;
    border: none;
    transition: background 0.13s;
    width: 100% !important;           /* full width of column */
    min-width: 0px !important;
    margin-top: 4.4rem;
}
[data-testid="stButton"] button:hover {
    background: #1553a1 !important;
}
.material-log-title {
    letter-spacing: .01em;
    font-size: 1.22rem;
    font-weight: 700;
    color: #1976d2;
    margin-bottom: 1.18rem;
}
</style>
<link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

col_left, col_right = st.columns([8, 1])  
with col_left:
    st.markdown('<div class="material-title">Live CLI Log Terminal</div>', unsafe_allow_html=True)
    status_placeholder = st.empty()
with col_right:
    st.write("")
    # No st.container needed, button is forced wide by CSS
    if st.button("Generate reports", key="to_report2", help="View HTML reports"):
        st.switch_page("pages/report.py")

log_box = st.empty()
output = ""
dots_cycle = ["", ".", "..", "..."]
i = 0

def escape_html(text):
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
    )

command = ["python3", "cli.py", "run", "config/sample_config.json", "--report", "html"]

try:
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, cwd="Core") as proc:
        for line in proc.stdout:
            status_placeholder.markdown(
                f'<span class="material-log-title">Streaming logs{dots_cycle[i % 4]}</span>',
                unsafe_allow_html=True
            )
            i += 1
            output += line
            log_html = f"""
                <div id='logbox'>{escape_html(output)}</div>
                <script>
                var logDiv = document.getElementById("logbox");
                if(logDiv) {{ logDiv.scrollTop = logDiv.scrollHeight; }}
                </script>
            """
            log_box.markdown(log_html, unsafe_allow_html=True)
            time.sleep(0.1)
        retcode = proc.wait()
        if retcode != 0:
            st.error(f"Process exited with error code {retcode}")
except Exception as e:
    import traceback
    st.error("Error running command: " + repr(e))
    st.code(traceback.format_exc())

status_placeholder.markdown(
    '<span class="material-log-title">Streamed log</span>',
    unsafe_allow_html=True
)
