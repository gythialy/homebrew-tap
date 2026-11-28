cask "fermata" do
  version "1.1.4"
  sha256 "0767ed1dda4902aeac59ec9b09505bf25be6a301ec8802094a727e682be985e6"

  url "https://github.com/gythialy/fermata/releases/download/v#{version}/fermata-#{version}-macos-universal.dmg"
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
