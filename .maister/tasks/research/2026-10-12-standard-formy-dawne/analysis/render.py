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
source = TASK/'outputs'/sys.argv[1] if len(sys.argv)>1 else TASK/('outputs/candidate-assessment.md' if candidate and (TASK/'outputs/candidate-assessment.md').exists() else 'outputs/research-report.md')
report_candidate = source.stem == 'candidate-assessment'
approved = bool(state['phase_summaries'][phase if report_candidate else 'research_foundation']['gate']['answer'])
badge = ('Ocena kandydatów' if report_candidate else 'Research') + (' · przyjęta' if approved else ' · do omówienia')
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
page = '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
page += '<title>'+html.escape(title)+'</title><style>'+base.CSS+'</style></head><body>'
page += '<nav class="crumbs"><a href="../dashboard.html">← Dashboard</a><span>Raport</span><a href="'+source.name+'" target="_blank" rel="noopener">Markdown ↗</a><a href="../analysis/findings/'+('round3/proposal.json' if report_candidate else 'round2/live-review.json')+'" target="_blank" rel="noopener">Dane ↗</a></nav>'
page += '<header><span class="badge">'+badge+'</span><h1>'+html.escape(title)+'</h1><p>'+now+'</p></header>'
metrics = json.loads((TASK/'analysis/findings/round2/metrics.json').read_text())
review = json.loads((TASK/'analysis/findings/round2/live-review.json').read_text())
tiles = [(str(metrics['qualified_lemma_ids']),'grup w pełnym spisie'),(str(metrics['only_arch_lemma_ids']),'grup wyłącznie z arch.'),(str(review['summary']['queries']),'zapytań KWJP'),(str(review['summary']['inspected_contexts']),'ocenionych konkordancji')]
if report_candidate:
    proposal=json.loads((TASK/'analysis/findings/round3/proposal.json').read_text())
    current=json.loads((TASK/'analysis/findings/round3/context-review.json').read_text())
    tiles=[(proposal['counts']['new'],'proponowanych form'),(proposal['counts']['families_with_additions'],'rodzin z dodatkami'),(current['current_words'],'obecnych przyjęć w kontroli'),(current['reviewed_contexts'],'ocenionych konkordancji rundy 3')]
page += '<div class="tiles">'+''.join(f'<div class="tile"><b>{value}</b><span>{label}</span></div>' for value,label in tiles)+'</div>'
page += '<section class="tldr">'+''.join(blocks[:split])+'</section>'
page += '<nav class="toc">'+ ' · '.join(f'<a href="#{a}">{html.escape(t)}</a>' for a,t in toc[3:])+'</nav>'
page += '<main>'+''.join(blocks[split:])+'</main></body></html>'
source.with_suffix('.html').write_text(page+'\n')
waiting = state['task']['status'] == 'awaiting_approval'
activity = ('Wyniki oceny kandydatów i wpływ na POP do omówienia' if waiting else 'Ocena kandydatów i walidacja wpływu') if candidate else ('Research zakończony; kierunek przyjęty, wdrożenie niezatwierdzone' if state['task']['status'] == 'completed' else 'Pogłębiony research i weryfikacja dowodów')
phases=[dict(s,id=k,name='Badanie i synteza' if k=='research_foundation' else 'Ocena kandydatów i wpływu',icon_hint='analysis',status='completed' if s['completed'] else state['task']['status']) for k,s in state['phase_summaries'].items()]
data = {'generated':now, 'task':dict(state['task'], type='research', path=str(TASK), current_activity=activity),
        'characteristics':state['research_context'], 'phases':phases+[
            {'id':'solution_generation','name':'Brainstorming','status':'skipped','skip_reason':'Tylko research — prośba użytkownika.'},
            {'id':'high_level_design','name':'Projekt','status':'skipped','skip_reason':'Tylko research — prośba użytkownika.'}],
        'verification':{'status':state['verification_context']['last_status'],'issues':state['verification_context']['issues_found'],
                        'fixes':[], 'reverify_count':0}}
(TASK/'dashboard-data.js').write_text('window.MAISTER_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(source.with_suffix('.html'))
