from decimal import Decimal
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.pop00 import classify_analysis, select_forms, load_config, read_orth, check_inputs, read_analyses
from tests.pop00_helpers import fixture, ROOT


class Pop00RulesTests(unittest.TestCase):
    def test_protected_segmented_and_rare_inflections(self):
        for tag in ('praet:sg:f:pri:perf','cond:sg:m1:pri:perf','subst:pl:loc:m1',
                    'impt:pl:sec:imperf','pcon:imperf','ger:sg:nom:n:imperf:aff'):
            self.assertEqual(classify_analysis(tag),('ordinary',))
        self.assertEqual(classify_analysis('praet:sg:n:sec:imperf'),('neuter-person-1-2',))
        self.assertEqual(classify_analysis('ppron12:pl:nom:m1.f.n:pri'),('neuter-person-1-2','ordinary'))

    def test_constructions_follow_their_own_rules(self):
        self.assertEqual(classify_analysis('aglt:sg:pri:imperf:nwok','by-aglt-nwok-v1'),('ordinary',))
        self.assertEqual(classify_analysis('adj:sg:nom:m1:sup','nie-prefix-degree-v2'),('degree-com-sup',))
        self.assertEqual(classify_analysis('impt:sg:sec:imperf','impt-single-particle-v1'),('construction',))
        for tag,rule in [('impt:sg:sec:imperf','unknown'),('inf:new',None),('new',None),
                         ('subst:sg:nom:m1','by-aglt-nwok-v1')]:
            with self.assertRaises(GeneratorError):
                classify_analysis(tag,rule)

    def test_threshold_and_alternative_analysis(self):
        config=load_config(ROOT/'config/generator/pop00.json')
        def source(word,tag,ident):
            return word,{'id':ident,'member':'x@own','tag':tag,'rule':None}
        words={'kot','milszy','milszemu','nijako'}
        records=[source('kot','subst:sg:nom:m1','1'),source('milszy','adj:sg:nom:m1:com','2'),
                 source('milszemu','adj:sg:dat:m1:com','3'),source('nijako','praet:sg:n:pri:imperf','4')]
        for value,expected in [('0.09',False),('0.1',True),('0.11',True),('0',False)]:
            selected,_=select_forms(words,{'x@own'},records,{'milszy':{'ipm':value}},config)
            self.assertEqual('milszy' in selected,expected)
            self.assertNotIn('nijako',selected)
        records.append(source('milszemu','subst:sg:dat:m1','5'))
        selected,_=select_forms(words,{'x@own'},records,{},config)
        self.assertIn('milszemu',selected)
        with self.assertRaises(GeneratorError):
            select_forms(words,{'x@own','missing@own'},records,{},config)
        with self.assertRaises(GeneratorError):
            select_forms(words|{'uncovered'},{'x@own'},records,{},config)

    def test_fixture_reconstructs_base_and_keeps_every_lexeme(self):
        with tempfile.TemporaryDirectory() as t:
            f=fixture(t);data=check_inputs(f['manifest']);config=load_config(f['config'])
            selected,rows=select_forms(data['pop0'],data['members'],read_analyses(data['paths']['database'],
                data['pop0'],data['members']),data['orth'],config)
            self.assertEqual(selected,{'kot','kotach','zrobiłem','miły','najmilszy','nieczytanie','by','my','bym'})
            self.assertEqual(rows['zrobiłem']['evidence']['status'],'NO_PUBLISHED_EVIDENCE')
            self.assertFalse(rows['czytanymi']['kept'])
