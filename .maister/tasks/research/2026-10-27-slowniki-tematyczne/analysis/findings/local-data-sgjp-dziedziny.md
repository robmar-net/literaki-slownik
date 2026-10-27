# Dane lokalne: etykiety dziedzin w SGJP 20260823

## TL;DR
- Etykietę dziedziny (73 tematy) ma tylko **4472 z 387 398 leksemów SGJP (1,2%)**.
- Trafność jest wysoka: próbka 30 przykładów daje 29/30 (morze), 27/30 (rolnictwo), 30/30 (matematyka).
- Pokrycie jest niskie: oczywiste słowa z tematu mają etykietę w 27% (morze), 0% (rolnictwo), 23% (matematyka).
- Wniosek: SGJP pozwala zbudować krótką, pewną listę „rdzenia”, ale nie pełny słownik tematyczny. Rolnictwa praktycznie nie da się zbudować z samych etykiet.

## Key Decisions
- Leksem = pole 2 eksportu (lemat z przyrostkiem homonimu, np. `pancernik:Sm2.m3`). Eksport nie ma liczbowego ID; tak samo działa baza (`lexeme.lemma_id`).
- Etykieta dosłowna = fragment pola 5 między `|` (separator techniczny wg `config/generator/qualifiers.json`, `technical_separator: "|"`). Atom = dalszy podział po przecinku.
- Leksem ma etykietę, jeśli ma ją choć jeden wiersz. Dla 4032 z 4472 leksemów etykieta jest na ≥90% wierszy, więc to cecha leksemu, nie formy.
- „W liście” = któraś forma z etykietą jest w liście (kolumny `form_*`); dla porównania też lemat bazowy (`lemma_*`).
- Listy: v30 = `data/work/lists-v30-20261010-165826-a/lists/{broad,standard}.txt`; v31 = `data/work/release-LL-PL-v30/LL-PL-{BROAD,STANDARD}.txt`. Uwaga: pakiet `release-LL-PL-v30` jest zbudowany z przebiegu `lists-v31-20261012-162111-a` (`release-manifest.json`, `source_run.run_name`), a `LL-PL-BROAD.txt` ma ten sam SHA-256 co `lists-v31-*/lists/broad.txt` (`4f1aace9…`).

## Open Questions / Risks
- Próbki oceniałem sam (bez drugiej osoby). Słowa do testu pokrycia też wybrałem sam; `całka` i `całkowanie` są zarazem w próbce.
- Etykieta jest przy leksemie, nie przy znaczeniu. Leksem wieloznaczny dostaje jedną etykietę dla wszystkich znaczeń (np. `buchtować` ma `łow.,żegl.`).
- Etykiety rozkładają się nierówno: `cosinus` ma `mat.`, `sinus` nie ma; `kil` ma `żegl.`, `kotwica` nie ma. Nie widać reguły, kiedy autorzy ją dodają. Za etykietą nie stoi homonimia: wśród leksemów z dziedziną homonimów jest 652/4472 (14,6%), wśród wszystkich 76 578/387 398 (19,8%).

## Metoda i polecenia
Skrypty (poza repo): `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/td/`
- `measure.py` — strumień `cache/sgjp/sgjp-20260823.tab.gz`: 7 458 520 wierszy, 387 398 leksemów (17 s).
- `analyze.py` — liczniki na atom i etykietę, przecięcia z listami → `counts.json` w tym samym katalogu.
- `sample.py` — próbka 30, `random.Random(20261027)`.
- `cover.py` — test pokrycia na oczywistych słowach.
- `hom.py`, `forms.py`, `kwjp.py` — homonimia, liczby form, gatunki KWJP.

Zgodność z dowodami projektu: rozkład pola 5 (`cut -f5 | sort | uniq -c`, 637 wartości) daje te same liczby wierszy co `raw_combinations` w `config/generator/qualifiers.json` i `compact_interpretations` w `label-coverage.json` (np. `mat.` 859, `żegl.` 3187, `mors.` 1619, `roln.` 1946).
Baza przebiegu (`data/work/lists-v31-20261012-162111-a/build.sqlite`, otwarta `?mode=ro`) daje te same etykiety dla próby: `całka|mat.`, `kil|żegl.`, `arfować|roln.`, `kotwica|` (puste), `sinus|`, `brona|`. Sprawdziłem tylko te leksemy; bazy nie skanowałem w całości.

## Zasięg: leksemy na etykietę (atomy)
Liczba wierszy w eksporcie mówi niewiele: `mat.` ma 859 wierszy, ale tylko 62 leksemy.

- Leksemy z którymkolwiek z 73 atomów-tematów: **4472** (z 7 atomami spoza mapy, np. `astron.`, `kolej.`, `flis.`, `fot.`, `gry`: 4514).
- Ich formy: 66 371, z czego 56 658 w BROAD v31 i 54 804 w STANDARD v31 (`forms.py`).

Największe atomy (leksemy; formy z etykietą w BROAD v31 / STANDARD v31):

| Atom | Leksemy | BROAD v31 | STD v31 |
|---|---:|---:|---:|
| zool. | 665 | 653 | 649 |
| bot. | 407 | 406 | 405 |
| hist. | 307 | 253 | 239 |
| techn. | 208 | 203 | 196 |
| med. | 195 | 178 | 177 |
| żegl. | 185 | 185 | 182 |
| jęz. | 185 | 156 | 153 |
| muz. | 172 | 162 | 162 |
| kulin. | 162 | 154 | 153 |
| chem. | 134 | 130 | 129 |
| mat. | 62 | 60 | 59 |
| mors. | 58 | 53 | 53 |
| roln. | 38 | 38 | 38 |
| ogr. | 21 | 21 | 21 |
| ryb. | 16 | 16 | 16 |
| zootechn. | 16 | 16 | 16 |
| leśn. | 14 | 14 | 13 |
| pszcz. | 8 | 8 | 8 |

Pełna tabela (wszystkie atomy i etykiety dosłowne, v30 i v31, forma i lemat): `counts.json` w katalogu skryptów.
v30 i v31 różnią się tu najwyżej o 1 leksem na atom.
Etykiety dosłowne złożone są małe; np. `mors.,żegl.` 56 wierszy, `łow.,żegl.` 227 wierszy, `fiz.,mat.` 11 wierszy.

## Trzy tematy

| Temat | Atomy | Leksemy | W BROAD v31 | W STD v31 | Formy z etykietą w BROAD v31 |
|---|---|---:|---:|---:|---:|
| Morze | `mors.`, `żegl.`, `ryb.` | 254 | 249 | 246 | 4487 |
| Rolnictwo | `roln.`, `ogr.`, `zootechn.`, `pszcz.`, `leśn.` | 96 | 96 | 95 | 2721 |
| Matematyka | `mat.` | 62 | 60 | 59 | 603 |

Części mowy (pierwszy tag leksemu): morze — 214 rzeczowników, reszta to głównie czasowniki; rolnictwo — 68 rzeczowników, 26 czasowników; matematyka — 56 rzeczowników.
Etykietowane słowa są rzadkie w tekstach: w KWJP100 (lista lematów, próg 5 wystąpień) jest tylko 75 z 254 lematów morskich, 17 z 96 rolniczych i 25 z 62 matematycznych (`kwjp.py`).

### Próbka 30 (trafne / wątpliwe / błędne)
- **Morze: 29 / 1 / 0.** Np. `bajdewind`, `bombramstenga`, `cuma`, `hals`, `saling`, `trałowiec`, `zęzowy`, `brander` (`mors.,wojsk.`). Wątpliwe: `buchtować` (`łow.,żegl.`, dwa znaczenia).
- **Rolnictwo: 27 / 3 / 0.** Np. `arfować`, `głęboszować`, `stogować`, `opielacz`, `forwarder` (`leśn.`), `wytopki` (`pszcz.`), `klajdesdal` (`zootechn.`). Wątpliwe: `glinować` (`roln.` i `techn.`), `sorbować` (`chem.,ogr.`), `perukarz` (`łow.,zootechn.`).
- **Matematyka: 30 / 0 / 0.** Np. `całka`, `cotangens`, `graniastosłup`, `iloczyn`, `odjemna`, `wektor`, `wielomian`, `logarytmicznie`.

### Pokrycie: oczywiste słowa z tematu (`cover.py`)
Wszystkie 107 słów są w SGJP. Liczę, czy któryś leksem o tym lemacie ma atom tematu.

| Temat | Słów | Z etykietą | Odsetek |
|---|---:|---:|---:|
| Morze | 37 | 10 | 27% |
| Rolnictwo | 35 | 0 | 0% |
| Matematyka | 35 | 8 | 23% |

- Morze, z etykietą: `kil`, `kambuz`, `bandera`, `reja`, `bom`, `fok`, `halsować`, `kuk`, `bakburta`, `achtersztag`. Bez: `kotwica`, `maszt`, `żagiel`, `ster`, `bosman`, `rufa`, `burta`, `pokład`, `statek`, `okręt`, `jacht`, `sztorm`, `kuter`, `cumować`, `sterburta`, `knaga`, `trał` i in.
- Rolnictwo, bez etykiety wszystkie: `orka`, `brona`, `pług`, `kombajn`, `siew`, `żniwa`, `snop`, `stóg`, `obora`, `nawóz`, `ul`, `pasieka`, `bronować`, `orać`, `ugór`, `miedza` i in.
- Matematyka, z etykietą: `całka`, `wektor`, `cosinus`, `logarytm`, `iloraz`, `przeciwprostokątna`, `przyprostokątna`, `całkowanie`. Bez: `macierz`, `pochodna`, `ułamek`, `równanie`, `funkcja`, `trójkąt`, `sinus`, `pierwiastek`, `potęga`, `kąt`, `parabola`, `dodawanie` i in.

Wzór: etykietę mają słowa wąsko fachowe (`bombramstenga`, `głęboszować`, `traktrysa`). Słowa podstawowe dla tematu jej zwykle nie mają. Jeśli test pokrycia jest reprezentatywny, temat morski ma w SGJP rząd ~1000 leksemów (254 / 0,27), a matematyczny ~270 (62 / 0,23). To szacunek z małej próbki, o niskiej pewności.

## Skąd pochodzą etykiety
- `cache/sgjp/oznaczenia.html`: `mors.` „morskie”, `żegl.` „żeglarskie”, `ryb.` „rybackie”, `roln.` „rolnicze”, `ogr.` „ogrodnicze”, `zootechn.` „zootechniczne”, `pszcz.` „pszczelarskie”, `leśn.` „leśnicze”, `mat.` „matematyczne”.
- `cache/sgjp-docs/instrukcja.html`: „mogą pojawić się kwalifikatory wskazujące dziedzinę, w której dany leksem jest używany”. Słowo „mogą” oznacza, że etykieta nie jest obowiązkowa.
- `cache/sgjp-docs/lexeme_export.py` (w. 139–149): kwalifikatory eksportu pochodzą z trzech tabel (`kwalifikatory_leksemow`, `kwalifikatory_odmieniasiow`, `kwalifikatory_zakonczen`). Etykiety dziedzin wiszą przy leksemie.
- `config/generator/sgjp-supplement.tab` (11 linii) nie ma etykiet dziedzin.
- Licencja SGJP: nagłówek eksportu, licencja 2-klauzulowa BSD („Redistribution and use … are permitted”). Szczegóły licencji opisuje zbieracz `code-docs` / `pan-resources`.
