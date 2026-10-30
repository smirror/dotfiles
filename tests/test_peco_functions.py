"""Exercise the helper with an isolated HOME and controlled selector output."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "fish/functions/peco_select_history.fish"
FISH = shutil.which("fish")


@unittest.skipUnless(FISH, "fish is required")
class PecoFunctionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home"
        self.cwd = self.home / "work"
        self.bin = self.home / "bin"
        for directory in (self.cwd, self.bin, self.home / ".config"):
            directory.mkdir(parents=True)
        self.env = {
            "HOME": str(self.home), "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.home / ".local/share"),
            "XDG_CACHE_HOME": str(self.home / ".cache"),
            "PATH": f"{self.bin}:/usr/bin:/bin", "TERM": "dumb",
            "PECO_HELPER": str(HELPER), "PECO_SELECTION": str(self.home / ".config"),
        }
        self.executable("peco", """#!/bin/sh
cat > "$HOME/candidates"
printf '%s\n' "$@" > "$HOME/selector-args"
[ "${PECO_CANCEL:-0}" = 1 ] && exit 130
printf '%s\n' "$PECO_SELECTION"
""")
        (self.home / "commandline").write_text("existing commandline\n")

    def executable(self, name, contents):
        path = self.bin / name
        path.write_text(contents)
        path.chmod(0o755)

    def fish(self, body):
        boot = '''source "$PECO_HELPER"
function commandline
    printf '%s\\n' $argv > "$HOME/commandline"
end
'''
        result = subprocess.run([FISH, "--no-config", "-c", boot + body],
                                cwd=self.cwd, env=self.env, capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(result.stderr, "")
        return result

    def candidates(self):
        return (self.home / "candidates").read_text().splitlines()

    def test_directory_uses_z_data_ranking_and_deduplicates_ghq(self):
        recent = self.home / "recent directory"
        middle, old = self.home / "middle", self.home / "old"
        for path in (recent, middle, old):
            path.mkdir()
        data = self.home / "z-data"
        data.write_text(f"{old}|1|1\n{recent}|1|10\n{middle}|1|2\n")
        self.env["Z_DATA"] = str(data)
        self.executable("ghq", "#!/bin/sh\nprintf '%s/\\n' \"$HOME/recent directory\"\n")
        self.fish("peco_change_directory; or exit 1\n")
        self.assertEqual(self.candidates(),
                         [str(self.home / ".config"), str(recent), str(middle), str(old)])

    def test_missing_history_and_ghq_in_empty_directory_are_quiet(self):
        self.env["Z_DATA"] = str(self.home / "missing-z-data")
        self.fish("peco_change_directory; or exit 1\n")
        self.assertEqual(self.candidates(), [str(self.home / ".config")])

    def test_unset_history_variable_is_quiet(self):
        self.fish("peco_change_directory; or exit 1\n")
        self.assertEqual(self.candidates(), [str(self.home / ".config")])

    def test_directory_with_spaces_is_used_without_escape_characters(self):
        target = self.cwd / "directory (with spaces)"
        target.mkdir()
        self.env["PECO_SELECTION"] = str(target)
        self.fish('''set -g peco_flags sentinel
peco_change_directory 'with spaces'; or exit 1
test "$peco_flags" = sentinel; or exit 2
printf '%s' $PWD > "$HOME/result-pwd"
''')
        self.assertEqual(Path((self.home / "result-pwd").read_text()).resolve(), target.resolve())
        self.assertIn(target.resolve(), [Path(path).resolve() for path in self.candidates()])
        self.assertEqual((self.home / "selector-args").read_text().splitlines(),
                         ["--layout=bottom-up", "--query", "with spaces"])

    def test_directory_cancel_preserves_cwd_and_commandline(self):
        self.env["PECO_CANCEL"] = "1"
        self.fish('''peco_change_directory
test $status -ne 0; or exit 1
printf '%s' $PWD > "$HOME/result-pwd"
''')
        self.assertEqual(Path((self.home / "result-pwd").read_text()).resolve(), self.cwd.resolve())
        self.assertEqual((self.home / "commandline").read_text(), "existing commandline\n")

    def test_history_selection_preserves_command_text_and_globals(self):
        selection = 'printf "%s" "two words"'
        self.env["PECO_SELECTION"] = selection
        self.fish('''function history; printf '%s\\n' 'first command' 'second command'; end
set -g selection sentinel
set -g peco_flags sentinel
peco_select_history 'two words'; or exit 1
test "$selection" = sentinel; or exit 2
test "$peco_flags" = sentinel; or exit 3
''')
        self.assertEqual(self.candidates(), ["first command", "second command"])
        self.assertEqual((self.home / "commandline").read_text(), f"--\n{selection}\n")

    def test_history_cancel_preserves_commandline(self):
        self.env["PECO_CANCEL"] = "1"
        self.fish('''function history; printf '%s\\n' 'dummy command'; end
peco_select_history
test $status -ne 0; or exit 1
''')
        self.assertEqual((self.home / "commandline").read_text(), "existing commandline\n")


if __name__ == "__main__":
    unittest.main()
