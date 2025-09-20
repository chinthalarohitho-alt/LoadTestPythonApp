import json
from statistics import mean


def _percentile(values, percentile):
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

def generate_html_report(input_file, output_file):
    with open(input_file) as f:
        data = [json.loads(line) for line in f if line.strip()]

    # Parse check points: k6 outputs streaming JSON where check results are "Point" entries
    # with metric=="checks" and data.value of 1 (pass) or 0 (fail)
    check_points = [d for d in data if d.get("type") == "Point" and d.get("metric") == "checks"]
    total_checks = len(check_points)
    passed_checks = sum(1 for c in check_points if c.get("data", {}).get("value") == 1)
    failed_checks = total_checks - passed_checks
    pass_rate = (passed_checks / total_checks * 100.0) if total_checks else 0.0

    # HTTP request metrics
    http_req_points = [d for d in data if d.get("type") == "Point" and d.get("metric") == "http_req_duration"]
    durations_ms = [float(p.get("data", {}).get("value", 0)) for p in http_req_points]
    avg_ms = mean(durations_ms) if durations_ms else 0
    p90_ms = _percentile(durations_ms, 90) if durations_ms else 0
    p95_ms = _percentile(durations_ms, 95) if durations_ms else 0
    min_ms = min(durations_ms) if durations_ms else 0
    max_ms = max(durations_ms) if durations_ms else 0

    http_reqs_points = [d for d in data if d.get("type") == "Point" and d.get("metric") == "http_reqs"]
    total_http_reqs = len(http_reqs_points)

    html = f"""
    <html>
    <head>
        <meta charset=\"utf-8\" />
        <title>Load Test Report</title>
        <style>
            body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 40px; color: #222; }}
            h1 {{ color: #2E86C1; margin-bottom: 8px; }}
            .subtitle {{ color: #666; margin-top: 0; }}
            .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin: 24px 0; }}
            .card {{ border: 1px solid #eee; border-radius: 8px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
            .muted {{ color: #666; }}
            .pass {{ color: #2e7d32; font-weight: 600; }}
            .fail {{ color: #c62828; font-weight: 600; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
            th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #eee; }}
            th {{ background: #fafafa; font-weight: 600; }}
            .small {{ font-size: 12px; }}
        </style>
    </head>
    <body>
        <h1>📊 Load Test Report</h1>
        <p class="subtitle muted">Generated from k6 results</p>

        <div class="cards">
            <div class="card">
                <div class="muted small">HTTP Requests</div>
                <div style="font-size: 28px; font-weight: 700;">{total_http_reqs}</div>
            </div>
            <div class="card">
                <div class="muted small">Checks Passed</div>
                <div style="font-size: 28px; font-weight: 700;" class="pass">{passed_checks} / {total_checks}</div>
                <div class="muted small">Pass rate: {pass_rate:.2f}%</div>
            </div>
            <div class="card">
                <div class="muted small">Duration (avg)</div>
                <div style="font-size: 28px; font-weight: 700;">{avg_ms:.2f} ms</div>
                <div class="muted small">min {min_ms:.2f} · p90 {p90_ms:.2f} · p95 {p95_ms:.2f} · max {max_ms:.2f} (ms)</div>
            </div>
        </div>

        <h3>Checks Summary</h3>
        <table>
            <thead>
                <tr><th>Check</th><th>Result</th></tr>
            </thead>
            <tbody>
                <tr><td>Total</td><td>{total_checks}</td></tr>
                <tr><td class="pass">Passed</td><td>{passed_checks}</td></tr>
                <tr><td class="fail">Failed</td><td>{failed_checks}</td></tr>
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html)
