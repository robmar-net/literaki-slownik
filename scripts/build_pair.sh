#!/bin/sh
# Dwa niezależne pełne buildy (A i B do verify --peer-run) uruchomione równolegle.
# Każdy build działa na jednym rdzeniu, więc para trwa tyle co jeden przebieg.
# Użycie: scripts/build_pair.sh PREFIKS   → data/work/PREFIKS-RRRRMMDD-GGMMSS-a i -b
set -u
[ $# -eq 1 ] || { echo "użycie: $0 PREFIKS (np. lists-v32)" >&2; exit 2; }
cd "$(dirname "$0")/.." || exit 2
[ -z "$(git status --porcelain -- literaki_slownik)" ] || { echo "kod generatora niezacommitowany: verify odmówi (K8)" >&2; exit 2; }
stamp=$(date +%Y%m%d-%H%M%S)
pids=
for side in a b; do
  run="data/work/$1-$stamp-$side"
  [ -e "$run" ] && { echo "istnieje: $run" >&2; exit 2; }
  /usr/bin/time -l python3 -m literaki_slownik build --manifest config/generator/sources.json \
    --run-dir "$run" --json > "$run.out.json" 2> "$run.err" &
  pids="$pids $!"
  echo "$side: $run (pid $!)"
done
rc=0
for pid in $pids; do wait "$pid" || rc=1; done
echo "koniec: rc=$rc"
exit $rc
