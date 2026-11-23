#!/bin/sh
# Dwa niezależne pełne buildy (A i B do verify --peer-run) na wolumenie roboczym, każdy pod nadzorcą
# (scripts/build_supervised.py: po zniknięciu dysku czeka i wznawia). Każdy build działa na jednym
# rdzeniu, więc para trwa tyle co jeden przebieg. Obaj nadzorcy działają pod `caffeinate -dimsu`.
# Użycie: LITERAKI_WORK_ROOT=<korzeń wolumenu> scripts/build_pair.sh PREFIKS
#   → data/work/PREFIKS-RRRRMMDD-GGMMSS-a i -b (symlinki na wolumen), logi w logs/ na dysku wewnętrznym.
# Kody: 0 obie strony 0; 2 argumenty, brak LITERAKI_WORK_ROOT albo niezacommitowany kod;
# 75 brak wolumenu; 76 zły wolumen; 78 mniej niż 100 GB wolnego; 1 któryś nadzorca nie skończył 0.
set -u
[ $# -eq 1 ] || { echo "użycie: LITERAKI_WORK_ROOT=<korzeń> $0 PREFIKS (np. lists-v32)" >&2; exit 2; }
[ -n "${LITERAKI_WORK_ROOT:-}" ] || { echo "brak LITERAKI_WORK_ROOT: korzeń wolumenu roboczego" >&2; exit 2; }
cd "$(dirname "$0")/.." || exit 2
[ -z "$(git status --porcelain -- literaki_slownik)" ] || { echo "kod generatora niezacommitowany: verify odmówi (K8)" >&2; exit 2; }
python3 -c '
import os, sys
from literaki_slownik import volume
from literaki_slownik.inputs import GeneratorError
root = sys.argv[1]
try:
    if not os.path.isdir(root):
        raise GeneratorError("LITERAKI_WORK_ROOT nie istnieje; wolumen niezamontowany?", 75)
    mount = volume.mount_point(root)
    if mount == volume.repo_mount() or volume.read_marker(mount) is None:
        raise GeneratorError("LITERAKI_WORK_ROOT bez znacznika wolumenu roboczego", 76)
    volume.check_space(mount, volume.MIN_FREE_PAIR)
except GeneratorError as error:
    print(error, file=sys.stderr)
    sys.exit(error.code)
' "$LITERAKI_WORK_ROOT" || exit $?
mkdir -p logs || exit 2
stamp=$(date +%Y%m%d-%H%M%S)
pids=
for side in a b; do
  name="$1-$stamp-$side"
  run="data/work/$name"
  [ -e "$run" ] || [ -L "$run" ] && { echo "istnieje: $run" >&2; exit 2; }
  caffeinate -dimsu python3 scripts/build_supervised.py --manifest config/generator/sources.json \
    --run-dir "$run" --work-root "$LITERAKI_WORK_ROOT" >> "logs/$name.supervisor.log" 2>> "logs/$name.err" &
  pids="$pids $!"
  echo "$side: $run (pid $!, logi logs/$name.*)"
done
rc=0
for pid in $pids; do wait "$pid" || rc=1; done
echo "koniec: rc=$rc"
exit $rc
