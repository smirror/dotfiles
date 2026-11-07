# Global agent instructions

`global.md` preserves the existing graphify instruction shared by Codex and Claude Code, using the installed shared skill path. Home Manager links this one source to `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md`.

External skills remain under their existing installers. In particular, graphify must already be installed at `~/.agents/skills/graphify/`; this migration does not download it or replace any skill directories. Credentials, histories, sessions, client settings and permission files are not managed here.

Changes to the instruction policy and to third-party skill distribution are separate from this Nix migration. Review the target files before activating Home Manager.
