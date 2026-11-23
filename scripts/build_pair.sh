#!/bin/sh
# Dwa niezależne pełne buildy (A i B do verify --peer-run) na wolumenie roboczym, każdy pod nadzorcą
# (scripts/build_supervised.py: po zniknięciu dysku czeka i wznawia). Każdy build działa na jednym
# rdzeniu, więc para trwa tyle co jeden przebieg. Obaj nadzorcy działają pod `caffeinate -dimsu`.
# Użycie (odpięte od terminala; zamknięcie okna nie kończy pary):
#   mkdir -p logs && LITERAKI_WORK_ROOT=<korzeń wolumenu> \
#     nohup scripts/build_pair.sh PREFIKS > logs/pair-PREFIKS.log 2>&1 & disown
#   → data/work/PREFIKS-RRRRMMDD-GGMMSS-a i -b (symlinki na wolumen), logi w logs/ na dysku wewnętrznym:
#   logs/<nazwa>.supervisor.log (zdarzenia nadzorcy), .supervisor.out (jego końcowy JSON), .out.json, .err.
# Kody: 0 obie strony 0; 2 argumenty, brak LITERAKI_WORK_ROOT albo niezacommitowany kod;
# 75 brak wolumenu; 76 zły wolumen (także korzeń na dysku repo); 78 mniej niż 100 GB wolnego;
# 1 któryś nadzorca nie skończył 0.
set -u
[ $# -eq 1 ] || { echo "użycie: LITERAKI_WORK_ROOT=<korzeń> $0 PREFIKS (np. lists-v32)" >&2; exit 2; }
[ -n "${LITERAKI_WORK_ROOT:-}" ] || { echo "brak LITERAKI_WORK_ROOT: korzeń wolumenu roboczego" >&2; exit 2; }
cd "$(dirname "$0")/.." || exit 2
[ -z "$(git status --porcelain -- literaki_slownik)" ] || { echo "kod generatora niezacommitowany: verify odmówi (K8)" >&2; exit 2; }
python3 -c '
import sys
from literaki_slownik import volume
from literaki_slownik.inputs import GeneratorError
try:
    volume.check_work_root(sys.argv[1], volume.MIN_FREE_PAIR)
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
    --run-dir "$run" --work-root "$LITERAKI_WORK_ROOT" >> "logs/$name.supervisor.out" 2>> "logs/$name.err" &
  pids="$pids $!"
  echo "$side: $run (pid $!, logi logs/$name.*)"
done
rc=0
for pid in $pids; do wait "$pid" || rc=1; done
echo "koniec: rc=$rc"
exit $rc
