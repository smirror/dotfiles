"""Run with python3 -m unittest discover -s tests -v; never load the real HOME."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


CONFIG = Path(__file__).resolve().parents[1] / "fish/config.fish"
FISH, GIT = shutil.which("fish"), shutil.which("git")


@unittest.skipUnless(FISH and GIT, "fish and git are required")
class FishConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.bin = self.home / "bin"
        for rel in ("bin", ".config", ".cache", ".local/share", ".local/bin",
                    "go/bin", ".cargo/bin", ".bun/bin", "Library/pnpm/bin",
                    ".antigravity-ide/antigravity-ide/bin", ".ssh"):
            (self.home / rel).mkdir(parents=True, exist_ok=True)
        self.env = {"HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_CACHE_HOME": str(self.home / ".cache"),
                    "XDG_DATA_HOME": str(self.home / ".local/share"),
                    "PATH": f"{self.bin}:/usr/bin:/bin", "TERM": "dumb",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "DOTFILES_CONFIG": str(CONFIG), "REAL_GIT": GIT}
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.executable("git", '#!/bin/sh\nif [ "$1" = checkout ]; then printf "%s\\n" "$@" >> "$HOME/checkouts"; fi\nexec "$REAL_GIT" "$@"\n')

    def executable(self, name, body):
        path = self.bin / name
        path.write_text(body)
        path.chmod(0o755)

    def fish(self, body):
        # Function stubs also override a real initializer found by command -q.
        boot = '''function starship; end
function hub; end
function mcfly; end
source "$DOTFILES_CONFIG"; or exit 99
'''
        result = subprocess.run([FISH, "--no-config", "-c", boot + body],
                                cwd=self.repo, env=self.env, text=True,
                                capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def git(self, *args):
        return subprocess.check_output([GIT, *args], cwd=self.repo,
                                       env=self.env, stderr=subprocess.DEVNULL).decode().strip()

    def branches(self, base="main"):
        self.git("init", "-b", base)
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.file = self.repo / "file with spaces.txt"
        self.file.write_text("base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.git("checkout", "-b", "feature")
        self.file.write_text("feature\n")
        self.git("commit", "-am", "feature")
        self.git("checkout", base)

    def select(self, *choices):
        values = " ".join("'" + value.replace("'", "\\'") + "'" for value in choices)
        return f'''set -gx PATH "$HOME/bin" /usr/bin /bin
set -g choices {values}
set -g choice_index 0
function fzf
    command cat >/dev/null
    set -g choice_index (math $choice_index + 1)
    set -l choice "$choices[$choice_index]"
    test -n "$choice"; or return 130
    printf '%s\\n' "$choice"
end
'''

    def test_paths_are_repeatable_and_do_not_persist_user_paths(self):
        self.env["PATH"] += ":/usr/local/bin:/opt/homebrew/bin"
        result = self.fish('''set -l first $PATH
source "$DOTFILES_CONFIG"; or exit 98
test (string join : $first) = (string join : $PATH); or exit 1
set -q --universal fish_user_paths; and exit 2
test "$GOPATH" = "$HOME/go"; or exit 3
test "$PNPM_HOME" = "$HOME/Library/pnpm"; or exit 4
printf '%s\\n' $PATH
''')
        paths = result.stdout.splitlines()
        self.assertEqual(len(paths), len(set(paths)))
        self.assertLess(paths.index("/opt/homebrew/bin"), paths.index("/usr/local/bin"))
        for rel in (".local/bin", "go/bin", ".cargo/bin", ".bun/bin", "Library/pnpm/bin"):
            self.assertIn(str(self.home / rel), paths)
        self.assertNotIn("/usr/local/texlive/2024/bin/universal-darwin", paths)

    def test_fco_selects_and_does_not_checkout_on_cancel(self):
        self.branches()
        self.fish(self.select("feature", "") + "fco; or exit 1\nfco\ntrue\n")
        self.assertEqual(self.git("branch", "--show-current"), "feature")
        self.assertEqual((self.home / "checkouts").read_text().splitlines(), ["checkout", "feature"])

    def test_snag_cancel_preserves_edits_and_global_variables(self):
        self.branches()
        self.fish(self.select("feature", self.file.name, "", "feature", "") + '''set -g branch sentinel
set -g files sentinel
snag; or exit 1
printf 'local edit\\n' > 'file with spaces.txt'
snag
snag
test "$branch" = sentinel; or exit 2
test "$files" = sentinel; or exit 3
true
''')
        self.assertEqual(self.file.read_text(), "local edit\n")
        self.assertEqual((self.home / "checkouts").read_text().splitlines(),
                         ["checkout", "feature", "--", self.file.name])

    def test_fzum_handles_main_master_and_remote_default(self):
        for base in ("main", "master"):
            with self.subTest(base=base):
                self.branches(base)
                capture = '''function fzf
    printf '%s\\n' $argv > "$HOME/fzf-args"
    command cat > "$HOME/branches"
end
fzum
'''
                self.fish(capture)
                self.assertEqual((self.home / "branches").read_text().strip(), "feature")
                self.git("update-ref", f"refs/remotes/origin/{base}", self.base)
                self.git("symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{base}")
                self.git("checkout", "feature")
                self.fish(capture)
                self.assertEqual((self.home / "branches").read_text().strip(), "feature")
                self.assertIn(f"git log {self.base}..{{}}", (self.home / "fzf-args").read_text())
                shutil.rmtree(self.repo / ".git")

    def test_fssh_parses_aliases_and_never_connects_on_cancel(self):
        (self.home / ".ssh/config").write_text(
            "  Host alpha beta # comment\nHost *.invalid !excluded gamma? delta\n\tHOST epsilon\nHostName ignored\n")
        self.fish('''function ssh
    printf '%s\\n' $argv >> "$HOME/ssh-call"
end
function fzf
    command cat > "$HOME/hosts"
    printf 'beta\\n'
end
fssh; or exit 1
function fzf; command cat >/dev/null; return 130; end
fssh
true
''')
        self.assertEqual((self.home / "hosts").read_text().splitlines(), ["alpha", "beta", "delta", "epsilon"])
        self.assertEqual((self.home / "ssh-call").read_text().splitlines(), ["--", "beta"])

    def test_history_widget_uses_fzf_reversal_without_tac(self):
        for name in ("old", "recent", "current"):
            (self.home / name).mkdir()
        self.fish('''function __fzfcmd; printf 'fzf'; end
function commandline; end
function fzf
    printf '%s\\n' $argv > "$HOME/widget-args"
    command cat > "$HOME/widget-input"
    return 130
end
set -g dirprev "$HOME/old" "$HOME/recent" "$HOME/current"
fzf-cdhist-widget
true
''')
        self.assertIn("--tac", (self.home / "widget-args").read_text().splitlines())
        self.assertEqual((self.home / "widget-input").read_text().splitlines(),
                         [str(self.home / "old"), str(self.home / "recent")])

    def test_fpass_failure_returns_instead_of_exiting_shell(self):
        self.executable("lpass", '#!/bin/sh\nprintf "%s\\n" "$1" >> "$HOME/lpass-calls"\nexit 1\n')
        result = self.fish('''set -gx PATH "$HOME/bin" /usr/bin /bin
fpass
test $status -eq 1; or exit 2
printf 'still running\\n'
''')
        self.assertEqual(result.stdout, "still running\n")
        self.assertEqual((self.home / "lpass-calls").read_text().splitlines(), ["status", "login", "status"])

    def test_fpass_missing_tool_returns_127(self):
        self.fish('''set -gx PATH "$HOME/bin" /usr/bin /bin
fpass
test $status -eq 127; or exit 1
true
''')


if __name__ == "__main__":
    unittest.main()
