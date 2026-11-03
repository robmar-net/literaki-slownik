# docs: zasady doboru haseł SGJP

## TL;DR
SGJP nie ma listy kryteriów doboru haseł. Ma tylko zasady ogólne: hasła z wybranych słowników (przede wszystkim Doroszewski), z około miliarda słów z tekstów i z decyzji redaktorów. Słowo ma być „powtarzalne”. Zapożyczenie wchodzi, jeśli „dostatecznie często” powtarza się w tekstach z ostatnich lat. Terminy wchodzą „w pewnym zakresie”.
Nigdzie nie ma reguły, która wykluczałaby słownictwo anatomiczne, seksualne albo medyczne. SGJP ma kwalifikatory `anat.`, `med.`, `fizjol.`, `wulg.` i `euf.`.
„Wulw” w SGJP to nazwisko. Nazwiska weszły ze słownika Rymuta opartego na PESEL, gdy noszą je co najmniej 50 osoby jednej płci. Z rzeczownikiem pospolitym to nazwisko nie ma związku.
Eksport pomija leksemy o statusie `cand` (kandydat) i `litt` oraz leksemy ze słownika `antyMorfeusz`. Czy „wulwa” jest w bazie Kuźni z takim statusem, nie da się sprawdzić lokalnie.

## Kluczowe decyzje
- Za źródło zasad przyjęto *Podstawy teoretyczne SGJP*, wyd. 4 (2020; wersja 2021.01.11), plik `cache/constructions/sgjp-theory.pdf`. Strony to numeracja druku, a tekst wyciągnięto przez `gs -sDEVICE=txtwrite`, bo `pdftotext` nie jest zainstalowany.
- Kod eksportu (`cache/sgjp-docs/lexeme_export.py`, `kuznia-models-61daf78.py`) potraktowano jako źródło dokumentacji tego, co trafia do TSV.

## Otwarte pytania
- Kryterium częstości jest jakościowe („dostatecznie często”). Progu liczbowego dla wyrazów pospolitych nie podano. Liczbowy próg jest tylko dla nazwisk: 50 nosicieli.
- Nie wiadomo, czy „wulwa” jest w Kuźni jako `cand` albo w `antyMorfeusz`. Publiczny eksport tego nie pokazuje. To sprawa dla zbieracza `external` (sgjp.pl).
- *Podstawy* opisują wydanie z 2020 roku. Zasad wydania 20260823 nie opisano osobno: `release.html` to tylko lista plików.

## Ustalenia

### 1. Źródła materiału (§1.2, s. 9–10)
- Słowniki: „Prace wstępne zostały przeprowadzone już w latach osiemdziesiątych XX wieku na materiale SJPDor. Potem do zasadniczego zbioru zostały wprowadzone — **w wyborze** — leksemy z innych słowników polskich” (Szymczak, ISJP Bańki, USJP Dubisza, NSO Polańskiego, SWJP Dunaja). (s. 9)
- Teksty: „około miliarda słów tekstowych … przede wszystkim z materiałów prasowych … (braliśmy stamtąd tylko teksty reprezentujące zadowalający poziom językowy …)”. Z tekstów weszły „m.in. jednostki, które na ogół nie występują w słownikach ogólnych: skróty i skrótowce oraz nazwy własne”. (s. 9)
- Korpusy: korpus PWN, korpus IPI PAN, a przy wyd. II NKJP. (s. 9)
- „Niektóre jednostki słownikowe zostały wprowadzone z naszej inicjatywy na podstawie własnego doświadczenia językowego.” (s. 10)
- **Wniosek:** obecność w SGJP zależy od tego, czy słowo jest w słownikach źródłowych, i od wyboru redakcji. Jeśli wyraz jest rzadki w prasie i nie ma go w Doroszewskim, łatwo wypada. Nie sprawdzono tutaj, czy „wulwa” jest w Doroszewskim lub w słownikach PWN; to zadanie zbieracza `external`.

### 2. Zakres: wyrazy rzadkie i terminy (§1.1, s. 7)
- SGJP obejmuje „główny zrąb współczesnego słownictwa polskiego, z uwzględnieniem wyrazów rzadkich … a **w pewnym zakresie** także jednostek charakterystycznych dla określonych środowisk, przede wszystkim zawodowych, oraz **terminów z różnych dziedzin**”.
- „Celem … jest podanie charakterystyki gramatycznej wyrazów polskich. Obejmuje on ponad 450000 leksemów”. (s. 7)
- **Wniosek:** terminologia wchodzi tylko wybiórczo. Brak terminu medycznego nie jest więc niczym wyjątkowym.

### 3. Kryterium „słowa polskiego” i zapożyczeń (§1.3.3, s. 12–13)
- „Trudno tu sformułować wyraźną procedurę … tendencja jest tu zupełnie wyraźna: słowa polskie powinny występować częściej i być powtarzalne … O tym, który ciąg takich znaków jest polskim słowem, decyduje uzus”. (s. 12)
- Zapożyczenia: „Dajemy w SGJP takie jednostki, jeśli spełniają warunek **dostatecznie częstej powtarzalności**. Wypada tu jednak dodać zastrzeżenie: muszą się powtarzać **w tekstach ostatnich lat**.” (s. 13)
- W przypisie 7 redakcja przyznaje, że decyzje „były niejednokrotnie bardzo trudne”. (s. 12)
- **Wniosek:** „wulwa” to zapożyczenie z łaciny w spolszczonej pisowni. Według tych zasad wchodzi, jeśli jest częste w tekstach. To najlepiej udokumentowane możliwe wyjaśnienie braku: niska frekwencja. Liczby ma podać zbieracz `local`.

### 4. Słowa obce i cytaty (§9.2, s. 145)
- Słowa obce zakwalifikowano „na podstawie naszego **subiektywnego wyczucia**, nie ma bowiem wyraźnej granicy między wyrazem zapożyczonym i już należącym do języka polskiego i wyrazem cytowanym”. Przykłady: *checker, lamentoso, passim, quarto, sic*. (s. 145)
- **Wniosek:** to dotyczy pisowni *vulva*. Pisownia *wulwa* jest spolszczona, więc pod regułę cytatu nie podpada.

### 5. Skróty specjalistyczne (§8.1, s. 142)
- „Pominęliśmy natomiast skróty specjalistyczne, nawet rozumiane, ale niewystępujące poza zastosowaniami specjalistycznymi”. (s. 142)
- To jedyna jawna reguła „pomijamy, bo specjalistyczne”. Dotyczy tylko skrótów, nie rzeczowników.

### 6. Nazwisko „Wulw” (§3.3.2, s. 43–44)
- Źródłem jest „Słownik nazwisk używanych w Polsce na początku XXI wieku Kazimierza Rymuta, oparty o dane … PESEL … Do SGJP włączyliśmy wszystkie nazwiska, które są wyraźnie powtarzalne, tj. mają co najmniej 50 nosicieli jednej płci”. (s. 44)
- **Wniosek:** „Wulw” to osobna ścieżka doboru, niezależna od rzeczownika pospolitego. Z obecności nazwiska nie wynika nic o pominięciu „wulwy”.

### 7. Kwalifikatory dziedzin i rejestru (`cache/sgjp/oznaczenia.html`)
- Lista oznaczeń zawiera `anat.` („anatomiczne”), `med.` („medyczne”), `fizjol.` („fizjologiczne”), `wulg.` („wulgarne”) i `euf.` („eufemistyczne”).
- `cache/sgjp-docs/instrukcja.html`: w artykule „mogą pojawić się kwalifikatory wskazujące dziedzinę, w której dany leksem jest używany (np. muz. …), lub jego nacechowanie stylistyczne”.
- **Wniosek:** SGJP opisuje słownictwo anatomiczne i wulgarne. Nigdzie nie udokumentowano, że pomija temat ciała czy seksualności.

### 8. Co trafia do eksportu TSV (kod)
- `cache/sgjp-docs/lexeme_export.py:78–80`: domyślnie `'vocabs': ['SGJP']`, `'antivocabs': ['antyMorfeusz']`.
- `lexeme_export.py:206` i `:307`: `exclude(status__in=Lexeme.HIDDEN_STATUSES)` oraz `l.status not in ('cand', 'litt') and not l.usuniety`.
- `cache/sgjp-docs/kuznia-models-61daf78.py:290–300`: `STATUS_CANDIDATE = 'cand'`, `STATUS_LITTER = 'litt'`, `HIDDEN_STATUSES = (STATUS_CANDIDATE, STATUS_LITTER)`.
- **Wniosek:** eksport może nie mieć leksemu, który w bazie jest, jeśli to kandydat, odpad albo wpis z `antyMorfeusz`. Tak było z „się”/„siebie” (zob. `docs-korpusy-slowosiec-precedensy.md`). Dla „wulwy” to hipoteza do sprawdzenia na sgjp.pl.

### 9. Czego nie udokumentowano
- Nie ma żadnej zasady o słownictwie medycznym, anatomicznym ani seksualnym.
- Nie ma liczbowego progu frekwencji dla wyrazów pospolitych.
- Nie ma listy słowników, z których wybierano terminy medyczne.
- `cache/constructions/rjp-2026.pdf` (Zasady pisowni RJP): w treści nie ma „wulw”/„vulv”. Grep po „zapożycz” i „termin” nie dał reguły o tym rzeczowniku.
