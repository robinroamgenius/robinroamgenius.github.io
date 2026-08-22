#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import webbrowser
from datetime import datetime

GREEN, YELLOW, RED, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[0m"

build_stats = {
    "status": "In Progress",
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "clean_status": "Pending", "build_status": "Pending",
    "verify_status": "Pending", "upload_status": "Pending",
    "target": "TestPyPI", "artifacts": [], "logs": []
}

def log(level, msg):
    if level == "INFO": print(f"{GREEN}[INFO]{RESET} {msg}")
    elif level == "WARN": print(f"{YELLOW}[WARN]{RESET} {msg}")
    elif level == "ERROR": print(f"{RED}[ERROR]{RESET} {msg}", file=sys.stderr)
    build_stats["logs"].append(f"[{level}] {msg}")

def clean_artifacts():
    log("INFO", "Starting cleaning process...")
    try:
        for d in ["build", "dist"]:
            if os.path.exists(d): shutil.rmtree(d)
        for item in os.listdir("."):
            if item.endswith(".egg-info") and os.path.isdir(item): shutil.rmtree(item)
        build_stats["clean_status"] = "Success"
    except Exception as e:
        build_stats["clean_status"] = "Failed"
        log("ERROR", f"Cleaning failed: {str(e)}")

def build_package():
    log("INFO", "Compiling package distributions...")
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True, capture_output=True, text=True)
        build_stats["build_status"] = "Success"
        if os.path.exists("dist"): build_stats["artifacts"] = os.listdir("dist")
    except subprocess.CalledProcessError as e:
        build_stats["build_status"] = "Failed"
        log("ERROR", f"Build failed: {e.stderr}")
        generate_hub(False)
        sys.exit(1)

def verify_package():
    log("INFO", "Running Twine verification checks...")
    try:
        subprocess.run([sys.executable, "-m", "twine", "check", "dist/*"], check=True, capture_output=True, text=True)
        build_stats["verify_status"] = "Success"
    except subprocess.CalledProcessError as e:
        build_stats["verify_status"] = "Failed"
        log("ERROR", f"Verification failed: {e.stderr}")
        generate_hub(False)
        sys.exit(1)

def upload_package(production):
    target = "Production PyPI" if production else "TestPyPI"
    build_stats["target"] = target
    log("INFO", f"Initiating upload to {target}...")
    if input(f"Confirm upload to {target}? (y/N): ").lower() != "y":
        build_stats["upload_status"] = "Aborted"
        return
    repo_args = [] if production else ["--repository", "testpypi"]
    try:
        subprocess.run([sys.executable, "-m", "twine", "upload"] + repo_args + ["dist/*"], check=True, capture_output=True, text=True)
        build_stats["upload_status"] = "Success"
    except subprocess.CalledProcessError as e:
        build_stats["upload_status"] = "Failed"
        log("ERROR", f"Upload failed: {e.stderr}")
        generate_hub(False)
        sys.exit(1)

def generate_hub(success=True):
    build_stats["status"] = "SUCCESS" if success else "FAILED"
    os.makedirs("dist", exist_ok=True)
    hub_path = os.path.abspath("dist/hub.html")
    
    # Generujeme HTML čistě pomocí funkcí Pythonu bez obřích textových šablon
    lines = [
        "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Python Publish Hub</title>",
        "<style>",
        "body { font-family: sans-serif; background-color: #0f141c; color: #e1e7ef; padding: 40px; }",
        "header { display: flex; justify-content: space-between; border-bottom: 1px solid #2d3748; padding-bottom: 20px; }",
        "h1 { color: #38bdf8; margin: 0; } .badge { font-weight: bold; color: " + ("#4ade80" if success else "#f87171") + "; }",
        ".grid { display: flex; gap: 20px; margin: 30px 0; }",
        ".card { background-color: #1e293b; padding: 20px; border-radius: 8px; flex: 1; border: 1px solid #334155; }",
        ".console { background-color: #020617; padding: 15px; border-radius: 8px; font-family: monospace; max-height: 200px; overflow-y: auto; }",
        "</style></head><body>",
        "<header><div><h1>Python Deployment Hub</h1><p>Ran: " + build_stats["timestamp"] + "</p></div>",
        "<div class='badge'>STATUS: " + build_stats["status"] + "</div></header>",
        "<div class='grid'>",
        "<div class='card'><h3>Clean</h3><p>" + build_stats["clean_status"] + "</p></div>",
        "<div class='card'><h3>Build</h3><p>" + build_stats["build_status"] + "</p></div>",
        "<div class='card'><h3>Verify</h3><p>" + build_stats["verify_status"] + "</p></div>",
        "<div class='card'><h3>Target</h3><p>" + build_stats["target"] + "</p></div>",
        "</div>",
        "<h2>Artifacts</h2><ul>" + "".join(f"<li>{a}</li>" for a in build_stats["artifacts"]) + "</ul>",
        "<h2>Logs</h2><div class='console'>" + "".join(f"<div>{l}</div>" for l in build_stats["logs"]) + "</div>",
        "</body></html>"
    ]
    
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"\n{GREEN}[HUB] Dashboard generated: {hub_path}{RESET}")
    webbrowser.open(f"file://{hub_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", action="store_true")
    args = parser.parse_args()
    clean_artifacts()
    build_package()
    verify_package()
    upload_package(args.production)
    generate_hub(True)

if __name__ == "__main__":
    if not os.path.exists("pyproject.toml") and not os.path.exists("setup.py"):
        print(f"{RED}[ERROR]{RESET} Run from root directory.")
        sys.exit(1)
    main()
