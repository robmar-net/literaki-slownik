"""Explain zachowuje wpisy i niewiadome; odczyt nie zmienia przebiegu."""
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.helpers import fixture_manifest, rewrite
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, sha256, write_json
from literaki_slownik.database import connect
from literaki_slownik.explain import explain


class ExplainTests(unittest.TestCase):
    def test_persisted_expanded_assessments_are_reachable_readonly(self):
        from tests.test_build import BuildTests
        root=Path(self.temp.name)/'snapshots';root.mkdir()
        p=BuildTests().manifest(root,'#</COPYRIGHT>\nkot\tkot\tsubst:sg:nom.acc:m2\t\t\n')
        run=root/'run';build(p,run)
        before=sha256(run/'build.sqlite')
        value=explain(run,'kot')
        self.assertEqual({a['expanded_tag'] for a in value['persisted_analyses']},{'subst:sg:nom:m2','subst:sg:acc:m2'})
        self.assertEqual(len(value['persisted_analyses']),2)
        self.assertTrue(all(a['assessment']['membership']['status']=='unresolved' for a in value['persisted_analyses']))
        self.assertEqual(sha256(run/'build.sqlite'),before)

    def test_personal_construction_rejected_game_analysis_preserves_independent_homonym(self):
        from tests.test_build import BuildTests
        root=Path(self.temp.name)/'personal';root.mkdir()
        p=BuildTests().manifest(root,'#</COPYRIGHT>\nja\tja\tppron12:sg:nom:m1:pri\t\t\nm\tbyć:A\taglt:sg:pri:imperf:nwok\t\t\njam\tjama\tsubst:pl:gen:f\t\t\n')
        run=root/'run';build(p,run)
        value=explain(run,'jam');c,=value['derivations']
        self.assertIsNotNone(c['persisted_candidate_key'])
        self.assertEqual(c['assessment']['game']['status'],'reject')
        self.assertEqual(value['analyses'][0]['assessment']['game']['status'],'unresolved')
        self.assertEqual(value['source_presence'],'present')

    def test_source_kinds_visible_and_bound_homonym_does_not_remove_word(self):
        from tests.test_build import BuildTests
        root=Path(self.temp.name)/'source-kinds';root.mkdir()
        p=BuildTests().manifest(root,'#</COPYRIGHT>\nbiało\tbiały\tadja\t\t\nbiało\tbiało\tadv:pos\t\t\nnp\tnp\tbrev:npun\t\t\n')
        run=root/'run';build(p,run)
        analyses=explain(run,'biało')['analyses']
        statuses={a['raw_tag']:a['assessment']['game']['status'] for a in analyses}
        self.assertEqual(statuses,{'adja':'reject','adv:pos':'unresolved'})
        self.assertEqual(explain(run,'np')['analyses'][0]['assessment']['game']['status'],'reject')

    def test_unexplained_label_visible_without_automatic_language_acceptance(self):
        from tests.test_build import BuildTests
        from literaki_slownik.explain import format_explanation
        root=Path(self.temp.name)/'unexplained';root.mkdir()
        p=BuildTests().manifest(root,'#</COPYRIGHT>\nciemni\tciemnia\tsubst:sg:dat:f\tnazwa_pospolita\tfot.\n')
        run=root/'run';build(p,run)
        value=explain(run,'ciemni')
        a,=value['analyses']
        self.assertEqual(a['qualifiers'],'fot.')
        self.assertEqual(a['assessment']['language']['standard']['status'],'unresolved')
        self.assertIn('objaśnienie nieustalone',format_explanation(value))
        report=load_json(run/'reports/qualifier-conditions.json')
        self.assertEqual(report['unexplained_first_release_labels'],['fot.'])

    def test_historical_conditional_host_sequence_is_reachable_with_2026_assessment(self):
        from tests.test_build import BuildTests
        root=Path(self.temp.name)/'conditional';root.mkdir()
        p=BuildTests().manifest(root,'#</COPYRIGHT>\nchyba\tchyba:T\tpart\t\t\nby\tby:T\tpart\t\t\nm\tbyć:A\taglt:sg:pri:imperf:nwok\t\t\n')
        run=root/'run';build(p,run)
        for word in ('chybaby','chybabym'):
            c,=explain(run,word)['derivations']
            self.assertIsNotNone(c['persisted_candidate_key'])
            self.assertEqual(c['assessment']['language']['standard']['status'],'reject')
            self.assertEqual(c['assessment']['release_scope']['status'],'accept')
            check=next(x for x in c['assessment']['language']['broad']['checks'] if x['rule_id']=='orthography-2026-host-by-sequence-v1')
            self.assertEqual(check['status'],'accept')
            self.assertEqual(c['components'][0]['interpretation']['original'],'chyba')
        self.assertEqual(explain(run,'nibybym')['derivations'],[])

    def test_first_release_contraction_scope_preserves_candidates_and_direct_homonym(self):
        from tests.test_build import BuildTests
        root=Path(self.temp.name)/'scope';root.mkdir()
        p=BuildTests().manifest(root,'#</COPYRIGHT>\nkoło\tkoło:P\tprep:gen\t\t\ndo\tdo:P\tprep:gen\t\t\nń\ton:S\tppron3:sg:gen:m1:ter:nakc:praep\t\tpisane_łącznie_z_przyimkiem\nkołoń\twłasny-homonim\tsubst:sg:nom:m3\t\t\n')
        run=root/'run';build(p,run)
        value=explain(run,'kołoń');c,=value['derivations']
        self.assertIsNotNone(c['persisted_candidate_key'])
        self.assertEqual(c['linguistic_evidence']['status'],'unresolved')
        self.assertEqual(c['assessment']['release_scope']['status'],'reject')
        self.assertEqual(c['assessment']['language']['standard']['status'],'unresolved')
        self.assertEqual(c['assessment']['membership']['standard']['status'],'reject')
        self.assertEqual(value['analyses'][0]['assessment']['release_scope']['status'],'accept')
        self.assertEqual(explain(run,'doń')['derivations'][0]['assessment']['release_scope']['status'],'accept')
        report=load_json(run/'reports/construction-candidates.json')['release_scope']
        self.assertEqual(report['in_scope_candidate_analyses'],1)
        self.assertEqual(report['outside_scope_candidate_analyses'],1)
        self.assertEqual(report['outside_scope_forms'],[{'original':'kołoń','candidate_analyses':1}])

    def test_closed_mobile_source_host_is_reachable_and_persisted(self):
        from tests.test_build import BuildTests
        root = Path(self.temp.name) / 'mobile-source'
        root.mkdir()
        p = BuildTests().manifest(root,'#</COPYRIGHT>\nczyż\tczyż:T\tpart\t\t\neś\tbyć:A\taglt:sg:sec:imperf:wok\t\t\n')
        run = root / 'run'
        build(p,run)
        c, = explain(run,'czyżeś')['derivations']
        self.assertEqual(c['rule_id'],'mobile-source-host-aglt-v1')
        self.assertIsNotNone(c['persisted_candidate_key'])
        self.assertEqual([x['interpretation']['original'] for x in c['components']],['czyż','eś'])
        self.assertEqual(c['assessment']['membership']['standard']['status'],'reject')
        self.assertEqual(c['assessment']['game']['status'],'reject')
        self.assertEqual(explain(run,'czyżś')['derivations'],[])

    def test_orthography_2026_direct_and_inherited_without_removing_source(self):
        from tests.test_build import BuildTests
        root = Path(self.temp.name) / 'orthography'
        root.mkdir()
        p = BuildTests().manifest(root,'#</COPYRIGHT>\njeśliby\tjeśliby\tcomp\t\t\nm\tbyć:A\taglt:sg:pri:imperf:nwok\t\t\n')
        run = root / 'run'
        build(p,run)
        before = [sha256(run/f) for f in ('manifest.json','build.sqlite')]
        direct = explain(run,'jeśliby')['analyses'][0]
        derived, = explain(run,'jeślibym')['derivations']
        for analysis in (direct,derived):
            self.assertEqual(analysis['assessment']['language']['standard']['status'],'reject')
            checks = analysis['assessment']['language']['broad']['checks']
            rule = next(c for c in checks if c['rule_id']=='orthography-2026-conjunction-by-v1')
            self.assertEqual(rule['status'],'accept')
            self.assertEqual(rule['source_lemma_id'],'jeśliby')
        self.assertEqual(explain(run,'jeśliby')['source_presence'],'present')
        self.assertEqual(before,[sha256(run/f) for f in ('manifest.json','build.sqlite')])

    def test_mobile_by_host_trace_distinguishes_same_spelling_wrong_pos(self):
        from tests.test_build import BuildTests
        root = Path(self.temp.name) / 'mobile'
        root.mkdir()
        p = BuildTests().manifest(root,'#</COPYRIGHT>\naby\taby:M\tcomp\t\t\naby\taby:T\tpart\t\t\nśmy\tbyć:A\taglt:pl:pri:imperf:nwok\t\t\n')
        run = root / 'run'
        build(p,run)
        c, = explain(run,'abyśmy')['derivations']
        self.assertEqual(c['lemma_id'],'aby:M')
        self.assertEqual(c['rule_id'],'mobile-by-host-aglt-v1')
        self.assertIsNotNone(c['persisted_candidate_key'])
        self.assertEqual(explain(run,'nibyśmy')['derivations'],[])

    def test_derived_corpus_only_matches_whole_form_and_never_copies_root_frequency(self):
        root = Path(self.temp.name)
        p = root / 'sources.json'
        manifest = load_json(p)
        for sid, kind, filename, contents in [
            ('LEMMA','kwjp_lemma','root.csv.gz',',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nczytać,impt,99,1,1,0,0,1,99\n'),
            ('ORTH','kwjp_orth','whole.csv.gz',',freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nczytajże,5,1,1,0,0,1,5\n')]:
            corpus = root / filename
            with gzip.open(corpus,'wt',encoding='utf-8') as stream:
                stream.write(contents)
            artifact = dict(manifest['artifacts'][0])
            artifact.update(source_id=sid,kind=kind,role='corpus_evidence',path=filename,sha256=sha256(corpus),genre='all')
            manifest['artifacts'].append(artifact)
        rewrite(p,manifest)
        run = root / 'whole-form-corpus'
        build(p,run)
        value = explain(run,'czytajże')
        observations = value['corpus']['observations']
        self.assertEqual([o['source_id'] for o in observations],['ORTH'])
        self.assertEqual(observations[0]['typed_metrics']['freq'],5)
        self.assertEqual(observations[0]['candidates'][0]['candidate_key'],value['derivations'][0]['persisted_candidate_key'])
        self.assertFalse(observations[0]['sense_identity_confirmed'])
        self.assertEqual(explain(run,'czytaj')['corpus']['observations'][0]['typed_metrics']['freq'],99)

    def test_preposition_proof_separate_from_source_homonym_and_full_membership(self):
        from tests.test_build import BuildTests
        root = Path(self.temp.name) / 'contraction'
        root.mkdir()
        p = BuildTests().manifest(root, '#</COPYRIGHT>\ndo\tdo:P\tprep:gen\t\t\nkoło\tkoło:P\tprep:gen\t\t\nń\ton:S\tppron3:sg:gen:m1:ter:nakc:praep\t\tpisane_łącznie_z_przyimkiem\ndoń\tdonia\tsubst:pl:gen:f\t\t\n')
        run = root / 'run'
        build(p, run)
        before = [sha256(run / f) for f in ('manifest.json','build.sqlite')]
        value = explain(run, 'doń')
        self.assertEqual([a['lemma_id'] for a in value['analyses']], ['donia'])
        candidate, = value['derivations']
        self.assertEqual(candidate['lemma_id'], 'on:S')
        self.assertIsNotNone(candidate['persisted_candidate_key'])
        for variant in ('broad','standard'):
            checks = candidate['assessment']['language'][variant]['checks']
            self.assertTrue(any(c['rule_id']=='preposition-n-whole-form-proof-v1' and c['status']=='accept' for c in checks))
        self.assertEqual(value['list_membership']['status'], 'unresolved')
        unproved, = explain(run,'kołoń')['derivations']
        self.assertEqual(unproved['linguistic_evidence']['status'], 'unresolved')
        self.assertEqual(before, [sha256(run / f) for f in ('manifest.json','build.sqlite')])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        manifest_path, manifest = fixture_manifest(root)
        lines = ['PCV\tPCV\tsubst:sg:nom:m3\tnazwa_pospolita\t',
                 'DNA\tDNA\tsubst:sg:nom:n\tnazwa_pospolita\t',
                 'dna\tdno\tsubst:pl:nom.acc:n\t\t',
                 'dna\tdna\tsubst:sg:nom:f\t\t',
                 'żaba\tżaba\tsubst:sg:nom:f\t\t']
        lines.append('kakaa\tkakao\tsubst:sg:gen:n\t\tniezal.')
        lines.append('regionalna\tregionalny\tadj:sg:nom:f:pos\t\treg.,rzad.')
        lines.append('abolicjoniźmie\tabolicjonizm\tsubst:sg:loc:m3\tnazwa_pospolita\tniepopr.')
        lines.append('techniczne\ttechniczny\tadj:sg:nom:n:pos\t\ttechn.')
        lines.append('procenta\tprocent\tsubst:sg:gen:m3\tnazwa_pospolita\tpo_liczebniku')
        lines += ['czytaj\tczytać\timpt:sg:sec:imperf\t\trzad.',
                  'dajcie\tdać\timpt:pl:sec:perf\t\t',
                  'by\tby:T\tpart\t\t',
                  'm\tbyć\taglt:sg:pri:imperf:nwok\t\t',
                  'ś\tbyć\taglt:sg:sec:imperf:nwok\t\t',
                  'Zrób\tzrobić\timpt:sg:sec:perf\t\tniepopr.',
                  'zrób\tzrobić\timpt:sg:sec:perf\t\t']
        lines += ['masny\tmasny\tadj:sg:nom:m3:pos\t\tdaw._dziś_gwar.',
                  'masniejszy\tmasny\tadj:sg:nom:m3:com\t\tdaw.,daw._dziś_gwar.,rzad.']
        lines += [f'kot\tkot:S{i}\tsubst:sg:nom:m2\t\t' for i in range(150)]
        source = root / 'source.gz'
        with gzip.open(source, 'wt', encoding='utf-8') as stream:
            stream.write('#</COPYRIGHT>\n' + '\n'.join(lines) + '\n')
        manifest['artifacts'][0]['sha256'] = sha256(source)
        rewrite(manifest_path, manifest)
        self.run = root / 'run'
        build(manifest_path, self.run)

    def test_usage_condition_visible_with_full_membership_unresolved(self):
        value = explain(self.run, 'regionalna')
        for variant in ('broad', 'standard'):
            language = value['analyses'][0]['assessment']['language'][variant]
            self.assertEqual(language['status'], 'unresolved')
            self.assertTrue(any(c['rule_id'] == 'linguistic-informal-rare-non-excluding-v1'
                                and c['status'] == 'accept' for c in language['checks']))
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_descriptive_condition_visible_without_full_acceptance(self):
        value = explain(self.run, 'techniczne')
        for variant in ('broad','standard'):
            language = value['analyses'][0]['assessment']['language'][variant]
            self.assertEqual(language['status'], 'unresolved')
            self.assertTrue(any(c['rule_id'] == 'linguistic-descriptive-non-excluding-v1' for c in language['checks']))
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_required_context_visible_in_json_and_text_without_full_acceptance(self):
        from literaki_slownik.explain import format_explanation
        value = explain(self.run, 'procenta')
        for variant in ('broad','standard'):
            language = value['analyses'][0]['assessment']['language'][variant]
            check = next(c for c in language['checks'] if c['rule_id'] == 'linguistic-context-non-excluding-v1')
            self.assertEqual(check['required_context'], 'after_numeral')
            self.assertEqual(check['status'], 'accept')
            self.assertEqual(language['status'], 'unresolved')
        self.assertIn('Użycie po liczebniku.', format_explanation(value))
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_confirmed_derivations_have_all_source_components_and_stay_candidates(self):
        before = sha256(self.run / 'build.sqlite')
        for word, rule in [('czytajże','impt-single-particle-v1'),
                           ('dajcież','impt-single-particle-v1'), ('bym','by-aglt-nwok-v1')]:
            value = explain(self.run, word)
            self.assertEqual(value['source_presence'], 'absent')
            candidate, = value['derivations']
            self.assertEqual(candidate['original'], word)
            self.assertEqual(candidate['rule_id'], rule)
            self.assertEqual(candidate['status'], 'candidate_not_qualified')
            self.assertTrue(candidate['components'])
            self.assertEqual(value['list_membership']['status'], 'unresolved')
            self.assertEqual(candidate['assessment']['membership']['standard']['status'], 'unresolved')
        self.assertEqual(sha256(self.run / 'build.sqlite'), before)

    def test_no_derivation_from_guessed_host_or_double_particle(self):
        for word in ('nibym','czytajżeż','technicznem'):
            self.assertEqual(explain(self.run, word)['derivations'], [])

    def test_derivation_preserves_uppercase_and_incorrect_component_separately(self):
        candidates = explain(self.run, 'zróbże')['derivations']
        self.assertEqual({c['original'] for c in candidates}, {'Zróbże','zróbże'})
        bad = next(c for c in candidates if c['original'] == 'Zróbże')
        self.assertEqual(bad['qualifiers'], 'niepopr.')
        self.assertEqual(bad['components'][0]['interpretation']['original'], 'Zrób')
        self.assertEqual(bad['assessment']['language']['broad']['status'], 'reject')
        self.assertEqual(bad['assessment']['game']['status'], 'reject')
        good = next(c for c in candidates if c['original'] == 'zróbże')
        self.assertEqual(good['assessment']['membership']['broad']['status'], 'unresolved')

    def test_incorrect_source_analysis_preserved_and_rejected_both_variants(self):
        value = explain(self.run, 'abolicjoniźmie')
        self.assertEqual(value['source_presence'], 'present')
        self.assertEqual(value['analyses'][0]['qualifiers'], 'niepopr.')
        for variant in ('broad','standard'):
            language = value['analyses'][0]['assessment']['language'][variant]
            self.assertEqual(language['status'], 'reject')
            self.assertTrue(any(c['rule_id'] == 'linguistic-incorrect-form-v1' for c in language['checks']))
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_approved_disrecommended_condition_visible_without_full_acceptance(self):
        value = explain(self.run, 'kakaa')
        analysis = value['analyses'][0]
        self.assertEqual(analysis['qualifiers'], 'niezal.')
        for variant in ('broad', 'standard'):
            language = analysis['assessment']['language'][variant]
            self.assertEqual(language['status'], 'unresolved')
            confirmed = [c for c in language['checks'] if c['rule_id'] == 'linguistic-disrecommended-non-excluding-v1']
            self.assertEqual(len(confirmed), 1)
            self.assertEqual(confirmed[0]['status'], 'accept')
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_current_and_historical_forms_have_separate_age_checks(self):
        current = explain(self.run, 'masny')['analyses'][0]['assessment']
        old = explain(self.run, 'masniejszy')['analyses'][0]['assessment']
        self.assertEqual(current['language']['standard']['status'], 'unresolved')
        self.assertEqual(old['language']['standard']['status'], 'reject')
        self.assertEqual(old['language']['broad']['status'], 'unresolved')
        self.assertTrue(any(c['rule_id'] == 'linguistic-historical-form-v1'
                            for c in old['language']['standard']['checks']))
        self.assertEqual(explain(self.run, 'masniejszy')['list_membership']['status'], 'unresolved')

    def test_readonly_all_originals_homonyms_and_expanded_tags(self):
        before = [sha256(self.run / f) for f in ('manifest.json', 'build.sqlite')]
        value = explain(self.run, 'DNA')
        self.assertEqual(value['source_presence'], 'present')
        self.assertEqual(len(value['analyses']), 3)
        by_lemma = {a['lemma_id']: a for a in value['analyses']}
        self.assertEqual(by_lemma['DNA']['assessment']['game']['status'], 'reject')
        self.assertEqual(by_lemma['dno']['expanded_tags'], ['subst:pl:nom:n', 'subst:pl:acc:n'])
        self.assertEqual(value['list_membership']['status'], 'unresolved')
        self.assertEqual(len(explain(self.run, 'kot')['analyses']), 150)
        self.assertEqual(explain(self.run, 'z\u0307aba')['source_presence'], 'present')
        self.assertEqual(before, [sha256(self.run / f) for f in ('manifest.json', 'build.sqlite')])

    def test_uppercase_and_profile_both_visible_without_lexical_accept(self):
        value = explain(self.run, 'pcv')
        assessed = value['analyses'][0]['assessment']
        self.assertEqual(assessed['language']['standard']['status'], 'unresolved')
        self.assertEqual(assessed['game']['status'], 'reject')
        self.assertEqual(assessed['profile']['invalid_characters'], ['v'])
        self.assertEqual(assessed['membership']['standard']['status'], 'reject')

    def test_absence_in_partial_import_is_not_absence_in_source(self):
        self.assertEqual(explain(self.run, 'nieistniejące')['source_presence'], 'absent')
        path = self.run / 'manifest.json'
        manifest = load_json(path)
        manifest['stages']['import_sgjp']['status'] = 'failed'
        write_json(path, manifest)
        value = explain(self.run, 'nieistniejące')
        self.assertEqual(value['source_presence'], 'not_observed_in_incomplete_import')
        self.assertTrue(value['diagnostics'])
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_corpus_observation_once_with_all_candidates_and_no_sense_claim(self):
        # Rzeczywisty build importuje korpus i tworzy relacje; explain tylko odczytuje.
        root = Path(self.temp.name)
        manifest_path = root / 'sources.json'
        manifest = load_json(manifest_path)
        corpus = root / 'lemma.csv.gz'
        with gzip.open(corpus, 'wt', encoding='utf-8') as stream:
            stream.write(',,freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nkot,subst,7,1,1,0,0,1,7\n')
        artifact = dict(manifest['artifacts'][0])
        artifact.update(source_id='KWJP', kind='kwjp_lemma', role='corpus_evidence',
                        path=corpus.name, sha256=sha256(corpus), genre='all')
        manifest['artifacts'].append(artifact)
        rewrite(manifest_path, manifest)
        run = root / 'with-corpus'
        build(manifest_path, run)
        before = [sha256(run / f) for f in ('manifest.json', 'build.sqlite')]
        value = explain(run, 'kot')
        observations = value['corpus']['observations']
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]['typed_metrics']['freq'], 7)
        self.assertEqual(len(observations[0]['candidates']), 150)
        self.assertFalse(observations[0]['sense_identity_confirmed'])
        self.assertEqual(value['corpus']['unavailable'][0]['source_id'], 'NKJP')
        self.assertEqual(before, [sha256(run / f) for f in ('manifest.json', 'build.sqlite')])

    def test_cli_json_text_and_operational_error(self):
        cmd = [sys.executable, '-m', 'literaki_slownik', 'explain', '--run-dir', str(self.run), '--word', 'pcv']
        result = subprocess.run(cmd + ['--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['result']['source_presence'], 'present')
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PCV', result.stdout)
        self.assertIn('niewiadome', result.stdout)
        result = subprocess.run(cmd + ['--variant', 'other', '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        cmd[cmd.index(str(self.run))] = str(self.run / 'missing')
        result = subprocess.run(cmd + ['--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        self.assertNotIn('Traceback', result.stderr)

    def test_explain_connects_reconstructed_candidate_to_persisted_trace(self):
        from literaki_slownik.explain import format_explanation
        value = explain(self.run, 'czytajże')
        candidate, = value['derivations']
        self.assertEqual(len(candidate['persisted_candidate_key']), 64)
        with connect(self.run / 'build.sqlite', readonly=True) as db:
            row = db.execute('select payload from derivation_candidate where candidate_key=?',
                             (candidate['persisted_candidate_key'],)).fetchone()
            self.assertEqual(json.loads(row[0])['components'], candidate['components'])
        self.assertIn(candidate['persisted_candidate_key'], format_explanation(value))
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_legacy_database_without_candidate_tables_still_explains_on_demand(self):
        with connect(self.run / 'build.sqlite') as db:
            db.execute('drop table variant_decision')
            db.execute('drop table decision_payload')
            db.execute('drop table analysis')
            db.execute('drop table derivation_component')
            db.execute('drop table derivation_candidate')
        value = explain(self.run, 'czytajże')
        candidate, = value['derivations']
        self.assertIsNone(candidate['persisted_candidate_key'])
        self.assertEqual(candidate['original'], 'czytajże')
