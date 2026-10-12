"""HTML raportu i dashboard jako projekcja kanonicznych Markdown/JSON-YAML."""
import html
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('base_report', ROOT/'scripts/render_report.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
source = TASK/'outputs/research-report.md'
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
page += '<nav class="crumbs"><a href="../dashboard.html">← Dashboard</a><span>Raport</span><a href="research-report.md" target="_blank" rel="noopener">Markdown ↗</a><a href="../analysis/findings/sample-review.md" target="_blank" rel="noopener">Próbki ↗</a></nav>'
page += '<header><span class="badge">Research · do omówienia</span><h1>'+html.escape(title)+'</h1><p>'+now+'</p></header>'
page += '<div class="tiles">'+''.join(f'<div class="tile"><b>{value}</b><span>{label}</span></div>' for value,label in [('5','kategorii źródeł'),('4559','dodatków: lemma ≥30'),('35/40','grup tylko z arch.'),('wysoka','pewność pomiarów')])+'</div>'
page += '<section class="tldr">'+''.join(blocks[:split])+'</section>'
page += '<nav class="toc">'+ ' · '.join(f'<a href="#{a}">{html.escape(t)}</a>' for a,t in toc[3:])+'</nav>'
page += '<main>'+''.join(blocks[split:])+'</main></body></html>'
source.with_suffix('.html').write_text(page+'\n')
state = json.loads((TASK/'orchestrator-state.yml').read_text())
summary = state['phase_summaries']['research_foundation']
data = {'generated':now, 'task':dict(state['task'], type='research', path=str(TASK), current_activity='Wyniki gotowe; rozmowa z właścicielem'),
        'characteristics':state['research_context'], 'phases':[
            dict(summary, id='research_foundation', name='Badanie i synteza', icon_hint='analysis', status='awaiting_approval'),
            {'id':'solution_generation','name':'Brainstorming','status':'skipped','skip_reason':'Tylko research — prośba użytkownika.'},
            {'id':'high_level_design','name':'Projekt','status':'skipped','skip_reason':'Tylko research — prośba użytkownika.'}],
        'verification':{'status':state['verification_context']['last_status'],'issues':state['verification_context']['issues_found'],
                        'fixes':[], 'reverify_count':0}}
(TASK/'dashboard-data.js').write_text('window.MAISTER_DATA = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n')
print(source.with_suffix('.html'))
