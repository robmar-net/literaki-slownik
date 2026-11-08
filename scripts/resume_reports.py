#!/usr/bin/env python3
"""Dokończenie etapu `reports` przerwanego przebiegu build (#16).

Użycie:
  python3 scripts/resume_reports.py --manifest config/generator/sources.json --run-dir data/work/<przebieg>

Działa tylko wtedy, gdy etapy do `links` mają status complete, a `reports` running albo failed,
i gdy kod generatora oraz manifest wejść są te same co przy build. Powtarza kod etapu `reports`
z `build.py` na istniejącej bazie. Czasy wcześniejszych etapów zginęły z procesem, więc
`performance.json` ma tylko czasy raportów i pole `resumed`. Kody: 0 gotowe, 2 przebieg
nie nadaje się do wznowienia.
"""
import argparse
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from literaki_slownik.canonical import load_json, write_json  # noqa: E402
from literaki_slownik.database import connect  # noqa: E402
from literaki_slownik.inputs import checked_file, inspect_sources  # noqa: E402
from literaki_slownik.reports import (canonical_index, coverage_report, logical_content_report,  # noqa: E402
                                      persisted_filter_impact, unresolved_report)
from literaki_slownik.run import STAGES, code_identity, set_stage  # noqa: E402

DONE = ('preflight', 'import_sgjp', 'import_kwjp', 'constructions', 'decisions', 'links')


def fail(message):
    print(json.dumps({'error': message}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(2)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--run-dir', required=True)
    args = parser.parse_args(argv)
    run = Path(args.run_dir)
    manifest = load_json(run / 'manifest.json')
    stages = manifest['stages']
    if any(stages.get(name, {}).get('status') != 'complete' for name in DONE):
        fail('etapy do links nie są ukończone')
    if stages.get('reports', {}).get('status') not in {'running', 'failed'}:
        fail('etap reports nie czeka na wznowienie')
    if manifest['code']['tree_sha256'] != code_identity()['tree_sha256'] or code_identity()['git_dirty']:
        fail('kod generatora różni się od kodu build')
    inputs = inspect_sources(args.manifest)
    if inputs['manifest_sha256'] != manifest['inputs']['manifest_sha256']:
        fail('manifest wejść różni się od manifestu build')
    base = Path(args.manifest).resolve().parent
    performance = {'resumed': {'stage': 'reports', 'earlier_stage_seconds': 'niedostępne'}}
    stage = 'reports'
    set_stage(run, stage, 'running')
    with connect(run / 'build.sqlite') as db:
        start = time.monotonic()
        unresolved = unresolved_report(db)
        write_json(run / 'reports/unresolved.json', unresolved)
        performance['diagnostic_unresolved'] = {'seconds': time.monotonic() - start}
        start = time.monotonic()
        write_json(run / 'reports/filter-impact.json', persisted_filter_impact(db, unresolved))
        performance['diagnostic_filter_impact'] = {'seconds': time.monotonic() - start}
        quality_reference = inputs['manifest']['configurations'].get('quality')
        if quality_reference:
            from literaki_slownik.quality import sample_persisted_analyses, sample_corpus_links
            start = time.monotonic()
            config = load_json(checked_file(base, quality_reference))
            write_json(run / 'reports/quality-analyses.json', sample_persisted_analyses(db, config, unresolved))
            performance['diagnostic_quality_analyses'] = {'seconds': time.monotonic() - start}
            start = time.monotonic()
            write_json(run / 'reports/quality-links.json', sample_corpus_links(db, config))
            performance['diagnostic_quality_links'] = {'seconds': time.monotonic() - start}
            words_reference = inputs['manifest']['configurations'].get('quality-words')
            if words_reference:
                from literaki_slownik.quality import sample_word_analyses
                definitions = load_json(checked_file(base, words_reference))
                start = time.monotonic()
                write_json(run / 'reports/quality-words.json',
                           sample_word_analyses(db, config, definitions, unresolved))
                performance['diagnostic_quality_words'] = {'seconds': time.monotonic() - start}
        start = time.monotonic()
        write_json(run / 'reports/logical-content.json', logical_content_report(db))
        performance['diagnostic_logical_content'] = {'seconds': time.monotonic() - start}
        start = time.monotonic()
        coverage = coverage_report(db, unresolved)
        write_json(run / 'reports/coverage.json', coverage)
        performance['diagnostic_coverage'] = {'seconds': time.monotonic() - start}
        set_stage(run, stage, 'complete' if coverage['status'] == 'COMPLETE' else 'pending')
        if inspect_sources(args.manifest)['manifest_sha256'] != inputs['manifest_sha256']:
            fail('manifest zmienił się w trakcie wznowienia')
    performance['peak_rss'] = {'value': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               'unit': 'bytes on macOS, KiB on Linux'}
    performance['database_bytes'] = (run / 'build.sqlite').stat().st_size
    write_json(run / 'reports/performance.json', performance)
    write_json(run / 'reports/canonical-index.json', canonical_index(run))
    stages = load_json(run / 'manifest.json')['stages']
    print(json.dumps({'run_dir': str(run.resolve()),
                      'completed': [n for n in STAGES if stages[n]['status'] == 'complete'],
                      'pending': [n for n in STAGES if stages[n]['status'] == 'pending']}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
