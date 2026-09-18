#!/usr/bin/env python3
"""Update the recent-projects block using public GitHub repository metadata."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

ACCOUNT = "ddocde"
README = Path(__file__).resolve().parents[1] / "README.md"
START = "<!-- recent-projects:start -->"
END = "<!-- recent-projects:end -->"


def load_repositories() -> list[dict[str, object]]:
    request = urllib.request.Request(
        f"https://api.github.com/users/{ACCOUNT}/repos?per_page=100&type=owner&sort=updated",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{ACCOUNT}-profile-readme",
            **(
                {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
                if os.environ.get("GITHUB_TOKEN")
                else {}
            ),
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def render(repositories: list[dict[str, object]]) -> str:
    original = [
        repo
        for repo in repositories
        if not repo["fork"] and repo["name"] != ACCOUNT and not repo["archived"]
    ][:5]
    lines = []
    for repo in original:
        language = repo["language"] or "Mixed"
        description = str(repo["description"] or "No description yet.").replace("\n", " ")
        updated = str(repo["updated_at"])[:10]
        lines.append(
            f"- [{repo['name']}]({repo['html_url']}) — {language} · "
            f"{description} _({updated})_"
        )
    return "\n".join(lines)


def main() -> None:
    content = README.read_text(encoding="utf-8")
    replacement = f"{START}\n{render(load_repositories())}\n{END}"
    updated, count = re.subn(
        rf"{re.escape(START)}.*?{re.escape(END)}",
        replacement,
        content,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise SystemExit("recent-projects markers are missing or duplicated")
    README.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
