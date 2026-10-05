PRAGMA user_version=1;
CREATE TABLE source_artifact (
 source_id TEXT PRIMARY KEY, kind TEXT NOT NULL, metadata TEXT NOT NULL
);
CREATE TABLE sgjp_record (
 source_id TEXT NOT NULL REFERENCES source_artifact,
 row_number INTEGER NOT NULL, form TEXT NOT NULL, lemma TEXT NOT NULL,
 tag TEXT NOT NULL, names TEXT NOT NULL, qualifiers TEXT NOT NULL,
 PRIMARY KEY(source_id,row_number)
);
CREATE TABLE lexeme (
 id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_artifact,
 lemma_id TEXT NOT NULL, lemma_base TEXT NOT NULL,
 UNIQUE(source_id,lemma_id)
);
CREATE TABLE surface_form (
 id INTEGER PRIMARY KEY, original TEXT NOT NULL UNIQUE, nfc TEXT NOT NULL,
 game_key TEXT NOT NULL, length INTEGER NOT NULL
);
CREATE TABLE interpretation (
 id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_artifact,
 first_row INTEGER NOT NULL, form_id INTEGER NOT NULL REFERENCES surface_form,
 lexeme_id INTEGER NOT NULL REFERENCES lexeme, tag TEXT NOT NULL,
 names TEXT NOT NULL, qualifiers TEXT NOT NULL,
 UNIQUE(source_id,form_id,lexeme_id,tag,names,qualifiers)
);
CREATE INDEX form_game_key ON surface_form(game_key);
CREATE INDEX form_nfc ON surface_form(nfc);
CREATE INDEX lemma_base ON lexeme(lemma_base);
CREATE INDEX interpretation_form ON interpretation(form_id);
CREATE INDEX interpretation_lexeme ON interpretation(lexeme_id);
CREATE TABLE corpus_evidence (
 id INTEGER PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source_artifact,
 row_number INTEGER NOT NULL, unit_1 TEXT NOT NULL, unit_2 TEXT,
 pos TEXT, raw_metrics TEXT NOT NULL, typed_metrics TEXT NOT NULL,
 freq INTEGER NOT NULL, UNIQUE(source_id,row_number)
);
CREATE INDEX evidence_unit ON corpus_evidence(unit_1,unit_2,pos);
CREATE TABLE derivation_candidate (
 candidate_key TEXT PRIMARY KEY, rule_id TEXT NOT NULL,
 original TEXT NOT NULL, game_key TEXT NOT NULL, lemma_id TEXT NOT NULL,
 expanded_tag TEXT NOT NULL, names TEXT NOT NULL, qualifiers TEXT NOT NULL,
 payload TEXT NOT NULL
);
CREATE INDEX derivation_game_key ON derivation_candidate(game_key);
CREATE TABLE derivation_component (
 candidate_key TEXT NOT NULL REFERENCES derivation_candidate,
 position INTEGER NOT NULL, kind TEXT NOT NULL,
 source_id TEXT, source_row INTEGER,
 PRIMARY KEY(candidate_key,position),
 FOREIGN KEY(source_id,source_row) REFERENCES sgjp_record(source_id,row_number),
 CHECK ((kind='source_interpretation' AND source_id IS NOT NULL AND source_row IS NOT NULL)
     OR (kind='grammatical_particle' AND source_id IS NULL AND source_row IS NULL))
);
