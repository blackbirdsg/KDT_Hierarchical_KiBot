"""Mocked launcher regression tests; no CAD or KiBot generation is performed."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = r'C:\Program Files\Git\bin\bash.exe'

def posix(path):
    value = Path(path).resolve().as_posix()
    return '/' + value[0].lower() + value[2:] if value[1:2] == ':' else value

class LauncherTests(unittest.TestCase):
    def run_case(self, version, cli_exit=0, kibot_exit=0):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'kicad-cli').write_text('#!/bin/bash\necho "$MOCK_VERSION"\nexit "$MOCK_CLI_EXIT"\n')
            (folder / 'kibot').write_text('#!/bin/bash\nprintf "%s\\n" "$*" >> "$MOCK_LOG"\nexit "$MOCK_KIBOT_EXIT"\n')
            env = dict(os.environ, MOCK_VERSION=version, MOCK_CLI_EXIT=str(cli_exit),
                       MOCK_KIBOT_EXIT=str(kibot_exit), MOCK_LOG=posix(folder / 'calls'))
            command = f'export PATH="{posix(folder)}:$PATH"; bash ./kibot_launch.sh --version fixture -v CHECKED'
            result = subprocess.run([BASH, '-c', command], cwd=ROOT, env=env, capture_output=True, text=True)
            calls = (folder / 'calls').read_text().splitlines() if (folder / 'calls').exists() else []
            return result, calls

    def test_supported_versions(self):
        for version, group in [('8.0.9', 'all_group'), ('9.0.7', 'all_group_k9'),
                               ('9.0.0-rc1', 'all_group_k9'), ('10.0.3', 'all_group_k10')]:
            with self.subTest(version=version):
                result, calls = self.run_case(version)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[-1].split()[-1], group)

    def test_unknown_version_stops(self):
        result, calls = self.run_case('11.0.0')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])

    def test_version_failure_stops(self):
        result, calls = self.run_case('10.0.3', cli_exit=2)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])

    def test_first_generation_failure_stops(self):
        result, calls = self.run_case('10.0.3', kibot_exit=7)
        self.assertEqual(result.returncode, 7)
        self.assertEqual(len(calls), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
