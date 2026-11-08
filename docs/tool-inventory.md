# ツールの棚卸しと段階的な追加

実機の記録は2026-10-29に取得し、2026-11-07に更新しました。導入定義の更新日は2026-11-07です。旧 `scripts/install.sh`、共通の `home.nix`、読み取り専用で調査したmacOS実機の状態を比較します。定義の変更と採用順序の案を記録したもので、導入完了の記録ではありません。WSLの棚卸し・試験は未実施です。実機やパッケージ管理ツールの生の出力はGitに含めません。

## 現在の導入定義

`tool-packages.nix` は、独立したツール出力向けに20パッケージを明示しています。

```
bat coreutils fd findutils fzf gawk getopt gh ghq git gnugrep gnused
jq lazygit neovim peco perl ripgrep starship tmux
```

これにFishを加えた21のプログラムを導入します。Home Managerによる設定反映は別の入口で、共通パッケージ一覧をその設定から導入することはなくなりました。依存パッケージとNixの初期導入は別に数えます。当初の13パッケージにfd・lazygitを加えて15とし、今回Git、gh、tmux、jq、Neovimを追加しました。実機へのツール導入はしていません。[再導入対象](tool-installation.md)に用途、導入・更新の担当、バージョン方針を記録しています。

旧インストーラーには、重複を除いて30のapt・Cargoパッケージがあります。この定義との共通項目はbat、ripgrep、fzf、fish、fd-find（fdとして導入）、git、gh、tmux、jqの9件です。ほかの12のCLIパッケージはヘルパーの依存関係や新しい使い方を補います。設定の配布にはHome Managerを追加しました。旧一覧の残り21件を、自動で再導入対象にすることはありません。

## 旧一覧と現在の定義の比較

| 旧一覧の項目 | 現在のNix定義 | 扱い |
| --- | --- | --- |
| `bat`, `ripgrep`, `fzf`, `fish` | 定義済み | 維持。反映前にバージョンとコマンドの優先順位を確認する |
| `git`, `tmux` | 追加済み | 実行ファイルだけを追加し、既存設定は維持する |
| `curl`, `wget`, `htop`, `tree`, `unzip`, `gnupg` | 未定義 | 既存ツールと不足コマンドを分け、現在の導入状態を維持する |
| `vim` | 未定義 | 現在はNeovim + LazyVimを使用。旧エディター設定を再導入しない |
| `build-essential`, `ca-certificates`, `lsb-release` | 未定義 | OS・初期導入の前提。apt名をそのまま共通CLI一覧へ移さない |
| `exa` | 未定義 | `eza` を別途検討。既存Fishエイリアスはまだ `exa` の存在を確認する |
| `fd-find` | `pkgs.fd` として追加 | コマンド名は `fd`。既存Fishの `find` エイリアスも有効になる |
| `du-dust` | 未定義 | 既存Brewの `dust` を維持し、将来 `pkgs.dust` を検討する |
| `procs`, `tokei`, `hyperfine` | 未定義 | 旧CLIの用途を補う任意の追加候補 |
| `jq` | 追加済み | Nix版は現在のOS版とバージョンが異なる |
| `httpie`, `silversearcher-ag` | 未定義 | `pkgs.httpie`・`pkgs.silver-searcher` の任意の追加候補 |
| `nodejs`, `python3-pip`, `python3-venv` | 未定義 | 現在のランタイム・パッケージ管理方法を維持し、移行前に版を選ぶ |
| `gh` | 追加済み | 認証情報とクライアント設定は維持する |
| `hub` | 未定義 | 旧ツールを自動で戻さない |

旧スクリプトは、条件に応じたRust・rustupとFisherの初期導入やpipの更新も行います。これらは30パッケージの数には含めず、新定義でも実行しません。既存Fishヘルパーのソースは、Fisherで更新する代わりにHome Managerから直接配置します。

## まず追加し、その後に導入・更新の担当を移す

以下の「不足」は調査した通常シェルのPATHにないという意味で、プロジェクト、エディター、キャッシュ内にも存在しないという意味ではありません。パッケージの有無は固定済みソースの調査に基づきます。三つの対象での評価・ビルドは別途必要です。

| 順序 | ツール | 変更と理由 |
| --- | --- | --- |
| 1 | `fzf`, `ghq` | 定義済みだが実機のグローバルPATHにはない。既存Fishヘルパーの依存関係を補う |
| 2 | `fd`, `lazygit` | 定義へ追加済み。調査時のグローバル環境にはなく、現在のLazyVim利用を補う |
| 3 | `procs`, `tokei`, `hyperfine`, `wget`, `tree`, `httpie`, `silver-searcher` | グローバル環境にはない。旧用途を補う任意の候補とし、必要なものだけ追加する |
| 4 | `eza` | 旧 `exa` の任意の代替候補。関連エイリアスと一緒に確認する |
| 追加済み | `git`, `gh`, `tmux`, `jq`, `neovim` | 再導入対象として選定。既存の実行ファイルも導入したまま維持する |
| 後で判断 | `htop`, `dust`, GnuPG | 既存ツール。導入・更新の担当を別途選ぶ |

`fd`、`procs`、`eza` を追加すると、条件付きFishエイリアスが有効になり、`find`、`ps`、`ls` の動作が変わる場合があります。追加ごとに確認してください。今回の構成を反映すると、既存の `find='fd'` が有効になります。元のfind構文が必要な場合は `command find` を使います。エイリアスのソースは変更しておらず、`procs` と `eza` も未定義です。

この段階ではBrewのパッケージを削除しません。PATHではNixが優先されるため、旧パッケージを残していても、反映後に同じ実行ファイル・バージョンが選ばれる保証にはなりません。

## Neovim + LazyVimの維持

調査時のNeovimはBrew版0.12.6で、LuaJITを使用しています。`~/.config/nvim` にLazyVimのスターター設定と `lazy-lock.json` があり、プラグインはlazy.nvimが管理しています。このディレクトリは現在Git管理外です。

- Neovimは実行ファイルだけを定義しました。LazyVim設定とプラグインは既存の管理方法を維持します。
- 別途比較せず、既存の `init.lua` の上にHome ManagerのNeovim設定・プラグイン層を重ねません。
- MasonのbinにはTree-sitter CLI 0.26.3が存在します。BrewのTree-sitterライブラリがあるだけでは、グローバルCLIが使える証拠になりません。通常のPATHにないことだけを理由にCLIを重複導入しません。
- Masonは言語サーバーやフォーマッターも提供します。グローバル一覧へ追加する前に、既存のものを確認します。
- LazyVimの設定管理は対象外です。新しい端末での任意の初期化だけを記録します。書き込み可能なlockファイルはlazy.nvimが保持し、プラグイン、Masonのダウンロード、エディター状態はGit管理しません。
- 削除したのは引退済みの `.SpaceVim.d/init.toml` だけです。使用中のLazyVimファイル、OS付属Vim、Vim履歴は変更していません。

調査したNeovimのバージョンとLuaJITビルドは、[LazyVimのNeovim要件](https://www.lazyvim.org/#%EF%B8%8F-requirements)を満たします。環境全体のヘルスチェックは未実施です。任意ツールの案内は、既存の提供元をすべて置き換える指示ではありません。棚卸しでは通常のエディター起動、プラグイン更新、ヘルスチェックを行っていません。

## バージョン変更は別途判断する

固定したNixpkgsは `6dadaf4375be35033e1c84395adbd53ff5fded96`、Home Managerは `b787c48e2ec57a9d098f5c2721882a3bc1e16f97` です。開発ブランチのリビジョンとソースハッシュを `flake.lock` に記録しています。対象はApple Silicon macOSとarm64・x86_64 Linux（WSL）で、Intel Macは明示的に対象外としました。以下のNix版は、実際のNixでApple Silicon macOS向けに評価して読み取った値です。macOSでのビルド成功を示すものではありません。実機のFish、ripgrep、Neovimは2026-11-06に再確認しました。

| ツール | 調査時の提供元・バージョン | 固定したNixソース | 採用時の影響 |
| --- | --- | --- | --- |
| Fish | Brew 4.9.3 | [4.9.3](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/fi/fish/package.nix) | ソースの版は同じ。提供元が変わる |
| ripgrep | Brew 15.2.0 | [15.2.0](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/ri/ripgrep/package.nix) | ソースの版は同じ。提供元が変わる |
| Starship | 既存の単体バイナリ1.24.2 | [1.27.0](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/st/starship/package.nix#L15) | 新しい版・提供元へ変わる。定義済み |
| Neovim | Brew 0.12.6 | [0.12.6](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/ne/neovim-unwrapped/package.nix#L108) | 版は同じ。実行ファイルを新たに定義 |
| Tree-sitter CLI | Mason 0.26.3 | [0.26.11](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/tr/tree-sitter/package.nix#L115) | 提供元が競合するため未定義 |
| GitHub CLI | Brew 2.103.3 | [2.103.3](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/gh/gh/package.nix#L17) | 版は同じ。実行ファイルを新たに定義 |
| fzf | グローバルPATHにない | [0.74.5](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/fz/fzf/package.nix#L14) | 追加対象。定義済み |
| fd | グローバルPATHにない | [10.5.0](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/fd/fd/package.nix#L14) | 新たに定義 |
| lazygit | グローバルPATHにない | [0.66.2](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/la/lazygit/package.nix#L11) | 新たに定義 |

使用中の環境へ反映する前に、その環境でのシェル動作と、実際に選ばれるコマンドのパスを確認します。固定先を更新する場合も、対応するHome Managerのリビジョンと各パッケージの版を確認します。棚卸しによって自動変更しません。

## 実機の一覧を丸ごと取り込まない

更新した調査記録には、Brewの170 formulaと4 caskがあり、34 formulaに `installed_on_request` の記録があります。これは過去の導入情報で、希望する直接導入対象の確定一覧ではありません。すべて取り込むと、ライブラリの重複や偶発的な依存関係を残してしまいます。

ランタイムの版とパッケージの依存関係を比較するまで、既存のNode・Corepack・pnpm、Bun、Python・pipx・uv、Rust・rustup、Goの管理方法を維持します。特に、新しいBrew版Pythonが入っていても、調査時の既定 `python3` はOS版です。新たなグローバルPythonの定義は、実際の動作を変えます。

グローバルのnpm・Cargo・Pythonツール、AIクライアント、外部Skills、TeX・フォント、専門アプリは非公開の場所に記録しています。ここで自動追加・削除・再配布はしません。Bunのグローバル一覧取得は `InvalidNPMLockfile` で失敗し、パッケージ一覧は未確認です。更新調査では `/Applications` とユーザーのApplicationsディレクトリにある53のアプリバンドルも非公開で記録しました。存在の一覧であり、再導入対象の選定結果や、GUIアプリを完全に網羅した証拠ではありません。

## 定義更新の検証記録

2026-10-30には既存の隔離テスト29件がすべて成功し、二つのNixソースも利用可能な構文パーサーで検査に通りました。固定済みソースの `fd`・`lazygit` 定義を確認しました。実際のFishと一時的な `fd` 代替プログラムによる隔離試験では、条件付きエイリアスと `command find` による回避を確認しました。Nixでビルドした `fd` の試験ではありません。

この時点ではNixがなかったため、実際の `home-manager.sh check` は停止しました。評価・ビルド・Home Managerの反映は行われず、実機のツールの導入・削除もしていません。Dockerデーモンも利用できず、この確認のためには起動しませんでした。

2026-11-07の更新では、Intel Macを対象から外し、二つの固定入力を更新して、実際に生成したlockを記録しました。使い捨てDockerコンテナ内のNix 2.35.4で、三つのプロファイルの評価が成功しました。arm64 LinuxのHome Managerビルド、使い捨てホームへの反映、競合保護、初回反映からの復元も成功しました。更新後の回帰テストは30件成功しています。対象範囲は[検証記録](nix-migration.md#validated-snapshot-2026-11-07)を参照してください。macOS上とWSLでの動作確認は別途必要です。使用中のホスト設定は反映していません。

今回の追加や今後の採用では、[移行の検証・復元手順](nix-migration.md)に従います。定義の変更、実際の配布確認、使用中の環境への反映を分けて記録してください。

## 共通CLIの再導入定義の更新

追加したGit、gh、tmux、jq、Neovimは既存のlockを使います。三つのプロファイルの評価とarm64 Linuxのビルドが成功しました。ビルドした環境から五つのコマンドを起動し、jqのテストデータ処理と、ユーザー設定・プラグイン・履歴を使わないLuaJIT付きNeovimのヘッドレス起動を確認しました。macOS上やWSLでの実行試験ではなく、ホスト設定も反映していません。

## 導入と設定反映を分離した後の状態

ツール導入と設定反映は独立した入口になりました。現在の作業用PCでは実際の導入・更新確認をせず、別PCで検証します。前述のコンテナでの成功は、新しい分離構成を検証したものではありません。現構成で実施したのは、構文検査と代替Nixプログラムによるテストだけです。固定済みパッケージの版は変更していません。

フォント本体とTeXテンプレートは対象外です。[アプリ候補と公式の導入方法](macos-apps.md)は記録しましたが、アプリのインストーラーは実行していません。
