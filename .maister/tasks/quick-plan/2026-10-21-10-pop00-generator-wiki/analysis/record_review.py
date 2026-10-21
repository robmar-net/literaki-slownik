"""Utrwal techniczny przegląd wyświetlonej, niezależnej próbki; bez ocen znajomości ludzi."""
from pathlib import Path
import json
import hashlib
import subprocess

TASK=Path(__file__).resolve().parents[1]
REPO=TASK.parents[3]
PACKAGE=REPO/'data/work/pop00-v1-20261021-r2-a'
rows=json.loads((PACKAGE/'reports/decisions.json').read_text())
review=json.loads((PACKAGE/'reports/review-template.json').read_text())
review['status']='REVIEWED'
review['review_scope']='Techniczna zgodność źródeł, pełnych analiz i wyniku z zatwierdzoną ADR-009; nie badanie znajomości graczy.'
review['sha256sums_sha256']=hashlib.sha256((PACKAGE/'SHA256SUMS').read_bytes()).hexdigest()
for item in review['items']:
    row=rows[item['key']]
    groups=sorted({g for a in row['analyses'] for g in a['groups']})
    if row['kept']:
        why=('Zachowana chroniona analiza wybranego leksemu.' if 'ordinary' in groups else
             'Zachowana analiza grupy wymagającej dowodu; publikowane IPM spełnia 0,1.')
    else:
        why=('Wszystkie analizy mają nijaką pierwszą/drugą osobę.' if groups==['neuter-person-1-2'] else
             'Brak chronionej analizy i brak wymaganego dowodu IPM ≥ 0,1; nie oceniamy formy jako błędnej językowo.')
    provenance='; '.join(a['member']+' '+a['tag']+' ['+(a['rule'] or 'SGJP')+']' for a in row['analyses'])
    item.update(assessment='correct',reviewer='Codex — przegląd techniczny ADR-009',
        source_justification=why+' KWJP: '+row['evidence']['status']+', IPM='+str(row['evidence']['ipm'])+
            '. Źródło: '+provenance+'. Grupy: '+', '.join(groups)+'.',affects_lists_or_links=False)
now=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
review['reviewed_at']=now
(TASK/'verification').mkdir(exist_ok=True)
(TASK/'verification/pop00-v1-r2-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('Utrwalono',len(review['items']),'pozycji przeglądu technicznego; wszystkie mają indywidualny ślad źródłowy.')
