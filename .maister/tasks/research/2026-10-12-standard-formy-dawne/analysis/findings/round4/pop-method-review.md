# Niezależny przegląd mechanizmu POP

## TL;DR

**2430 ubytków z POP jest spójnym skutkiem obecnego progu, bez wykazanego błędu implementacji.**
2422 formy wypadają z blokiem remisu, a 8 przez ocenę członka grupy; dowody i miary pozostają bez zmian.
`dekagram` był w POP0 dzięki wyjątkowi dla najmocniejszego członka; cofnięcie `dag` rozbija grupę.
Jego własna miara już wcześniej nie wystarczała do POP0. To zależność metody, nie spadek popularności.

## Key Decisions

- Rekomendacja: zachować obecne limity i pełne remisy; cofnięcia rozstrzygnąć osobno.
- Rozliczono wszystkie 2430 ubytków oraz ślad `dag` → `dekagram`; zachowanie jest zgodne z kodem i ADR-007.
- Poprawiono zakres kontrolnego eksperymentu KWJP. Wszystkie 25 uruchomionych testów przeszły; nie zmieniano kodu, konfiguracji ani list.

## Open Questions / Risks

- Czy właściciel akceptuje wyjątek utrzymujący najmocniejszego członka poniżej własnego progu? To decyzja o definicji POP, odrębna od współczesności STANDARD.
- Jeżeli przegląd zmieni paczkę, trzeba przeliczyć jej deltę; 2430 ubytków dotyczy dokładnie 2382 dodatków. Końcowy przegląd pozostawił ten zbiór bez zmian.
- Przegląd korzysta z pomiarów koordynatora. Testy nie dowodzą trafności definicji popularności, a audyt nie przypisuje znaczenia każdemu wystąpieniu `dag`.

## Dowody i zgodność z metodą

Przeczytano `AGENTS.md`, ADR-007, `config/generator/pop.json`, ścieżkę `load_forms` → `units` → `measure` → `threshold` → `member_units`/`prune_members` → `forms_for` i produkcyjne `_build_pop`.
Sprawdzono też testy rankingu, grupowania, brakujących danych, wariantów lematu i przycinania członków.

- Reguła (i) bierze wszystkie analizy zapisu dopuszczonego w STANDARD. Nie wymaga przyjęcia każdej z tych analiz. To jawna decyzja D2, nie przypadkowe pominięcie filtra.
- `form_owners` obejmuje również analizy odrzucone i nazwy własne. D5e łączy właścicieli obserwowanej formy tylko wtedy, gdy wszyscy należą do dopuszczonej populacji.
- `PROPER_SHARED` obejmuje dowolnego właściciela spoza tej populacji; nazwa statusu nie oznacza, że dany przypadek zawiera nazwę własną.
- Limit 60 000/20 000 liczy leksemy przed przycinaniem członków. Blok identycznej miary musi wejść w całości. Lista nie ma gwarantowanej liczby form ani monotonicznego wzrostu.
- Najmocniejszy członek wybranej grupy może zostać mimo własnej miary poniżej progu. ADR-007 opisuje ten wyjątek wprost.

## Pełne 2430 ubytków

Źródło: [pop-losses.json](pop-losses.json), odtworzenie opublikowanej bazy i całej delty rundy 3.

| Mechanizm | Członkowie | Utracone formy | Co się zmieniło |
|---|---:|---:|---|
| Cały blok remisu poza progiem | 111 w 108 jednostkach | 2422 | Ranga względem granicy; jednostki i ich miary bez zmian |
| Przycięcie `wypełzły` w grupie z `wypełznąć` | 1 | 8 | Własna ranga 45030 → 45060; miara bez zmian |

Obie kategorie form są rozłączne i wyczerpują 2430 ubytków. Wszystkie 111 pierwszych członków miały i mają miarę −1,042878629.
Tę samą wartość ma własna miara `wypełzły`.
Próg jednostek przeszedł z rangi 45137 do 45059. Po zmianie zostało 91 miejsc, a kolejny blok potrzebuje 116 leksemów.
Przed zmianą wchodziło 59 991 leksemów; po zmianie 59 909. Liczby te dotyczą etapu przed przycinaniem.

**Interpretacja:** to przesunięcie granicy przy stałym limicie i nierozdzielaniu remisów. Nie wykazano utraty danych, zmiany częstości tych leksemów ani niezamierzonego dzielenia remisu.
Sama rotacja nie uzasadnia zmiany progu. Nie dowodzi też, że wszystkie słowa poza granicą są mało znane.

## `dag` → `dekagram`

Źródło: [dag-mechanism.json](dag-mechanism.json); scenariusz usuwa tylko `dag` z bazowego STANDARD.

1. `dag` należy w bazie do `daga` i `dekagram`. Jego obecność w STANDARD daje leksemowi `daga` jedyną formę kwalifikującą do populacji rankingu.
2. Obserwowane `dag` w NKJP łączy `daga` i `dekagram`. Grupa ma rangę 10311, więc mieści się w POP0 (próg 11638).
3. Własna miara `dekagram` to 0,017383523, ranga 21474. Sama nie wystarcza. Członek zostaje jako najmocniejszy w wybranej grupie. `daga` jest z POP0 przycięta.
4. Cofnięcie `dag` usuwa `daga` z populacji. Grupa przestaje istnieć. Obcy właściciel wspólnej formy nadaje jednoelementowemu `dekagram` status `PROPER_SHARED`; miara opiera się tylko na KWJP.
5. Miara wynosi nadal 0,017383523, teraz z rangą jednostki 21476. `dekagram` i 9 jego pozostałych form zostają w POP oraz STANDARD, ale wypadają z POP0.

Kontrola z zamrożoną populacją rankingu, lecz usuniętą formą `dag`, usuwa z obu list wyłącznie `dag`.
Potwierdza to zależność od kwalifikacji leksemu i grupowania. Zamrożenie jest tu eksperymentem, nie rekomendacją produkcyjną.

Kontrole samej punktacji KWJP oraz całkowitego wyłączenia NKJP dają po cofnięciu `dag` brak delty POP0 i tylko −`dag` w POP.
W obu `dekagram` był poza POP0 już przed cofnięciem. Pełna kontrola bez NKJP ma własny, inny skład list; nie należy porównywać jej rang wprost z bazową metodą mieszaną.

## Kontrola skryptu badawczego

`analysis/round4_pop.py` odtwarza zasadniczą produkcyjną ścieżkę dla obecnej konfiguracji. Asercje sprawdzają pełne zbiory bazowe, delty rundy 3 oraz pokrycie wszystkich ubytków.
Klasyfikacja ubytku według jednostki i miary jest trafna dla obecnego wyniku; kontrola zbiorów potwierdza brak nakładania kategorii.

Zgłoszono wcześnie jeden błąd opisu kontroli: zmiana samego `d3.source` na KWJP nadal pozostawiała grupy budowane z NKJP.
Taki eksperyment izoluje **punktację KWJP przy topologii NKJP**, a nie pełne wycofanie NKJP. Koordynator rozdzielił obie kontrole.
Odczytano poprawiony skrypt oraz obie sekcje wyniku. `kwjp_full_control` przekazuje `nkjp=None` do grupowania i oceny członków; zapisane ślady mają status `NOT_APPLICABLE`. Zgłoszony problem jest rozwiązany; nie znaleziono dalszego błędu obliczeń w sprawdzanej ścieżce.
Nie dotyczy to scenariusza głównego, cofnięcia `dag` ani zamrożonej populacji.

Uruchomiono 25 istniejących testów: `PopRankingTests`, `PopPruneTests`, `VariantPoolTests`, `SharedDominantTests`, `AsymmetricBoundTests`, `NkjpOutdatedTests`. Wszystkie przeszły (2026-10-12).
Nie zmieniano kodu, konfiguracji, progów ani list.

## Rekomendacja do decyzji

1. Utrzymać obecny limit i regułę pełnych remisów dla oceny dodatków. Po ewentualnym zawężeniu paczki trzeba przeliczyć jej rzeczywistą deltę; obecne 2430 dotyczy dokładnie propozycji 2382 form.
2. Decyzję o cofnięciach, w tym `dag`, oddzielić od przyjęcia nowych form. Obecne zachowanie nie dowodzi błędu, ale pokazuje cenę wyjątku „najmocniejszy członek”.
3. Jeśli ta zależność jest nieakceptowalna, przed implementacją porównać jeden ograniczony wariant dotyczący kwalifikacji grup lub tego wyjątku na pełnej populacji. Wymaga to decyzji metodologicznej i przeglądu zysków/strat, również częstych słów z niejednoznacznymi dowodami. Nie dobierać reguły wyłącznie do `dekagram`.

Nie rekomenduję automatycznej unii ze starą listą, zamrażania starej populacji ani podnoszenia limitu do wielkości potrzebnej dla wybranego przykładu.

## Ograniczenia przeglądu

- To niezależny przegląd rozumowania i kodu, ale z użyciem danych pomiarowych koordynatora; nie jest drugim niezależnym odtworzeniem całej bazy.
- Testy sprawdzają zaimplementowaną metodę. Nie potwierdzają automatycznie trafności jej definicji popularności.
- Audyt nie rozstrzyga, które znaczenie wytworzyło każde wystąpienie `dag` w korpusie. Zależność algorytmu od wspólnego zapisu jest potwierdzona bez takiego założenia.
- Nazwy statusów i rangi grup mogą zaciemniać różnicę między dowodem własnym a wynikiem odziedziczonym po grupie. W omówieniu należy tę różnicę pokazać.
