#!/bin/zsh
# Seria budów v2 (#13; kopia buduj_fale.sh z #12): 7 tematów po kolei, każdy a, potem b, potem
# verify_real.py --fala (checker na a i b, a = b, bez T3/IATE, srodladowe = null).
# Nigdy równolegle. Bez commitów w trakcie serii (code_identity zapisuje HEAD).
# Błąd budowy albo kontroli zatrzymuje serię (kod != 0).
# Użycie: buduj_fale.sh [DATA] [temat…]  (domyślnie dzisiejsza data i 7 tematów v2)
set -u
setopt pipefail

TASK=${0:A:h:h}
REPO=${TASK:h:h:h:h}
cd "$REPO" || exit 5

DATA=${1:-$(date +%Y%m%d)}
(( $# )) && shift
TEMATY=(grzyby pogoda matematyka muzyka sport kuchnia medycyna)
(( $# )) && TEMATY=("$@")
LOG=data/work/fala-1-v2-$DATA.log
CZASY=data/work/fala-1-v2-$DATA-czasy
mkdir -p "$CZASY"

log() { print -r -- "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" | tee -a "$LOG"; }

log "START seria v2, HEAD $(git rev-parse HEAD), tematy: $TEMATY"
if [[ -n "$(git status --porcelain --untracked-files=normal -- config scripts literaki_slownik)" ]]; then
  log "STOP: zmiany w config/, scripts/ lub literaki_slownik/"; exit 5
fi

for t in $TEMATY; do
  topic=config/generator/tematy/$t.json
  wersja=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["wersja"])' "$topic") || exit 2
  json="{"
  for s in a b; do
    out=data/work/tematy-$wersja-$DATA-$s
    log "BUDOWA $t $s → $out"
    start=$(date +%s)
    python3 -m literaki_slownik tematy --manifest config/generator/tematy-sources.json \
      --config config/generator/tematy.json --topic "$topic" --output-dir "$out" --json \
      >"$CZASY/$t-$s.out.json" 2>"$CZASY/$t-$s.err"
    kod=$?
    end=$(date +%s)
    log "KONIEC $t $s kod $kod, $((end - start)) s"
    [[ $s == b ]] && json+=","
    json+="\"$s\": {\"start\": $start, \"end\": $end, \"exit\": $kod, \"sekundy\": $((end - start))}"
    if (( kod != 0 )); then
      log "STOP: budowa $t $s kod $kod"; tail -5 "$CZASY/$t-$s.err" | tee -a "$LOG"; exit $kod
    fi
  done
  print -r -- "$json}" >"$CZASY/$t.json"
  log "KONTROLA $t (checker a, b; verify_real --fala)"
  python3 "$TASK/analysis/verify_real.py" --fala --topic "$topic" \
    --a data/work/tematy-$wersja-$DATA-a --b data/work/tematy-$wersja-$DATA-b \
    --times "$CZASY/$t.json" --output "$TASK/verification/verify-$t.json" 2>&1 | tee -a "$LOG"
  kod=$?
  if (( kod != 0 )); then
    log "STOP: kontrola $t kod $kod"; exit 1
  fi
  log "OK $t"
done
log "KONIEC serii, HEAD $(git rev-parse HEAD)"
