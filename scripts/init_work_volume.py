#!/usr/bin/env python3
"""Jednorazowe założenie znacznika `.literaki-work-volume` na wolumenie roboczym (#22).

Użycie:
  python3 scripts/init_work_volume.py <korzeń>

Znacznik trafia do korzenia wolumenu, na którym leży <korzeń>. Zawiera UUID wolumenu
z `diskutil info -plist` i losowy `marker_id`. UUID zostaje tylko na wolumenie: stdout
to JSON z samym `marker_id`. Odmowa, gdy znacznik już istnieje (4) albo korzeń leży
na dysku repo (76). Brak korzenia albo błąd diskutil: 75.
"""
import argparse
import json
import os
from pathlib import Path
import plistlib
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import volume  # noqa: E402
from literaki_slownik.canonical import write_json  # noqa: E402
from literaki_slownik.inputs import GeneratorError  # noqa: E402


def volume_uuid(mount):
    try:
        result = subprocess.run(['diskutil', 'info', '-plist', str(mount)], capture_output=True,
                                check=True, timeout=60)
        uuid = plistlib.loads(result.stdout).get('VolumeUUID')
    except (OSError, subprocess.SubprocessError, plistlib.InvalidFileException, ValueError) as error:
        raise GeneratorError('diskutil nie podał UUID wolumenu', 75) from error
    if not isinstance(uuid, str) or not uuid:
        raise GeneratorError('diskutil nie podał UUID wolumenu', 75)
    return uuid


def init(root):
    # Wspólna kontrola korzenia bez wymogu znacznika: brak → 75, dysk repo → 76.
    mount, _ = volume.check_work_root(root, marker=False)
    target = mount / volume.MARKER
    if os.path.lexists(target):
        raise GeneratorError('Znacznik wolumenu już istnieje; nic nie zmieniono', 4)
    marker_id = secrets.token_hex(16)
    write_json(target, {'schema_version': 1, 'marker_id': marker_id, 'volume_uuid': volume_uuid(mount)})
    return marker_id


def main(argv=None):
    parser = argparse.ArgumentParser(description='Znacznik wolumenu roboczego')
    parser.add_argument('root')
    args = parser.parse_args(argv)
    try:
        marker_id = init(args.root)
    except GeneratorError as error:
        print(str(error), file=sys.stderr)
        return error.code
    print(json.dumps({'marker_id': marker_id}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
