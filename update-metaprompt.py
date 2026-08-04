#!/usr/bin/env python3
"""
Fetch the latest metaprompt from Anthropic's claude-cookbooks repo,
extract the metaprompt text, and update metaprompt.py if it has changed.

Usage:
    python update-metaprompt.py          # check + update
    python update-metaprompt.py --check  # check only, no write
"""

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

NOTEBOOK_URL = (
    "https://raw.githubusercontent.com/anthropics/claude-cookbooks"
    "/main/misc/metaprompt.ipynb"
)
LOCAL_SCRIPT = Path(__file__).parent / "metaprompt.py"

# Sentinel that marks the start of the metaprompt string in the notebook source
METAPROMPT_START_MARKER = 'metaprompt = """'
METAPROMPT_END_MARKER = '"""'


def fetch_notebook(url: str) -> dict:
    print(f"Fetching {url} ...")
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode())


def extract_source(notebook: dict) -> str:
    """Concatenate all code cell sources into one string."""
    parts = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "code":
            parts.append("".join(cell.get("source", [])))
    return "\n".join(parts)


def extract_metaprompt_text(source: str) -> str | None:
    """Pull the triple-quoted metaprompt string out of the source."""
    # Match: metaprompt = """..."""  (multiline, non-greedy)
    m = re.search(r'metaprompt\s*=\s*"""(.*?)"""', source, re.DOTALL)
    if m:
        return m.group(1)
    return None


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def update_local(new_text: str) -> None:
    """Replace the metaprompt string in the local metaprompt.py."""
    original = LOCAL_SCRIPT.read_text(encoding="utf-8")
    updated = re.sub(
        r'(metaprompt\s*=\s*""").*?(""")',
        lambda m: m.group(1) + new_text + m.group(2),
        original,
        flags=re.DOTALL,
    )
    if updated == original:
        print("No change after substitution — pattern not found in local file.")
        sys.exit(1)
    LOCAL_SCRIPT.write_text(updated, encoding="utf-8")
    print(f"Updated {LOCAL_SCRIPT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update metaprompt from upstream")
    parser.add_argument(
        "--check", action="store_true", help="Check only; do not write changes"
    )
    args = parser.parse_args()

    notebook = fetch_notebook(NOTEBOOK_URL)
    source = extract_source(notebook)
    remote_text = extract_metaprompt_text(source)

    if remote_text is None:
        print("ERROR: could not extract metaprompt string from upstream notebook.")
        print("Upstream structure may have changed — inspect manually:")
        print(f"  {NOTEBOOK_URL}")
        sys.exit(1)

    # Extract local metaprompt text for comparison
    local_source = LOCAL_SCRIPT.read_text(encoding="utf-8")
    local_text_match = re.search(
        r'metaprompt\s*=\s*"""(.*?)"""', local_source, re.DOTALL
    )
    local_text = local_text_match.group(1) if local_text_match else ""

    remote_hash = sha256(remote_text)
    local_hash = sha256(local_text)

    print(f"Local  sha256: {local_hash[:16]}...")
    print(f"Remote sha256: {remote_hash[:16]}...")

    if remote_hash == local_hash:
        print("Already up-to-date.")
        return

    print("Upstream has changed.")

    if args.check:
        print("--check mode: not writing. Run without --check to apply.")
        sys.exit(2)  # exit 2 = update available

    update_local(remote_text)
    print("Done. Review changes with: git diff metaprompt.py")


if __name__ == "__main__":
    main()
