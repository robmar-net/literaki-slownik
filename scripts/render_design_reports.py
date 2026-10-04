#!/usr/bin/env python3
"""Tworzy widoki HTML porównania i projektu; Markdown pozostaje źródłem."""
import html
import re
from pathlib import Path

from render_report import CSS, inline

TASK = Path(__file__).resolve().parents[1] / '.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow'
REPORTS = {
    'research-handoff': ('Przekazanie', 'Research zakończony', [('2', 'kandydaci w projekcie'), ('3', 'wybory zakresu'), ('0', 'wdrożonych generatorów')]),
    'solution-exploration': ('Porównanie', 'Wybory zakresu zatwierdzone', [('3', 'warianty wyniku'), ('G1', 'wybrany zakres'), ('N1', 'NKJP później'), ('C1', 'konstrukcje w bazie')]),
    'high-level-design': ('Projekt', 'Projekt zatwierdzony', [('6', 'modułów'), ('2', 'kandydatów'), ('10', 'kryteriów odbioru')]),
    'decision-log': ('Decyzje', 'Statusy według rejestru', [('5', 'ADR'), ('5', 'ADR zaakceptowane'), ('3', 'decyzje zakresu')]),
}


def blocks(text):
    lines = text.splitlines()
    result, sections = [], []
    i = 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith('```'):
            content = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                content.append(lines[i])
                i += 1
            result.append('<pre><code>' + html.escape('\n'.join(content)) + '</code></pre>')
            i += 1
        elif line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            title = line[level:].strip()
            anchor = 'section-' + str(len(sections))
            sections.append((anchor, title, level))
            result.append(f'<h{level} id="{anchor}">{inline(title)}</h{level}>')
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            result.append('<div class="table-scroll"><table>' + ''.join(
                '<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in row) + '</tr>'
                for index, row in enumerate(rows) for tag in ['th' if index == 0 else 'td']
            ) + '</table></div>')
        elif re.match(r'^(- |\d+\. )', line):
            tag = 'ul' if line.startswith('- ') else 'ol'
            items = []
            while i < len(lines) and re.match(r'^(- |\d+\. )', lines[i]):
                items.append('<li>' + inline(re.sub(r'^(- |\d+\. )', '', lines[i])) + '</li>')
                i += 1
            result.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
        else:
            paragraph = []
            while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\||```|- |\d+\. )', lines[i]):
                paragraph.append(lines[i].removeprefix('> '))
                i += 1
            result.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return result, sections


def render(slug, label, status, tiles):
    source = TASK / 'outputs' / (slug + '.md')
    text = source.read_text()
    title = text.splitlines()[0].lstrip('# ')
    content, sections = blocks(text)
    boundary = next(i for i, block in enumerate(content) if 'id="section-3"' in block)
    nav = ['<a href="../dashboard.html">← Dashboard</a>', '<a href="research-report.html">Raport</a>']
    for name, (name_label, _, _) in REPORTS.items():
        nav.append(f'<span class="here">{name_label}</span>' if name == slug else f'<a href="{name}.html">{name_label}</a>')
    nav.append(f'<a class="md" href="{slug}.md" target="_blank" rel="noopener">Markdown ↗</a>')
    css = CSS + '.crumbs{font-size:13px;margin-bottom:18px}.here{font-weight:650}.crumbs .md{margin-left:auto}.choices{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}.choices .card{margin:0}.selected{border:2px solid var(--accent)}details{margin:12px 0}.toc{margin:18px 0}.tile span{font-size:11px}'
    page = '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) + '</title><style>' + css + '</style></head><body>'
    page += '<nav class="crumbs">' + ' '.join(nav) + '</nav><header><span class="badge">' + status + '</span><h1>' + html.escape(title) + '</h1></header>'
    page += '<div class="tiles">' + ''.join('<div class="tile"><b>' + value + '</b><span>' + caption + '</span></div>' for value, caption in tiles) + '</div>'
    page += '<section class="tldr">' + ''.join(content[:boundary]) + '</section>'
    if slug == 'solution-exploration':
        page += '<div class="choices"><div class="card selected"><b>G1 · wybrany</b><p>BROAD i STANDARD, pełna dopuszczalna fleksja, wyjaśnienia i KWJP.</p></div><div class="card"><b>G2 · niewybrany</b><p>Niepełny pilot może być etapem prac, ale nie wynikiem końcowym.</p></div><div class="card"><b>G3 · odroczony</b><p>Dodatkowe warianty ATTESTED w późniejszym etapie.</p></div></div>'
    page += '<nav class="toc">' + ' · '.join(f'<a href="#{anchor}">{html.escape(heading)}</a>' for anchor, heading, level in sections[3:] if level == 2) + '</nav><main>'
    # Sekcje szczegółowe są rozwijane; pełna treść pozostaje dostępna.
    groups = []
    for block in content[boundary:]:
        if block.startswith('<h2 '):
            groups.append([block])
        elif groups:
            groups[-1].append(block)
    for group in groups:
        heading = re.sub(r'</?h2[^>]*>', '', group[0])
        anchor = re.search(r'id="([^"]+)"', group[0]).group(1)
        page += f'<details class="card" open id="{anchor}"><summary>{heading}</summary>' + ''.join(group[1:]) + '</details>'
    page += '</main></body></html>\n'
    source.with_suffix('.html').write_text(page)


if __name__ == '__main__':
    for slug, values in REPORTS.items():
        render(slug, *values)
