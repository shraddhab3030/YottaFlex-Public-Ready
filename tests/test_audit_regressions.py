"""Confirmed final-audit portability regression; no change to business policies."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from yottaflex import deliverables
from yottaflex.deliverables import build_package,verify_package
from yottaflex.generation_config import GenerationConfig


class SourceProvenanceTests(unittest.TestCase):
    def test_package_builds_and_verifies_when_git_metadata_is_unavailable(self):
        with tempfile.TemporaryDirectory(prefix='yottaflex-source-export-') as name:
            root=Path(name)
            with patch('yottaflex.deliverables.subprocess.check_output',side_effect=subprocess.CalledProcessError(128,['git'])):
                manifest,_=build_package(root/'package',GenerationConfig())
            self.assertIsNone(manifest['generator_git_commit'])
            self.assertEqual(len(manifest['generator_source_sha256']),64)
            result,_=verify_package(root/'package',root/'restore')
            self.assertTrue(result['passed'])

    def test_unrelated_ancestor_repository_is_not_claimed_as_source_revision(self):
        with patch('yottaflex.deliverables.subprocess.check_output',return_value='/unrelated-repository\n'):
            self.assertIsNone(deliverables.source_revision())

    def test_missing_git_executable_does_not_block_source_fingerprint(self):
        with patch('yottaflex.deliverables.subprocess.check_output',side_effect=FileNotFoundError('git unavailable')):
            self.assertIsNone(deliverables.source_revision())
