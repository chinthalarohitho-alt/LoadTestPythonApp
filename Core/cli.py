import argparse
from core.generator import generate_k6_script
from core.runner import run_k6

def main():
    parser = argparse.ArgumentParser(description="Loadwrap - k6 Wrapper Tool")
    parser.add_argument("command", choices=["run"], help="Action to perform")
    parser.add_argument("config", help="Path to config JSON file")
    parser.add_argument("--report", choices=["console", "json", "html"], default="console")

    args = parser.parse_args()

    if args.command == "run":
        script_path = "scripts/load_test.js"
        generate_k6_script(args.config, script_path)
        run_k6(script_path, args.report)

if __name__ == "__main__":
    main()
