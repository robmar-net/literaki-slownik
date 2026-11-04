"""#16: przepięcie na nowy eksport SGJP i spójność pinu w konfiguracjach."""
import gzip
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rebase_sgjp_pin', ROOT / 'scripts/rebase_sgjp_pin.py')
rebase = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rebase)

HEADER = '#!DICT-ID test\n#<COPYRIGHT>\nx\n#</COPYRIGHT>\n'
ROWS = [f'f{i}\tl{i}\tsubst:sg:nom:m1\t\t' for i in range(6)]


def export(folder, name, rows):
    path = Path(folder) / name
    with gzip.open(path, 'wt', encoding='utf-8') as stream:
        stream.write(HEADER + ''.join(row + '\n' for row in rows))
    return path


class RebaseTests(unittest.TestCase):
    def test_one_inserted_block_shifts_only_later_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            old = export(folder, 'old.tab.gz', ROWS)
            new = export(folder, 'new.tab.gz', ROWS[:3] + ['m\tm\tsubst:sg:nom:f\t\t'] * 2 + ROWS[3:])
            self.assertEqual(rebase.insertion(old, new), (4, 2))
            self.assertEqual(rebase.fetch(new, {6})[6][0], 'f3')

    def test_changed_or_removed_row_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            old = export(folder, 'old.tab.gz', ROWS)
            for rows in (ROWS[:2] + ['x\tx\tsubst:sg:nom:f\t\t'] + ROWS[3:] + ['y\ty\tsubst:sg:nom:f\t\t'],
                         ROWS[:2] + ['x\tx\tsubst:sg:nom:f\t\t'] + ROWS[4:] + ['y\ty\tsubst:sg:nom:f\t\t'] * 2,
                         ROWS):
                new = export(folder, 'new.tab.gz', rows)
                with self.assertRaises(SystemExit) as raised:
                    rebase.insertion(old, new)
                self.assertEqual(raised.exception.code, 3)

    def test_every_config_cites_the_pinned_export(self):
        manifest = json.loads((ROOT / 'config/generator/sources.json').read_text(encoding='utf-8'))
        pinned, = [a for a in manifest['artifacts'] if a['kind'] == 'sgjp_tab']
        cited = set()
        for path in (ROOT / 'config/generator').glob('*.json'):
            text = path.read_text(encoding='utf-8')
            cited |= set(re.findall(r'"(sgjp-\d{8})"', text))
            if pinned['source_id'] in text:
                self.assertNotIn('3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810', text, path.name)
        self.assertEqual(cited, {pinned['source_id']})


if __name__ == '__main__':
    unittest.main()
