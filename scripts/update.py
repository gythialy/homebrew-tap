#!/usr/bin/env python3
"""Refresh the casks from the latest stable upstream releases.

Fermata publishes fermata-<version>-macos-universal.dmg and a rolling fermata.dmg; exDesktop
publishes separate arm64 and x64 DMGs for both its stable and pre-release
channels. The GitHub release API already carries
a sha256 digest for each asset, so the common path needs no download.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
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


def version_of(release: dict) -> str:
    tag = release["tag_name"]
    return tag[1:] if tag.startswith("v") else tag


def digest(asset: dict) -> str:
    value = (asset.get("digest") or "").strip()
    if value.startswith("sha256:"):
        return value.removeprefix("sha256:")
    data = fetch(asset["browser_download_url"])
    return hashlib.sha256(data).hexdigest()


def asset(release: dict, name: str) -> dict | None:
    return next((a for a in release.get("assets", []) if a["name"] == name), None)


def write(path: Path, text: str) -> bool:
    if path.exists() and path.read_text() == text:
        return False
    path.write_text(text)
    return True


def fermata_cask(release: dict) -> str | None:
    version = version_of(release)
    item = asset(release, f"fermata-{version}-macos-universal.dmg")
    if item is None:
        return None
    checksum = digest(item)
    return f'''cask "fermata" do
  version "{version}"
  sha256 "{checksum}"

  url "https://github.com/gythialy/fermata/releases/download/v#{{version}}/fermata-#{{version}}-macos-universal.dmg"
  name "Fermata"
  desc "Menu bar break reminder"
  homepage "https://github.com/gythialy/fermata"

  depends_on macos: :ventura

  app "Fermata.app"

  postflight_steps do
    run "/usr/bin/xattr",
        args:         ["-dr", "com.apple.quarantine", "{{{{appdir}}}}/Fermata.app"],
        must_succeed: false
  end

  zap trash: [
    "~/Library/Application Support/Fermata",
    "~/Library/Logs/Fermata",
    "~/Library/Preferences/breaktime.plist",
    "~/Library/Preferences/dev.gythialy.breaktime.plist",
    "~/Library/Preferences/dev.gythialy.fermata.plist",
  ]

  caveats <<~EOS
    Fermata is ad-hoc signed, not notarized. This cask clears the download
    quarantine; if macOS still blocks it, right-click the app and choose Open,
    or allow it in System Settings -> Privacy & Security.
  EOS
end
'''


def exdesktop_cask(release: dict) -> str:
    version = version_of(release)
    arm = asset(release, f"exDesktop-macos-arm64.{version}.dmg")
    intel = asset(release, f"exDesktop-macos-x64.{version}.dmg")
    if arm is None or intel is None:
        raise SystemExit(f"exDesktop {version} is missing a macOS DMG")

    return f'''cask "ex-desktop" do
  version "{version}"

  on_arm do
    sha256 "{digest(arm)}"

    url "https://github.com/metawka/exDesktop/releases/download/v#{{version}}/exDesktop-macos-arm64.#{{version}}.dmg"
  end
  on_intel do
    sha256 "{digest(intel)}"

    url "https://github.com/metawka/exDesktop/releases/download/v#{{version}}/exDesktop-macos-x64.#{{version}}.dmg"
  end

  name "exDesktop"
  desc "Telegram Desktop client with extended customisation"
  homepage "https://github.com/metawka/exDesktop"

  auto_updates true
  conflicts_with cask: "ex-desktop@beta"
  depends_on :macos

  app "exDesktop.app"

  postflight_steps do
    run "/usr/bin/xattr",
        args:         ["-dr", "com.apple.quarantine", "{{{{appdir}}}}/exDesktop.app"],
        must_succeed: false
  end

  zap trash: [
    "~/Library/Application Support/exDesktop",
    "~/Library/Preferences/com.tdesktop.Telegram.plist",
    "~/Library/Saved Application State/com.tdesktop.Telegram.savedState",
  ]

  caveats <<~EOS
    exDesktop is built and signed by its upstream project, not by Homebrew or
    Fermata. This cask clears the download quarantine; if macOS still blocks
    it, right-click the app and choose Open.
  EOS
end
'''


def exdesktop_beta_cask(release: dict) -> str | None:
    version = version_of(release)
    arm = asset(release, f"exDesktop-macos-arm64.{version}.dmg")
    intel = asset(release, f"exDesktop-macos-x64.{version}.dmg")
    if arm is None or intel is None:
        return None

    return f'''cask "ex-desktop@beta" do
  version "{version}"

  on_arm do
    sha256 "{digest(arm)}"

    url "https://github.com/metawka/exDesktop/releases/download/v#{{version}}/exDesktop-macos-arm64.#{{version}}.dmg"
  end
  on_intel do
    sha256 "{digest(intel)}"

    url "https://github.com/metawka/exDesktop/releases/download/v#{{version}}/exDesktop-macos-x64.#{{version}}.dmg"
  end

  name "exDesktop"
  desc "Telegram Desktop client with extended customisation"
  homepage "https://github.com/metawka/exDesktop"

  auto_updates true
  conflicts_with cask: "ex-desktop"
  depends_on :macos

  app "exDesktop.app"

  postflight_steps do
    run "/usr/bin/xattr",
        args:         ["-dr", "com.apple.quarantine", "{{{{appdir}}}}/exDesktop.app"],
        must_succeed: false
  end

  zap trash: [
    "~/Library/Application Support/exDesktop",
    "~/Library/Preferences/com.tdesktop.Telegram.plist",
    "~/Library/Saved Application State/com.tdesktop.Telegram.savedState",
  ]

  caveats <<~EOS
    This is the upstream pre-release channel of exDesktop. Installing it
    replaces the stable ex-desktop cask; both share the same app bundle and
    data directory.
  EOS
end
'''


def main() -> int:
    CASKS.mkdir(exist_ok=True)
    changed = []

    fermata = latest("gythialy/fermata")
    if fermata is not None:
        cask = fermata_cask(fermata)
        if cask is not None and write(CASKS / "fermata.rb", cask):
            changed.append("fermata")
    else:
        print("fermata: no stable release yet, leaving the cask alone")

    exdesktop = latest("metawka/exDesktop")
    if exdesktop is None:
        raise SystemExit("exDesktop has no stable release")
    if write(CASKS / "ex-desktop.rb", exdesktop_cask(exdesktop)):
        changed.append("ex-desktop")

    beta = latest_prerelease("metawka/exDesktop")
    if beta is None:
        print("ex-desktop@beta: no pre-release yet, leaving the cask alone")
    else:
        cask = exdesktop_beta_cask(beta)
        if cask is None:
            print(
                "ex-desktop@beta: pre-release is missing a macOS DMG, leaving the cask alone"
            )
        elif write(CASKS / "ex-desktop@beta.rb", cask):
            changed.append("ex-desktop@beta")

    print("updated: " + (", ".join(changed) if changed else "nothing"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
