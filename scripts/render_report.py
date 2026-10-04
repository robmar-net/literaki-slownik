#!/usr/bin/env python3
"""Renderuje prosty raport Markdown do samodzielnego HTML bez zależności."""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / '.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow'
SOURCE = TASK / 'outputs/research-report.md'
CSS = ''':root {
  --bg:#f6f7f9; --surface:#fff; --border:#e2e5ea; --text:#1a1d23; --dim:#6b7280;
  --accent:#4f46e5; --accent-soft:#eef2ff; --ok:#16a34a; --ok-soft:#ecfdf3;
  --warn:#d97706; --warn-soft:#fffbeb; --crit:#dc2626; --crit-soft:#fef2f2;
  --info:#2563eb; --info-soft:#eff6ff; --radius:10px;
}
@media (prefers-color-scheme: dark) {
  :root { --bg:#111418; --surface:#1a1f26; --border:#2e3640; --text:#e6e9ee; --dim:#9aa4b2;
    --accent:#818cf8; --accent-soft:#26294a; --ok:#4ade80; --ok-soft:#11291a;
    --warn:#fbbf24; --warn-soft:#2e2410; --crit:#f87171; --crit-soft:#321616;
    --info:#60a5fa; --info-soft:#15233a; }
}
* { box-sizing:border-box; }
body { margin:0 auto; max-width:1100px; padding:24px 20px 64px; background:var(--bg);
  color:var(--text); font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
a { color:var(--accent); text-decoration:none; } a:hover { text-decoration:underline; }
h1 { font-size:22px; letter-spacing:-.01em; } h2 { font-size:16px; margin-top:28px; }
.card { background:var(--surface); border:1px solid var(--border); border-radius:var(--radius);
  padding:16px 18px; margin:14px 0; }
.badge { display:inline-block; font-size:11px; font-weight:600; text-transform:uppercase;
  letter-spacing:.04em; padding:2px 8px; border-radius:99px; background:var(--accent-soft); color:var(--accent); }
.sev { display:inline-block; font-size:10.5px; font-weight:700; text-transform:uppercase;
  padding:1.5px 7px; border-radius:99px; margin-right:6px; }
.sev.critical { background:var(--crit-soft); color:var(--crit); }
.sev.warning  { background:var(--warn-soft); color:var(--warn); }
.sev.info     { background:var(--info-soft); color:var(--info); }
.pass { color:var(--ok); font-weight:600; } .fail { color:var(--crit); font-weight:600; }
table { width:100%; border-collapse:collapse; }
th, td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--border); vertical-align:top; }
th { font-size:11.5px; text-transform:uppercase; letter-spacing:.04em; color:var(--dim); }
code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12.5px;
  background:var(--accent-soft); padding:1px 5px; border-radius:4px; }
img.shot { max-width:100%; border:1px solid var(--border); border-radius:var(--radius); }
details > summary { cursor:pointer; font-weight:600; }
.crumbs{display:flex;gap:14px;flex-wrap:wrap}.tiles{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}.tile{padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:10px;flex:1;min-width:120px}.tile b{display:block;font-size:24px}.tile span{color:var(--dim)}.table-scroll{overflow-x:auto;margin:18px 0}pre{overflow-x:auto;padding:14px;background:var(--surface)}p,li,td{overflow-wrap:anywhere}.source-url{font-size:12px;color:var(--dim)}.toc{padding:14px;background:var(--surface)}.tldr{border-left:4px solid var(--accent);padding-left:18px}'''


def inline(text):
    slots = []
    def keep(value):
        slots.append(value)
        return f'@@SLOT{len(slots)-1}@@'
    text = re.sub(r'`([^`]+)`', lambda m: keep('<code>'+html.escape(m[1])+'</code>'), text)
    def link(match):
        label, target = match.groups()
        if target.startswith(('https://', 'http://')):
            return keep(html.escape(label)+' <span class="source-url">('+html.escape(target)+')</span>')
        attr = ' target="_blank" rel="noopener"' if '.md' in target else ''
        return keep('<a href="'+html.escape(target,quote=True)+'"'+attr+'>'+html.escape(label)+'</a>')
    text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', link, text)
    text = html.escape(text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    for i, value in enumerate(slots):
        text = text.replace(f'@@SLOT{i}@@', value)
    return text


def render():
    lines = SOURCE.read_text().splitlines()
    blocks, toc = [], []
    i = 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('```'):
            chunk=[]; i+=1
            while i<len(lines) and not lines[i].startswith('```'):
                chunk.append(lines[i]);i+=1
            blocks.append('<pre><code>'+html.escape('\n'.join(chunk))+'</code></pre>');i+=1
        elif line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));title=line[level:].strip();anchor='section-'+str(len(toc))
            toc.append((anchor,title));blocks.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>');i+=1
        elif line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c) for c in cells):rows.append(cells)
                i+=1
            table='<div class="table-scroll"><table>'
            for j,cells in enumerate(rows):
                tag='th' if j==0 else 'td';table+='<tr>'+''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells)+'</tr>'
            blocks.append(table+'</table></div>')
        elif re.match(r'^(- |\d+\. )',line):
            ordered=not line.startswith('- ');tag='ol' if ordered else 'ul';items=[]
            while i<len(lines) and re.match(r'^(- |\d+\. )',lines[i]):
                items.append('<li>'+inline(re.sub(r'^(- |\d+\. )','',lines[i]))+'</li>');i+=1
            blocks.append('<'+tag+'>'+''.join(items)+'</'+tag+'>')
        else:
            parts=[]
            while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','- ')):
                parts.append(lines[i]);i+=1
            blocks.append('<p>'+inline(' '.join(parts))+'</p>')
    title=lines[0].lstrip('# ')
    # Pierwsze trzy sekcje: podsumowanie, decyzje i ryzyka.
    split=next(index for index,b in enumerate(blocks) if 'id="section-3"' in b)
    contents=' · '.join(f'<a href="#{a}">{html.escape(n)}</a>' for a,n in toc[3:])
    page='<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style></head><body>'
    page+='<nav class="crumbs"><a href="../dashboard.html">← Dashboard</a><a href="../analysis/findings/model-procesu.md" target="_blank" rel="noopener">Model procesu</a><a href="research-report.md" target="_blank" rel="noopener">Raport Markdown</a></nav><header><span class="badge">Audyt · do przeglądu</span><h1>'+html.escape(title)+'</h1></header>'
    page+='<div class="tiles"><div class="tile"><b>7 458 520</b><span>rekordów SGJP</span></div><div class="tile"><b>13</b><span>list KWJP</span></div><div class="tile"><b>10</b><span>punktów audytu</span></div><div class="tile"><b>1</b><span>rodzina źródeł z blokadą warunków</span></div></div>'
    page+='<section class="tldr">'+''.join(blocks[:split])+'</section><nav class="toc">'+contents+'</nav><main>'+''.join(blocks[split:])+'</main></body></html>'
    SOURCE.with_suffix('.html').write_text(page+'\n')


if __name__ == '__main__':
    render()
