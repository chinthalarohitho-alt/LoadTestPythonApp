import streamlit as st
import pandas as pd

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
""", unsafe_allow_html=True)
    

st.set_page_config(layout="wide")

# with st.sidebar:
#       st.header('Menu')
#       refresh_value = st.slider("Choose a value for autorefresh (seconds)", 1, 10, value=5)
#       enable_refresh = st.checkbox("Enable auto-refresh")

st.markdown(
    "<h2 style='text-align: center;'>Analysis of Load Test Data</h2>",
    unsafe_allow_html=True
)
st.markdown("&nbsp;") 

data = {
    "x": [5, 1, 9, 14],
    "y": [10, 15, 10, 0]
    }
df = pd.DataFrame(data)


# Convert to CSV
csv = df.to_csv(index=False).encode('utf-8')


# Layout: empty columns to create space, button at the right
col1, col2, col3 = st.columns([5, 1, 1])
with col3:
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="dashboard_data.csv",
        mime="text/csv"
    )

col1, col2 = st.columns(2)
with col1 : 
     st.line_chart(
        df,
        x_label="x-axis", 
        y_label="y-axis", 
        color=["#fd0", "#f0f"]
     )
     
with col2 : 
     st.line_chart(
        df,
        x_label="x-axis", 
        y_label="y-axis", 
        color=["#fd0", "#f0f"]
    )
     
     
col3, col4 = st.columns(2)
with col3 : 
     st.line_chart(
        df,
        x_label="x-axis", 
        y_label="y-axis", 
        color=["#fd0", "#f0f"]
     )
     
with col4 : 
     st.line_chart(
        df,
        x_label="x-axis", 
        y_label="y-axis", 
        color=["#fd0", "#f0f"]
    )
     
if st.button("Go to JSON Input"):
    st.switch_page("app.py")      