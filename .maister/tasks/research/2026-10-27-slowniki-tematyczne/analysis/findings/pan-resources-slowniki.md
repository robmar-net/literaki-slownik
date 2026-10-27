# Zasoby PAN: słowniki (SGJP, Kuźnia, WSJP)

## TL;DR
- SGJP ma kwalifikatory dziedzinowe: `mat.`, `roln.`, `mors.`, `żegl.`, `ryb.` i ok. 75 innych. Są w eksporcie tab, który projekt już ma. Licencja: BSD-2.
- WSJP (IJP PAN) ma dwie osobne warstwy: 90 kwalifikatorów specjalistycznych i klasyfikację tematyczną każdego znaczenia (ponad 160 tys. znaczeń).
- WSJP nie ma eksportu, API ani licencji. Jest tylko „Copyright © IJP PAN”. Danych WSJP nie możemy brać hurtowo.
- Kwalifikator dziedzinowy oznacza termin specjalistyczny, a nie temat. Zwykłe słowa z tematu (np. „sos”, „grypa”) zwykle go nie mają. Lista z kwalifikatorów będzie więc wąska.

## Key Decisions
- Główne źródło dziedzin w PAN to SGJP. Dane już mamy, a licencja jest znana (BSD-2).
- WSJP traktujemy tylko jako punkt odniesienia: ręczne sprawdzenie próbki w przeglądarce. Nie bierzemy z niego danych, bo brak licencji.

## Open Questions / Risks
- W SGJP nie ma znanej liczby leksemów na kwalifikator. Policzy ją zbieracz local-data z `sgjp-20260823.tab.gz`.
- Strona `oznaczenia` ma `astr.` i `fotogr.`. Dane projektu mają też `astron.`, `kolej.` i `fot.` (wg `sources.md`, `unmapped_atoms`). Repertuar w danych jest więc szerszy niż strona.
- Kuźnia nie ma pliku licencji w repozytorium. Kod tylko czytamy.
- Klasyfikacja tematyczna WSJP nie ma pola „matematyka” ani „morze”. Najbliżej są „Ilość, liczby i liczenie” oraz „transport wodny”.

## SGJP (IPI PAN, sgjp.pl)

**Jaka informacja o dziedzinie.** Kwalifikatory przy leksemie. Instrukcja mówi o nich wprost: „kwalifikatory wskazujące dziedzinę, w której dany leksem jest używany” (przykład: `muz.` przy *solmizować*).
Źródło: https://sgjp.pl/instrukcja/ (dostęp 2026-10-27).

**Kwalifikatory dla trzech tematów** (https://sgjp.pl/oznaczenia/, dostęp 2026-10-27; kopia lokalna `cache/sgjp/oznaczenia.html`):

| Temat | Kwalifikatory SGJP |
|---|---|
| marynistyka | `mors.` morskie, `żegl.` żeglarskie, `ryb.` rybackie, `flis.` flisackie, `hydrol.` hydrologiczne |
| rolnictwo | `roln.` rolnicze, `ogr.` ogrodnicze, `pszcz.` pszczelarskie, `zootechn.` zootechniczne, `wet.` weterynaryjne, `leśn.` leśnicze |
| matematyka | `mat.` matematyczne (blisko: `fiz.`, `komp.`) |

Uwaga: SGJP ma `mors.`, a nie `mor.`.

**Ile kwalifikatorów.** Na stronie oznaczeń jest ok. 77 skrótów dziedzinowych. To moje liczenie, bo strona nie oddziela dziedziny od stylu ani języka. Do granicznych należą np. `szkol.`, `term.` i `bibl.`.

**Typy w kodzie.** Model Kuźni ma trzy typy kwalifikatorów: `styl` (stylistic), `zakr` (scope) i `form` (at forms). Ma też „klasy wykluczania” (`QualifierExclusionClass`).
Źródło: `cache/sgjp-docs/kuznia-models-61daf78.py:99-117`.
To, że kwalifikatory dziedzinowe mają typ `zakr`, jest tylko wnioskiem z nazwy. Nie sprawdziłem tego.

**Filtr po kwalifikatorze.** Jest w formularzu leksemów. Instrukcja wymienia go wśród kryteriów: „Pozostałe kryteria zamknięte: Typ wzoru, Pospolitość, Kwalifikator”. Kilka wybranych wartości działa jak alternatywa (OR). Można też włączyć kolumnę „kwal.”. Lista ma „Eksport aktualnie filtrowanej listy”.
Źródła: https://sgjp.pl/instrukcja/ i https://sgjp.pl/leksemy/ (dostęp 2026-10-27).
Pobranie przez WebFetch nie pokazało samego filtra, bo formularz działa w JS. Format eksportu nie jest opisany.

**Ile haseł ma kwalifikator.** Strona tego nie podaje (`https://sgjp.pl/w-liczbach/` zwraca 404).

**Dostęp.** Eksport tab z Morfeusza (już w `cache/sgjp/`) i eksport listy z formularza.

**Licencja.** Licencja BSD, wersja dwuklauzulowa: „The program including contained linguistic data is hereby released under the conditions of the so called 2-clause BSD License”. Autorzy danych SGJP: Saloni, Gruszczyński, Woliński, Wołosz, Skowrońska. Stopka: „Copyright © Instytut Podstaw Informatyki PAN, 2014–2026”.
Źródła: https://morfeusz.sgjp.pl/doc/license/ (dostęp 2026-10-27) oraz `cache/sgjp-docs/license.html`.

**Status.** Aktywny: „Wydanie IV online, Warszawa 2020”, eksport z 2026-08-23 w cache.

## Kuźnia (IPI PAN)

- Co to jest: „Narzędzie do tworzenia słowników fleksyjnych” (Django + PostgreSQL). Repozytorium ma 885 commitów.
  Źródło: https://git.nlp.ipipan.waw.pl/SGJP/Kuznia (dostęp 2026-10-27).
- Informacja o dziedzinie: tabele `kwalifikatory` i `kwalifikatory_leksemow`. Eksport (`lexeme_export.py`) dokleja kwalifikatory jako `string_agg(kwal, '|')` i umie wykluczać leksemy z wybranym kwalifikatorem (`excluding_qualifiers`).
  Źródło: `cache/sgjp-docs/lexeme_export.py:82-150, 215-223`.
- Licencja: na stronie repozytorium nie ma żadnej.
- Wniosek: Kuźnia nie daje nowych danych. Wyjaśnia tylko, skąd biorą się kwalifikatory w eksporcie tab.

## WSJP — Wielki słownik języka polskiego PAN (IJP PAN, wsjp.pl)

**Jaka informacja o dziedzinie.** Dwie niezależne warstwy:
1. **Kwalifikatory specjalistyczne.** Lista 2.7.6.1 ma 90 kwalifikatorów jednodziedzinowych (moje liczenie z PDF). Do tego dochodzą 3 wielodziedzinowe: `kultur.`, `nauk.` i `techn.`. Formularz wyszukiwania pokazuje ok. 88 kwalifikatorów jednodziedzinowych (bez `mason.`).
2. **Klasyfikacja tematyczna.** Trzy poziomy: sfera, pole i podpole. „Do odpowiedniego pola tematycznego zakwalifikowane jest każde znaczenie hasła”, z wyjątkiem wyrazów funkcyjnych. Obejmuje „ponad sto sześćdziesiąt tysięcy jednostek (znaczeń)” (stan na koniec 2025).

Źródło: *WSJP PAN — Zasady opracowania*, wyd. 9, luty 2026, rozdz. 2.7.6 i 2.8, s. 36–48: https://pliki.wsjp.pl/zasady_opracowania_wsjp.pdf (dostęp 2026-10-27).

**Kwalifikatory dla trzech tematów** (ta sama lista 2.7.6.1):

| Temat | Kwalifikatory WSJP | Pola tematyczne WSJP |
|---|---|---|
| marynistyka | `żegl.` żeglarstwo, `ryb.` rybołówstwo | „transport wodny”, „zbiorniki wodne”, „zwierzęta wodne” |
| rolnictwo | `roln.` rolnictwo, `agr.` agronomia, `ogrod.`, `zootechn.`, `pszcz.`, `wet.` | „rolnictwo”, „rośliny uprawne”, „zwierzęta domowe i hodowlane” |
| matematyka | `mat.` matematyka, `log.` logika, `metrol.` | brak pola „matematyka”; najbliżej „Ilość, liczby i liczenie” |

Źródła pól: https://wsjp.pl/slownik_tematyczny i https://wsjp.pl/szukaj/zaawansowane (dostęp 2026-10-27).

**Kwalifikator to nie temat.** Zasady mówią: „Należy więc ściśle odróżnić kwalifikację specjalistyczną od klasyfikacji tematycznej […] Nie każdy więc wyraz związany z danym polem tematycznym ma odpowiedni kwalifikator.” Przykład: *sos* nie ma kwalifikatora, a *glazura 3.* ma `kulin.`. Podobnie *grypa* nie ma `med.`, a *nadwzroczność* ma (s. 37 i 47).
Dla nas to ważne: lista z samych kwalifikatorów obejmie terminy, ale pominie zwykłe słowa tematu. Ta sama logika dotyczy SGJP.

**Próbka.** Hasło *kliwer*: kwalifikator `żegl.`; temat CZŁOWIEK I TECHNIKA → Transport → transport wodny. Kwalifikator i temat są przypisane do znaczenia, nie do całego hasła.
Źródło: https://wsjp.pl/szukaj/podstawowe/wyniki?szukaj=kliwer (dostęp 2026-10-27).

**Ile haseł.** „liczba opracowanych haseł osiągnęła 100 tysięcy” (styczeń 2026).
Źródło: https://wsjp.pl/page/historia (dostęp 2026-10-27).
Strona nie podaje liczby haseł na kwalifikator ani na pole.

**Dostęp.** Tylko przeglądarka (wyszukiwanie zaawansowane z filtrem po kwalifikatorze i po kategorii tematycznej) oraz aplikacje mobilne. Strona nie podaje eksportu ani API. Link `https://wsjp.pl/haslo/json` z dołu strony zwraca 404.

**Licencja.** Żadna nie jest podana. Jest tylko stopka „Copyright© Instytut Języka Polskiego PAN” i polityka prywatności. Słownik jest „udostępniany bezpłatnie w Internecie”, ale to darmowy dostęp, nie licencja.
Źródła: https://wsjp.pl/jak_korzystac i https://wsjp.pl/page/historia (dostęp 2026-10-27).
Wniosek: pobieranie hurtowe lub skrobanie danych bez zgody nie wchodzi w grę. Kontaktu z autorami nie podejmujemy (zasada projektu).

**Status.** Aktywny, finansowany z NPRH na lata 2024–2026, nowe hasła na bieżąco.

## Kandydaci spoza PAN
- Słowosieć / plWordNet (Politechnika Wrocławska): domeny leksykalne synsetów; licencja „plWordNet license” (typu WordNet), do sprawdzenia.
- Wikisłownik: kwalifikatory dziedzinowe; CC BY-SA. Odroczony decyzją użytkownika.
