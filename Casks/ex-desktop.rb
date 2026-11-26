cask "ex-desktop" do
  version "7.4.4.1"

  on_arm do
    sha256 "27e1d317700f1ab2b6826630cadbd1b43da4da47ad630b5f37a792143d7e7f06"

    url "https://github.com/metawka/exDesktop/releases/download/v#{version}/exDesktop-macos-arm64.#{version}.dmg"
  end
  on_intel do
    sha256 "d40a8f1a81b296ae5b4114fb40fb4c770d38d3155f39281d624f4648a3231302"

    url "https://github.com/metawka/exDesktop/releases/download/v#{version}/exDesktop-macos-x64.#{version}.dmg"
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
        args:         ["-dr", "com.apple.quarantine", "{{appdir}}/exDesktop.app"],
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
