import streamlit as st
import time

st.set_page_config(layout="centered")

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)

cols = st.columns([1,6,1])

with cols[1]:
    st.markdown("<h1 style='text-align:center;'>Loading reports</h1>", unsafe_allow_html=True)
    # Display custom spinner/image for better centering
    st.markdown("<div style='text-align:center;'><img src='https://i.imgur.com/llF5iyg.gif' width='50'/><br>Processing...</div>", unsafe_allow_html=True)
    time.sleep(2)  # Simulate work

st.switch_page("pages/report.py")
