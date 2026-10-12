"""HTML raportu i dashboard jako projekcja kanonicznych Markdown/JSON-YAML."""
import html
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('base_report', ROOT/'scripts/render_report.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
state = json.loads((TASK/'orchestrator-state.yml').read_text())
phase = state['orchestrator']['current_phase']
candidate = phase == 'candidate_assessment'
audit = phase == 'targeted_audit'
calibration = phase == 'pop_calibration'
source = TASK/'outputs'/sys.argv[1] if len(sys.argv)>1 else TASK/('outputs/candidate-assessment.md' if candidate and (TASK/'outputs/candidate-assessment.md').exists() else 'outputs/research-report.md')
report_candidate = source.stem == 'candidate-assessment'
report_audit = source.stem == 'targeted-audit'
report_calibration = source.stem == 'pop-calibration'
report_phase = 'pop_calibration' if report_calibration else 'targeted_audit' if report_audit else 'candidate_assessment' if report_candidate else 'research_foundation'
approved = bool(state['phase_summaries'][report_phase]['gate']['answer'])
badge = ('Kalibracja POP' if report_calibration else 'Audyt celowany' if report_audit else 'Ocena kandydatów' if report_candidate else 'Research') + (' · przyjęty' if approved else ' · do omówienia')
lines = source.read_text().splitlines()
blocks, toc = [], []
i = 1
while i < len(lines):
    line = lines[i]
    if not line.strip():
        i += 1
    elif line.startswith('#'):
        level = len(line)-len(line.lstrip('#'))
        title = line[level:].strip()
        anchor = f'section-{len(toc)}'
        toc.append((anchor, title))
        blocks.append(f'<h{level} id="{anchor}">{base.inline(title)}</h{level}>')
        i += 1
    elif line.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                rows.append(cells)
            i += 1
        table = '<div class="table-scroll"><table>'
        for index, cells in enumerate(rows):
            tag = 'th' if index == 0 else 'td'
            table += '<tr>'+''.join(f'<{tag}>{base.inline(c)}</{tag}>' for c in cells)+'</tr>'
        blocks.append(table+'</table></div>')
    elif line.startswith('- '):
        items = []
        while i < len(lines) and lines[i].startswith('- '):
            items.append('<li>'+base.inline(lines[i][2:])+'</li>')
            i += 1
        blocks.append('<ul>'+''.join(items)+'</ul>')
    else:
        parts = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','- ')):
            parts.append(lines[i])
            i += 1
        blocks.append('<p>'+base.inline(' '.join(parts))+'</p>')
split = next(j for j,b in enumerate(blocks) if 'id="section-3"' in b)
title = lines[0].lstrip('# ')
now = subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'], text=True).strip()
page = '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,">'
page += '<title>'+html.escape(title)+'</title><style>'+base.CSS+'td:first-child{min-width:110px}</style></head><body>'
suite = [('research-report.html','Research'),('candidate-assessment.html','Kandydaci'),('targeted-audit.html','Audyt'),('pop-calibration.html','Granica POP')]
nav = ''.join('<span>'+label+'</span>' if name == source.with_suffix('.html').name else '<a href="'+name+'">'+label+'</a>' for name,label in suite if (source.parent/name).exists() or name == source.with_suffix('.html').name)
dataset = 'round5/baseline-measurements.json' if report_calibration else 'round4/pop-losses.json' if report_audit else 'round3/proposal.json' if report_candidate else 'round2/live-review.json'
page += '<nav class="crumbs"><a href="../dashboard.html">← Dashboard</a>'+nav+'<a href="'+source.name+'" target="_blank" rel="noopener">Markdown ↗</a><a href="../analysis/findings/'+dataset+'" target="_blank" rel="noopener">Dane ↗</a></nav>'
page += '<header><span class="badge">'+badge+'</span><h1>'+html.escape(title)+'</h1><p>'+now+'</p></header>'
metrics = json.loads((TASK/'analysis/findings/round2/metrics.json').read_text())
review = json.loads((TASK/'analysis/findings/round2/live-review.json').read_text())
tiles = [(str(metrics['qualified_lemma_ids']),'grup w pełnym spisie'),(str(metrics['only_arch_lemma_ids']),'grup wyłącznie z arch.'),(str(review['summary']['queries']),'zapytań KWJP'),(str(review['summary']['inspected_contexts']),'ocenionych konkordancji')]
if report_candidate:
    proposal=json.loads((TASK/'analysis/findings/round3/proposal.json').read_text())
    current=json.loads((TASK/'analysis/findings/round3/context-review.json').read_text())
    tiles=[(proposal['counts']['new'],'proponowanych form'),(proposal['counts']['families_with_additions'],'rodzin z dodatkami'),(current['current_words'],'obecnych przyjęć w kontroli'),(current['reviewed_contexts'],'ocenionych konkordancji rundy 3')]
if report_audit:
    proposal=json.loads((TASK/'analysis/findings/round3/proposal.json').read_text())
    losses=json.loads((TASK/'analysis/findings/round4/pop-losses.json').read_text())
    previous=json.loads((TASK/'analysis/findings/round3/current-review.json').read_text())
    tiles=[(proposal['counts']['families_with_additions'],'rodzin w przeglądzie'),(proposal['counts']['new'],'form w propozycji'),(losses['removed_forms'],'wyjaśnionych ubytków POP'),(len(previous['unsupported_evidence_words']),'obecnych zapisów zbadanych osobno')]
if report_calibration:
    measurements=json.loads((TASK/'analysis/findings/round5/baseline-measurements.json').read_text())
    sample=json.loads((TASK/'analysis/findings/round5/sample-design.json').read_text())
    tiles=[(len(measurements['variants']),'wariantów'),(2,'warianty STANDARD'),(sample['unique_lemmas'],'haseł w próbie'),('0','zmian produkcyjnych')]
page += '<div class="tiles">'+''.join(f'<div class="tile"><b>{value}</b><span>{label}</span></div>' for value,label in tiles)+'</div>'
page += '<section class="tldr">'+''.join(blocks[:split])+'</section>'
page += '<nav class="toc">'+ ' · '.join(f'<a href="#{a}">{base.inline(t)}</a>' for a,t in toc[3:])+'</nav>'
page += '<main>'+''.join(blocks[split:])+'</main></body></html>'
source.with_suffix('.html').write_text(page+'\n')
waiting = state['task']['status'] == 'awaiting_approval'
activity = ('Wyniki oceny kandydatów i wpływ na POP do omówienia' if waiting else 'Ocena kandydatów i walidacja wpływu') if candidate else ('Research zakończony; kierunek przyjęty, wdrożenie niezatwierdzone' if state['task']['status'] == 'completed' else 'Pogłębiony research i weryfikacja dowodów')
if audit:
    activity = 'Wyniki audytu POP, rodzin i obecnych przyjęć do omówienia' if waiting else 'Audyt POP oraz niezależna kontrola rodzin i obecnych przyjęć'
    if state['task']['status'] == 'completed':
        activity = 'Audyt przyjęty do omówienia; decyzje o paczce, POP i cofnięciach otwarte'
if calibration:
    activity = 'Kalibracja POP: pełne pomiary, próbki i próg dowodów' if not waiting else 'Wyniki kalibracji POP do omówienia; bez wdrożenia'
names = {'research_foundation':'Badanie i synteza','candidate_assessment':'Ocena kandydatów i wpływu','targeted_audit':'Audyt POP i niezależny przegląd','pop_calibration':'Merytoryczna granica POP'}
phases=[dict(s,id=k,name=names.get(k,k),icon_hint='analysis',status='completed' if s['completed'] else state['task']['status']) for k,s in state['phase_summaries'].items()]
context = state['research_context']
characteristics = {'runda':context['round'], 'tryb':'Tylko research; wdrożenie niezatwierdzone',
                   'pytanie':context['research_question'],
                   'metody':', '.join(context['methodology']),
                   'zakres bieżący':context.get('pop_calibration' if calibration else 'targeted_audit',{}).get('scope','Badanie STANDARD i ocena kandydatów'),
                   'pewność':'Wysoka dla pomiarów; średnia dla ocen językowych'}
data = {'generated':now, 'task':dict(state['task'], type='research', path=str(TASK), current_activity=activity),
        'characteristics':characteristics, 'research_context':context, 'phases':phases+[
            {'id':'solution_generation','name':'Brainstorming','status':'skipped','skip_reason':'Tylko research — prośba użytkownika.'},
            {'id':'high_level_design','name':'Projekt','status':'skipped','skip_reason':'Tylko research — prośba użytkownika.'}],
        'verification':{'status':state['verification_context']['last_status'],'issues':state['verification_context']['issues_found'],
                        'fixes':[], 'reverify_count':0}}
(TASK/'dashboard-data.js').write_text('window.MAISTER_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(source.with_suffix('.html'))
