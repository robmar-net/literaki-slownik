"""Runda 3 (2026-10-08, decyzje agenta z upoważnienia właściciela): macierz klas i aktywacja."""
import unittest
from literaki_slownik.canonical import load_json
from literaki_slownik.decisions import assess_diagnostic, assessment
from literaki_slownik.policy import CLASS_MATRIX, approved_qualifier_checks, source_game_checks

# 34 klasy obserwowane w przypiętym SGJP sgjp-20260823 (pełny import, 2026-10-08).
OBSERVED = ('adj adja adjc adjp adv aglt bedzie brev comp cond conj depr fin frag ger imps impt inf interj num '
            'numcomp pact pacta pant part pcon ppas ppron12 ppron3 praet pred prep subst winien').split()


def source(tag, original='kot', qualifiers=''):
    return {'original': original, 'lemma_id': original, 'raw_tag': tag, 'names': '', 'qualifiers': qualifiers,
            'source_id': 'x', 'first_source_row': 1}


class AgentDecisionsRound3Tests(unittest.TestCase):
    def test_matrix_covers_exactly_observed_classes(self):
        # Runda 4: klasa siebie pochodzi z uzupełnienia eksportu (sgjp-supplement.tab).
        self.assertEqual(sorted(CLASS_MATRIX), sorted(OBSERVED + ['siebie']))
        self.assertEqual(set(CLASS_MATRIX.values()), {'word', 'bound', 'abbreviation'})

    def test_matrix_behavior_matches_game_checks(self):
        for cls, behavior in CLASS_MATRIX.items():
            status = assessment(source_game_checks(source(cls)))['status']
            self.assertEqual(status, 'accept' if behavior == 'word' else 'reject', cls)

    def test_plain_word_accepted_with_explicit_activation_rules(self):
        a = assess_diagnostic('kot', '', source_analyses=[source('subst:sg:nom:m2')])
        for variant in ('broad', 'standard'):
            self.assertEqual(a['membership'][variant]['status'], 'accept')
            self.assertIn('linguistic-policy-active-v1', [c['rule_id'] for c in a['language'][variant]['checks']])
        self.assertIn('game-documented-conditions-v1', [c['rule_id'] for c in a['game']['checks']])
        self.assertFalse(any(c['status'] == 'unresolved' for v in ('broad', 'standard')
                             for c in a['membership'][v]['checks']))

    def test_construction_fulfilled_requirement_is_not_unknown(self):
        # Build v24: 57 analiz przyimek+ń zostało unresolved przez odziedziczoną etykietę składnika.
        from literaki_slownik.constructions import preposition_n_candidates
        prep = dict(source('prep:gen', 'do'), lemma_id='do:P')
        pronoun = dict(source('ppron3:sg:gen:m1.m2.m3:ter:nakc:praep', 'ń', 'pisane_łącznie_z_przyimkiem'),
                       lemma_id='on:S')
        candidates = preposition_n_candidates(prep, pronoun)
        self.assertEqual(len(candidates), 3)
        for c in candidates:
            components = [i['interpretation'] for i in c['components']]
            a = assess_diagnostic(c['original'], c['qualifiers'], [c['linguistic_evidence']], components, c)
            for variant in ('broad', 'standard'):
                checks = a['language'][variant]['checks']
                self.assertNotIn('linguistic-unknown-qualifier-v1', [x['rule_id'] for x in checks])
                self.assertIn('linguistic-fulfilled-component-requirement-v1', [x['rule_id'] for x in checks])
                self.assertEqual(a['membership'][variant]['status'], 'accept', c['expanded_tag'])
        # Samodzielne ń: etykieta nadal bez warunku, a gra odrzuca segment.
        alone = assess_diagnostic('ń', 'pisane_łącznie_z_przyimkiem', source_analyses=[pronoun])
        self.assertEqual(alone['membership']['broad']['status'], 'reject')
        self.assertIn('linguistic-unknown-qualifier-v1', [x['rule_id'] for x in alone['language']['broad']['checks']])

    def test_unknown_qualifier_label_stays_unresolved(self):
        checks = approved_qualifier_checks('archit.,hist.|nowa_etykieta', 'broad')
        unknown = [c for c in checks if c['rule_id'] == 'linguistic-unknown-qualifier-v1']
        self.assertEqual([c['unknown_labels'] for c in unknown], [['nowa_etykieta']])
        self.assertEqual(assessment(checks)['status'], 'unresolved')
        a = assess_diagnostic('kot', 'nowa_etykieta', source_analyses=[source('subst:sg:nom:m2', qualifiers='nowa_etykieta')])
        self.assertEqual(a['membership']['broad']['status'], 'unresolved')
        self.assertEqual(approved_qualifier_checks('', 'broad'), [])

    def test_class_outside_matrix_blocks_coverage(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from literaki_slownik.build import build
        from literaki_slownik.database import connect
        from literaki_slownik.reports import coverage_report
        from tests.release_helpers import fixture_inputs
        with tempfile.TemporaryDirectory() as directory:
            inputs, run = Path(directory) / 'in', Path(directory) / 'run'
            inputs.mkdir()
            build(fixture_inputs(inputs), run)
            with connect(run / 'build.sqlite', readonly=True) as db:
                self.assertEqual(coverage_report(db)['status'], 'COMPLETE')
                narrowed = {k: v for k, v in CLASS_MATRIX.items() if k != 'subst'}
                with patch('literaki_slownik.policy.CLASS_MATRIX', narrowed):
                    report = coverage_report(db)
        self.assertEqual(report['source_classes']['subst']['semantic_qualification'], 'UNKNOWN_CLASS')
        self.assertFalse(report['source_semantic_population_complete'])
        self.assertEqual(report['status'], 'INCOMPLETE')

    def test_coverage_config_closes_both_matrix_pendings(self):
        coverage = load_json('config/generator/coverage.json')
        self.assertEqual(coverage['pending'], [])
        for key in ('class_matrix_34_classes_agent_decided', 'game_conditions_from_published_rules_agent_decided',
                    'closed_first_release_constructor_set_agent_decided'):
            self.assertIn(key, coverage['confirmed'])


if __name__ == '__main__':
    unittest.main()
