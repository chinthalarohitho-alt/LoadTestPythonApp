import json
import time
from pathlib import Path
from statistics import mean

import streamlit as st


def load_data(results_path: Path):
    if not results_path.exists():
        return []
    with results_path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def compute_metrics(events):
    check_points = [d for d in events if d.get("type") == "Point" and d.get("metric") == "checks"]
    http_req_points = [d for d in events if d.get("type") == "Point" and d.get("metric") == "http_req_duration"]
    http_reqs_points = [d for d in events if d.get("type") == "Point" and d.get("metric") == "http_reqs"]

    total_checks = len(check_points)
    passed_checks = sum(1 for c in check_points if c.get("data", {}).get("value") == 1)
    failed_checks = total_checks - passed_checks
    pass_rate = (passed_checks / total_checks * 100.0) if total_checks else 0.0

    durations_ms = [float(p.get("data", {}).get("value", 0)) for p in http_req_points]
    avg_ms = mean(durations_ms) if durations_ms else 0
    p90_ms = percentile(durations_ms, 90) if durations_ms else 0
    p95_ms = percentile(durations_ms, 95) if durations_ms else 0
    min_ms = min(durations_ms) if durations_ms else 0
    max_ms = max(durations_ms) if durations_ms else 0

    total_http_reqs = len(http_reqs_points)

    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "pass_rate": pass_rate,
        "total_http_reqs": total_http_reqs,
        "avg_ms": avg_ms,
        "p90_ms": p90_ms,
        "p95_ms": p95_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
    }


def percentile(values, percentile):
    if not values:
        return 0
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (percentile / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return d0 + d1


def main():
    st.set_page_config(page_title="Loadwrap - k6 Report", layout="wide")
    st.title("📊 Loadwrap - k6 Report")
    st.caption("Interactive dashboard for k6 results")

    results_path = Path("scripts/results.json")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_secs = st.sidebar.slider("Refresh interval (sec)", 1, 10, 3)

    if not results_path.exists():
        st.info("No results found. Run: `python3 cli.py run config/sample_config.json --report html` to generate results.")
        return

    events = load_data(results_path)
    m = compute_metrics(events)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("HTTP Requests", m["total_http_reqs"])
    col2.metric("Checks Passed", f"{m['passed_checks']} / {m['total_checks']}", f"{m['pass_rate']:.2f}%")
    col3.metric("Avg Duration (ms)", f"{m['avg_ms']:.2f}")
    col4.metric("p95 (ms)", f"{m['p95_ms']:.2f}")

    st.subheader("Durations Distribution (ms)")
    durations = [float(p.get("data", {}).get("value", 0)) for p in events if p.get("type") == "Point" and p.get("metric") == "http_req_duration"]
    if durations:
        st.line_chart(durations)
    else:
        st.write("No duration data available.")

    # st.subheader("Raw Events (last 200)")
    # last_events = events[-200:]
    # st.code(json.dumps(last_events, indent=2)[:50000])

    if auto_refresh:
        time.sleep(refresh_secs)
        st.rerun()


if __name__ == "__main__":
    main()