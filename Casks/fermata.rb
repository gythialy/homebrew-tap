cask "fermata" do
  version "1.0.0"
  sha256 "7cd9cb1376994bcd5bd4f564dd0b5e9af3837c9d1b51439b681acccd4888f036"

  url "https://github.com/gythialy/fermata/releases/download/v#{version}/Fermata-#{version}.dmg"
  name "Fermata"
  desc "Menu bar break reminder"
  homepage "https://github.com/gythialy/fermata"

  depends_on macos: :ventura

  app "Fermata.app"

  postflight_steps do
    run "/usr/bin/xattr",
        args:         ["-dr", "com.apple.quarantine", "{{appdir}}/Fermata.app"],
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
