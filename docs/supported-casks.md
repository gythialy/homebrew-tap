# Supported casks

This tap is for personal use: it holds casks for the apps I use on macOS. The
list below is the current set, and more apps may be added over time.

| Cask | Upstream | Channel | Notes |
|---|---|---|---|
| `fermata` | [gythialy/fermata](https://github.com/gythialy/fermata) | stable | Menu bar break reminder, macOS 13+. Ad-hoc signed, not notarized; the cask clears the quarantine. |
| `ex-desktop` | [metawka/exDesktop](https://github.com/metawka/exDesktop) | stable | Telegram Desktop client with extended customisation, GPL-3.0. arm64 and Intel builds. |
| `ex-desktop@beta` | [metawka/exDesktop](https://github.com/metawka/exDesktop) | pre-release | Newest non-draft pre-release of `ex-desktop`. Same app bundle and data directory, so the two casks conflict. |

## Adding a cask

Release sources live in
[`casks.toml`](https://github.com/gythialy/homebrew-tap/blob/main/casks.toml).
Each entry names a GitHub repository, a release channel, the asset names, and
the cask metadata. Run `python3 scripts/update.py` to generate
`Casks/<token>.rb`, then add a row to the table above. Python 3.11+ is required
for `tomllib`; CI uses 3.12.

A missing release or asset leaves the existing cask untouched unless the entry
sets `required = true`. When an asset's digest is absent from the release API,
the updater downloads it to compute SHA-256.
