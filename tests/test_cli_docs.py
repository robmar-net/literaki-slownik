"""Dokumentacja #22: cli.md opisuje nowe skrypty, flagi i kody; ADR-014..021 są w repo."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'docs' / 'generator' / 'cli.md'
SCRIPTS = ('init_work_volume.py', 'measure_fullfsync.py', 'build_supervised.py', 'promote_run.py',
           'clean_work.py', 'resume_reports.py')
NAMES = SCRIPTS + ('build_pair.sh', 'LITERAKI_WORK_ROOT', '--resume', '--work-root', 'resumed_from',
                   'build_history', 'promotion.json', 'logs/<nazwa>.lock')
CODES = ('0', '2', '3', '4', '5', '75', '76', '77', '78', '130')
UUID = re.compile(r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}')
HOME = re.compile(r'/Users/|/home/|~/')


def section(text, heading):
    start = text.index(heading)
    end = text.find('\n## ', start + len(heading))
    return text[start:] if end < 0 else text[start:end]


class CliDocsTests(unittest.TestCase):
    def test_cli_md_names_new_scripts_flags_and_codes(self):
        text = CLI.read_text(encoding='utf-8')
        for name in NAMES:
            self.assertIn(name, text)
        # Każda flaga argparse nowych skryptów jest w cli.md.
        for script in SCRIPTS:
            source = (ROOT / 'scripts' / script).read_text(encoding='utf-8')
            for flag in re.findall(r"add_argument\('(--[a-z-]+)'", source):
                self.assertIn(flag, text, f'{script}: {flag}')
        codes = section(text, '## Kody i kontrola')
        for code in CODES:
            self.assertRegex(codes, rf'\b{code}\b', f'kod {code}')

    def test_adr_014_to_021_exist_without_uuid_or_home_path(self):
        for number in range(14, 22):
            found = sorted((ROOT / 'docs' / 'adr').glob(f'ADR-{number:03d}-*.md'))
            self.assertEqual(len(found), 1, f'ADR-{number:03d}')
            text = found[0].read_text(encoding='utf-8')
            self.assertTrue(text.startswith(f'# ADR-{number:03d}: '), found[0].name)
            self.assertIsNone(UUID.search(text), found[0].name)
            self.assertIsNone(HOME.search(text), found[0].name)


if __name__ == '__main__':
    unittest.main()
