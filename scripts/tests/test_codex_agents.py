"""Behavior checks for installation without touching the real Codex home."""

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "plugins/mynrd-flow/scripts/install_codex_agents.py"
spec = importlib.util.spec_from_file_location("installer", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class AgentInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.destination = self.root / "agents"

    def install(self, check=False):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return installer.install(self.destination, check)

    def snapshot(self):
        return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.destination.iterdir()}

    def test_check_missing_does_not_create_directory(self):
        self.assertEqual(self.install(check=True), 1)
        self.assertFalse(self.destination.exists())

    def test_install_check_and_repeat_preserve_agents(self):
        self.assertEqual(self.install(), 0)
        self.assertEqual(len(list(self.destination.glob("*.toml"))), 6)
        unrelated = self.destination / "personal.toml"
        unrelated.write_text('name = "personal"')
        before = self.snapshot()
        self.assertEqual(self.install(check=True), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.install(), 0)
        for name, original in before.items():
            if name.endswith(".toml"):
                self.assertEqual(self.snapshot()[name], original)

    def test_conflict_prevents_entire_batch(self):
        self.destination.mkdir()
        target = self.destination / "mynrd-python-dev.toml"
        target.write_text('name = "my-custom-python"')
        before = self.snapshot()
        self.assertEqual(self.install(), 1)
        self.assertEqual(self.snapshot(), before)

    def test_local_edit_is_preserved(self):
        self.install()
        target = self.destination / "mynrd-python-dev.toml"
        target.write_text(target.read_text(encoding="utf-8") + "# customized\n", encoding="utf-8")
        before = self.snapshot()
        self.assertEqual(self.install(), 1)
        self.assertEqual(self.snapshot(), before)

    def test_managed_old_version_is_upgraded(self):
        self.install()
        target = self.destination / "mynrd-python-dev.toml"
        expected = target.read_bytes()
        previous = expected + b"# previous generated version\n"
        target.write_bytes(previous)
        receipt_path = self.destination / installer.RECEIPT
        receipt = installer.json.loads(receipt_path.read_text())
        receipt[target.name] = installer.digest(previous)
        receipt_path.write_text(installer.json.dumps(receipt))
        self.assertEqual(self.install(check=True), 1)
        self.assertEqual(target.read_bytes(), previous)
        self.assertEqual(self.install(), 0)
        self.assertEqual(target.read_bytes(), expected)

    def test_cli_scope_and_custom_codex_home(self):
        env = dict(os.environ, CODEX_HOME=str(self.root / "custom home"))
        for args, destination in [
            (["--user"], self.root / "custom home/agents"),
            (["--project", str(self.root / "project space")], self.root / "project space/.codex/agents"),
        ]:
            result = subprocess.run([sys.executable, str(SCRIPT), *args], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(list(destination.glob("*.toml"))), 6)


if __name__ == "__main__":
    unittest.main()
