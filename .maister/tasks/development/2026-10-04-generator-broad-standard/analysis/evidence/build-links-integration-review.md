# Integracja powiązań KWJP z build

## TL;DR
Build tworzy teraz powiązania bezpośrednich form i leksemów oraz raport links.json.
Częstości pozostają przy jednej jednostce korpusu, także dla wielu homonimów.
106 testów generatora i 5 testów historycznego audytu przechodzi.
Pełne powiązania konstrukcji oraz końcowe wydanie pozostają nieukończone.

## Key Decisions
- Użyto istniejącego create_links/link_report po materializacji potwierdzonych kandydatów. Brak nowej kwalifikacji językowej, list słów lub wejść.
- Nie przypisano częstości korzenia do nowej konstrukcji. Pełny etap links pozostaje pending do wykonania wszystkich wymaganych relacji G5.
- Awaria zapisuje failed na links; ukończone importy i wcześniejsze ślady nie są wycofywane.
- Test explain korzysta z rzeczywistego build z syntetycznym korpusem, zamiast ręcznie dopisywać dane po build. Odczyt explain nie zmienia hashy manifestu ani bazy.

## Open Questions / Risks
- To integracja technicznego podzbioru G5, nie pełny odbiór grupy ani nowe pełne przebiegi G8.
- Pozostałe konstrukcje, ich relacje, finalne decyzje i pełne raporty jakości pozostają wymagane.

## Weryfikacja
Dwa nowe testy miały red po poprawieniu fikstury do rzeczywistego formatu gzip/CSV KWJP: brak evidence_link i brak integracji create_links. Następnie green. Pierwszy szkic fikstury miał błędną rolę i nagłówek; nie traktujemy tej odmowy preflight jako właściwego red funkcjonalności.

Regresja starego testu explain ujawniła próbę ponownego utworzenia relacji już zbudowanych przez build. Przeniesiono przygotowanie korpusu przed build, zachowując wszystkie dotychczasowe asercje. 28 testów build/links/explain oraz cała suita 106/106 i baseline 5/5 przeszły. Test integracyjny sprawdza dwie jednostki (AMBIGUOUS i UNMATCHED), dwie krawędzie dla homonimów, sumę F=12 liczoną raz, FK oraz pending/INCOMPLETE i raport czasu. Drugi sprawdza zachowanie importu po awarii powiązań. Existing full-links-report.json i full-links-performance.json pozostają wcześniejszym pełnym dowodem samego modułu, bez przypisywania im nowego pełnego build.
