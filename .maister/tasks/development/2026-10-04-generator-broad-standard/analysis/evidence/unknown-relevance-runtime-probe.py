"""Dwa readonly raporty związku niewiadomych z wynikiem całego słowa."""
import argparse
import hashlib
from pathlib import Path
from literaki_slownik.canonical import sha256,dumps,write_json
from literaki_slownik.database import connect
from literaki_slownik.reports import unresolved_report


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',action='append',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();out=[]
    for run in args.run:
        path=Path(run)/'build.sqlite';before=sha256(path)
        with connect(path,readonly=True) as db:
            first=unresolved_report(db);second=unresolved_report(db)
            assert first==second and db.total_changes==0
        assert sha256(path)==before
        for rule in first['rules']:
            assert sum(rule['word_keys_by_membership'].values())==rule['word_keys']
        out.append({'run':run,'source_unchanged':True,'db_sha256':before,
            'repeat_equal':True,'report_sha256':hashlib.sha256(dumps(first).encode()).hexdigest(),'report':first})
    write_json(Path(args.output),{'schema_version':1,'scope':'rule_occurrence_by_word_result_not_counterfactual_causality','outputs':out})
    print([(r['run'],r['report']['variants']['standard']['word_membership']) for r in out])

if __name__=='__main__':main()
