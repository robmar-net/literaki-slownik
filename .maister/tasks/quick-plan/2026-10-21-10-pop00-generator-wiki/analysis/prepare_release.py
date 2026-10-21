"""Pakiet publicznych plików po niezależnym odbiorze; bez nadpisywania wydania."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

TASK=Path(__file__).resolve().parents[1]
REPO=TASK.parents[3]
proof=json.loads((TASK/'verification/real-builds-r2.json').read_text())
review_check=json.loads((TASK/'verification/review-check-r2.json').read_text())
assert proof['all_files_identical'] and all(c['status']=='pass' for c in proof['checks'])
assert review_check['status']=='pass' and review_check['review_checked']
base=REPO/proof['packages'][0]
out=REPO/'tmp/release-pop00-v1'
out.mkdir(exist_ok=False)
for name,source in {'POP00.txt.gz':base/'POP00.txt.gz','release-manifest.json':base/'release-manifest.json',
                    'pop00-v1-review.json':TASK/'verification/pop00-v1-r2-review.json'}.items():
    shutil.copyfile(source,out/name)
with open(out/'pop00-v1-pakiet.tar.gz','wb') as raw:
    with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0,compresslevel=9) as gz:
        with tarfile.open(fileobj=gz,mode='w') as archive:
            for path in sorted(base.rglob('*')):
                if path.is_file():
                    name='pop00-v1/'+path.relative_to(base).as_posix()
                    info=tarfile.TarInfo(name)
                    info.size=path.stat().st_size;info.mode=0o444;info.mtime=0
                    with path.open('rb') as f:archive.addfile(info,f)
plain=gzip.decompress((base/'POP00.txt.gz').read_bytes())
(out/'SHA256SUMS-rozpakowane').write_text(hashlib.sha256(plain).hexdigest()+'  POP00.txt\n')
sums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
(out/'SHA256SUMS').write_text(''.join(d+'  '+name+'\n' for name,d in sums.items()))
print(json.dumps({'directory':str(out.relative_to(REPO)),'files_sha256':sums},ensure_ascii=False,indent=2))
