# Dowód nazwy mieszkańca z jawnych odsyłaczy SGJP

## TL;DR
Publiczny czytnik zawiera dokładniejsze dowody niż etn.: jawne odsyłacze nazwy mieszkańca.
Warszawa wskazuje warszawianka; artykuł docelowy wskazuje odwrotnie miejscowość i męski odpowiednik.
Przed użyciem nowego rodzaju dowodu w kwalifikacji wymagane rozstrzygnięcie A/B.
Dane maszynowe i filtr pozostają nieaktywne; klasa nie jest kompletna.

## Key Decisions
- Norma2026 i reguły gry już zatwierdzone: nie pytamy ponownie o obowiązek wielkiej litery ani o zmianę zasad.
- Publiczny czytnik ujawnia semantyczną relację, której nie ma w pięciopolowym eksporcie. Dokładne znaczenie dokumentujemy własnym przeglądem, bez importowania całego słownika online.
- [Instrukcja SGJP](https://sgjp.pl/instrukcja/) zastrzega swobodę i niepełność odsyłaczy. Dodatni link może być dowodem użycia; brak linku nie jest dowodem nieprzynależności do klasy.
- Nie zakładamy, że pełne ID SGJP oznacza jedno znaczenie. Ocenę przypinamy do potwierdzonego użycia, zachowujemy nierozpoznaną pozostałość i homonimy.

## Open Questions / Risks
- Bramka pending: nowy rodzaj dodatniego dowodu semantycznego może zmienić ocenę analizy, więc nie został aktywowany.
- Metadane internetowe nadal nie są wejściem: brak ustalonej licencji maszynowego snapshotu i pełnej zgodności wersji.
- Publiczne filtry/odsyłacze nie zapewniają zamkniętej populacji wszystkich mieszkańców; G3 nadal otwarte.

## Konkretny przypadek i wpływ

Źródła: [Warszawa](https://sgjp.pl/leksemy/#7791/Warszawa), [warszawianka](https://sgjp.pl/leksemy/#61637/warszawianka). Bezpośredni odsyłacz jest oznaczony nazwą klasy mieszkańca; cel potwierdza pochodzenie od miejscowości. Pięciopolowy eksport dla pełnego ID warszawianka ma nazwa_pospolita i puste kwalifikatory: 11 kompaktowych interpretacji, 14 rozwinięć tagów, z dokładnymi wierszami/hashem w [własnej obserwacji](resident-relations-observation.json). Przyrost nie obejmuje nowych leksemów ani przepisywania źródłowych form.

Po A własny przegląd pozwoli przypiąć do tego udokumentowanego użycia istniejący warunek obowiązkowej wielkiej litery. Żeńska nazwa mieszkańca będzie oceniana tak samo jak zatwierdzony męski przypadek. Przykładowe odmienne zapisy pozostaną w bazie, bez lowercase omijającego regułę gry. Nie przenosimy tego na inne znaczenia ani inne słowa po sufiksie. Finalnej delty list nie deklarujemy, ponieważ pozostałe warunki i analizy pozostają unresolved.

## Wybór

**A — rekomendowane:** dopuścić jawny, ręcznie sprawdzony odsyłacz nazwy mieszkańca w SGJP jako dowód klasy konkretnego użycia. Własny przegląd wiąże źródłowy hash, pełne ID i rekordy, rodzaj relacji, oba artykuły i hashe odpowiedzi. Wdrożyć na pierwszym dokładnie sprawdzonym przypadku warszawianka; dalsze przypadki wymagają tej samej kontroli. Zachować pozostałość i brak kompletności klasy, bez maszynowej aktywacji metadanych online.

**B:** traktować odsyłacze tylko jako pomoc wyszukiwania; kwalifikacja wymaga dodatkowego, dosłownego opisu konkretnego użycia w dokumentacji. Obecna luka pozostaje unresolved, bez odrzucenia słowa z powodu braku dowodu.

## Kontrola odkrycia

Sprawdzono komplet17 definicji atrybutów w publicznej stronie oraz dostępne2 w czytniku: nie ma jawnego zamkniętego filtra mieszkańców ani filtrowania glosy. Nie wywodzimy braku danych w bazie z braku filtra UI. Repertuar relacji zawiera substhab/habsubst; artykuł Warszawa rzeczywiście pokazuje nazwaną relację. Odtworzenie parametrów API: pierwsze błędne żądanie wskazało query_params/exponent; poprawione anonimowe GET200 dało dokładny artykuł. Sandbox timeout25s, ponowienie poza sandboxem poprawne. Web.open nie obsłużył AJAX; nie uznano tego za brak danych. Surowe odpowiedzi wyłącznie tmp, własne obserwacje w repo.

## Przyczyna bramki

[AGENTS.md](../../../../../../AGENTS.md) wymaga: „Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem”. A rozszerza dopuszczony dowód semantyczny o jawne relacje czytnika. Skill maister-implementation-plan-executor wymaga: „At a material deviation or recovery decision […] ask […] and pause”. Dlatego wynik odczytu i projekt są gotowe, a filtr czeka na odpowiedź.
