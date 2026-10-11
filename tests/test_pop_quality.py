"""Próbki POP używają drugiej zamkniętej konfiguracji pop-quality-v1 (A7, C17)."""
import unittest

from literaki_slownik.inputs import GeneratorError
from literaki_slownik.quality import ENCODING, sample_strata

POP = {'version': 'pop-quality-v1', 'seed': 'literaki-slownik-pop-v1',
       'size_per_stratum': 30, 'encoding': ENCODING}


class PopQualityConfigTests(unittest.TestCase):
    def refused(self, config):
        with self.assertRaises(GeneratorError) as caught:
            sample_strata({'x': ['a']}, config)
        self.assertEqual(caught.exception.code, 2)

    def test_pop_config_accepted_and_reproducible(self):
        keys = [f'unit:{n:04}' for n in range(200)]
        first = sample_strata({'pop_in': iter(keys)}, dict(POP))
        second = sample_strata({'pop_in': iter(keys)}, dict(POP))
        self.assertEqual(first, second)
        self.assertEqual(first['version'], 'pop-quality-v1')
        self.assertEqual(first['seed'], 'literaki-slownik-pop-v1')
        self.assertEqual(first['strata']['pop_in']['sample_size'], 30)

    def test_other_values_refused(self):
        for field, value in [('version', 'pop-quality-v2'), ('seed', 'literaki-slownik-pop-v2'),
                             ('size_per_stratum', 31), ('size_per_stratum', True),
                             ('encoding', 'concatenation'), ('extra', 1)]:
            with self.subTest(field=field, value=value):
                self.refused({**POP, field: value})

    def test_mixed_version_and_seed_refused(self):
        self.refused({**POP, 'version': 'quality-v1'})
        self.refused({**POP, 'seed': 'literaki-slownik-g1-v1'})


if __name__ == '__main__':
    unittest.main()
