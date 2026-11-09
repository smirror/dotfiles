"""Definition updates only; every Nix invocation is a temporary fake."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class UpdateLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        (self.repo / "scripts").mkdir()
        shutil.copy2(Path(__file__).resolve().parents[1] / "scripts/update-lock.sh",
                     self.repo / "scripts/update-lock.sh")
        for name in ("flake.nix", "flake.lock", "README.md"):
            (self.repo / name).write_text("fixture\n")
        self.bin = self.repo / "bin"
        self.bin.mkdir()
        self.calls = self.repo / "nix-call.json"
        self.env = {"HOME": str(self.repo), "PATH": f"{self.bin}:/usr/bin:/bin",
                    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q")
        self.git("add", "flake.nix", "flake.lock", "README.md")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "fixture")
        fake = self.bin / "nix"
        fake.write_text(f"#!{sys.executable}\nimport json,sys\n"
                        f"from pathlib import Path\nPath({str(self.calls)!r}).write_text(json.dumps(sys.argv[1:]))\n")
        fake.chmod(0o755)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=self.env,
                       check=True, capture_output=True)

    def run_update(self, *args):
        return subprocess.run(["/bin/sh", str(self.repo / "scripts/update-lock.sh"), *args],
                              cwd=self.repo, env=self.env, capture_output=True, text=True)

    def test_only_definition_update_is_invoked(self):
        (self.repo / "README.md").write_text("unrelated edits\n")
        result = self.run_update()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.calls.read_text()),
                         ["--extra-experimental-features", "nix-command flakes", "flake", "update"])
        self.assertEqual((self.repo / "README.md").read_text(), "unrelated edits\n")

    def test_unstaged_and_staged_input_changes_are_protected(self):
        for staged in (False, True):
            with self.subTest(staged=staged):
                (self.repo / "flake.nix").write_text("unreviewed input\n")
                if staged:
                    self.git("add", "flake.nix")
                result = self.run_update()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("existing flake changes", result.stderr)
                self.assertFalse(self.calls.exists())

    def test_arguments_cannot_select_an_install_or_activation(self):
        result = self.run_update("switch")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_staged_change_is_protected_when_worktree_matches_head(self):
        (self.repo / "flake.nix").write_text("staged input\n")
        self.git("add", "flake.nix")
        (self.repo / "flake.nix").write_text("fixture\n")
        result = self.run_update()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())
