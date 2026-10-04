# Niezależny przegląd skryptów audytowych

## TL;DR

04.10.2026 sprawdzono `scripts/audit_sgjp.py`, `config/audit-policy.json` i `scripts/pilot_links.py` względem §6, §8 i §14 specyfikacji v3. Pięć syntetycznych kontroli kwalifikowania i deduplikacji przeszło. Nie znaleziono fałszywej akceptacji wynikającej z agregacji masek OR. W pilotażu wykryto rzeczywisty problem z klasyfikowaniem „Róży” jako braku na liście bez rozróżniania wielkości liter; koordynator przyjął poprawkę.

## Key Decisions

- Kontrole utrwalono w `scripts/test_audit_sgjp.py`; używają wyłącznie biblioteki standardowej Pythona i skryptu audytowego. Dane są syntetyczne, nie pochodzą ze słowników.
- Każdy test tworzy gzip i wynik JSON w osobnym `tempfile`. Osobny katalog roboczy obejmuje także cache sortowania; testy nie zmieniają rzeczywistych źródeł, raportów ani konfiguracji.
- Asercje sprawdzają liczby i decyzje wyjściowe, nie polegają na deklarowanych flagach `checks` skryptu.

## Open Questions / Risks

Testy potwierdzają wymienione własności mechanizmu audytowego. Nie dowodzą kompletności lingwistycznej filtrów, poprawności całej klasyfikacji segmentów ani gotowości generatora produkcyjnego. Nie badano tu pełnego procesu generowania, którego ten etap nie obejmuje. Status poprawki pilotażu wymaga osobnej weryfikacji przez koordynatora; niniejszy przegląd nie przedstawia zaakceptowanej propozycji jako już sprawdzonej zmiany.

## Wyniki pięciu kontroli

| Przypadek | Oczekiwany i zaobserwowany wynik |
|---|---|
| Dwie interpretacje `kot`: pospolita dawna i własna współczesna | Każdy filtr osobno ma interpretację przechodzącą, ale STANDARD nie przyjmuje klucza; BROAD przyjmuje jedną interpretację. |
| Własna `Róża` oraz pospolita `róża` | Dwa zapisy źródłowe, jeden klucz; jedna interpretacja i klucz pozostają w STANDARD. |
| Zależne `em` jako `aglt` oraz pospolite `em` jako `subst` | Odrzucona tylko interpretacja zależna; jedna interpretacja i klucz pozostają. |
| `pol-ski` | Filtr znaków odrzuca napis; normalizacja nie wytwarza `polski`. |
| Dwukrotna kopia tego samego rekordu `kot` | Dwa rekordy wejściowe, jeden duplikat, jedna unikalna interpretacja, jedna alternatywa gramatyczna, jeden klucz. |

Reprodukcja od katalogu głównego repozytorium:

```sh
python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'
```

Zaobserwowany wynik: `Ran 5 tests ... OK`.

SHA256 wersji użytej w tej weryfikacji:

- `scripts/audit_sgjp.py`: `eddfb8f8806f438b48a1ee360839aba234c9164dbe2e6055b962b99e07c53b4b`.
- `config/audit-policy.json`: `ec55f8a2a1be19f669d4d72f7bb992a3bea2021c332c139d0d8db11ce2c887c4`.
- `scripts/test_audit_sgjp.py`: `1a95f5ff792ee9be785bb58c2e4bf477e5979a66dbfb9a6d045a31a968f1f2d1`.

## Agregacja masek i braków

`audit_sgjp.py` oblicza oddzielne bity dla pojedynczych filtrów oraz dla całych prefiksów filtrów **wewnątrz jednej interpretacji**. Dopiero te bity agreguje OR po kluczu growym. Dzięki temu nie składa poprawności z różnych interpretacji. Syntetyczny przypadek pospolitej dawnej i własnej współczesnej interpretacji sprawdza właśnie tę pułapkę.

W `pilot_links.py` konstrukcja `evidence or ...` nie zamienia obecnej częstości zero na brak: `evidence` jest niepustym słownikiem zawierającym status oraz metryki. Wartość częstości nie stanowi warunku prawdziwości. Braki nie są imputowane zerem, a częstości pozostają przy jednostkach korpusowych.

## Znaleziony problem pilotażu

Przeglądana wersja `scripts/pilot_links.py`, sekcja dopasowania list `orth`/`orth_lc` (linie 57–66 przed poprawką), używała dokładnego napisu `Róża` również dla listy `orth_lc`. Wynikiem był `NOT_IN_PUBLISHED_LIST`. Rzeczywista lista zawiera jednostkę `róża` w wierszu danych 6226 z F=1373. To nieporównywalność klucza ze względu na wielkość liter, nie zaobserwowany brak jednostki korpusowej.

Zaproponowano jawne `UNMATCHED` z powodem utraty rozróżnienia wielkości liter albo osobne powiązanie ze wspólną jednostką korpusową, z zachowaniem niejednoznaczności. Koordynator wybrał **`UNMATCHED` bez kopiowania częstości** i zapowiedział poprawkę. Samo powiązanie obu zapisów z tym samym agregatem nie może podwajać dowodu ani przypisywać całej częstości nazwie i rzeczownikowi osobno.

## Weryfikacja poprawki przez koordynatora

2026-10-04T02:28:36Z — poprawiono orth_lc/Róża na UNMATCHED z wyjaśnieniem utraty wielkości liter. Ponowny pilotaż i kontrola JSON potwierdzają wynik. Wszystkie pięć utrwalonych testów przeszło po końcowej korekcie dwóch tagów ń. Model CorpusEvidence uzupełniono o komplet źródłowych miar, raw_record i osobną rangę wyliczoną zgodnie z przeglądem KWJP.
