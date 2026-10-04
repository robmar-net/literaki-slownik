#!/usr/bin/env python3
"""Syntetyczne kontrole kwalifikowania interpretacji i deduplikacji audytu SGJP.

Uruchomienie: python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'
Fixture'y są własnymi danymi testowymi; nie pochodzą z żadnego słownika.
"""
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_sgjp.py"
POLICY = ROOT / "config/audit-policy.json"


class AuditSgjpTests(unittest.TestCase):
    def run_audit(self, rows):
        # Osobny cwd zatrzymuje także wewnętrzny cache sortowania w tempfile.
        with tempfile.TemporaryDirectory(prefix="literaki-sgjp-test-") as temp:
            directory = Path(temp)
            source = directory / "synthetic.tab.gz"
            output = directory / "result.json"
            with gzip.open(source, "wt", encoding="utf-8") as stream:
                stream.write("# Syntetyczny nagłówek testu\n#</COPYRIGHT>\n")
                for row in rows:
                    stream.write("\t".join(row) + "\n")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), str(output),
                 "--policy", str(POLICY)],
                cwd=directory, capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            return json.loads(output.read_text(encoding="utf-8"))

    def filter_result(self, result, name):
        return next(row for row in result["filters"] if row["filter"] == name)

    def test_entire_policy_must_be_satisfied_by_one_interpretation(self):
        # Jedna interpretacja jest pospolita, ale dawna; druga współczesna,
        # ale własna. Żadna nie spełnia wszystkich warunków STANDARD.
        result = self.run_audit([
            ("kot", "kot:S", "subst:sg:nom:m2", "", "daw."),
            ("kot", "kot:S2", "subst:sg:nom:m2", "nazwa_wlasna", ""),
        ])
        self.assertEqual(self.filter_result(result, "nazwa_wlasna")["lost_keys_alone"], 0)
        self.assertEqual(self.filter_result(result, "historycznosc")["lost_keys_alone"], 0)
        self.assertEqual(self.filter_result(result, "niepoprawnosc")["remaining_keys_cumulative"], 1)
        self.assertEqual(self.filter_result(result, "historycznosc")["remaining_keys_cumulative"], 0)
        self.assertTrue(all(not row["key_in_standard_screen"] for row in result["pilot_sgjp"]))

    def test_common_noun_survives_proper_name_with_same_game_key(self):
        result = self.run_audit([
            ("Róża", "Róża", "subst:sg:nom:f", "imię", ""),
            ("róża", "róża", "subst:sg:nom:f", "", ""),
        ])
        self.assertEqual(result["unique_original_forms"], 2)
        self.assertEqual(result["unique_nfc_lower_keys"], 1)
        final = self.filter_result(result, "historycznosc")
        self.assertEqual(final["remaining_keys_cumulative"], 1)
        self.assertEqual(final["remaining_interpretations_cumulative"], 1)
        by_form = {row["source_row"][0]: row for row in result["pilot_sgjp"]}
        self.assertIn("nazwa_wlasna", by_form["Róża"]["failed_filters"])
        self.assertEqual(by_form["róża"]["failed_filters"], [])

    def test_common_em_survives_dependent_agglutinant(self):
        result = self.run_audit([
            ("em", "być", "aglt:sg:pri:imperf:wok", "", ""),
            ("em", "em", "subst:sg:nom:n:ncol", "", ""),
        ])
        segment = self.filter_result(result, "segment_do_oceny")
        self.assertEqual(segment["rejected_interpretations_alone"], 1)
        self.assertEqual(segment["lost_keys_alone"], 0)
        self.assertEqual(segment["remaining_interpretations_cumulative"], 1)
        final = self.filter_result(result, "historycznosc")
        self.assertEqual(final["remaining_interpretations_cumulative"], 1)
        self.assertEqual(final["remaining_keys_cumulative"], 1)

    def test_hyphen_is_not_removed_to_create_an_acceptable_word(self):
        result = self.run_audit([
            ("pol-ski", "polski", "adj:sg:nom:m1:pos", "", ""),
        ])
        self.assertEqual(result["unique_original_forms"], 1)
        self.assertEqual(result["unique_nfc_lower_keys"], 1)
        characters = self.filter_result(result, "znaki")
        self.assertEqual(characters["rejected_interpretations_alone"], 1)
        self.assertEqual(characters["remaining_keys_cumulative"], 0)
        self.assertEqual(self.filter_result(result, "historycznosc")["remaining_keys_cumulative"], 0)

    def test_duplicate_row_does_not_double_interpretations(self):
        row = ("kot", "kot", "subst:sg:nom:m2", "", "")
        result = self.run_audit([row, row])
        self.assertEqual(result["counts"]["records"], 2)
        self.assertEqual(result["counts"]["duplicate_records"], 1)
        self.assertEqual(result["counts"]["unique_compact_interpretations"], 1)
        self.assertEqual(result["counts"]["expanded_grammar_alternatives"], 1)
        self.assertEqual(result["unique_source_lemma_identifiers"], 1)
        self.assertEqual(result["unique_original_forms"], 1)
        self.assertEqual(self.filter_result(result, "historycznosc")["remaining_interpretations_cumulative"], 1)
        self.assertEqual(self.filter_result(result, "historycznosc")["remaining_keys_cumulative"], 1)


if __name__ == "__main__":
    unittest.main()
