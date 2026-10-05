# Przegląd znaczeń PAN — pełna inwentaryzacja frag

## TL;DR
Rejestr obejmuje wszystkie 147 kompaktowych analiz frag z przypiętego SGJP, zgodne z wcześniejszą pełną inwentaryzacją: 109 małoliterowych i 38 z wielką literą.
64 przypadki mają alternatywne analizy napisu w SGJP, 108 ma kandydatów w listach KWJP, 62 ma trafienia w publicznych próbkach; 39 nie ma trafień w obu tych rodzajach materiałów.
Wstępny odczyt kontekstów ujawnił homonimię, cytaty obcojęzyczne i części zapisów z łącznikiem. Nie nadano automatycznych werdyktów znaczeniowych ani growych.
Dwa odtworzenia identyczne; baza źródłowa bez zmian; 152/152 testów przeszło. Pełna klasyfikacja i inne wyjątki pozostają otwarte.

## Key Decisions
- Inwentaryzacja zawiera pełne ID, tag, nazwy, kwalifikatory i wszystkie numery surowych wierszy. Inne interpretacje zachowują odrębne znaczenia i pisownie.
- NFC/lower służy wyłącznie wyszukiwaniu kandydatów. Dowód tekstowy nie jest przypisany automatycznie do konkretnego ID/homonimu ani do reguły gry.
- Przeszukano wszystkie 13 dopuszczonych list KWJP, wszystkie 5500 plików publicznych próbek oraz pełne źródłowe rekordy SGJP dla alternatywnych analiz. Listy mają kontrolę SHA256, baza kontrolę przypiętego source_id/hash metadanych.
- Bibliografia próbek i rekordy list są zapisane raz i wskazywane przez przypadki. Nie kopiujemy całych tekstów do Git. Dopasowanie tekstowe nie rozbija zapisu z łącznikiem na pozornie osobne słowa.
- Żaden nowy filtr, leksykalne wejście generatora ani kryterium dopuszczalności nie zostały aktywowane. Kontakt z innymi grupami pozostaje wykluczony.

## Open Questions / Risks
- Wszystkie 147 przypadków nadal mają semantic_status=unresolved: zebrano kandydatów na dowody, nie kompletną tabelę znaczeń. Wstępnie przeczytano pierwszy kontekst każdego z 62 przypadków z trafieniami; nie rozstrzygnięto indywidualnie wszystkich 1141 powiązań z próbkami.
- 39 przypadków bez trafień wymaga innych dostępnych dowodów SGJP/PAN. Brak użycia w próbce/listach nie oznacza błędności, obcości lub niedopuszczalności.
- Należy przejrzeć rzeczywiste glosy/uwagi SGJP. Publiczny HTML strony haseł nie zawiera żądanych wartości glos, a narzędzie UI zgłosiło brak dostępnej przeglądarki. Nie pobierano chronionych endpointów redakcyjnych ani całej internetowej bazy. Ta droga pozostaje dostępnościowo nieukończona.
- Nie zinwentaryzowano tu nazw mieszkańców ani wszystkich innych wyjątków znaczeniowych; PAN-1 jako cały etap pozostaje częściowy. Nie zadeklarowano wpływu na finalne listy ani odbioru G3/G8.

## Co pokazuje wstępny odczyt
- oścież/wznak: konteksty KWJP pokazują polskie połączenia z na; nie należy odrzucać wszystkich frag za samo wymaganie kontekstu. oścież ma ponadto odrębną interpretację rzeczownikową.
- jam: pierwsze trafienie to polskie zdanie z formą Jam, a lista bigramów zawiera też jam session oraz Pearl Jam. Są to różne użycia napisu; nie przypisujemy cytatu automatycznie do frag.
- bin: pierwszy odczytany kontekst jest niemiecką wypowiedzią, a bigramy pokazują także człon nazwiska. Samo wystąpienie w polskim korpusie nie dowodzi polskiego samodzielnego znaczenia.
- Las/Los/koń/kole/ziem/przemian: pierwsze trafienia należą do zwykłych polskich użyć napisu i nie dowodzą konkretnej interpretacji frag. SGJP zachowuje inne analizy.
- Addis/San/Phnom/Penh/Wall: odczytane konteksty pokazują wielowyrazowe nazwy. Inne trafienia, np. Rio/Rico, dotyczą osób, co dodatkowo pokazuje granicę dopasowania po napisie.
- pro: wstępny tokenizer błędnie potraktował pro-Jelcynowską jako trafienie osobnego pro. Dodano regresję red→green wyłączającą składniki zapisu z łącznikiem; wcześniejszych plików diagnostycznych nie nadpisano.

## Odtworzenie i dowody
[Pełny rejestr](pan-semantic-cases.json) obejmuje także 13 969 unikalnych rekordów list i bibliografię 844 plików próbek z trafieniami. [Pokrycie i kontrola](pan-semantic-coverage.json) zawiera hashe, równość odtworzeń i hash bazy źródłowej przed/po.

Komenda z głównego katalogu repo; cel musi być nowym plikiem:

```sh
python3 scripts/probe_pan_semantics.py --database data/work/import-20261004-1302/build.sqlite --samples tmp/kwjp-halfm-samples.tar.gz --sources config/generator/sources.json --output tmp/pan-frag-cases-new.json
```

Skrypt jest narzędziem przeglądu G3, nie nową komendą generatora. Ścieżki są jawne, źródła i próbki zgodne z [wcześniejszym przeglądem](pan-data-recheck.md). Dopasowanie list zachowuje źródło, wiersz i oryginalną częstość; nie sumuje ich między gatunkami ani nie przenosi na homonim. Status unresolved dotyczy klasyfikacji znaczeniowej, nie nowej decyzji o błędności wszystkich wpisów.

## Następna praca
Przejrzeć konteksty i ich zgodność z konkretnymi interpretacjami, zaczynając od oścież/wznak i niejednoznacznych jam/bin. Potem sprawdzić pozostałe dowody dla 39 przypadków bez trafień oraz glosy SGJP, gdy dostępny będzie ich odczyt. Osobno zinwentaryzować nazwy mieszkańców obu rodzajów. Dopiero rozstrzygnięcia z wykazanym wpływem przekazywać do omówienia i G4.

## Pełna lista przypadków
Liczby w kolumnach odnoszą się do kandydatów dowodowych, nie znaczeń ani werdyktów. Alternatywy obejmują także zapis różniący się wielkością liter. Każdy przypadek w rejestrze zachowuje source_id i numery wierszy.

| Forma | Pełny ID | Inne analizy SGJP | Rekordy list KWJP | Trafienia w próbkach |
|---|---|---:|---:|---:|
| Addis | Addis | 0 | 17 | 1 |
| Ata | Ata:F | 2 | 15 | 0 |
| Banja | Banja | 0 | 11 | 0 |
| Ben | Ben:F | 2 | 89 | 2 |
| Buenos | Buenos | 0 | 38 | 2 |
| Burkina | Burkina | 0 | 19 | 0 |
| Cruz | Cruz | 0 | 26 | 2 |
| Faso | Faso | 1 | 13 | 0 |
| Francisco | Francisco:F | 1 | 41 | 1 |
| Janeiro | Janeiro | 0 | 18 | 1 |
| La | La | 3 | 242 | 24 |
| Las | Las:F | 6 | 722 | 17 |
| Le | Le:F | 5 | 141 | 6 |
| Leone | Leone | 0 | 19 | 1 |
| Los | Los:F | 4 | 771 | 26 |
| Manche | Manche | 0 | 13 | 0 |
| Marino | Marino:F | 3 | 17 | 0 |
| Mont | Mont | 0 | 24 | 1 |
| Monte | Monte | 0 | 48 | 1 |
| Mount | Mount | 0 | 33 | 1 |
| New | New | 1 | 154 | 10 |
| Paulo | Paulo | 1 | 23 | 0 |
| Penh | Penh | 0 | 16 | 1 |
| Phnom | Phnom | 0 | 21 | 1 |
| Plata | Plata:F | 5 | 19 | 0 |
| Rico | Rico | 0 | 19 | 3 |
| Rio | Rio | 0 | 67 | 4 |
| Saint | Saint:F | 2 | 38 | 1 |
| San | San:F | 3 | 105 | 4 |
| Sankt | Sankt | 0 | 34 | 2 |
| Santa | Santa | 0 | 53 | 3 |
| Sao | Sao | 0 | 20 | 0 |
| Sierra | Sierra | 1 | 38 | 0 |
| Sri | Sri | 0 | 24 | 0 |
| Street | Street | 0 | 81 | 4 |
| Tel | Tel | 1 | 36 | 6 |
| Vegas | Vegas | 0 | 32 | 3 |
| Wall | Wall:F | 3 | 41 | 2 |
| bajduś | bajduś | 0 | 0 | 0 |
| bałyku | bałyku | 2 | 0 | 0 |
| bezcen | bezcen | 0 | 23 | 0 |
| bezdurno | bezdurno | 1 | 0 | 0 |
| bin | bin | 0 | 48 | 3 |
| bździu | bździu | 0 | 0 | 0 |
| chrapickiego | chrapickiego | 1 | 0 | 0 |
| ciup | ciup:F | 5 | 14 | 0 |
| cna | cna | 2 | 16 | 4 |
| cyku | cyku | 3 | 0 | 0 |
| czwórnasób | czwórnasób | 0 | 0 | 0 |
| dala | dala | 0 | 27 | 12 |
| dawien | dawien | 0 | 14 | 0 |
| de | de:F | 1 | 603 | 53 |
| del | del | 1 | 89 | 4 |
| derdy | derdy | 4 | 0 | 0 |
| don | don | 1 | 98 | 2 |
| dubelt | dubelt:F | 1 | 2 | 0 |
| dwóchnasób | dwóchnasób | 0 | 0 | 0 |
| dwójnasób | dwójnasób | 0 | 14 | 0 |
| dyrdum | dyrdum | 0 | 0 | 0 |
| dyrdy | dyrdy:F | 5 | 0 | 0 |
| dziejski | dziejski | 0 | 0 | 0 |
| dzieju | dzieju | 0 | 13 | 0 |
| dziesięćnasób | dziesięćnasób | 0 | 0 | 0 |
| eleison | eleison | 0 | 16 | 0 |
| elemele | elemele | 0 | 0 | 0 |
| fiksum | fiksum | 0 | 0 | 0 |
| friko | friko | 0 | 13 | 0 |
| hopla | hopla:F | 2 | 11 | 0 |
| ibn | ibn | 0 | 41 | 1 |
| ichmość | ichmość:F | 1 | 0 | 0 |
| jako | jako:F | 4 | 5487 | 562 |
| jam | jam | 3 | 35 | 1 |
| kilkanasób | kilkanasób | 0 | 0 | 0 |
| kole | kole | 11 | 15 | 1 |
| koń | koń:F | 4 | 392 | 8 |
| kroćset | kroćset | 0 | 0 | 0 |
| ledwością | ledwością | 0 | 8 | 0 |
| lelum | lelum | 0 | 8 | 0 |
| mać | mać:F | 2 | 67 | 2 |
| mimo | mimo:F | 4 | 1352 | 176 |
| mniejsza | mniejsza | 1 | 12 | 8 |
| mocia | mocia | 0 | 0 | 0 |
| mociu | mociu | 0 | 0 | 0 |
| mocium | mocium | 0 | 13 | 0 |
| mości | mości | 10 | 19 | 3 |
| mościa | mościa | 1 | 4 | 0 |
| mąż | mąż:F | 1 | 957 | 51 |
| młodu | młodu | 0 | 22 | 2 |
| naprzeciwka | naprzeciwka | 0 | 28 | 0 |
| niemiara | niemiara | 0 | 16 | 1 |
| niwecz | niwecz | 1 | 13 | 0 |
| oddala | oddala | 1 | 12 | 4 |
| odlew | odlew:F | 1 | 29 | 0 |
| odpierdol | odpierdol | 1 | 12 | 0 |
| odtrąbiono | odtrąbiono | 1 | 8 | 0 |
| owąd | owąd | 0 | 0 | 0 |
| oścież | oścież:F | 2 | 26 | 2 |
| oślep | oślep | 1 | 33 | 2 |
| polelum | polelum | 0 | 8 | 0 |
| pomimo | pomimo:F | 2 | 297 | 28 |
| porząsiu | porząsiu | 0 | 0 | 0 |
| porącz | porącz | 0 | 0 | 0 |
| pro | pro | 0 | 99 | 6 |
| propos | propos | 0 | 24 | 1 |
| przemian | przemian | 1 | 33 | 11 |
| razą | razą | 0 | 0 | 0 |
| rozcież | rozcież:F | 2 | 0 | 0 |
| roścież | roścież:F | 2 | 0 | 0 |
| rydy | rydy | 0 | 0 | 0 |
| schwał | schwał | 0 | 17 | 0 |
| session | session | 0 | 25 | 0 |
| siam | siam | 1 | 10 | 0 |
| sir | sir:F | 1 | 46 | 2 |
| siu | siu | 0 | 0 | 0 |
| skroś | skroś:F | 4 | 9 | 0 |
| spół | spół | 1 | 0 | 0 |
| szwady | szwady | 0 | 0 | 0 |
| trochu | trochu | 0 | 19 | 1 |
| troszeczku | troszeczku | 0 | 6 | 0 |
| troszku | troszku | 0 | 9 | 0 |
| trymiga | trymiga | 0 | 12 | 0 |
| trójnasób | trójnasób | 0 | 13 | 0 |
| van | van:F | 1 | 137 | 6 |
| vice | vice | 0 | 33 | 1 |
| von | von | 0 | 226 | 17 |
| waj | waj | 0 | 9 | 0 |
| wespół | wespół | 0 | 30 | 2 |
| wewte | wewte | 0 | 15 | 0 |
| wskroś | wskroś:F | 1 | 29 | 1 |
| wskróś | wskróś:F | 1 | 0 | 0 |
| wte | wte | 0 | 22 | 0 |
| wykol | wykol | 0 | 8 | 0 |
| wykole | wykole | 0 | 6 | 0 |
| wyprzodki | wyprzodki | 0 | 0 | 0 |
| wyprzody | wyprzody | 0 | 0 | 0 |
| wyprzód | wyprzód | 0 | 0 | 0 |
| wyprzódki | wyprzódki | 0 | 8 | 0 |
| wznak | wznak | 0 | 24 | 2 |
| wścieżaj | wścieżaj | 0 | 0 | 0 |
| wściąż | wściąż | 0 | 0 | 0 |
| zacz | zacz:F | 2 | 13 | 0 |
| zamian | zamian | 2 | 62 | 23 |
| ziem | ziem | 2 | 12 | 8 |
| łupnia | łupnia:F | 1 | 8 | 0 |
| ścież | ścież | 1 | 0 | 0 |
| ścieżaj | ścieżaj | 0 | 0 | 0 |
| ściężaj | ściężaj | 0 | 0 | 0 |
