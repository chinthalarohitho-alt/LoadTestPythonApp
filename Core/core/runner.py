import subprocess
import os

def run_k6(script_path, report=None):
    results_file = "scripts/results.json"

    cmd = ["k6", "run", script_path]
    if report in ["json", "html"]:
        cmd = ["k6", "run", "--out", f"json={results_file}", script_path]

    print("🚀 Running:", " ".join(cmd))
    subprocess.run(cmd)

    if report == "html":
        from core.reporter import generate_html_report
        if os.path.exists(results_file):
            generate_html_report(results_file, "scripts/report.html")
            print("📊 HTML report generated: scripts/report.html")
