"""Offline release boundaries: these tests must never attach to a broker."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
import server


class ReleaseTests(unittest.TestCase):
    def test_server_denies_live_access_before_starting_worker(self):
        with patch.dict(os.environ, {'AJAIB_ENABLE_LIVE_ACCESS': '0'}), patch.object(server, 'worker') as worker:
            for action in ('status', 'portfolio', 'quote', 'buying_power'):
                with self.assertRaisesRegex(RuntimeError, 'Live access is disabled'):
                    asyncio.run(server.read(action))
            worker.assert_not_called()

    def test_direct_worker_denies_live_access_before_importing_adapter(self):
        process = subprocess.run([sys.executable, '-X', 'utf8', str(Path(__file__).with_name('worker.py'))],
            input='{"action":"portfolio"}', capture_output=True, text=True, timeout=10,
            env=dict(os.environ, AJAIB_ENABLE_LIVE_ACCESS='0'))
        self.assertIn('Live access is disabled', json.loads(process.stdout)['error'])
        self.assertEqual(process.stderr, '')

    def test_bad_worker_output_is_not_echoed(self):
        completed = subprocess.CompletedProcess([], 0, stdout='PRIVATE ACCOUNT TEXT', stderr='')
        with patch.object(server.subprocess, 'run', return_value=completed):
            with self.assertRaisesRegex(RuntimeError, 'valid response') as error:
                server.worker('status', None)
            self.assertNotIn('PRIVATE', str(error.exception))


if __name__ == '__main__':
    unittest.main()
