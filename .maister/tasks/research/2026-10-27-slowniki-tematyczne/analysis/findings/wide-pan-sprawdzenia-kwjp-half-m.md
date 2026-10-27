# KWJP½M: czy `meta_topic` daje podkorpus tematyczny

## TL;DR
- `meta_topic` ma 777 z 5500 tekstów, czyli dokładnie wszystkie książki. 228 różnych wartości, głównie gatunki („powieść” 128 tekstów).
- Pasują: morze 3 książki, rolnictwo 2 (pszczelarstwo), matematyka 1. Tytuły czasopism dokładają „Namiary na Morze i Handel” (19) i „Pasieka” (10).
- Razem to bardzo mało: morze 1466 słów, rolnictwo 881, matematyka 400 (na 513 tys.).
- Rdzeń SGJP prawie się tam nie pojawia (morze 5 trafień, rolnictwo i matematyka 0). Teksty tematu niosą za to słowa podstawowe bez etykiety: `pszczół`, `pasieka`, `miodzie`, `jachtów`, `regat`.
- Wniosek: KWJP½M nie da podkorpusu tematycznego. Daje tylko słaby sygnał, że korpus dziedzinowy (Zadanie E, metoda 2) łapie to, czego brak w SGJP.

## Key Decisions
- Tekst = jeden plik JSON (pole `meta.id`). Próbki liczę z listy `samples`.
- Tekst tematu: `meta_topic` zawiera „morze”/„żeglar”, „pszczel”, „matematyka”, albo `meta_main_title` to „Namiary na Morze i Handel” lub „Pasieka”. Czasopisma dodałem, bo to też metadana tekstu.
- Rdzeń tematu = leksemy SGJP z etykietą (254 / 96 / 62; `local-data-sgjp-dziedziny.md`). Dopasowanie po formie, małe litery.
- Trafienie „jednoznaczne” = forma nie należy do żadnego leksemu SGJP spoza rdzenia tematu (np. `fok` odpada, bo to też forma `foka`).

## Open Questions / Risks
- Liczby są bardzo małe (5 trafień). Kierunek, nie miara.
- Słowa bez etykiety to lista słów specyficznych dla tekstów (≥2 razy w temacie, ≤1 raz poza nim), bez lematyzacji. Tylko przykład.
- Pełny KWJP ma w serwisie zakładkę „Texts”. Czy da się tam wybrać czasopisma typu „Pasieka” jako podkorpus, nie sprawdziłem. Pobrania tekstów serwis nie oferuje.

## Pobranie
- URL: https://github.com/ipipan/kwjp100-varia/raw/main/KWJP%C2%BDM/KWJP%C2%BDM_samples.tar.gz
- Rozmiar 2 860 455 B (zgodny z `cache/kwjp/tree.json`). SHA-256 `aedad77022508fe10d0d537e6a082884b8e7a97d4836a184ff744a5261db55b1`.
- Dostęp 2026-10-27. Licencja: CC BY 4.0 (README repozytorium).
- Lokalnie: `data/work/kwjp-half-m/dl/samples.tar.gz`, rozpakowane w `data/work/kwjp-half-m/x/samples/` (gitignore: `/data/work/`).
- Skrypty: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/pan2/` — `meta.py`, `titles.py`, `hits.py`, `keyness.py`; wyniki `*.out`.

## Metadane
5500 tekstów, 11 108 próbek, 513 009 słów (zgodnie z README).

Pola tekstu i ile tekstów ma je wypełnione: `meta_title` 5500, `meta_published` 5500, `meta_publisher` 5438, `meta_pubplace` 5401, `meta_author` 4878, `meta_main_title` 4819, `meta_issn` 4643, `meta_pubnumber` 4723, `meta_topic` 777, `meta_isbn` 777, `meta_first_published` 777, `meta_editor` 112. Do tego `meta_kwjp_type`, `meta_kwjp_channel`, `meta_label` (5500).

- `meta_kwjp_type`: publicystyka 3660, fakt 1215, fikcja 625.
- `meta_kwjp_channel`: dziennik 1957, tygodnik 1286, miesięcznik 962, książka 777, prasa inne 491, internet 27.
- `meta_topic`: pusty w 4723 tekstach; 777 wypełnionych = 777 książek. Najczęstsze: „powieść” 128, „fantastyka, opowiadania i nowele” 55, „powieść obyczajowa” 42, „antologia, kryminał, opowiadania i nowele” 41, „reportaż” 40, „polityka zagraniczna, raport” 38. Pełna lista: `meta.out`.
- `meta_main_title`: 139 wartości (tytuł czasopisma lub tomu). Tematyczne wśród nich: „Namiary na Morze i Handel” 19, „Pasieka” 10. Dla matematyki brak („Wiedza i Życie” 18 i „Programista” 20 są ogólne). Pełna lista: `titles.out`.

### Teksty tematu
| Temat | Źródło | Teksty | Próbki | Słowa |
|---|---|---:|---:|---:|
| Morze | `meta_topic`: „wspomnienia, morze, żeglarstwo”, „morze, żeglarstwo”, „reportaż historyczny, morze” | 3 | 14 | 583 |
| Morze | czasopismo „Namiary na Morze i Handel” | 19 | 19 | 883 |
| Rolnictwo | `meta_topic`: „poradnik, pszczelarstwo” | 2 | 10 | 474 |
| Rolnictwo | czasopismo „Pasieka” | 10 | 10 | 407 |
| Matematyka | `meta_topic`: „popularnonaukowe, matematyka” | 1 | 7 | 400 |

Inne zbliżone wartości (nie liczyłem jako temat): „popularnonaukowe: przyroda”, „wywiady, przyroda”, „ekologia”, „poradnik, kulinaria”; czasopisma „Dzikie Życie”, „Weranda Country”.

## Rdzeń SGJP w tekstach tematu i poza nimi
| Temat | Grupa | Słowa | Trafienia (wszystkie) | Jednoznaczne | na 1000 słów | Leksemy |
|---|---|---:|---:|---:|---:|---|
| Morze | temat | 1 466 | 6 | 5 | 3,41 | `armator` 3, `masowiec` 2 |
| Morze | reszta | 498 127 | 181 | 11 | 0,02 | `prom` 3, `cuma` 2, `trałowiec` 1 i in. (8) |
| Rolnictwo | temat | 881 | 0 | 0 | 0 | — |
| Rolnictwo | reszta | 498 712 | 292 | 0 | 0 | — |
| Matematyka | temat | 400 | 0 | 0 | 0 | — |
| Matematyka | reszta | 499 193 | 101 | 28 | 0,06 | `parametr` 10, `kwadratowy` 10, `współczynnik` 4 i in. (7) |

- Morze: w tekstach tematu rdzeń jest ok. 150 razy gęstszy, ale to 5 trafień i 2 leksemy.
- Rolnictwo: zero jednoznacznych trafień w całym KWJP½M. Rdzeń rolniczy jest za rzadki na ten korpus.
- Matematyka: jedna książka popularnonaukowa (o statystyce) nie ma żadnego słowa z rdzenia.

## Słowa tematu bez etykiety SGJP
Słowa ≥2 razy w tekstach tematu i ≤1 raz poza nimi (`keyness.py`):
- Rolnictwo (pszczelarstwo): `pszczół` 4, `pasieki` 3, `miodzie` 3, `pasieka` 2, `plastry` 2, `pszczele` 2, `pszczelich` 2, `odkładów` 2, `pasiekę` 2, `pasożyty` 2, `pszczelarza` 2.
- Morze: `masowców` 2, `przeładunków` 2, `statkowego` 2, `regat` 2, `łódka` 2, `jachtów` 2, `kontenerów` 2.
- Matematyka: brak.

To słowa podstawowe, których brak w rdzeniu SGJP (por. `ul`, `pasieka` bez etykiety w W4). Potwierdza to sens metody „korpus dziedzinowy”, ale nie ten korpus.
