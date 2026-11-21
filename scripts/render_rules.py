#!/usr/bin/env python3
"""Strona „Reguły” (#21) z config/generator/rule-docs.json.

Użycie:
  python3 scripts/render_rules.py            # zapisuje docs/generator/reguly.md
  python3 scripts/render_rules.py --check    # 1, gdy katalog niezgodny z kodem albo strona nieaktualna
  python3 scripts/render_rules.py --wiki PLIK  # strona wiki (linki bezwzględne)
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik import rule_docs  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--wiki')
    args = parser.parse_args(argv)
    docs = rule_docs.load()
    errors = rule_docs.problems(docs, rule_docs.code_rule_ids())
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    page = rule_docs.render(docs, base='../../')
    if args.check:
        if rule_docs.PAGE.read_text(encoding='utf-8') != page:
            print('docs/generator/reguly.md nieaktualne: uruchom scripts/render_rules.py', file=sys.stderr)
            return 1
        return 0
    rule_docs.PAGE.write_text(page, encoding='utf-8')
    if args.wiki:
        Path(args.wiki).write_text(rule_docs.render(docs), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
