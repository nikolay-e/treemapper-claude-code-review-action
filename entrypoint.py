#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys


def detect_diff_range():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")

    if event_path and os.path.exists(event_path):
        with open(event_path, "r") as f:
            event = json.load(f)
    else:
        event = {}

    if event_name == "pull_request" or event_name == "pull_request_target":
        pr = event.get("pull_request", {})
        base_sha = pr.get("base", {}).get("sha")
        head_sha = pr.get("head", {}).get("sha")
        if base_sha and head_sha:
            print(f"::notice::Auto-detected PR diff: {base_sha[:7]}..{head_sha[:7]}")
            return f"{base_sha}..{head_sha}"

    if event_name == "push":
        before = event.get("before")
        after = event.get("after")
        if before and after and before != "0" * 40:
            print(f"::notice::Auto-detected push diff: {before[:7]}..{after[:7]}")
            return f"{before}..{after}"

    print("::notice::Using fallback diff: HEAD~1..HEAD")
    return "HEAD~1..HEAD"


def main():
    diff_range = sys.argv[1] if len(sys.argv) > 1 else ""
    path = sys.argv[2] if len(sys.argv) > 2 else "."
    budget = sys.argv[3] if len(sys.argv) > 3 else "50000"
    output_format = sys.argv[4] if len(sys.argv) > 4 else "yaml"
    alpha = sys.argv[5] if len(sys.argv) > 5 else "0.60"
    tau = sys.argv[6] if len(sys.argv) > 6 else "0.08"
    full = sys.argv[7] if len(sys.argv) > 7 else "false"
    no_content = sys.argv[8] if len(sys.argv) > 8 else "false"

    if not diff_range:
        diff_range = detect_diff_range()

    workspace = os.environ.get("GITHUB_WORKSPACE", "/github/workspace")
    repo_path = os.path.join(workspace, path) if path != "." else workspace

    os.chdir(repo_path)

    git_config_result = subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", repo_path],
        capture_output=True,
        text=True,
    )
    if git_config_result.returncode != 0:
        print(f"::warning::Failed to set safe.directory: {git_config_result.stderr}")

    output_filename = f"treemapper-context.{output_format}"
    output_file = f"{workspace}/{output_filename}"

    cmd = [
        "treemapper",
        ".",
        "--diff",
        diff_range,
        "--budget",
        budget,
        "--alpha",
        alpha,
        "--tau",
        tau,
        "-f",
        output_format,
        "-o",
        output_file,
    ]

    if full.lower() == "true":
        cmd.append("--full")

    if no_content.lower() == "true":
        cmd.append("--no-content")

    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"::error::TreeMapper failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    with open(output_file, "r") as f:
        context = f.read()

    fragment_count = "0"
    if output_format in ("yaml", "yml"):
        fragment_count = str(len(re.findall(r"^\s+- path:", context, re.MULTILINE)))
    elif output_format == "json":
        try:
            data = json.loads(context)
            fragments = data.get("fragments", [])
            fragment_count = str(len(fragments))
        except json.JSONDecodeError:
            pass

    stderr = result.stderr or ""
    token_match = re.search(r"([\d,]+)\s+tokens", stderr)
    size_match = re.search(r"([\d.]+\s*[KMG]?B)", stderr)
    token_count = token_match.group(1).replace(",", "") if token_match else "0"
    size = size_match.group(1) if size_match else "0"

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"context-file={output_filename}\n")
            f.write(f"fragment-count={fragment_count}\n")
            f.write(f"token-count={token_count}\n")
            f.write(f"size={size}\n")

            delimiter = "EOF_CONTEXT_DELIMITER"
            f.write(f"context<<{delimiter}\n")
            f.write(context)
            if not context.endswith("\n"):
                f.write("\n")
            f.write(f"{delimiter}\n")

    print(f"::notice::Extracted {fragment_count} fragments (~{token_count} tokens)")


if __name__ == "__main__":
    main()
