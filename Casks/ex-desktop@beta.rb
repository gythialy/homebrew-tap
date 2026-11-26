cask "ex-desktop@beta" do
  version "7.4.4.2b"

  on_arm do
    sha256 "6ef757d7dafccf99aab45ce9af12aa455f45c79183902f74acbe5a018ef481b3"

    url "https://github.com/metawka/exDesktop/releases/download/v#{version}/exDesktop-macos-arm64.#{version}.dmg"
  end
  on_intel do
    sha256 "5e8de59be2a44525c165dff4e2012c0f9147c93cdc31a8e3c5ed9c469ae5402e"

    url "https://github.com/metawka/exDesktop/releases/download/v#{version}/exDesktop-macos-x64.#{version}.dmg"
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
        args:         ["-dr", "com.apple.quarantine", "{{appdir}}/exDesktop.app"],
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
