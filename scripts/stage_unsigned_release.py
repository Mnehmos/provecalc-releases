"""Stage draft-only unsigned binaries; signature/manifest publication stays private."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
sys.path.insert(0, str(Path('scripts').resolve()))
from updater_release import UPDATER_ARTIFACTS


def stage(platform: str, bundle: Path, output: Path) -> None:
    artifacts = [a for a in UPDATER_ARTIFACTS if a.platform == platform]
    if not artifacts:
        raise ValueError('Unsupported build platform.')
    output.mkdir(parents=True, exist_ok=True)
    for artifact in artifacts:
        matches = list(bundle.glob(artifact.bundle_glob))
        if len(matches) != 1 or matches[0].stat().st_size == 0:
            raise ValueError('Required unsigned artifact is missing or ambiguous.')
        source = matches[0]
        shutil.copyfile(source, output / artifact.asset)
        if not source.name.endswith('.app.tar.gz'):
            shutil.copyfile(source, output / source.name)
    if platform.startswith('darwin-'):
        installers = list(bundle.glob('dmg/*.dmg'))
        if len(installers) != 1 or installers[0].stat().st_size == 0:
            raise ValueError('The native Mac disk image is missing or ambiguous.')
        shutil.copyfile(installers[0], output / installers[0].name)


def record(directory: Path, output: Path) -> None:
    names = {p.name for p in directory.iterdir() if p.is_file()}
    if {a.asset for a in UPDATER_ARTIFACTS} - names:
        raise ValueError('Cannot record a partial platform set.')
    data = {
        'sourceSha': os.environ['SOURCE_SHA'], 'sourceTag': os.environ['SOURCE_TAG'],
        'capsuleSha256': os.environ['SOURCE_CAPSULE_SHA256'],
        'runId': os.environ['GITHUB_RUN_ID'], 'runAttempt': os.environ['GITHUB_RUN_ATTEMPT'],
        'workflowSha': os.environ['GITHUB_WORKFLOW_SHA'],
        'assets': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in directory.iterdir() if p.is_file()},
    }
    output.write_text(json.dumps(data, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    if args.record:
        record(args.record, args.out)
    else:
        stage(args.platform, args.bundle, args.out)
