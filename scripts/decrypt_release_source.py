"""Decrypt a hash-bound source capsule; never expose its key in arguments/logs."""
import argparse
import hashlib
import os
import platform
from pathlib import Path, PurePosixPath
import subprocess
import shutil
import tempfile
import zipfile


def extract_source(archive: Path, target: Path, revision: str) -> None:
    with zipfile.ZipFile(archive) as source:
        if source.comment.decode('ascii') != revision:
            raise ValueError('Source archive does not match the requested commit.')
        for item in source.infolist():
            relative = PurePosixPath(item.filename)
            if relative.is_absolute() or '..' in relative.parts or '\\' in item.filename:
                raise ValueError('Source archive contains an unsafe path.')
        source.extractall(target)
        for item in source.infolist():
            if not item.is_dir():
                (target / item.filename).chmod((item.external_attr >> 16) & 0o777 or 0o644)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--capsule', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--source-sha', required=True)
    parser.add_argument('--target', type=Path, default=Path('.'))
    parser.add_argument('--openssl', default=shutil.which('openssl'))
    args = parser.parse_args()
    if platform.system() == 'Darwin':
        prefix = subprocess.run(['brew','--prefix','openssl@3'],capture_output=True,text=True)
        if prefix.returncode:
            raise SystemExit('The runner requires Homebrew OpenSSL 3 for source decryption.')
        args.openssl = str(Path(prefix.stdout.strip()) / 'bin/openssl')
    if not args.openssl:
        raise SystemExit('OpenSSL is unavailable on this runner.')
    if hashlib.sha256(args.capsule.read_bytes()).hexdigest() != args.sha256:
        raise SystemExit('Encrypted source capsule checksum mismatch.')
    if not os.environ.get('SOURCE_ARCHIVE_KEY'):
        raise SystemExit('Source capsule credential is missing.')
    with tempfile.TemporaryDirectory() as directory:
        archive = Path(directory) / 'source.zip'
        result = subprocess.run([args.openssl, 'enc', '-d', '-aes-256-cbc', '-pbkdf2',
                                 '-iter', '200000', '-pass', 'env:SOURCE_ARCHIVE_KEY',
                                 '-in', str(args.capsule), '-out', str(archive)], capture_output=True)
        if result.returncode:
            raise SystemExit('Source capsule decryption failed.')
        extract_source(archive, args.target, args.source_sha)
    print('Source capsule checksum and commit identity verified.')


if __name__ == '__main__':
    main()
