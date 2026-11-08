# macOSアプリの導入候補

再導入方法の候補を整理したもので、既定のインストール一覧ではありません。この作業で現在のPC上のアプリ、インストーラー、更新処理は実行していません。フォントとTeXテンプレートは対象外です。アプリ本体、フォント、ライセンス、アカウントデータはリポジトリに保存しません。確認した更新時点の最新安定版を選びますが、cask名だけでは過去の特定バージョンを固定できません。

## caskで導入できる候補

Homebrewのカタログ情報に基づく安定版caskの候補と、配布元のサイトです。名前だけでは同じ製品か確認できないため、導入対象に加える前にバンドル情報・配布元を照合します。Brewfileによる反映や、別PCでのインストーラーによる配置確認は未実施です。

| アプリ | cask候補 | カタログに記載された公式・配布元サイト |
| --- | --- | --- |
| VLC | `vlc` | [配布元](https://www.videolan.org/vlc/) |
| Antigravity | `antigravity` | [配布元](https://antigravity.google/product/antigravity-2) |
| Simple Comic | `simple-comic` | [配布元](https://github.com/MaddTheSane/Simple-Comic) |
| Claude | `claude` | [配布元](https://claude.com/download) |
| TradingView | `tradingview` | [配布元](https://www.tradingview.com/desktop/) |
| Raycast | `raycast` | [配布元](https://raycast.com/) |
| Steam | `steam` | [配布元](https://store.steampowered.com/about/) |
| Google Chrome | `google-chrome` | [配布元](https://www.google.com/chrome/) |
| Spotify | `spotify` | [配布元](https://www.spotify.com/) |
| PyCharm | `pycharm` | [配布元](https://www.jetbrains.com/pycharm/) |
| Scroll Reverser | `scroll-reverser` | [配布元](https://pilotmoon.com/scrollreverser/) |
| RustRover | `rustrover` | [配布元](https://www.jetbrains.com/rust/) |
| Docker | `docker-desktop` | [配布元](https://www.docker.com/products/docker-desktop) |
| Obsidian | `obsidian` | [配布元](https://obsidian.md/) |
| KeyClu | `keyclu` | [配布元](https://sergii.tatarenkov.name/apps/keyclu/) |
| Thunderbird | `thunderbird` | [配布元](https://www.thunderbird.net/en-US/) |
| Antigravity IDE | `antigravity-ide` | [配布元](https://antigravity.google/product/antigravity-ide) |
| iTerm | `iterm2` | [配布元](https://iterm2.com/) |
| Firefox | `firefox` | [配布元](https://www.mozilla.org/firefox/) |
| AltTab | `alt-tab` | [配布元](https://alt-tab.app/) |
| Postman | `postman` | [配布元](https://www.postman.com/) |
| JetBrains Toolbox | `jetbrains-toolbox` | [配布元](https://www.jetbrains.com/toolbox-app/) |
| Ollama | `ollama-app` | [配布元](https://ollama.com/) |
| Discord | `discord` | [配布元](https://discord.com/) |

## 個別の判断・確認が必要な導入方法

| アプリ | 方法・方針 | 公式情報 |
| --- | --- | --- |
| Orca（Stably AI） | 公式リリースの配布物を使う。別製品であるPlotlyの `orca` caskは使わない | [公式リポジトリ・リリース](https://github.com/stablyai/orca) |
| OpenAIのデスクトップアプリ | ローカルのChatGPT.appがCodexのバンドルIDを返すため、意図する製品を確認してからインストーラーを選ぶ | 公式製品とインストーラーの対応は要確認 |
| Kanary | 配布元から取得する。自動化前に対象の配布物を固定・検証する | [公式サイト](https://kanary.to/) |
| Photomator | Mac App Store。アカウント・ライセンスが必要な場合がある | [公式サイト](https://www.pixelmator.com/photomator/) |
| Karabiner-Elements | 公式インストーラー。システム拡張・入力権限はユーザーが別途判断する | [公式サイト](https://karabiner-elements.pqrs.org/) |
| Karabiner EventViewer / VirtualHID helper | Karabiner本体の配布方法で管理し、個別の導入対象にはしない | [本体のプロジェクト](https://karabiner-elements.pqrs.org/) |
| Tailscale | macOS向けの配布方法を選ぶ。VPN・拡張の権限は別途扱う | [公式ダウンロード](https://tailscale.com/download/mac) |
| RunCat Neo | プロジェクトが案内するMac App Storeを使う | [公式リポジトリ](https://github.com/runcat-dev/RunCatNeo) |
| World Monitor | 配布元・ソースのリリースを使う。自動化前にmacOS向け配布物と完全性を確認する | [公式リポジトリ](https://github.com/koala73/worldmonitor) |
| Xcode | Appleから導入する。バージョン、macOS互換性、サインインは別途扱う | [Appleのダウンロード案内](https://developer.apple.com/xcode/resources/) |
| Safari・Apple製アプリ | OSまたはAppleのストア経由。無人インストールできるとは仮定しない | [Apple](https://www.apple.com/) |
| Burp Suite Community | ホストへの再導入対象から除外。隔離したGUI・VM環境を検討する | [公式製品ページ](https://portswigger.net/burp/communitydownload) |

## 未確定項目と実行範囲

ゲーム、補助バンドル、製品の同一性が未確認のものを含む53アプリの完全な存在一覧は非公開のまま保持します。配布元を確認できない項目は未設定とし、ミラーを作り上げたり、ファイル名からcaskを推測したりしません。ストアやランチャーが管理するアプリは、正規のアカウントまたは親アプリから復元します。この記録は、購入、ライセンス同意、ログイン・常駐サービスの有効化、セキュリティ設定の変更を許可するものではありません。

今後選ぶアプリについては、製品・バンドルの同一性、公式の取得元、導入方法、アーキテクチャ、バージョン・ビルド番号、完全性の確認方法、更新動作を記録します。選んだストアやインストーラーで厳密な固定ができない場合は、反映前に例外として記録します。
