# Dotfiles

個人の開発環境で使う設定と、ツールの再導入定義を管理します。

## 主な内容

- **Fish**：エイリアス、関数、補完、キー割り当て
- **Git**：よく使う操作のエイリアスを含む設定
- **Tmux**：端末の分割・セッション管理の設定
- **CLIツール**：bat、exa、fd、rgなど、従来のUnixコマンドを補うツール

## Nix + Home Manager（macOS・WSL共通）

共通環境を `flake.nix` と `home.nix` で定義しています。macOSとWSLで同じ定義・コマンドを使い、OS・CPUの判定と、ローカルのユーザー名・ホームディレクトリだけを切り替えます。nix-darwin、NixOS、Ansibleは不要です。

- `tool-packages.nix` にCLI一覧を定義し、`packages.<system>.tools` でFishと一緒に導入します。ホームディレクトリの設定反映とは独立しています。
- `home.nix` は、必要な場合にFishと共通エージェント指示を配置します。Fish・Home Managerのモジュール自身が必要とする実行時パッケージは引き続き導入します。
- CodexとClaude Codeは `agents/global.md` を共用します。外部Skillsの導入・更新は既存の方法を維持します。
- Git・Tmuxの設定、`fish_variables`、履歴、認証情報、クライアントの権限設定は、この移行の対象外です。
- Home Managerは通常、管理対象をNix storeへのリンクとして配置します。既存の通常ファイルが同一内容なら、そのまま残る場合があります。親ディレクトリと無関係なローカルファイルは管理対象にしません。

反映前に[ツールの棚卸しと追加候補](docs/tool-inventory.md)を確認してください。Fishとripgrepは調査時の実機と同じバージョンです。Intel Macは対応対象外です。

### 別の検証用PCで準備・ビルドする

初期導入用シェルスクリプトは、Nixがない場合に、バージョン固定・チェックサム確認済みの公式Nixを導入します。macOSではNix用ボリューム、ビルド用ユーザー、デーモンが追加されるため、実行前に[移行手順](docs/nix-migration.md)を確認してください。ログインシェルの変更やHome Managerによる設定反映は行いません。

```sh
./scripts/bootstrap.sh
# Nix導入後、新しいシェルを開く。
nix --extra-experimental-features 'nix-command flakes' build --no-update-lock-file .#tools --out-link result-tools
# 設定の生成も必要な場合は、別途実行する。
./scripts/home-manager.sh check
./scripts/home-manager.sh build
```

`DOTFILES_USER` と `DOTFILES_HOME` の既定値は、現在のユーザー名とホームディレクトリです。共通定義は `aarch64-darwin`、`aarch64-linux`、`x86_64-linux` に対応します。明示的な上書きは隔離した評価・ビルド用であり、他人が使用中のホームに反映するためのものではありません。

NixpkgsとHome Managerは開発ブランチのリビジョンを固定し、`flake.lock` をGit管理します。更新時は両者をまとめて確認してください。`home.stateVersion` は `26.05` のままです。これは設定の互換性を制御する値で、パッケージのリリース番号ではありません。構文検査だけでは、Nixの評価やビルドが成功したことにはなりません。

### 別の検証用PCで差分を確認・反映する

`result/home-files` を確認し、管理先を一つずつ比較して、[移行手順](docs/nix-migration.md)に沿ったバックアップを用意します。既存ファイルと内容が異なる場合は競合として停止し、自動で強制上書きしません。

```sh
# ファイル・プロファイルの変更と復元手順を確認した後に限り実行する。
./scripts/home-manager.sh switch
```

Nix管理下のヘルパーファイルに対して `fisher update` を実行しないでください。Git管理しているソースを変更し、再ビルドします。`fish_variables` はHome Managerへの取り込み元ではありません。実機のファイルをこのリポジトリへコピーしないでください。

### 設定を反映せずに検査する

```sh
python3 -B -m unittest discover -s tests -v
```

テストは一時ホーム・一時リポジトリを使います。インストーラーとNixのコマンド呼び出しに関するテストは代替プログラムを使うため、実際のNix導入・ビルドの成功を示すものではありません。実機のFishの認証情報は読み込みません。

### 既存の配置方法

Git・Tmuxから `~/.dotfiles` への既存リンクは維持します。実機のFish設定は、Home Managerで明示的に反映するまで別管理です。旧 `scripts/install.sh` はLinux専用で、`scripts/setup.sh` はFishのサブディレクトリをリポジトリ外へ移動します。どちらもNixの手順には含めず、この移行のために実行しないでください。

## 設定の内容

### Fish

- コマンドの置き換え（lsの代わりにexa、catの代わりにbatなど）
- よく使うGit操作のエイリアス
- プレビュー付きFZF連携
- 履歴・ディレクトリ移動のキー割り当て
- Fisherによるプラグイン管理との連携

### Git

- ユーザー設定（利用時にメールアドレスを変更）
- 操作のエイリアス（st、co、br、lgなど）
- 色付き出力
- pull・pushの既定動作

### Tmux

- マウス操作
- ペイン移動のキー割り当て
- ステータスバーのカスタマイズ
- 256色表示

## ツールの導入定義

初期の導入対象、バージョン方針、新しい端末での任意のLazyVim初期化については、[再導入対象と導入元](docs/tool-installation.md)を参照してください。

ツール一式は、明示した20のCLIパッケージとFishで構成します。Home Managerによる設定反映は別の入口です。Git、gh、tmux、jq、Neovimも含みますが、既存の個別設定まで管理対象を広げるものではありません。旧Linux用の導入一覧より小さい構成です。[ツールの棚卸し](docs/tool-inventory.md)では、定義済みの対象、追加候補、導入元・バージョンの判断が残る既存ツールを区別しています。

現在のエディターはNeovim + LazyVimです。既存設定は引き続き別管理とし、使わなくなったSpaceVim設定は削除済みです。

## 自分の環境に合わせる

### Git設定

利用前に `config/git/gitconfig` のメールアドレスを変更してください。

```ini
[user]
    name = smirror
    email = your-actual-email@example.com
```

### Fishプラグイン

Fisherのプラグインを追加・削除する場合は `fish/fish_plugins` を編集します。

```
jorgebucaran/fisher
jethrokuan/z
jethrokuan/fzf
decors/fish-ghq
0rax/fish-bd
```

## 旧スクリプト

以下は既存の配布方式です。今回のNix移行では実行しません。

- `scripts/install.sh`：ツールとdotfilesをまとめて導入するLinux用スクリプト
- `scripts/setup.sh`：既存設定をバックアップし、ファイルを `~/.config` へ移動して配置するスクリプト

## ディレクトリ構成（抜粋）

```
dotfiles/
├── config/
│   ├── git/
│   │   └── gitconfig
│   └── tmux/
│       └── tmux.conf
├── fish/
│   ├── config.fish
│   ├── fish_plugins
│   ├── functions/
│   ├── completions/
│   └── conf.d/
├── scripts/
│   ├── install.sh
│   └── setup.sh
└── README.md
```

## ライセンス

MIT License。詳細はLICENSEファイルを参照してください。

## 更新提案と任意のアプリ

DependabotはNixのlock更新を毎日提案する定義です。自動マージや実機へのインストールは行いません。`scripts/update-lock.sh` は別PCで手動のlock更新を準備するためのもので、導入・設定反映はしません。現在固定しているリビジョンは変更していません。[更新・配布方針](docs/tool-installation.md)を参照してください。

[macOSアプリの候補](docs/macos-apps.md)に導入方法と公式リンクを記録しています。フォントとTeXテンプレートは対象外です。[Kali・Parrotの環境](docs/security-environments.md)は任意の隔離ツール環境とし、セキュリティツールをホストへ導入しません。
