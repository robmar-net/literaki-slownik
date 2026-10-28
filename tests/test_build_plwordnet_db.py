"""Pochodna Słowosieci dla TEMATY (#11, W2): dane syntetyczne, bez sieci."""
import hashlib
import importlib.util
import os
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('build_plwordnet_db', ROOT / 'scripts/build_plwordnet_db.py')
build_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_module)

# Zrzut w kształcie mysqldump: kolumny redaktorów, tabele spoza listy, wiersz valid=0,
# wielowierszowy INSERT, ucieczki \' i \\ oraz średnik i nowy wiersz wewnątrz napisu.
DUMP = r"""-- MySQL dump
/*!40101 SET NAMES utf8 */;
CREATE TABLE `iplog` (
  `ID` bigint(20) NOT NULL,
  `ip` varchar(64) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM;
INSERT INTO `iplog` VALUES (1,'10.0.0.1');
CREATE TABLE `lexicalunit` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
  `lemma` varchar(255) NOT NULL DEFAULT '',
  `pos` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `comment` varchar(2048) DEFAULT NULL,
  `variant` int(11) NOT NULL,
  `owner` varchar(255) NOT NULL,
  `error_comment` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM;
LOCK TABLES `lexicalunit` WRITE;
INSERT INTO `lexicalunit` VALUES (30,'okręt',2,1,'uwaga; z \'cudzysłowem\'',1,'redaktor.a','błąd'),
(10,'statek',2,1,NULL,1,'redaktor.b',NULL),
(20,'d\'Artagnan \\ x',2,0,'wiersz
drugi;',2,'redaktor.c','');
INSERT INTO `lexicalunit` VALUES (40,'łódź',2,1,'',2,'redaktor.a',NULL);
UNLOCK TABLES;
CREATE TABLE `synset` (
  `ID` bigint(20) NOT NULL,
  `isabstract` int(1) NOT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  `owner` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM;
INSERT INTO `synset` VALUES (200,0,'k','o'),(100,1,NULL,'o'),(300,0,NULL,'o');
CREATE TABLE `unitandsynset` (
  `LEX_ID` bigint(20) NOT NULL,
  `SYN_ID` bigint(20) NOT NULL,
  `unitindex` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`SYN_ID`,`unitindex`)
) ENGINE=MyISAM;
INSERT INTO `unitandsynset` VALUES (40,300,0),(10,100,0),(30,200,0),(20,100,1);
CREATE TABLE `synsetrelation` (
  `PARENT_ID` bigint(20) NOT NULL,
  `CHILD_ID` bigint(20) NOT NULL,
  `REL_ID` bigint(20) NOT NULL,
  `valid` int(1) DEFAULT '1',
  `owner` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`PARENT_ID`,`CHILD_ID`,`REL_ID`)
) ENGINE=MyISAM;
INSERT INTO `synsetrelation` VALUES (100,300,11,1,'a'),(100,200,11,1,'b'),(200,300,25,0,'c'),(100,200,27,1,'');
CREATE TABLE `relationtype` (
  `ID` bigint(20) NOT NULL,
  `objecttype` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(500) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM;
INSERT INTO `relationtype` VALUES (27,0,'miejsce','x'),(11,0,'hiperonimia','y'),(25,0,'część','z'),(3,0,'inna','w');
CREATE TABLE `tracker_synset` (
  `ID` bigint(20) NOT NULL,
  `owner` varchar(255) NOT NULL
) ENGINE=MyISAM;
INSERT INTO `tracker_synset` VALUES (1,'redaktor.a');
"""

EXPECTED_COLUMNS = {
    'lexicalunit': ['ID', 'lemma', 'pos', 'variant'],
    'synset': ['ID', 'isabstract'],
    'unitandsynset': ['LEX_ID', 'SYN_ID', 'unitindex'],
    'synsetrelation': ['PARENT_ID', 'CHILD_ID', 'REL_ID'],
    'relationtype': ['ID', 'name'],
    'meta': ['key', 'value'],
}


def write_zip(path, dump):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('wordnet_work_4_5.sql', dump)


class BuildPlwordnetDbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.zip = self.root / 'wordnet.zip'
        write_zip(self.zip, DUMP)

    def tearDown(self):
        self.tmp.cleanup()

    def test_parser_multiline_insert_and_escapes(self):
        statements = list(build_module.iter_statements(DUMP.splitlines(keepends=True)))
        inserts = [s for s in statements if s.startswith('INSERT INTO `lexicalunit`')]
        self.assertEqual(2, len(inserts))
        table, rows = build_module.parse_insert(inserts[0])
        self.assertEqual('lexicalunit', table)
        self.assertEqual(3, len(rows))
        self.assertEqual((30, 'okręt', 2, 1, "uwaga; z 'cudzysłowem'", 1, 'redaktor.a', 'błąd'), rows[0])
        self.assertEqual("d'Artagnan \\ x", rows[2][1])
        self.assertEqual('wiersz\ndrugi;', rows[2][4])
        self.assertIsNone(rows[1][4])

    def test_derivative_has_only_allowed_tables_columns_and_valid_rows(self):
        out = self.root / 'out.sqlite'
        report = build_module.build(self.zip, out)
        db = sqlite3.connect(f'file:{out}?mode=ro', uri=True)
        try:
            tables = {name for (name,) in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual(set(EXPECTED_COLUMNS), tables)
            for table, columns in EXPECTED_COLUMNS.items():
                self.assertEqual(columns, [r[1] for r in db.execute(f'PRAGMA table_info({table})')])
            self.assertEqual([(100, 200, 11), (100, 200, 27), (100, 300, 11)],
                             db.execute('SELECT * FROM synsetrelation').fetchall())
            self.assertEqual([(10, 'statek', 2, 1), (20, "d'Artagnan \\ x", 2, 2), (30, 'okręt', 2, 1), (40, 'łódź', 2, 2)],
                             db.execute('SELECT * FROM lexicalunit').fetchall())
            meta = dict(db.execute('SELECT key, value FROM meta'))
            self.assertEqual(build_module.sha256_file(self.zip), meta['zip_sha256'])
            self.assertEqual(build_module.SCRIPT_VERSION, meta['script_version'])
            schema = ' '.join(sql for (sql,) in db.execute('SELECT sql FROM sqlite_master WHERE sql IS NOT NULL'))
        finally:
            db.close()
        for forbidden in ('owner', 'comment', 'iplog', 'iplimit', 'tracker'):
            self.assertNotIn(forbidden, schema)
        raw = out.read_bytes()
        for leaked in ('redaktor', '10.0.0.1', 'cudzysłow', 'wiersz'):
            self.assertNotIn(leaked.encode(), raw)
        self.assertEqual(3, report['counts']['synsetrelation'])
        self.assertEqual({'0': 1}, report['skipped_relations_by_valid'])

    def test_wrong_relation_name_is_an_error(self):
        bad = self.root / 'bad.zip'
        write_zip(bad, DUMP.replace("(25,0,'część','z')", "(25,0,'meronimia','z')"))
        out = self.root / 'bad.sqlite'
        with self.assertRaises(build_module.BuildError) as caught:
            build_module.build(bad, out)
        self.assertIn('25', str(caught.exception))
        self.assertFalse(out.exists())
        self.assertEqual(sorted(['wordnet.zip', 'bad.zip']), sorted(os.listdir(self.root)))

    def test_two_runs_are_byte_identical_and_output_is_never_replaced(self):
        first, second = self.root / 'a.sqlite', self.root / 'b.sqlite'
        build_module.build(self.zip, first)
        build_module.build(self.zip, second)
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
        self.assertEqual(digest(first), digest(second))
        before = digest(first)
        with self.assertRaises(build_module.BuildError):
            build_module.build(self.zip, first)
        self.assertEqual(before, digest(first))


if __name__ == '__main__':
    unittest.main()
