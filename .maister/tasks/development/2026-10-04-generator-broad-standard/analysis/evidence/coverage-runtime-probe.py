"""Powtarzalny raport pokrycia istniejących baz; wyłącznie readonly."""
import argparse
import json
from pathlib import Path
from literaki_slownik.canonical import sha256,write_json,dumps
from literaki_slownik.database import connect
from literaki_slownik.reports import coverage_report
import hashlib


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',action='append',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();results=[]
    for name in args.run:
        path=Path(name)/'build.sqlite';before=sha256(path)
        with connect(path,readonly=True) as db:
            first=coverage_report(db);second=coverage_report(db)
            assert first==second
            assert db.total_changes==0
        assert before==sha256(path)
        results.append({'run':name,'db_sha256':before,'source_unchanged':True,
            'repeated_equal':True,'report_sha256':hashlib.sha256(dumps(first).encode()).hexdigest(),
            'coverage':first})
    write_json(Path(args.output),{'schema_version':1,'scope':'readonly_diagnostic_not_release',
                                'outputs':results})
    print(json.dumps([{'run':r['run'],'compact':r['coverage']['source_compact_interpretations'],
        'classes':len(r['coverage']['source_classes']),
        'source_coverage':r['coverage']['source_assessment_coverage']} for r in results]))

if __name__=='__main__':main()
