# Przegląd pragmatyczny: POP/POP0 (#3)

Status: **zgodny ze skalą, drobne nadmiary**. Bez problemów Critical i High. 3 Medium, 4 Low.

## TL;DR
- Złożoność pasuje do zadania. To generator danych z wymogiem odtwarzalności bajtowej, a nie aplikacja. Kod jest w stdlib, bez nowych klas i bez infrastruktury.
- Opcje D1–D8, których nie wybrano, mają uzasadnienie. `measure_pop.py` porównuje je wszystkie. Rewizje 2 i 3 ADR-007 zmieniły D3, D5 i D8 tego samego dnia, właśnie na podstawie tych porównań.
- Nadmiar to zawężanie konfiguracji w dwóch warstwach, martwa gałąź `members: all` w `build_pop` i dwie funkcje używane tylko w testach. Razem około 120 linii.
- `spec.md` jest nieaktualny wobec ADR-007 rew. 2 i 3. Opisuje F z percentyli i `available-only`, nie zna przycinania. Kod i `pop-acceptance.md` są zgodne z ADR.
- Testy POP: 90 testów w 7 s. Szybka pętla zwrotna.

## Key Decisions
- Zostawiam kod opcji pomiarowych w `pop.py` (linie 1–1195). Pomiar był potrzebny dwa razy w jeden dzień. Wycięcie go utrudniłoby rewizję 4, a ADR-007 §Rewizja ją przewiduje.
- `scripts/check_pop_package.py` ma własne `sha256` i `load_json` i nie importuje `pop.py`. To nie jest duplikacja do usunięcia: niezależność kontroli wymaga D-3.
- Nie zalecam zmian przed wydaniem. Każde z uproszczeń poniżej zmienia `tree_sha256`/`code_identity` pakietu. Zrobić je przy następnej wersji metody albo osobnym PR.

## Open Questions / Risks
- `prune-weak-members` (rew. 3) to jedyna wybrana opcja, której `measure_pop.py` nie porównuje (`member_units` nie ma tam wywołania). Liczby z przycinaniem są tylko w raporcie progów `build_pop`. Przy rewizji 4 brakuje tu porównania „przed/po”.
- Rozjazd spec ↔ ADR może zmylić kolejnego wykonawcę: spec jest kontraktem odbioru, a ma stare liczby D-6 (1 328 263 formy, 98,5%). Pakiet ma 1 219 614 form i 97,35%.

## Ocena złożoności
| miara | wartość |
|---|---|
| `literaki_slownik/pop.py` | 1 773 linii (pomiar 1–1195, konfiguracja 1196–1313, `build_pop` 1315–1527, pakiet 1529–1773) |
| `scripts/measure_pop.py` | 747 |
| `scripts/check_pop_package.py` | 327 |
| `explain_pop` + pomocnicze (`explain.py`) | ~155 |
| testy POP | ~2 270 linii, 90 testów, 6,9 s |

Skala: jeden opiekun, generator w stdlib. Pakiet ma być odtwarzalny bajtowo (D-1), mieć piny i niezależną kontrolę. To wymagania zadania, nie dodane na zapas. Złożoność: **Medium**, proporcjonalna.

## Problemy

### Medium
**M1. Konfiguracja zawężana dwa razy** (`pop.py:1217-1297`).
`_validate_config` sprawdza całą przestrzeń opcji: klasy D2, D6 `coverage`, wszystkie D8, D5 `a`–`e`. Zaraz potem `_adr_007` przepuszcza tylko wartości ADR-007. Około 60 linii walidacji służy wartościom, które `load_config` i tak odrzuca. To przygotowanie na metodę, której jeszcze nie ma.
Uproszczenie: zostawić `_exact` dla kluczy oraz `_adr_007`, w którym `config[k] == ADR_007[k]`, `d3/d4 in ADR_007_D3_D4` i `d6.by == count`. Liczby D6 i `sampling` sprawdzać jak teraz. Zysk: około 50 linii, jeden komunikat błędu zamiast dwóch ścieżek.

**M2. Martwa gałąź `members: all` w `build_pop`** (`pop.py:1439-1453`, `1475-1476`, `_pruning_report` przy `pruned is None`).
`load_config` odrzuca `members: all` (test `tests/test_pop.py:974`). Wszystkie `if pruning else …` w `build_pop` nie dają się więc wykonać z CLI. Zostały po rew. 3.
Uproszczenie: albo usunąć gałąź (`pruning = True`), albo dopuścić `members: all` w `ADR_007` jako jawny wariant porównawczy. Teraz kod jest w połowie drogi.

**M3. `spec.md` nieaktualny wobec ADR-007 rew. 2/3** (`implementation/spec.md`, tabela metody, C6, D-6).
Zero wystąpień `log-ipm`, `prune`, `lower-bound`. Spec opisuje miarę z percentyli F i D8 `available-only`. Kod, `pop.json` i `verification/pop-acceptance.md` mają log-ipm, `lower-bound-absent` i `prune-weak-members`.
Naprawa: dopisać w spec sekcję „Rewizje metody”, która wskazuje ADR-007 rew. 2/3, i zaktualizować liczby D-6. To dokument, kod zostaje bez zmian.

### Low
**L1. Funkcje używane tylko w testach:** `nkjp_lexeme_ranks` (`pop.py:433`, 48 linii) i `nkjp_form_status` (`pop.py:424`). Nie wywołuje ich ani `build_pop`, ani `measure_pop.py`. Spec wymienia `nkjp_lexeme_ranks` jako kod do ponownego użycia, ale nic go nie używa. Ślad po etapie A. Usunąć razem z testami (`tests/test_pop.py:295-318`).

**L2. Dwie nazwy jednej flagi:** `bound:<źródło>` przy `lower-bound-absent` i `lower_bound:<źródło>` przy `lower-bound` (`pop.py:810`). Dotyczy tylko porównań pomiarowych. Wystarczy jedna nazwa.

**L3. Nazwy plików list w trzech miejscach:** `LIST_FILES` w `pop.py:1534`, `_POP_LIST_FILES` w `explain.py:286` i `LISTS` w `check_pop_package.py:31`. Kopia w kontrolerze ma uzasadnienie (niezależność). `explain.py` importuje z `pop` `COMMON_NAME`, ale nie `LIST_FILES`. Ujednolicić import.

**L4. Dwie ścieżki wycofania NKJP:** `ADR_007_D3_D4` dopuszcza samą KWJP jako `log-ipm` i jako `F` (`pop.py:1212-1214`). Komentarz w kodzie mówi, że obie dają tę samą kolejność. Do jednej potrzeby wystarczy jedna wartość.

## Opcje niewybrane: werdykt
| opcja | gdzie żyje | uzasadnienie |
|---|---|---|
| D2 klasy, reguła (ii) | `load_form_classes`, `load_forms_accepted`, `forms_for(classes=…)` | `measure_pop` pokazuje −45% form bez klas; to argument za D2 |
| D3 ARF/1-DP/gatunki/F, wagi 0,25/0,75 | `measure` | rew. 2 zmieniła F → log-ipm na podstawie porównania |
| D5 `a`–`d` | `units` | raport D5 (masa NKJP, największa grupa) |
| D6 `coverage` | `threshold` | pomiar progów pokryciem (`measure_pop.py:309`) |
| D8 `available-only`/`lower-bound`/`exclude` | `measure` | rew. 2 zmieniła D8; Jaccard między regułami |
| D5 `members: all` | `build_pop` | **nieosiągalne** (M2) |

Wniosek: kod opcji przechowywany dla pomiaru ma uzasadnienie. Każda opcja ma wywołanie w `measure_pop.py` i liczbę w raporcie. Wyjątek: M2 i L1.

## Doświadczenie dewelopera
- Szybka pętla: 90 testów w 7 s, bez sieci.
- Docstringi łączą kod z wymaganiami (C5, C14, D9), łatwo przejść od wymagania do kodu.
- `build_pop` ma około 110 linii z lambdami (`forms_of`, `report`). Funkcja jest długa, ale liniowa. Podział nie jest pilny.
- Docstring `measure` (`pop.py:743-757`) ma 14 linii o czterech regułach D8. Jest gęsty, ale zgodny z kodem.

## Uproszczenia, kolejność
1. M3: zaktualizować spec (dokument, 15 min, bez wpływu na pakiet).
2. M2 i L1: usunąć martwą gałąź i funkcje tylko testowe (około 70 linii, 30 min; zmienia `code_identity`, więc po wydaniu `pop-v1`).
3. M1: zawęzić walidację do `_adr_007` (około 50 linii, 30 min; ten sam warunek czasowy).

Po zmianach `pop.py` zmaleje z 1 773 do około 1 650 linii. Zależności i zachowanie pakietu bez zmian.
