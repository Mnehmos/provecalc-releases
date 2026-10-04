import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_capsule',ROOT/'scripts/decrypt_release_source.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SourceCapsuleTests(unittest.TestCase):
    def test_commit_mismatch_and_path_traversal_never_extract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root/'source.zip'
            with zipfile.ZipFile(archive,'w') as output:
                output.comment = b'1'*40
                output.writestr('../outside.txt','unsafe')
            with self.assertRaisesRegex(ValueError,'commit'):
                module.extract_source(archive,root/'extracted','2'*40)
            with self.assertRaisesRegex(ValueError,'unsafe'):
                module.extract_source(archive,root/'extracted','1'*40)
            self.assertFalse((root/'outside.txt').exists())
            self.assertFalse((root/'extracted').exists())

    def test_real_encryption_round_trip_and_checksum_failure(self):
        openssl = shutil.which('openssl')
        candidate = Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Git/usr/bin/openssl.exe'
        if not openssl and candidate.exists():
            openssl = str(candidate)
        if not openssl:
            self.skipTest('OpenSSL is required for the real source-capsule test')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive,capsule = root/'source.zip',root/'Source.enc'
            with zipfile.ZipFile(archive,'w') as output:
                output.comment=b'1'*40
                output.writestr('README.md','disposable source fixture')
            environment={**os.environ,'SOURCE_ARCHIVE_KEY':'non-signing-source-test-password'}
            subprocess.run([openssl,'enc','-aes-256-cbc','-pbkdf2','-iter','200000','-pass','env:SOURCE_ARCHIVE_KEY','-in',str(archive),'-out',str(capsule)],env=environment,check=True,capture_output=True)
            command=[sys.executable,str(ROOT/'scripts/decrypt_release_source.py'),'--capsule',str(capsule),'--source-sha','1'*40,'--target',str(root/'extracted'),'--openssl',openssl,'--sha256']
            result=subprocess.run([*command,hashlib.sha256(capsule.read_bytes()).hexdigest()],env=environment,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual((root/'extracted/README.md').read_text(),'disposable source fixture')
            result=subprocess.run([*command,'0'*64],env=environment,capture_output=True)
            self.assertNotEqual(result.returncode,0)
