# import streamlit as st
# import pandas as pd
# import altair as alt
# import json
# import os
# import time
# from statistics import mean
# from pathlib import Path
# from fpdf import FPDF
# import tempfile
# from streamlit_elements import elements, mui

# st.set_page_config(layout="wide")

# st.markdown("""
#     <style>
#     .block-container {
#         padding-top: 0.5rem !important;
#         padding-left: 1rem !important;
#         padding-right: 1rem !important;
#     }
#     div[data-testid="stHorizontalBlock"] > div {
#         gap: 1rem !important;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <style>
# [data-testid="stSidebar"] {display: none;}
# [data-testid="collapsedControl"] {display: none;}
# </style>
# """, unsafe_allow_html=True)

# RESULTS_PATH = "./Core/scripts/results.json"

# def fix_stacked_json(results_path):
#     if not os.path.exists(results_path):
#         return [], 0
#     try:
#         with open(results_path, "r") as f:
#             data = json.load(f)
#         if isinstance(data, list) and all(isinstance(x, dict) for x in data):
#             return data, 0
#     except Exception:
#         pass
#     metrics_list = []
#     skipped_lines = 0
#     with open(results_path, "r") as f:
#         for line_num, line in enumerate(f, 1):
#             line_strip = line.strip()
#             if not line_strip:
#                 skipped_lines += 1
#                 continue
#             try:
#                 obj = json.loads(line_strip)
#                 if isinstance(obj, dict):
#                     metrics_list.append(obj)
#                 else:
#                     skipped_lines += 1
#             except json.JSONDecodeError:
#                 skipped_lines += 1
#                 continue
#     with open(results_path, "w") as f:
#         json.dump(metrics_list, f, indent=2)
#     return metrics_list, skipped_lines

# def percentile(values, percentile):
#     if not values:
#         return 0
#     sorted_vals = sorted(values)
#     k = (len(sorted_vals) - 1) * (percentile / 100.0)
#     f = int(k)
#     c = min(f + 1, len(sorted_vals) - 1)
#     if f == c:
#         return sorted_vals[int(k)]
#     d0 = sorted_vals[f] * (c - k)
#     d1 = sorted_vals[c] * (k - f)
#     return d0 + d1

# def compute_metrics(events):
#     check_points = [d for d in events if d.get("type") == "Point" and d.get("metric") == "checks"]
#     http_req_points = [d for d in events if d.get("type") == "Point" and d.get("metric") == "http_req_duration"]
#     http_reqs_points = [d for d in events if d.get("type") == "Point" and d.get("metric") == "http_reqs"]

#     total_checks = len(check_points)
#     passed_checks = sum(1 for c in check_points if c.get("data", {}).get("value") == 1)
#     failed_checks = total_checks - passed_checks
#     pass_rate = (passed_checks / total_checks * 100.0) if total_checks else 0.0
#     durations_ms = [float(p.get("data", {}).get("value", 0)) for p in http_req_points]
#     avg_ms = mean(durations_ms) if durations_ms else 0
#     p90_ms = percentile(durations_ms, 90) if durations_ms else 0
#     p95_ms = percentile(durations_ms, 95) if durations_ms else 0
#     min_ms = min(durations_ms) if durations_ms else 0
#     max_ms = max(durations_ms) if durations_ms else 0
#     total_http_reqs = len(http_reqs_points)
#     return {
#         "total_checks": total_checks,
#         "passed_checks": passed_checks,
#         "failed_checks": failed_checks,
#         "pass_rate": pass_rate,
#         "total_http_reqs": total_http_reqs,
#         "avg_ms": avg_ms,
#         "p90_ms": p90_ms,
#         "p95_ms": p95_ms,
#         "min_ms": min_ms,
#         "max_ms": max_ms,
#     }

# def load_json_metrics(path):
#     records = []
#     try:
#         with open(path, "r") as f:
#             first = f.read(1)
#             if not first:
#                 return []
#             f.seek(0)
#             if first == '[':
#                 records = json.load(f)
#             else:
#                 f.seek(0)
#                 for line in f:
#                     line = line.strip()
#                     if not line:
#                         continue
#                     try:
#                         records.append(json.loads(line))
#                     except Exception:
#                         continue
#     except Exception as e:
#         st.error(f"Failed to read metrics: {e}")
#     return records

# def get_df(records):
#     rows = []
#     for r in records:
#         d = {}
#         d["metric"] = r.get("metric")
#         d["type"] = r.get("type")
#         data = r.get("data", {})
#         d["time"] = data.get("time")
#         d["value"] = float(data.get("value", 0))
#         tags = data.get("tags", {})
#         for k, v in tags.items():
#             d[k] = v
#         rows.append(d)
#     return pd.DataFrame(rows)

# pdf = FPDF()
# pdf.add_page()
# pdf.set_font("Arial", "B", 16)
# pdf.cell(0, 10, "VUs vs Response Time", ln=True, align="C")

# def main():
#     st.set_page_config(page_title="Load Test Dashboard", layout="wide")
#     st.markdown("<h1 style='text-align: center;'>Analysis of Load Test Data</h1>", unsafe_allow_html=True)
#     st.markdown("<br>", unsafe_allow_html=True)
#     records = load_json_metrics(RESULTS_PATH)
#     if not records:
#         st.error("No load test data found or file format not recognized.")
#         st.stop()
#     df = get_df(records)
#     df["timestamp"] = pd.to_datetime(df["time"], errors="coerce")

#     auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
#     refresh_secs = st.sidebar.slider("Refresh interval (sec)", 0, 10, 3)
#     metrics_json, skipped_lines = fix_stacked_json(RESULTS_PATH)
#     if skipped_lines > 0:
#         st.warning(f"Skipped {skipped_lines} empty or invalid lines in {RESULTS_PATH}")
#     if not metrics_json:
#         st.info("No results found. Run your test to generate results.json.")
#         return
#     m = compute_metrics(metrics_json)
#     col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
#     col1.metric("HTTP Requests", m["total_http_reqs"])
#     col2.metric("Checks Passed", f"{m['passed_checks']}")
#     col3.metric("Avg Duration (s)", f"{m['avg_ms']/1000:.2f}s")
#     col4.metric("p95 (s)", f"{m['p95_ms']/1000:.2f}s")
#     st.markdown("<br>", unsafe_allow_html=True)

#     col_left, col_right = st.columns([3, 1])

#     with col_left:
#         vu_metrics = [m for m in records if m.get("metric") == "vus"]
#         valid_vu = [
#             m for m in vu_metrics
#             if isinstance(m.get("data", None), dict)
#             and "time" in m["data"] and "value" in m["data"]
#         ]
#         resp_ms = df[df["metric"] == "http_req_duration"]
#         if valid_vu and not resp_ms.empty:
#             df_vu = pd.DataFrame([
#                 {"Time": pd.to_datetime(m["data"]["time"]), "VUs": m["data"]["value"]}
#                 for m in valid_vu
#             ])
#             df_resp = resp_ms.set_index("timestamp")["value"].resample("1S").mean().reset_index()
#             df_resp = df_resp.rename(columns={"value": "ResponseTime", "timestamp": "Time"})
#             max_vus = df_vu["VUs"].max()
#             max_resp = df_resp["ResponseTime"].max()
#             zoom = alt.selection_interval(bind="scales", encodings=["x"])

#             vu_chart = alt.Chart(df_vu).mark_line(
#                 color="#f98404", strokeWidth=4
#             ).encode(
#                 x=alt.X(
#                     "Time:T",
#                     title="Time",
#                     axis=alt.Axis(format="%I:%M:%S %p", labelAngle=-45)
#                 ),
#                 y=alt.Y(
#                     "VUs:Q",
#                     title="Virtual Users (VUs)",
#                     axis=alt.Axis(titleColor="#f98404"),
#                     scale=alt.Scale(domain=[0, max_vus * 1.1])
#                 ),
#                 tooltip=["Time:T", alt.Tooltip("VUs:Q", title="VUs")]
#             ).add_selection(zoom)

#             points_vu = alt.Chart(df_vu).mark_point(
#                 filled=True, color="red", size=110
#             ).encode(
#                 x="Time:T",
#                 y="VUs:Q"
#             )

#             resp_chart = alt.Chart(df_resp).mark_line(color="blue", strokeWidth=4).encode(
#                 x=alt.X("Time:T", axis=alt.Axis(format="%I:%M:%S %p")),
#                 y=alt.Y(
#                     "ResponseTime:Q",
#                     title="Response Time (ms)",
#                     axis=alt.Axis(titleColor="blue"),
#                     scale=alt.Scale(domain=[0, max_resp * 1.1])
#                 ),
#                 tooltip=["Time:T", alt.Tooltip("ResponseTime:Q", title="Resp Time (ms)")]
#             )

#             points_resp = alt.Chart(df_resp).mark_point(
#                 filled=True, color="blue", size=110
#             ).encode(
#                 x="Time:T",
#                 y="ResponseTime:Q"
#             )

#             dual_axis_chart = (
#                 alt.layer(vu_chart + points_vu, resp_chart + points_resp)
#                 .resolve_scale(y="independent")
#                 .properties(
#                     width=1200,
#                     height=420,
#                     padding={"top": 50, "left": 20, "right": 20, "bottom": 20}
#                 )
#             )
#             st.header("VUs vs Response Time")
#             st.altair_chart(dual_axis_chart, use_container_width=True)
#         else:
#             st.info("Not enough data for dual-axis chart.")

#     with col_right:
#         pass_percent = 100 * m['passed_checks'] / m['total_checks'] if m['total_checks'] else 0
#         fail_percent = 100 - pass_percent if m['total_checks'] else 0
#         col5.metric("Check Pass (%)", f"{pass_percent:.2f}%")
#         col6.metric("Check Fail (%)", f"{fail_percent:.2f}%")
#         percent_df = pd.DataFrame({
#             "Type": ["Pass", "Fail"],
#             "Percentage": [pass_percent, fail_percent]
#         })
#         selection = alt.selection_multi(fields=['Type'], bind='legend')
#         bar_chart = alt.Chart(percent_df).mark_bar().encode(
#             x=alt.X("Type", sort=["Pass", "Fail"]),
#             y=alt.Y("Percentage"),
#             color=alt.Color("Type", scale=alt.Scale(domain=["Pass", "Fail"], range=['#3CB371', '#DC143C'])),
#             opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
#             tooltip=["Type", "Percentage"]
#         ).add_selection(
#             selection
#         ).properties(
#            width=400,
#            height=420,
#         )
#         st.header('Check Pass vs Fail')
#         st.altair_chart(bar_chart, use_container_width=True)

#     st.markdown("<br><br>", unsafe_allow_html=True)
#     st.header("Load Test Insights Table")
#     useful_cols = [
#         "timestamp", "endpoint", "method", "metric", "value", "status", "error_code", "expected_response", "url"
#     ]
#     existing_cols = [col for col in useful_cols if col in df.columns]
#     st.dataframe(df[existing_cols].tail(25), use_container_width=True)

#     # PDF Export logic as before:
#     if valid_vu and not resp_ms.empty:
#         with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_png:
#             dual_axis_chart.save(tmp_png.name, format="png")
#             tmp_png.close()
#             pdf.image(tmp_png.name, x=10, y=25, w=190)
#         os.remove(tmp_png.name)

#     pdf_bytes = pdf.output(dest="S").encode("latin1")
#     st.download_button(
#         label="Download Dashboard PDF",
#         data=pdf_bytes,
#         file_name="dashboard_report.pdf",
#         mime="application/pdf"
#     )
#     if auto_refresh:
#         time.sleep(refresh_secs)
#         st.rerun()

# if __name__ == "__main__":
#     main()











import streamlit as st
import pandas as pd
import altair as alt
import json
from statistics import mean
from streamlit_elements import elements, mui

st.set_page_config(page_title="Material Dashboard", layout="wide")

st.markdown("""
<style>
body {
   background: linear-gradient(135deg,#f5f6fc 0,#ffffff 100%)!important;
   font-size: 0.22em !important;
}
.main, .block-container, [data-testid="stSidebar"], [data-testid="collapsedControl"] {
   margin: 1.7vh 0 0 0 !important ;
   padding: 0 !important ;
   width: 98vw !important ;
}
div[data-testid="stHorizontalBlock"], .element-container, .stApp {
   margin: 0 !important;
   padding: 0 !important;
   width: 100vw !important;
}
</style>
<link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
[data-testid="collapsedControl"] {display: none;}
</style>
<link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

RESULTS_PATH = "./Core/scripts/results.json"

def percentile(values, percentile):
    if not values: return 0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (percentile / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c: return sorted_vals[int(k)]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return d0 + d1

def load_json_metrics(path):
    records = []
    try:
        with open(path, "r") as f:
            first = f.read(1)
            if not first: return []
            f.seek(0)
            if first == '[':
                records = json.load(f)
            else:
                f.seek(0)
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try: records.append(json.loads(line))
                    except Exception: continue
    except Exception as e:
        st.error(f"Failed to read metrics: {e}")
    return records

def get_df(records):
    rows = []
    for r in records:
        d = {"metric": r.get("metric"), "type": r.get("type")}
        data = r.get("data", {})
        d["time"] = data.get("time")
        d["value"] = float(data.get("value", 0))
        tags = data.get("tags", {})
        for k, v in tags.items():
            d[k] = v
        rows.append(d)
    return pd.DataFrame(rows)

def compute_metrics(events):
    check_pts = [d for d in events if d.get("type") == "Point" and d.get("metric") == "checks"]
    http_req_durations = [d for d in events if d.get("type") == "Point" and d.get("metric") == "http_req_duration"]
    http_reqs_pts = [d for d in events if d.get("type") == "Point" and d.get("metric") == "http_reqs"]
    total_checks = len(check_pts)
    passed_checks = sum(1 for c in check_pts if c.get("data", {}).get("value") == 1)
    durations_ms = [float(p.get("data", {}).get("value", 0)) for p in http_req_durations]
    avg_ms = mean(durations_ms) if durations_ms else 0
    p95_ms = percentile(durations_ms, 95) if durations_ms else 0
    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": total_checks - passed_checks,
        "pass_rate": (passed_checks / total_checks * 100.0) if total_checks else 0.0,
        "total_http_reqs": len(http_reqs_pts),
        "avg_ms": avg_ms,
        "p95_ms": p95_ms,
    }

def main():
    st.markdown(
    '<div style="font-family:\'Roboto\',sans-serif;font-size:2rem;font-weight:700;color:#1976d2;text-align:center;margin-bottom:2rem;">Analysis of Load Test Data</div>',
    unsafe_allow_html=True
    )
    records = load_json_metrics(RESULTS_PATH)
    if not records:
        st.error("No load test data found or file format not recognized.")
        st.stop()
    df = get_df(records)
    df["timestamp"] = pd.to_datetime(df["time"], errors="coerce")
    m = compute_metrics(records)
    pass_percent = 100 * m['passed_checks'] / m['total_checks'] if m['total_checks'] else 0
    fail_percent = 100 - pass_percent if m['total_checks'] else 0

    # Metrics cards (Material)
    with elements("material-kpis-row"):
        mui.Grid(container=True, spacing=3, sx={"marginBottom": 3}, children=[
            mui.Grid(item=True, xs=2, children=[
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px","padding": "32px 24px 22px 32px","display": "flex","flexDirection": "column","alignItems": "flex-start","background": "#fff", 'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)","minHeight": "155px","width": "100%"},
                    children=[
                        mui.Typography("Total HTTP Requests", variant="subtitle1", sx={"color": "#1976d2","fontWeight":"bold","marginBottom":"0.33em"}),
                        mui.icon.DonutLarge(sx={"fontSize": "2.2rem", "color": "#1976d2", "marginBottom": "0.2em"}),
                        mui.Typography(str(m['total_http_reqs']), variant="h3", sx={"fontWeight":700, "color": "#232946"})
                    ]
                )
            ]),
            mui.Grid(item=True, xs=2, children=[
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px","padding": "32px 24px 22px 32px","display": "flex","flexDirection": "column","alignItems": "flex-start","background": "#fff"" 'box-shadow':" "0 4px 12px 4px rgba(33,150,243,0.13)","minHeight": "155px","width": "100%"},
                    children=[
                        mui.Typography("Passed HTTP Requests", variant="subtitle1", sx={"color": "#43a047","fontWeight":"bold","marginBottom":"0.33em"}),
                        mui.icon.TaskAlt(sx={"fontSize": "2.2rem", "color": "#43a047", "marginBottom": "0.2em"}),
                        mui.Typography(str(m['passed_checks']), variant="h3", sx={"fontWeight":700, "color": "#0c683d"})
                    ]
                )
            ]),
            mui.Grid(item=True, xs=2, children=[
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px","padding": "32px 24px 22px 32px","display": "flex","flexDirection": "column","alignItems": "flex-start","background": "#fff", 'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)","minHeight": "155px","width": "100%"},
                    children=[
                        mui.Typography("Avg Duration (s)", variant="subtitle1", sx={"color": "#9c27b0","fontWeight":"bold","marginBottom":"0.33em"}),
                        mui.icon.Timer(sx={"fontSize": "2.2rem", "color": "#9c27b0", "marginBottom": "0.2em"}),
                        mui.Typography(f"{m['avg_ms']/1000:.2f}", variant="h3", sx={"fontWeight":700, "color": "#9c27b0"})
                    ]
                )
            ]),
            mui.Grid(item=True, xs=2, children=[
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px","padding": "32px 24px 22px 32px","display": "flex","flexDirection": "column","alignItems": "flex-start","background": "#fff", 'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)","minHeight": "155px","width": "100%"},
                    children=[
                        mui.Typography("p95 (s)", variant="subtitle1", sx={"color": "#ff9800","fontWeight":"bold","marginBottom":"0.33em"}),
                        mui.icon.ShowChart(sx={"fontSize": "2.2rem", "color": "#ff9800", "marginBottom": "0.2em"}),
                        mui.Typography(f"{m['p95_ms']/1000:.2f}", variant="h3", sx={"fontWeight":700, "color": "#ff9800"})
                    ]
                )
            ]),
            mui.Grid(item=True, xs=2, children=[
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px","padding": "32px 24px 22px 32px","display": "flex","flexDirection": "column","alignItems": "flex-start","background": "#fff", 'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)","minHeight": "155px","width": "100%"},
                    children=[
                        mui.Typography("Pass (%)", variant="subtitle1", sx={"color": "#43a047","fontWeight":"bold","marginBottom":"0.33em"}),
                        mui.icon.TaskAlt(sx={"fontSize": "2.2rem", "color": "#43a047", "marginBottom": "0.2em"}),
                        mui.Typography(f"{pass_percent:.2f}%", variant="h3", sx={"fontWeight":700, "color": "#0c683d"})
                    ]
                )
            ]),
            mui.Grid(item=True, xs=2, children=[
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px","padding": "32px 24px 22px 32px","display": "flex","flexDirection": "column","alignItems": "flex-start","background": "#fff", 'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)","minHeight": "155px","width": "100%"},
                    children=[
                        mui.Typography("Fail (%)", variant="subtitle1", sx={"color": "#d32f2f","fontWeight":"bold","marginBottom":"0.33em"}),
                        mui.icon.Close(sx={"fontSize": "2.2rem", "color": "#d32f2f", "marginBottom": "0.2em"}),
                        mui.Typography(f"{fail_percent:.2f}%", variant="h3", sx={"fontWeight":700,"color":"#FF1B1B"})
                    ]
                )
            ]),
        ])

    col_left, col_right = st.columns([3, 1])
    with col_left:
        vu_metrics = [r for r in records if r.get("metric") == "vus"]
        valid_vu = [
            r for r in vu_metrics
            if isinstance(r.get("data", None), dict) and "time" in r["data"] and "value" in r["data"]
        ]
        resp_ms = df[df["metric"] == "http_req_duration"]
        if valid_vu and not resp_ms.empty:
            df_vu = pd.DataFrame([{"Time": pd.to_datetime(r["data"]["time"]), "VUs": r["data"]["value"]} for r in valid_vu])
            df_resp = resp_ms.set_index("timestamp")["value"].resample("1S").mean().reset_index()
            df_resp = df_resp.rename(columns={"value": "ResponseTime", "timestamp": "Time"})
            max_vus = df_vu["VUs"].max()
            max_resp = df_resp["ResponseTime"].max()
            zoom = alt.selection_interval(bind="scales", encodings=["x"])

            vu_tooltip = [alt.Tooltip("Time:T", title="Time"), alt.Tooltip("VUs:Q", title="VUs")]
            resp_tooltip = [alt.Tooltip("Time:T", title="Time"), alt.Tooltip("ResponseTime:Q", title="Resp Time (ms)")]

            vu_chart = alt.Chart(df_vu).mark_line(color="#1976d2", strokeWidth=4).encode(
                x=alt.X("Time:T", title="Time", axis=alt.Axis(format="%I:%M:%S %p", labelAngle=-45, labelFont="Roboto", labelFontSize=13, labelFontWeight="bold", titleFont="Roboto", titleFontSize=15, titleFontWeight="bold", titleColor="#1976d2", labelColor="#232946")),
                y=alt.Y("VUs:Q", title="Virtual Users (VUs)", axis=alt.Axis(titleFont="Roboto", titleFontSize=15, titleFontWeight="bold", titleColor="#1976d2", labelFont="Roboto", labelFontSize=13, labelFontWeight="bold", labelColor="#232946"), scale=alt.Scale(domain=[0, max_vus * 1.1])),
                tooltip=vu_tooltip
            ).add_selection(zoom)
            points_vu = alt.Chart(df_vu).mark_point(filled=True, color="#1976d2", size=110, opacity=0.9, stroke="#fff", strokeWidth=2).encode(
                x="Time:T", y="VUs:Q", tooltip=vu_tooltip
            )
            resp_chart = alt.Chart(df_resp).mark_line(color="#43a047", strokeWidth=4).encode(
                x=alt.X("Time:T", axis=alt.Axis(format="%I:%M:%S %p", labelFont="Roboto", labelFontSize=13, labelFontWeight="bold", labelColor="#232946")),
                y=alt.Y("ResponseTime:Q", title="Response Time (ms)", axis=alt.Axis(titleFont="Roboto", titleFontSize=15, titleFontWeight="bold", titleColor="#43a047", labelFont="Roboto", labelFontSize=13, labelFontWeight="bold", labelColor="#232946"), scale=alt.Scale(domain=[0, max_resp * 1.1])),
                tooltip=resp_tooltip
            )
            points_resp = alt.Chart(df_resp).mark_point(filled=True, color="#43a047", size=110, opacity=0.9, stroke="#fff", strokeWidth=2).encode(
                x="Time:T", y="ResponseTime:Q", tooltip=resp_tooltip
            )
            dual_axis_chart = (
                alt.layer(vu_chart + points_vu, resp_chart + points_resp)
                .resolve_scale(y="independent")
                .properties(width=1200, height=420, background="#fff", padding={"top": 40, "left": 30, "right": 30, "bottom": 20})
                .configure_view(strokeWidth=0)
                .configure_axis(gridColor="#e4e4e4", gridOpacity=0.6)
            )
            with elements("material-chart-panel-left"):
                mui.Paper(
                    elevation=8,
                    sx={"borderRadius": "28px", "padding": "14px 1px", "background": "#fff",  'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)", "display": "flex", "flexDirection": "column", "alignItems": "center", "width": "25%", "margin": "0 auto"},
                    children=[
                        mui.Typography("VUs vs Response Time", variant="h5", sx={"color": "#1976d2", "fontWeight": 700, "font-size":"1.1rem" ,"fontFamily": "'Roboto','Arial',sans-serif", "textAlign": "center", "width": "100%"})
                    ]
                )
            st.altair_chart(dual_axis_chart, use_container_width=True)
        else:
            st.info("Not enough data for dual-axis chart.")

    with col_right:
        with elements("material-passfail-card"):
            mui.Paper(
                elevation=8,
                sx={"borderRadius": "28px", "padding": "14px 1px", "background": "#fff",  'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)", "display": "flex", "flexDirection": "column", "alignItems": "center", "width": "60%", "margin": "0 auto"},
                children=[
                    mui.Typography("Check Pass vs Fail", variant="h5", sx={"color": "#1976d2", "fontWeight": 700, "font-size":"1.1rem" , "fontFamily": "'Roboto','Arial',sans-serif", "textAlign": "center", "width": "100%"})
                ]
            )

        percent_df = pd.DataFrame({"Type": ["Pass", "Fail"], "Percentage": [pass_percent, fail_percent]})
        selection = alt.selection_multi(fields=['Type'], bind='legend')
        bar_chart = alt.Chart(percent_df).mark_bar(cornerRadiusTopLeft=12, cornerRadiusTopRight=12, size=55).encode(
            x=alt.X("Type", sort=["Pass", "Fail"], axis=alt.Axis(title="Check Status", labelFont="Roboto", titleFont="Roboto", titleFontWeight="bold", labelFontWeight="bold", labelColor="#232946", titleColor="#1976d2", labelFontSize=15, titleFontSize=16)),
            y=alt.Y("Percentage", axis=alt.Axis(title="Percentage (%)", labelFont="Roboto", titleFont="Roboto", titleFontWeight="bold", labelFontWeight="bold", labelColor="#232946", titleColor="#1976d2", labelFontSize=15, titleFontSize=16)),
            color=alt.Color("Type", scale=alt.Scale(domain=["Pass", "Fail"], range=["#43a047", "#d32f2f"]), legend=None),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
            tooltip=[alt.Tooltip("Type", title="Status"), alt.Tooltip("Percentage", title="%", format=".2f")]
        ).add_selection(selection).properties(width=420, height=380, background="#fff").configure_view(strokeWidth=0).configure_axis(gridColor="#e4e4e4", gridOpacity=0.6)
        st.altair_chart(bar_chart, use_container_width=True)

    useful_cols = ["timestamp", "endpoint", "method", "metric", "value", "status", "error_code", "expected_response", "url"]
    existing_cols = [col for col in useful_cols if col in df.columns]
    with elements("material-table-card"):
        mui.Paper(
            elevation=8,
            sx={"borderRadius": "5px", "padding": "14px 1px", "marginTop": "1.2rem", "background": "#fff",  'box-shadow':" 0 4px 12px 4px rgba(33,150,243,0.13)", "display": "flex", "flexDirection": "column", "alignItems": "center", "width": "20%", "margin": "0 auto"},
            children=[
                mui.Typography("Load Test Insights Table",  variant="h5", sx={"color": "#1976d2", "font-size":"1.1rem" ,"fontWeight": 700, "fontFamily": "'Roboto','Arial',sans-serif", "textAlign": "center"})
            ]
        )

    st.dataframe(
    df[existing_cols].tail(25).reset_index(drop=True),
    use_container_width=True,
    column_config={
        "url": st.column_config.Column(width="large")  # try "large" or a pixel value like 500
    }
)
if __name__ == "__main__":
    main()



