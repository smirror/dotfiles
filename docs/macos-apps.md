# macOS application installation candidates

This is an inventory of possible reinstall routes, not a default installation list.
No application, installer or update has been executed on this PC by this work.
Fonts and TeX templates are excluded. Application binaries, fonts, licenses and
account data are not stored in this repository. Latest stable is selected at
a reviewed update; a cask name alone is not an exact historical-version lock.

## Catalogued cask routes

Homebrew catalog metadata lists these stable cask candidates and vendor homepages.
Names alone do not verify product identity; match the bundle/vendor before enrollment.
No Brewfile has been activated and installer placement has not been tested on another PC.

| Application | Candidate cask | Official/vendor homepage from catalog |
| --- | --- | --- |
| VLC | `vlc` | [Vendor](https://www.videolan.org/vlc/) |
| Antigravity | `antigravity` | [Vendor](https://antigravity.google/product/antigravity-2) |
| Simple Comic | `simple-comic` | [Vendor](https://github.com/MaddTheSane/Simple-Comic) |
| Claude | `claude` | [Vendor](https://claude.com/download) |
| TradingView | `tradingview` | [Vendor](https://www.tradingview.com/desktop/) |
| Raycast | `raycast` | [Vendor](https://raycast.com/) |
| Steam | `steam` | [Vendor](https://store.steampowered.com/about/) |
| Google Chrome | `google-chrome` | [Vendor](https://www.google.com/chrome/) |
| Spotify | `spotify` | [Vendor](https://www.spotify.com/) |
| PyCharm | `pycharm` | [Vendor](https://www.jetbrains.com/pycharm/) |
| Scroll Reverser | `scroll-reverser` | [Vendor](https://pilotmoon.com/scrollreverser/) |
| RustRover | `rustrover` | [Vendor](https://www.jetbrains.com/rust/) |
| Docker | `docker-desktop` | [Vendor](https://www.docker.com/products/docker-desktop) |
| Obsidian | `obsidian` | [Vendor](https://obsidian.md/) |
| KeyClu | `keyclu` | [Vendor](https://sergii.tatarenkov.name/apps/keyclu/) |
| Thunderbird | `thunderbird` | [Vendor](https://www.thunderbird.net/en-US/) |
| Antigravity IDE | `antigravity-ide` | [Vendor](https://antigravity.google/product/antigravity-ide) |
| iTerm | `iterm2` | [Vendor](https://iterm2.com/) |
| Firefox | `firefox` | [Vendor](https://www.mozilla.org/firefox/) |
| AltTab | `alt-tab` | [Vendor](https://alt-tab.app/) |
| Postman | `postman` | [Vendor](https://www.postman.com/) |
| JetBrains Toolbox | `jetbrains-toolbox` | [Vendor](https://www.jetbrains.com/toolbox-app/) |
| Ollama | `ollama-app` | [Vendor](https://ollama.com/) |
| Discord | `discord` | [Vendor](https://discord.com/) |

## Special or separately verified routes

| Application | Route / decision | Official source |
| --- | --- | --- |
| Orca (Stably AI) | Official release assets; reject the unrelated Plotly `orca` cask | [Official repository/releases](https://github.com/stablyai/orca) |
| OpenAI desktop app | The local ChatGPT.app reports a Codex bundle ID; confirm the intended product before choosing an installer | Official product/installer identity still needs confirmation |
| Kanary | Vendor distribution; pin and verify a selected asset before automation | [Official site](https://kanary.to/) |
| Photomator | Mac App Store; account/license may be required | [Official site](https://www.pixelmator.com/photomator/) |
| Karabiner-Elements | Vendor installer; system-extension/input permissions are separate user decisions | [Official site](https://karabiner-elements.pqrs.org/) |
| Karabiner EventViewer / VirtualHID helper | Managed by the parent Karabiner distribution; do not enroll independently | [Parent project](https://karabiner-elements.pqrs.org/) |
| Tailscale | Choose the macOS distribution deliberately; VPN/extension permissions remain separate | [Official downloads](https://tailscale.com/download/mac) |
| RunCat Neo | Mac App Store route linked by the project | [Official repository](https://github.com/runcat-dev/RunCatNeo) |
| World Monitor | Vendor/source release; verify macOS asset and integrity before automation | [Official repository](https://github.com/koala73/worldmonitor) |
| Xcode | Apple distribution; version/macOS compatibility and sign-in handled separately | [Apple downloads](https://developer.apple.com/xcode/resources/) |
| Safari / Apple apps | OS or Apple Store distribution; do not infer an unattended installer | [Apple](https://www.apple.com/) |
| Burp Suite Community | Excluded from host reinstall selection; consider the isolated GUI/VM toolbox route | [Official product](https://portswigger.net/burp/communitydownload) |

## Pending items and execution boundary

The complete 53-app presence inventory stays private, including games, helper
bundles and unresolved app identities. Items without a verified vendor/source
remain unconfigured; do not invent a mirror or infer a cask from a filename.
Store/launcher-managed applications must be restored through their authorized
account or parent application. This record does not grant permission to buy,
accept licenses, enable login/background services or change security settings.

For an application selected later, record product/bundle identity, official
source, installation method, architecture, version/build, integrity verification
and update behavior. If exact pinning is unavailable through the chosen store
or installer, record that exception before deployment.
