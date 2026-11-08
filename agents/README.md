# グローバルエージェント指示

`global.md` は、CodexとClaude Codeで共用する既存のgraphify指示を保持しています。インストール済みの共通Skillへのパスを使い、Home Managerがこの一つのソースを `~/.codex/AGENTS.md` と `~/.claude/CLAUDE.md` にリンクします。

外部Skillsの導入・更新は既存の方法を維持します。特にgraphifyは `~/.agents/skills/graphify/` に導入済みであることが前提です。この移行ではダウンロードやSkillディレクトリの置き換えをしません。認証情報、履歴、セッション、クライアント設定、権限ファイルも管理対象外です。

指示の方針変更と外部Skillsの配布方法の変更は、このNix移行とは別作業です。Home Managerで反映する前に、配置先のファイルを確認してください。
