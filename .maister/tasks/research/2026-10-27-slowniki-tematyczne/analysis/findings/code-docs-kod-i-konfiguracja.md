# Kod i konfiguracja: jak projekt traktuje etykiety dziedzin

## TL;DR
Etykieta dziedziny jest w bazie przy każdej formie (`interpretation.qualifiers`), jako surowy tekst z SGJP.
Polityka (`descriptive_checks`) tylko mówi „dziedzina nie wyklucza”. Nie buduje indeksu tematów.
Jedyny kod, który już dzieli etykiety na atomy i sprawdza 73 dziedziny, to warstwa `specialist` w `quality.py`.
Filtr tematyczny najprościej zbudować jak POP00: osobna komenda, konfiguracja i pakiet, podzbiór STANDARD.

## Key Decisions
- Zastane: `|` rozdziela etykiety, przecinek należy do etykiety (`qualifiers.json`: `technical_separator: "|"`, `comma_is_literal_inside_label: true`).
- Zastane: polityka nie dzieli przecinków w runtime (`policy.py:797-808`, `docs/generator/etykiety.md:58`). Rozbicie na atomy jest tylko w próbkowaniu jakości (`quality.py:278`).
- Wniosek: filtr tematyczny nie należy do `policy.py`. Temat nie zmienia dopuszczalności.

## Open Questions / Risks
- `pop.load_lexemes` dzieli kwalifikatory tylko po przecinku (`pop.py:175`), nie po `|`. Dla filtra tematów trzeba dzielić najpierw po `|`, potem po `,` (jak `quality.py:278`). Dziś to bez skutku: flaga `colloquial` (`pop.py:182`) nie jest nigdzie czytana.
- Kwalifikator jest przy formie, nie przy leksemie. Kuźnia składa go z poziomu leksemu, odmiany i końcówki (`etykiety.md:18`). Temat leksemu = suma po jego formach; trzeba sprawdzić, czy formy jednego leksemu mają różne dziedziny.
- Jeden ID SGJP może łączyć znaczenia (`etykiety.md:82`). Etykieta nie mówi, którego znaczenia dotyczy.

## 1. Skąd etykieta w bazie
- `sgjp.py:41-56` czyta eksport tab: 5 pól, pole 5 to kwalifikatory, bez parsowania.
- `build.py:34-47` zapisuje je do `sgjp_record`, potem do `interpretation` bez zmian.
- `schema.sql:5-10, 20-26`: `qualifiers TEXT` w `sgjp_record`, `interpretation` i `derivation_candidate` (w. 42). Leksem (`lexeme`, w. 11-15) nie ma kwalifikatorów.

## 2. Polityka (`policy.py`)
- `DESCRIPTIVE_LABELS` (`policy.py:436-…`): zamknięta mapa 357 dosłownych etykiet. Rejestr w `config/generator/policy.json:322` (`linguistic-descriptive-non-excluding-v1`). Test zgodności: `tests/test_policy.py:162-167`.
- `descriptive_checks` (`policy.py:797-808`): dla etykiety z mapy daje `accept` z komunikatem „Sama dziedzina, stylistyka lub opis wariantu formy nie wyklucza”. Porównuje całe etykiety (`set(qualifiers.split('|')) & DESCRIPTIVE_LABELS`).
- Mieszanki z wiekiem lub niepoprawnością nie są w mapie: `descriptive_checks('daw.,med.') == []` (`tests/test_policy.py:157-158`). Ich warunek daje `history_checks` lub `incorrect_checks`.
- Wywołanie: `_known_qualifier_checks` (`policy.py:404-408`). Etykieta bez warunku daje `unresolved` (`policy.py:416-433`).

## 3. Konfiguracja
| plik | co ma | rola |
|---|---|---|
| `config/generator/qualifiers.json` | 615 pól (`raw_combinations`), 605 dosłownych etykiet z licznikiem `compact_interpretations` i statusem | rejestr discovery, `status: not_active_policy` |
| `config/generator/policy.json:322` | lista 357 etykiet opisowych | rejestr reguły |
| `config/generator/quality-words.json:3-79` | `specialist_topics`: 73 atomy dziedzin, identyczne z `topics` w przeglądzie; `basis`: „own documented SGJP topical labels; sampling only, no eligibility effect” | próbka jakości |

Statusy 605 etykiet w `qualifiers.json` (policzone skryptem): 357 `confirmed_descriptive…`, 222 `pending_full_semantic_review`, 25 `user_approved_non_excluding_unestablished_gloss`, 1 akcent.

## 4. Istniejący kod z atomami dziedzin (`quality.py`)
- `sample_word_analyses` (`quality.py:251-…`) waliduje `quality-words.json` (`quality.py:264-270`).
- `specialist(q)` (`quality.py:278`): `{atom for label in q.split('|') for atom in label.split(',')} & topics`.
- Agregacja na słowo (`game_key`), `max(...)` po wszystkich analizach (`quality.py:286-295`). Słowo wpada do warstwy, gdy choć jedna analiza ma dziedzinę. To jest gotowy wzór filtra, ale na poziomie słowa, nie leksemu i nie tematu.

## 5. Inne moduły
- `kwjp.py` tylko parsuje 13 list KWJP (lemma/orth/orth_lc/bigram + miary). Bez dziedzin.
- `pop.py:162-185` (`load_lexemes`) agreguje POS, nazwy i kwalifikatory na leksem (`lexeme.id`). Dobry punkt startu dla tematu leksemu po poprawce podziału po `|`.
- `explain.py:284, 328` wypisuje kwalifikatory każdej analizy. Pozwala ręcznie sprawdzić przykład słowa z tematu.

## 6. Gdzie wpiąć filtr tematyczny
Wzór: POP/POP0/POP00 (ADR-007/008/009).
1. **Wejście:** zamrożony przebieg (`build.sqlite`) i pakiet LL-PL, przypięte hashami jak `BASE_KEYS` w `pop.py:19-20` (`database_sha256`, `release_manifest_sha256`, `standard_sha256`).
2. **Temat leksemu:** suma atomów po formach leksemu (`interpretation` → `lexeme`), dzielenie `|` potem `,`. Mapa temat → atomy w nowej konfiguracji (np. marynistyka = `mors.`, `żegl.`, `ryb.`).
3. **Formy:** formy leksemu, które są na liście bazowej (STANDARD lub BROAD). Podzbiór bazy jak `POP00 ⊆ POP0 ⊆ STANDARD` (`docs/adr/ADR-009-pop00-v1.md:9-12`).
4. **CLI:** nowa podkomenda obok `pop`/`pop00` (`cli.py:44-55`) i nowy `--variant` w `explain` (`cli.py:30`).
5. **Pakiet:** jak POP00: `<NAZWA>.txt.gz` (jedna forma na linię), `SHA256SUMS`, `method.json`, `release-manifest.json`, `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `reports/` (`data/work/pop00-v1-20261021-r2-b/`). Listy LL-PL to zwykły tekst, jedna forma na linię (`data/work/release-LL-PL-v30/LL-PL-STANDARD.txt`).
6. **Dokumenty:** nowy ADR w `docs/adr/` i strona wiki `Slownik-<NAZWA>` (zob. `code-docs-decyzje-i-dokumenty.md`).

`policy.py`, `verify` (K1–K10) i build LL-PL zostają bez zmian.
