#!/bin/bash
# Pliki wydania tematy-v2 (#14): ostatni checker --review, potem listy, archiwum pakietów i sumy.
# Użycie: bash wydaj.sh KATALOG_WYJŚCIOWY (nie może istnieć).
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../../../../.." && pwd)
TASK=$REPO/.maister/tasks/development/2026-10-29-14-tematy-przed-wydaniem
SERIA=$REPO/data/work/tematy-wydanie-20261029
OUT=$1
[ ! -e "$OUT" ] || { echo "cel istnieje: $OUT" >&2; exit 1; }
mkdir -p "$OUT/stage/tematy-v2/przeglady"
cd "$REPO"
for d in "$SERIA"/*-a; do
  id=$(python3 -c "import json,sys;print(next(iter(json.load(open(sys.argv[1]))['counts'])))" "$d/release-manifest.json")
  python3 scripts/check_tematy_package.py --package-dir "$d" --manifest config/generator/tematy-sources.json \
    --config config/generator/tematy.json --review "$TASK/verification/tematy-$id-review.json" > /dev/null
  echo "$id checker --review: ok"
  ID=$(ls "$d" | sed -n 's/\.txt\.gz$//p')
  cp "$d/$ID.txt.gz" "$OUT/"
  cp -R "$d" "$OUT/stage/tematy-v2/$(basename "$d" | sed 's/-a$//')"
  cp "$TASK/verification/tematy-$id-review.json" "$OUT/stage/tematy-v2/przeglady/"
done
chmod -R u+w "$OUT/stage"
COPYFILE_DISABLE=1 tar -C "$OUT/stage" --uid 0 --gid 0 --uname '' --gname '' -cf - tematy-v2 | gzip -n -9 > "$OUT/tematy-v2-pakiety.tar.gz"
rm -rf "$OUT/stage"
cd "$OUT"
for f in *.txt.gz; do printf '%s  %s\n' "$(gzip -dc "$f" | shasum -a 256 | cut -d' ' -f1)" "${f%.gz}"; done > SHA256SUMS-rozpakowane
shasum -a 256 *.txt.gz tematy-v2-pakiety.tar.gz SHA256SUMS-rozpakowane > SHA256SUMS
cat SHA256SUMS
