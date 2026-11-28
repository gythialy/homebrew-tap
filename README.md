# gythialy/tap

A personal Homebrew tap for the apps I use on macOS. It is not meant to cover
every piece of software; more apps may be added over time.

```sh
brew tap gythialy/tap
brew install --cask fermata
brew install --cask ex-desktop        # stable
brew install --cask ex-desktop@beta   # upstream pre-release channel
```

## Current casks

The supported casks are listed in
[docs/supported-casks.md](https://github.com/gythialy/homebrew-tap/blob/main/docs/supported-casks.md).

## First launch

These apps are outside the Mac App Store and are not notarized. The casks clear
the download quarantine in a `postflight_steps` step. If macOS still blocks an
app, right-click it in Applications and choose **Open**, or allow it in
**System Settings → Privacy & Security**.

## Uninstall

```sh
brew uninstall --cask fermata ex-desktop        # keep settings and data
brew uninstall --cask --zap fermata ex-desktop  # also delete the leftovers
brew untap gythialy/tap
```

`fermata` zaps `~/Library/Application Support/Fermata`, `~/Library/Logs/Fermata`
and the `dev.gythialy.fermata` preferences, including the legacy
`dev.gythialy.breaktime` and `breaktime` plists from earlier builds.

Both exDesktop casks zap the same paths, taken from the `telegram-desktop` cask
in homebrew/cask, which is the same Qt application under the shared
`com.tdesktop.Telegram` bundle identifier:
`~/Library/Application Support/exDesktop`,
`~/Library/Preferences/com.tdesktop.Telegram.plist` and
`~/Library/Saved Application State/com.tdesktop.Telegram.savedState`. Because
that identifier is shared, zapping exDesktop also resets a real Telegram
Desktop install's preferences.

## License

The casks are metadata. Fermata is MIT; exDesktop is GPL-3.0 and is distributed
by its own project.

## Updates

A scheduled workflow runs daily and on demand. It reads the latest stable
release of each upstream, takes the release asset's SHA-256 digest, rewrites
the matching cask, and commits the change here. There is no manual bump.

`fermata` starts as a rolling `:latest` cask; once Fermata publishes its first
versioned release, the updater switches it to a versioned cask. exDesktop is
versioned from the start. `ex-desktop@beta` tracks the newest non-draft
pre-release; when upstream has none, the workflow leaves that cask untouched.

Upgrade them with:

```sh
brew upgrade --cask fermata
brew upgrade --cask --greedy-auto-updates ex-desktop ex-desktop@beta
```

Both exDesktop casks set `auto_updates true` because the app ships its own
updater, so `brew upgrade` skips them by default; `--greedy-auto-updates`
forces a brew-managed reinstall when you want the tap's build instead.

## Cask API

The casks track the Cask DSL of the latest Homebrew release: `depends_on macos:
:ventura` instead of the deprecated `depends_on macos: ">= :ventura"` string
form, and declarative `postflight_steps` blocks with `run` steps instead of the
deprecated Ruby `postflight` blocks. `scripts/update.py` renders every cask, so
a Homebrew DSL change has to be made there and in `Casks/` together. Release
sources and per-app metadata live in
[`casks.toml`](https://github.com/gythialy/homebrew-tap/blob/main/casks.toml);
adding an app needs a config entry there and a row in
[docs/supported-casks.md](https://github.com/gythialy/homebrew-tap/blob/main/docs/supported-casks.md).
