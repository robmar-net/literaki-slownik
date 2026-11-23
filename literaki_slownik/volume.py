"""Strażnik wolumenu roboczego: G1 (montowanie), G2 (znacznik), G3 (st_dev) i wolne miejsce.

Kody: 75 dysk zniknął, 76 zły wolumen, 78 brak miejsca. UUID wolumenu leży tylko w znaczniku
na wolumenie; poza niego wychodzi wyłącznie losowy `marker_id`.
"""
import os
from pathlib import Path

from . import canonical
from .inputs import GeneratorError

MARKER = '.literaki-work-volume'
GB = 10 ** 9
MIN_FREE_PROCESS = 50 * GB  # start buildu albo wznowienia, jeden proces
MIN_FREE_PAIR = 100 * GB  # start pary A+B na jednym wolumenie (build_pair.sh)
REPO_ROOT = Path(__file__).resolve().parents[1]

_active = None  # (realpath przebiegu, st_dev) aktywnego przebiegu procesu


def mount_point(path):
    """Najbliższy przodek ścieżki po realpath, dla którego os.path.ismount jest prawdą."""
    current = Path(os.path.realpath(path))
    while not os.path.ismount(current) and current.parent != current:
        current = current.parent
    return current


def repo_mount():
    return mount_point(REPO_ROOT)


def read_marker(root):
    """Znacznik w korzeniu wolumenu albo None, gdy go nie ma."""
    path = Path(root) / MARKER
    if not path.exists():
        return None
    try:
        marker = canonical.load_json(path)
    except (OSError, ValueError) as error:
        raise GeneratorError('Nieczytelny znacznik wolumenu roboczego', 76) from error
    if not isinstance(marker, dict) or not isinstance(marker.get('marker_id'), str):
        raise GeneratorError('Znacznik wolumenu roboczego bez marker_id', 76)
    return marker


def free_bytes(path):
    stats = os.statvfs(path)
    return stats.f_bavail * stats.f_frsize


def check_space(path, minimum=MIN_FREE_PROCESS):
    free = free_bytes(path)
    if free < minimum:
        raise GeneratorError(f'Za mało miejsca na wolumenie roboczym: {free // GB} GB < {minimum // GB} GB', 78)


def _marked(mount):
    marker = read_marker(mount)
    if marker is None:
        raise GeneratorError('Zewnętrzny wolumen bez znacznika .literaki-work-volume; '
                             'uruchom scripts/init_work_volume.py', 76)
    return marker


def check_fresh(run_dir, work_root=None):
    """Kontrola przed świeżym buildem. Zwraca work_volume ({marker_id}) albo None (dysk wewnętrzny)."""
    if work_root is not None:
        if not os.path.isdir(work_root):
            raise GeneratorError('Katalog --work-root nie istnieje; dysk roboczy niezamontowany?', 75)
        mount = mount_point(work_root)
        if mount == repo_mount():
            raise GeneratorError('--work-root leży na dysku repo, a wymaga wolumenu ze znacznikiem', 76)
    else:
        mount = mount_point(run_dir)
        if mount == repo_mount():
            return None
    marker = _marked(mount)
    check_space(mount)
    return {'marker_id': marker['marker_id']}


def check_mounted(run_dir):
    """G1 dla istniejącego przebiegu: cel symlinku istnieje i leży na zamontowanym wolumenie."""
    if not os.path.exists(run_dir):
        raise GeneratorError('Cel przebiegu nie istnieje; dysk roboczy zniknął?', 75)
    mount = mount_point(run_dir)
    if os.path.islink(run_dir) and mount == repo_mount():
        raise GeneratorError('Przebieg-symlink wskazuje dysk repo; wolumen roboczy niezamontowany', 75)
    return mount


def check_marker(run_dir, expected_marker_id):
    """G2 dla istniejącego przebiegu. Zwraca work_volume albo None (przebieg wewnętrzny)."""
    mount = mount_point(run_dir)
    if mount == repo_mount():
        if expected_marker_id is None:
            return None
        raise GeneratorError('Przebieg ma marker_id, a wolumen roboczy jest niezamontowany', 75)
    marker = _marked(mount)
    if marker['marker_id'] != expected_marker_id:
        raise GeneratorError('Znacznik wolumenu nie zgadza się z manifestem przebiegu', 76)
    return {'marker_id': marker['marker_id']}


def check_resume(run_dir, expected_marker_id):
    """G1, G2 i miejsce przed --resume albo ponowieniem nadzorcy."""
    check_mounted(run_dir)
    work_volume = check_marker(run_dir, expected_marker_id)
    if work_volume is not None:
        check_space(mount_point(run_dir))
    return work_volume


def find_by_marker(marker_id, volumes='/Volumes'):
    """Punkt montowania w `volumes` ze znacznikiem o tym marker_id albo None."""
    try:
        entries = sorted(Path(volumes).iterdir())
    except OSError:
        return None
    for entry in entries:
        try:
            if os.path.ismount(entry) and (read_marker(entry) or {}).get('marker_id') == marker_id:
                return entry
        except (OSError, GeneratorError):
            continue
    return None


def activate(run_dir):
    """Zapamiętuje przebieg procesu i jego st_dev; podłącza G3 przed os.replace."""
    global _active
    real = os.path.realpath(run_dir)
    _active = (real, os.stat(real).st_dev)
    canonical.set_replace_guard(check_target)


def deactivate():
    global _active
    if _active is not None:
        canonical.set_replace_guard(None)
    _active = None


def check_active():
    """G3: st_dev aktywnego przebiegu bez zmian (przed etapem i przed os.replace)."""
    if _active is None:
        return
    real, device = _active
    try:
        current = os.stat(real).st_dev
    except OSError as error:
        raise GeneratorError('Katalog przebiegu zniknął; dysk roboczy odłączony?', 75) from error
    if current != device:
        raise GeneratorError('st_dev katalogu przebiegu się zmienił; dysk roboczy odłączony?', 75)


def check_target(path):
    """Hak zapisu trwałego: G3 tylko dla celów w aktywnym przebiegu."""
    if _active is None:
        return
    real = _active[0]
    target = os.path.realpath(Path(path).parent)
    if target == real or target.startswith(real + os.sep):
        check_active()
