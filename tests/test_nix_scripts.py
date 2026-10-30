"""Run with python3 -B -m unittest discover -s tests -v; no real installation."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "scripts"


class NixScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "dotfiles repo"
        self.bin = self.base / "bin"
        (self.repo / "scripts").mkdir(parents=True)
        self.bin.mkdir()
        for name in ("bootstrap.sh", "home-manager.sh"):
            shutil.copy2(SOURCE / name, self.repo / "scripts" / name)
        self.calls = self.base / "calls.jsonl"
        self.env = {"HOME": str(self.base / "home"), "TMPDIR": str(self.base),
                    "PATH": f"{self.bin}:/usr/bin:/bin", "CALLS": str(self.calls),
                    "TEST_OS": "Darwin", "TEST_ARCH": "arm64"}
        self.executable("uname", 'import os,sys\nprint(os.environ["TEST_OS" if sys.argv[1] == "-s" else "TEST_ARCH"])\n')
        self.executable("id", 'print("fixture-user")\n')
        self.executable("curl", '''import os,sys
from pathlib import Path
Path(os.environ["HOME"]).mkdir(exist_ok=True)
Path(os.environ["HOME"], "curl-called").touch()
Path(sys.argv[sys.argv.index("--output") + 1]).write_text("echo not-the-pinned-installer\\n")
''')
        self.executable("sh", '''import os,sys,json
with open(os.environ["CALLS"], "a") as f: f.write(json.dumps({"installer": sys.argv[1:]}) + "\\n")
''')

    def executable(self, name, code):
        path = self.bin / name
        path.write_text(f"#!{sys.executable}\n" + code)
        path.chmod(0o755)

    def fake_nix(self):
        self.executable("nix", '''import os,sys,json
with open(os.environ["CALLS"], "a") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "user": os.environ.get("DOTFILES_USER"), "home": os.environ.get("DOTFILES_HOME")}) + "\\n")
''')

    def run_script(self, name, *args):
        return subprocess.run(["/bin/sh", str(self.repo / "scripts" / name), *args],
                              env=self.env, text=True, capture_output=True, timeout=10)

    def records(self):
        return [json.loads(line) for line in self.calls.read_text().splitlines()] if self.calls.exists() else []

    def test_bootstrap_existing_nix_does_nothing(self):
        self.fake_nix()
        result = self.run_script("bootstrap.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("already available", result.stdout)
        self.assertFalse((Path(self.env["HOME"]) / "curl-called").exists())
        self.assertEqual(self.records(), [])

    def test_unsupported_platform_is_rejected_before_download(self):
        for os_name, arch in (("FreeBSD", "arm64"), ("Linux", "riscv64")):
            self.env.update(TEST_OS=os_name, TEST_ARCH=arch)
            for script in ("bootstrap.sh", "home-manager.sh"):
                result = self.run_script(script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Supported platforms", result.stderr)
        self.assertFalse((Path(self.env["HOME"]) / "curl-called").exists())
        self.assertEqual(self.records(), [])

    def test_checksum_failure_never_runs_installer(self):
        result = self.run_script("bootstrap.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((Path(self.env["HOME"]) / "curl-called").exists())
        self.assertEqual(self.records(), [])
        self.assertEqual(list(self.base.glob("dotfiles-nix.*")), [])

    def test_missing_curl_is_reported_before_download(self):
        (self.bin / "curl").unlink()
        for command in ("git", "mktemp", "rm"):
            (self.bin / command).symlink_to(shutil.which(command))
        self.env["PATH"] = str(self.bin)
        result = self.run_script("bootstrap.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Required command missing: curl", result.stderr)
        self.assertEqual(self.records(), [])

    def test_verified_installer_invocation_uses_platform_mode_only(self):
        # Replace the executor and checksum utility; never execute an installer.
        self.executable("sha256sum", 'import sys\nsys.stdin.read()\n')
        for os_name, arch, expected in (("Darwin", "arm64", "--daemon"), ("Linux", "aarch64", "--daemon" if Path("/run/systemd/system").is_dir() else "--no-daemon")):
            with self.subTest(os=os_name):
                self.env.update(TEST_OS=os_name, TEST_ARCH=arch)
                result = self.run_script("bootstrap.sh")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.records()[-1]["installer"][-1], expected)
                self.assertEqual(list(self.base.glob("dotfiles-nix.*")), [])

    def test_common_build_and_identity_are_forwarded_for_all_systems(self):
        self.fake_nix()
        self.env.update(DOTFILES_USER="test-user", DOTFILES_HOME="/temporary/home with spaces")
        for os_name, arch, target in (("Darwin", "arm64", "aarch64-darwin"),
                                      ("Darwin", "x86_64", "x86_64-darwin"),
                                      ("Linux", "aarch64", "aarch64-linux"),
                                      ("Linux", "x86_64", "x86_64-linux")):
            with self.subTest(target=target):
                self.env.update(TEST_OS=os_name, TEST_ARCH=arch)
                result = self.run_script("home-manager.sh")
                self.assertEqual(result.returncode, 0, result.stderr)
                row = self.records()[-1]
                self.assertEqual(row["argv"], ["--extra-experimental-features", "nix-command flakes", "run",
                    f"{self.repo}#home-manager", "--", "build", "--flake", f"{self.repo}#{target}", "--impure"])
                self.assertEqual((row["user"], row["home"]), ("test-user", "/temporary/home with spaces"))

    def test_check_explicitly_evaluates_all_profiles(self):
        self.fake_nix()
        result = self.run_script("home-manager.sh", "check")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = self.records()
        self.assertEqual(len(records), 4)
        for row, target in zip(records, ("aarch64-darwin", "x86_64-darwin", "aarch64-linux", "x86_64-linux")):
            self.assertEqual(row["argv"], ["--extra-experimental-features", "nix-command flakes", "eval", "--impure", "--raw",
                f"{self.repo}#homeConfigurations.{target}.activationPackage.drvPath"])
            self.assertEqual((row["user"], row["home"]), ("fixture-user", self.env["HOME"]))

    def test_failed_profile_evaluation_stops_the_check(self):
        self.executable("nix", '''import os,sys
with open(os.environ["CALLS"], "a") as f: f.write(sys.argv[-1] + "\\n")
sys.exit(7 if "x86_64-darwin" in sys.argv[-1] else 0)
''')
        result = self.run_script("home-manager.sh", "check")
        self.assertEqual(result.returncode, 7)
        self.assertEqual(len(self.calls.read_text().splitlines()), 2)

    def test_switch_is_explicit_and_has_no_forced_overwrite(self):
        self.fake_nix()
        result = self.run_script("home-manager.sh", "switch")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = self.records()[-1]["argv"]
        self.assertEqual(argv[5], "switch")
        self.assertNotIn("--force", argv)
        self.assertNotIn("-b", argv)

    def test_switch_rejects_other_identity_before_running_nix(self):
        self.fake_nix()
        for user, home in (("other-user", self.env["HOME"]),
                           ("fixture-user", "/temporary/other-home"),
                           ("other-user", "/temporary/other-home")):
            with self.subTest(user=user, home=home):
                self.env.update(DOTFILES_USER=user, DOTFILES_HOME=home)
                result = self.run_script("home-manager.sh", "switch")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("current user and HOME", result.stderr)
        self.assertEqual(self.records(), [])

    def test_check_and_build_keep_cross_identity_overrides(self):
        self.fake_nix()
        self.env.update(DOTFILES_USER="other-user", DOTFILES_HOME="/temporary/other-home")
        for action in ("check", "build"):
            result = self.run_script("home-manager.sh", action)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.records()), 5)
        for row in self.records():
            self.assertEqual((row["user"], row["home"]), ("other-user", "/temporary/other-home"))

    def test_root_home_is_rejected_for_every_action(self):
        self.fake_nix()
        self.env["DOTFILES_HOME"] = "/"
        for action in ("check", "build", "switch"):
            result = self.run_script("home-manager.sh", action)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("root directory", result.stderr)
        self.assertEqual(self.records(), [])

    def test_invalid_arguments_or_relative_home_do_not_run_nix(self):
        self.fake_nix()
        for args in (("invalid",), ("build", "extra")):
            self.assertNotEqual(self.run_script("home-manager.sh", *args).returncode, 0)
        self.env["DOTFILES_HOME"] = "relative/path"
        result = self.run_script("home-manager.sh")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute path", result.stderr)
        self.assertEqual(self.records(), [])


if __name__ == "__main__":
    unittest.main()
