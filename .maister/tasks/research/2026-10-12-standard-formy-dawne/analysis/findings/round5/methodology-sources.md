# Kalibracja POP: metodologia i źródła

## TL;DR

Porównanie 60/70/80 tys. sprawdza koszt większej listy; nie rozstrzyga samo, która granica jest właściwa.
Drugim porównaniem powinien być stały próg obecnej miary, a trzecim jawna siatka częstości i rozproszenia.
Rozmiar, pokrycie i ocena słów z różnic muszą być pokazane osobno. Nie mierzymy znajomości słów przez Polaków.
Wszystkie warianty są badawcze; nie ustalono nowej granicy ani zmiany metody.

## Key Decisions

- Zachować wspólne dane i `pop-v2` w porównaniu limitów. Osobno mierzyć zmianę granicy, zmianę kryterium i zmianę STANDARD.
- Zachować pełną odmianę, jawność homonimów i statusów braku danych. Częstość nie przechodzi automatycznie na każdy sens lub członka grupy.
- Nie importowano zewnętrznych list znajomości, Jasnopisu ani Logios. Publikacje służą ocenie metody, nie dostarczają słów do POP.

## Open Questions / Risks

- Nie ma empirycznego progu, który sam zmienia częstość lub rozproszenie w „słowo znane”. Nowe progi też wymagają uzasadnienia i przeglądu.
- KWJP opisuje redagowaną polszczyznę pisaną 2011–2020; nie rozstrzyga całej mowy potocznej ani zmian po 2020. NKJP pomaga, lecz ma starsze teksty i inną reprezentację danych.
- ARF/DP nie dają się odtworzyć dla dowolnej sumy homonimów z samych zagregowanych wierszy. Ocena agentów nie jest badaniem reprezentatywnej grupy graczy.

## Dowód: co ustalono wcześniej

Przeczytano [specyfikację POP](../../../../../development/2026-10-11-slowniki-pop-pop0/implementation/spec.md), [ADR-007](../../../../../../../docs/adr/ADR-007-metoda-pop-v1.md), [mapowanie KWJP](../../../../../../../docs/generator/mapowanie-kwjp.md), [ADR-006](../../../../../../../docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md), konfigurację, parser KWJP i właściwe funkcje `pop.py`.

Stare porównanie 60/80 tys. w [dodatku raportu pomiaru](../../../../../development/2026-10-11-slowniki-pop-pop0/analysis/pop-measure-report.md) używało percentyli i `available-only`, przed obecną oceną log-ipm i przycinaniem członków. Nie może rozstrzygać dzisiejszego porównania. Późniejsze rewizje miały przeglądy próbek: ADR odnotowuje m.in. 420 ocen dla rewizji 1 oraz 410 dla rewizji 2. Nie jest prawdą, że metoda nigdy nie była walidowana. Brakuje aktualnego porównania granic na obecnej metodzie, a nie całej historii kontroli.

## Dowód: dostępne miary i ich zakres

Dostęp do poniższych źródeł: **2026-10-12**. Metryki dostępu, ograniczenia oraz hashe lokalnych wejść są w [rejestrze JSON](methodology-sources.json).

| Źródło lub miara | Co można z niego odczytać | Czego nie dowodzi |
|---|---|---|
| KWJP100 | 100 mln słów; 35% publicystyki, 35% faktu, 30% fikcji; lata 2011–2020 | Reprezentacji rozmów i internetu |
| `F`, `ipm` | Liczbę wystąpień jednostki i częstość na milion w danym mianowniku | Znajomości przez odsetek osób |
| `ARF` | Częstość skorygowaną o skupienie wystąpień | Liczby niezależnych autorów ani zgodności sensu |
| `DP`, `DP_norm` | Nierównomierność względem części korpusu; większa wartość oznacza większe skupienie | Popularności niezależnej od częstości i podziału korpusu |
| `1-DP` | Odwrotną skalę DP: wyższa wartość oznacza bardziej równomierny rozkład | Tożsamości z `1-DP_norm` |
| Obecność w 1–3 gatunkach | Szerokość gatunkową na bardzo zgrubnym poziomie | Liczby dokumentów, autorów ani różnorodności znaczeń |

Opis zakresu: [IPI PAN — KWJP](https://kwjp.pl/overview). Definicje i próg publikacji: [dokumentacja list](https://kwjp.pl/lists/doc/about/). Definicje DP i normalizacji: [Gries 2020, s. 103–104](https://stgries.info/research/2020_STG_Dispersion_PHCL.pdf).

Próg `F≥5` dotyczy całego KWJP; podzbiór gatunkowy może mieć `F=1–4`. Listy powstały z automatycznej anotacji i mogą zawierać błędy. Zapytania dotyczą segmentów: część polskich słów pisanych łącznie zostaje rozbita. Zgodność lemat/POS nie rozpoznaje sensu. Źródła: [listy KWJP](https://kwjp.pl/lists/doc/about/), [instrukcja KWJP](https://kwjp.pl/manual), [segmentacja Korpusomatu](https://korpusomat.readthedocs.io/pl/latest/mtas.html), lokalne mapowanie.

**Kontrola własna wszystkich wierszy dwóch plików:** `1-DP = 1 − DP` w 184 917 wierszach `lemma-all` i 164 651 `lemma-fakt`; nie jest to `1 − DP_norm` (tolerancja 10⁻⁷). W `fakt` 49 474 wiersze mają `F<5`. Suma F w `all` to 81 664 894 i tego mianownika używa obecne `pop.py` w log-ipm. Nie należy wstawić w jego miejsce umownych 100 mln. Kolumna `total_freq` jest częstością danej jednostki w całości, nie rozmiarem korpusu. Wejścia i algorytm kontroli: [JSON](methodology-sources.json); kod: `literaki_slownik/kwjp.py`, `pop.py:kwjp_measures/_log_ipm_sources`.

[N-gramy NKJP](https://zil.ipipan.waw.pl/NKJPNGrams) pochodzą ze zrównoważonego podkorpusu 300 mln tokenów. Unigram to małoliterowy fragment między białymi znakami; zasób daje zapis i liczbę. Nasz plik nie ma rozkładu po dokumentach, gatunkach, latach ani sensach. Korpus NKJP obejmuje także rozmowy i internet ([opis projektu](https://nkjp.pl/)), ale ta cecha korpusu nie pozwala odzyskać takich kategorii dla każdego unigramu. Warunki użycia pozostają zgodne z ADR-006, bez publikacji surowych danych NKJP.

## Dowód: rozkład ARF/F i kontrola pierwszej sondy

Sprawdzono **184 917 oryginalnych wierszy lemma-all**, bez łączenia ich miar. To cała lista, także nazwy własne i jednostki spoza STANDARD; nie jest to wynik filtracji POP.

| F | Wiersze | Mediana ARF/F | 1. percentyl | ARF/F < 0,1 |
|---|---:|---:|---:|---:|
| 5–9 | 57 677 | 0,5500 | 0,1250 | 0 |
| 10–29 | 55 196 | 0,5350 | 0,0537 | 2244 |
| 30–99 | 34 939 | 0,5345 | 0,0246 | 1309 |
| 100–299 | 18 714 | 0,5246 | 0,0289 | 420 |
| 300–999 | 10 738 | 0,5046 | 0,0711 | 142 |
| 1000–9999 | 6718 | 0,4727 | 0,1639 | 33 |
| ≥10 000 | 935 | 0,4875 | 0,2348 | 0 |

Mediana całej listy wynosi 0,53; 1. percentyl 0,0556. Tylko 4148 wierszy (2,24%) ma ARF/F < 0,1. Korelacja Pearsona log10(F) z log10(ARF/F) wynosi −0,0269. **Nie wykazano globalnej katastrofy skalowania tego ilorazu z F.** Widać jednak problem niskich częstości: przy F=5–9 nawet ARF bliskie 1 daje iloraz powyżej 0,1. Sam iloraz nie wystarcza jako miara siły dowodów.

W oryginalnych wierszach ARF≥3 przechodzi 157 939 pozycji, a ARF≥3 wraz z ARF/F≥0,1 — 157 071. Takie wyniki nie wyjaśniają same w sobie olbrzymiego spadku pierwszej sondy POP. Wykryto w niej dwa problemy:

- `round5_measure.py` pobierał własny rekord tylko z `member_units`. Jednostki jednoelementowe nie mają tam podjednostki, więc trafiały błędnie do `unknown` mimo własnego KWJP.
- W agregatach `member_units/_kwjp_entry` ARF pochodzi z najlepszego wiersza, podczas gdy F może być sumą. Ich iloraz nie jest dyspersją całego agregatu.

Zgłoszono oba problemy koordynatorowi. Pierwszego wyniku — 17 894 leksemów, 391 166 form i 9168 braków straży — **nie wolno interpretować jako dowodu przeciw ARF lub dyspersji**. Koordynator przyjął korektę: własne oryginalne wiersze, w tym jednoelementowe jednostki; jawne OR wierszy bez transferu między różnymi podstawami lematu. Ten przegląd nie zmienia skryptu ani nie zastępuje jego ponownego pomiaru.

**Zalecana siatka badawcza:** ARF≥{1,1; 2; 3; 5; 10}, ARF/F≥{0; 0,01; 0,03; 0,1; 0,3}. Zero znaczy brak warunku ilorazu. Kontrole 0,001 i 0,003 są dopuszczalne, lecz w całej liście wycinają odpowiednio 0 i 3 wiersze. Dodatkowy próg własnego F, np. {5; 10; 30}, należy raportować osobno. Są to szerokie sondy wrażliwości, nie granice poparte badaniem znajomości.

Porównać wariant wymagający KWJP z wariantem zachowującym bazowe przyjęcie 80k, jeśli brakuje własnego wiarygodnego wiersza KWJP. Ten drugi sprawdza wpływ dyspersji tam, gdzie można ją ocenić; nie nazywa braku dowodu spełnieniem warunku. W obu policzyć osobno odrzucenia przez F, ARF, iloraz, mapowanie i brak własnych danych. Rozkłady, 42 kombinacje ARF/ilorazu i algorytm: [JSON](methodology-sources.json).

## Dowód: częstość, rozproszenie i znajomość

- **Adelman, Brown, Quesada (2006):** w analizach czasu nazywania i decyzji leksykalnej różnorodność dokumentów wyjaśniała wynik ponad częstość. To motywacja do kontroli rozproszenia; badanie nie wyznacza polskiego progu POP ani nie utożsamia ARF z odsetkiem znających słowo. Odczytano abstrakt i metodę/wyniki w [wersji autorów](https://wrap.warwick.ac.uk/399/1/WRAP_Adelman_cdps4.pdf).
- **Gries (2020):** częstość i dyspersja są odrębnymi wymiarami. Ich mechaniczne scalenie ukrywa różne profile użycia; próg dyspersji wymaga zewnętrznego uzasadnienia. Nie wynika z tego zakaz badania ARF, lecz potrzeba pokazania składowych i przypadków rozbieżnych. Odczytano definicje oraz dyskusję na [s. 103–104 i 111–114](https://stgries.info/research/2020_STG_Dispersion_PHCL.pdf).
- **Brysbaert i in. (2019):** badanie oddziela częstość od rozpowszechnienia znajomości mierzonego u ludzi. Wniosku o znajomości nie wolno zastąpić samym pokryciem tokenów. Wykorzystano wyłącznie [abstrakt w repozytorium autorów](https://biblio.ugent.be/publication/8647817); pełny tekst ograniczony do UGent. Nie pobrano norm ani listy słów.
- **Hlaváčová (2006):** ARF ma precedens w budowie słownika frekwencyjnego. [Abstrakt autorski w ACL](https://aclanthology.org/L06-1006/) uzasadnia porównanie takiego wariantu, nie konkretny próg dla polszczyzny. Próba pobrania PDF przez URL ACL zwróciła błąd; nie opieramy na niej szczegółów wzoru.

## Rekomendacja: warianty do porównania

Poniższe są propozycjami badawczymi, nie zaakceptowanymi kryteriami produktu.

| Wariant | Definicja i cel | Warunek uczciwego porównania |
|---|---|---|
| A: 60/70/80 tys. | Obecny `pop-v2`, zmienia się tylko limit POP | Te same grupy, miary i reguły; jawne leksemy przed/po przycięciu oraz graniczne remisy |
| B: stała minimalna wartość miary | Jednostka ma `score≥τ`; rozmiar wynika z danych | Ten sam τ na obu STANDARD; własna ocena członka również względem τ; jawny wyjątek najmocniejszego członka |
| C: częstość oraz rozproszenie | Własny dowód KWJP spełnia `F≥f` i `DP_norm≤d` albo jawnie wybrany warunek ARF | Ta sama jednostka dowodu; mała ustalona siatka f,d; osobna kategoria braków i homonimów |

**A** jest najprostszą odpowiedzią na pytanie, co daje większy limit. **B** oddziela minimalną siłę obecnej miary od liczby konkurentów. Nie usuwa zależności od grupowania ani problemów mieszania źródeł. Przy obu korpusach waga 0,5 średniej log-ipm odpowiada logarytmowi średniej geometrycznej częstości; `single_source` i `bound:kwjp` mają inną podstawę dowodową. Dlatego wynik B trzeba rozbić według tych statusów. To wniosek z `pop.py:measure`, nie psychometryczna interpretacja skali.

Dla **C** rekomenduję najpierw dwuwymiarowy raport i ocenę rozbieżnych przypadków. ARF/F może być wskaźnikiem skupienia, lecz samo wysokie ARF/F przy małym F nie daje mocnego dowodu. Warunek „co najmniej 2 gatunki” warto pokazać jako osobną analizę wrażliwości; nie narzucać go bez przeglądu słów słusznie ograniczonych tematycznie. Każdą liczbową siatkę trzeba oznaczyć jako eksperyment. Literatura nie uzasadnia uniwersalnego `F=30`, `DP_norm=0,9` ani 70 tys. leksemów.

ARF i DP zachować przy oryginalnym wierszu. `pop.py:kwjp_measures` sumuje F, ale inne miary bierze z wiersza o największym F. To nie jest dyspersja całej grupy. Połączenie kilku wierszy wymagałoby rozkładu wystąpień po tych samych częściach korpusu; sama suma ARF czy średnia DP go nie odtworzy.

## Rekomendacja: pomiar i interpretacja

1. Dla obu STANDARD policzyć rozmiar w jednostkach, leksemach przed/po przycięciu i formach, pełne różnice oraz stabilność składu. Próg wartości może ograniczyć rotację wynikającą z limitu, ale nie gwarantuje monotoniczności przy zmianie grup.
2. Pokazać pokrycie `kwjp-all` oraz `kwjp-standard` z jawnymi mianownikami. Drugie ma zmienną populację przy zmianie STANDARD; porównanie potrzebuje również stałego zbioru odniesienia. Pełne odmiany nie zwiększają automatycznie znanej masy korpusowej.
3. Rozbić wyniki według własnego/wspólnego dowodu, `EXACT_CANDIDATE`/`AMBIGUOUS`, źródła, imputacji, przycięcia i wyjątku najmocniejszego członka. `EXACT_CANDIDATE` znaczy jedno dopasowanie strukturalne, nie potwierdzony sens.
4. Próbki losować osobno z pasm 60–70, 70–80, poza 80 oraz z różnic A/B/C. Ocenić również słowa tracone, nie tylko dodatki. Ukryć przed oceniającym wariant/rangę; zapisać lemat, znaczenie, rejestr, właściwy dowód i niepewność. Kontrole znanych problemów zachować osobno od próby losowej. Nie uogólniać prostego odsetka ze zróżnicowanych warstw bez wag.

**Pokrycie tokenów nie jest trafnością listy.** Dominują w nim częste jednostki; niewielki zysk może towarzyszyć tysiącom sensownych dodatków albo tysiącom słabych. Liczenie rankingu i pokrycia z tej samej KWJP daje pomiar dopasowania do tych danych, nie niezależny test. Potrzebne są również oceny marginalnych słów i przypadków pozostawionych poza listą. To interpretacja celu POP i konstrukcji `pop.py:coverage`.

**Braki nie są zerem.** Brak opublikowanego KWJP, błąd mapowania, segmentacja, brak NKJP i nieprzypisywalność przez homonimy mają różne powody. Surowy próg własnego F bez ścieżki dla tych przypadków wytnie również prawidłowe słowa. Z drugiej strony dane grupy nie dowodzą wszystkich jej sensów. Proponuję raportować takie przypadki osobno i zachować je w próbce, zamiast ukrywać za imputacją lub automatycznym usunięciem. Podstawa: lokalne mapowanie, ADR-007 D5/D8, kod `units/member_units/measure`.

## Zakres wykonania

Ukończono przegląd metodologii i wymaganych typów źródeł. Nie wybrano zwycięskiego wariantu bez wyników pomiarów i ocen próbek. Nie pobierano list znajomości ani dodatkowych zbiorów słów; nie zmieniano produkcji, stanu zadania, konfiguracji ani publikacji. Dostępne abstrakty wykorzystano tylko do twierdzeń zawartych w abstraktach; ograniczenia dostępu zapisano jawnie.
