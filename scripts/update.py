#!/usr/bin/env python3
"""Refresh the configured casks from their latest GitHub releases.

casks.toml holds each cask's repository, release channel, asset names and
metadata. The GitHub release API already carries a sha256 digest for each
asset, so the common path needs no download.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parent.parent
CASKS = ROOT / "Casks"
TOKEN = os.environ.get("GITHUB_TOKEN", "")


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "fermata-tap"})
    if TOKEN:
        request.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def latest(repo: str) -> dict | None:
    try:
        return json.loads(fetch(f"{API}/repos/{repo}/releases/latest"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def latest_prerelease(repo: str) -> dict | None:
    try:
        releases = json.loads(fetch(f"{API}/repos/{repo}/releases?per_page=30"))
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    return next(
        (r for r in releases if r.get("prerelease") and not r.get("draft")), None
    )


def version_of(release: dict, prefix: str = "v") -> str:
    tag = release["tag_name"]
    return tag.removeprefix(prefix) if prefix else tag


def digest(asset_item: dict) -> str:
    value = (asset_item.get("digest") or "").strip()
    if value.startswith("sha256:"):
        return value.removeprefix("sha256:")
    data = fetch(asset_item["browser_download_url"])
    return hashlib.sha256(data).hexdigest()


def asset(release: dict, name: str) -> dict | None:
    return next((a for a in release.get("assets", []) if a["name"] == name), None)


def write(path: Path, text: str) -> bool:
    if path.exists() and path.read_text() == text:
        return False
    path.write_text(text)
    return True


def ruby_url(template: str) -> str:
    return template.replace("{version}", "#{version}")


def render(cask: dict, release: dict) -> str | None:
    token = cask["token"]
    version = version_of(release, cask.get("tag_prefix", "v"))
    assets = cask["asset"]
    urls = cask["url"]
    keys = ["universal"] if "universal" in assets else ["arm", "intel"]
    checksums = {}
    for key in keys:
        name = assets[key].format(version=version)
        item = asset(release, name)
        if item is None:
            if cask.get("on_missing_asset") == "skip":
                return None
            raise SystemExit(f"{token} {version} is missing {name}")
        checksums[key] = digest(item)

    lines = [f'cask "{token}" do', f'  version "{version}"']
    if keys == ["universal"]:
        lines += [
            f'  sha256 "{checksums["universal"]}"',
            "",
            f'  url "{ruby_url(urls["universal"])}"',
        ]
    else:
        lines.append("")
        for key in keys:
            lines += [
                f"  on_{key} do",
                f'    sha256 "{checksums[key]}"',
                "",
                f'    url "{ruby_url(urls[key])}"',
                "  end",
            ]
        lines.append("")

    lines += [
        f'  name "{cask["name"]}"',
        f'  desc "{cask["desc"]}"',
        f'  homepage "{cask["homepage"]}"',
        "",
    ]
    if cask.get("auto_updates"):
        lines.append("  auto_updates true")
    if cask.get("conflicts_with"):
        lines.append(f'  conflicts_with cask: "{cask["conflicts_with"]}"')
    lines += [f"  depends_on {cask['depends_on']}", "", f'  app "{cask["app"]}"', ""]
    if cask.get("clear_quarantine"):
        lines += [
            "  postflight_steps do",
            '    run "/usr/bin/xattr",',
            f'        args:         ["-dr", "com.apple.quarantine", "{{{{appdir}}}}/{cask["app"]}"],',
            "        must_succeed: false",
            "  end",
            "",
        ]
    lines += ["  zap trash: ["]
    lines += [f'    "{path}",' for path in cask["zap"]]
    lines += ["  ]", "", "  caveats <<~EOS"]
    lines += [f"    {line}" for line in cask["caveats"]]
    lines += ["  EOS", "end", ""]
    return "\n".join(lines)


def release_for(cask: dict) -> dict | None:
    if cask.get("channel") == "prerelease":
        return latest_prerelease(cask["repo"])
    return latest(cask["repo"])


def main() -> int:
    CASKS.mkdir(exist_ok=True)
    with (ROOT / "casks.toml").open("rb") as config_file:
        casks = tomllib.load(config_file)["cask"]

    changed = []
    for cask in casks:
        token = cask["token"]
        channel = cask.get("channel", "latest")
        release = release_for(cask)
        if release is None:
            if cask.get("required"):
                raise SystemExit(f"{token} has no {channel} release")
            print(f"{token}: no {channel} release yet, leaving the cask alone")
            continue
        cask_text = render(cask, release)
        if cask_text is None:
            print(f"{token}: release is missing a macOS asset, leaving the cask alone")
            continue
        if write(CASKS / f"{token}.rb", cask_text):
            changed.append(token)

    print("updated: " + (", ".join(changed) if changed else "nothing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
