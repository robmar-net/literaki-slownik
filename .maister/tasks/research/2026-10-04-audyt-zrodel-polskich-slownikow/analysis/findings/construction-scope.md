# Konstrukcje z segmentów — dowody do decyzji D3

## TL;DR

Jeden zapis ortograficzny może odpowiadać kilku jednostkom źródłowym.
Rozdzielamy obowiązkową fleksję od dodatkowych konstrukcji istniejących leksemów.
Rekomendujemy uwzględniać udokumentowane konstrukcje w głównych kandydatach po kontroli reguł; D3=A/C1 zatwierdzona przez użytkownika.

## Key Decisions

- D1=G1: BROAD i STANDARD z pełną dopuszczalną fleksją; D2=N1: SGJP/KWJP najpierw, NKJP po wyjaśnieniu warunków.
- Nowe dokumenty są źródłami objaśnień, nie listami wejściowymi. Wszystkie składniki przyszłej rekonstrukcji muszą pochodzić z dopuszczonego eksportu SGJP.
- To uzupełnienie audytu: pierwotny raport i jego manifest pozostają niezmienione. [Rejestr nowych dokumentów](construction-sources.json) zawiera URL, wersję, zakres i SHA256; PDF pozostają w ignorowanym cache.

## Open Questions / Risks

- D3=A/C1 rozstrzyga włączenie konstrukcji do głównych kandydatów; gotowość wykonawcza poszczególnych reguł pozostaje do wykazania.
- Nie zakończono macierzy wszystkich klas ani przeglądu ich kwalifikatorów. Dowód pisowni nie oznacza jeszcze przyjęcia do każdego wariantu.
- Mobilne końcówki, np. przy zaimkach/spójnikach, potrzebują osobnej kontroli. Niezgodność reguły z aktualną pisownią musi dawać jawny wynik, nie automatyczne sklejenie.

## Dowody bibliograficzne

[RJP PAN, tekst jednolity zasad](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf): §4.4.4 nakazuje łączny zapis przyimka z `-ń`; §4.6 obejmuje łączną pisownię `-że/-ż`, także ich połączenia. §4.5 rozróżnia formy z `by`: po spójnikach zapis rozdzielny, ale zachowuje odrębne wyrazy wymienione w regule. Samo podobieństwo budowy nie wystarcza do ujednolicenia pisowni.

[Podstawy teoretyczne SGJP, wydanie czwarte](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf): s.96–98 opisują `bym/byśmy` jako elementy trybu warunkowego mogące stać osobno. S.124 i §9.1, s.144, opisują przyimek z formą zaimka ON jako jeden zapis dwóch form wyrazowych, bez osobnego hasła dla całej konstrukcji. Lista zawiera również przypadki analogiczne; nie utożsamiamy jej z listą poświadczeń.

## Rozdzielone klasy i konsekwencje projektu

Poniższa kwalifikacja jest wnioskiem projektowym łączącym dokumentację z [wcześniejszym audytem eksportu i kodu](sgjp-rules.md). Nie wykonano nowego pomiaru liczebności ani generatora.

| Klasa | Przykład | Dowód techniczny | Konsekwencja |
|---|---|---|---|
| Pełne formy osobowe | `czytałem`, `czytałbym` | Już w eksporcie; kontrola `praet/cond` | Obowiązek pełnej fleksji; preferować rekordy źródłowe |
| Osobno zapisywany element trybu warunkowego | `bym`, `byśmy` | `segmenty.dat`, wiersze 136–140; składniki eksportu | Kontrola pokrycia wymaganej fleksji, bez nowej zgody produktowej |
| Przyimek z `-ń` | `przezeń`, `nań` | Wiersze 382–383; konieczne uzgodnienie tagów `ń` opisane w audycie | Kandydat D3: ślad obu składników, kontrola przypadka i wariantu przyimka |
| Rozkaźnik z partykułą | `czytajże`, `dajże` | Wiersze 334–345; warianty zależne od zakończenia | Kandydat D3: kontrolowane połączenie istniejących jednostek, nie swobodne doklejanie |
| Mobilna końcówka przy innym wyrazie | np. `jam`, `żeś` | Wiersze 142–185 wykazują ścieżki analizatora | Do dalszej weryfikacji klas; nie zatwierdzamy całości na podstawie kodu |
| Produktywne prefiksy, złożenia i tryb `permissive` | nowe leksemy lub dowolne połączenia | Ten sam plik zawiera szersze reguły analizatora | Wyłączone przez specyfikację; D3 tego nie zmienia |

Wiersze dotyczą przypiętego wydania Morfeusza 20260823; hash pliku reguł jest w [dotychczasowym rejestrze](sgjp-rules-sources.json). Dla rozkaźników liczba i zakończenie nie mogą być utożsamione bez kontroli wszystkich baz. Podwojone partykuły oraz rzadsze konstrukcje wymagają własnych przykładów dodatnich i ujemnych przed aktywacją.

## D3 — jeden wybór zakresu, odrębne reguły klas

| Opcja | Zakres | Koszt / korzyść |
|---|---|---|
| **A / C1 — rekomendacja** | Udokumentowane konstrukcje istniejących leksemów uwzględniamy w BROAD/STANDARD, zgodnie z filtrami każdego wariantu | Użytkownik gry otrzymuje kompletne zapisy; więcej reguł i kontroli przed odbiorem |
| **B / C2** | Dodatkowe konstrukcje badamy jako osobne rozszerzenie; podstawowi kandydaci mają jawnie węższą definicję | Mniejszy pierwszy zakres, dodatkowy zbiór do późniejszej oceny; wymaganej fleksji nie wolno odroczyć |
| **C / C3** | Odkładamy decyzję o włączeniu do czasu pełnej macierzy klas i skutków | Więcej informacji przed wyborem, późniejsze domknięcie projektu |

A oznacza wybór definicji słownika, a nie zatwierdzenie wszystkich ścieżek Morfeusza. W projekcie każda klasa ma własne warunki, źródła i status; nieznana semantyka pozostaje luką do wyjaśnienia. Jeżeli nie da się rozstrzygnąć klasy objętej przyjętym zakresem, końcowy wynik nadal nie spełnia kryterium G1. Nie zamieniamy wymaganej kontroli kompletności w arbitralne pominięcie.

## Zakres dostępu i ograniczenia

Zweryfikowano wskazane rozdziały dwóch oficjalnych PDF oraz istniejący kod reguł. Odczyt strony zbiorczej RJP przez narzędzie WWW zakończył się timeoutem; bezpośredni PDF odczytano i pobrano poprawnie. Wyszukiwarka zwróciła też źródła pomocnicze, lecz nie są podstawą tego uzupełnienia. Nie pozyskiwano danych benchmarku ani internetowej bazy haseł. Nowa dokumentacja nie rozstrzyga mieszanych kwalifikatorów ani całej polityki pisowni BROAD/STANDARD.
