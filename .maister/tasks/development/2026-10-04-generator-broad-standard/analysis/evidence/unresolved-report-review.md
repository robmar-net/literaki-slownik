# Raport niewiadomych zapisanych analiz

## TL;DR
Nowe build tworzą reports/unresolved.json. Raport obejmuje wszystkie zapisane oceny i niewiadome ukryte pod znaną odmową, osobno BROAD/STANDARD i całe słowa. Cztery testy red→green;160/160 generatora i5/5 audytu przeszły. Dwa rzeczywiste odczyty219713 analiz są identyczne i nie zmieniły bazy.

## Key Decisions
- Liczymy analizy, nie wspólne dokumenty powodów. Jeden powód w warstwie liczony raz dla danej analizy, nawet przy powtórzeniu checku.
- Powodów z membership nie liczymy ponownie: raport rozlicza language/game/profile/release_scope. Znana odmowa nie usuwa obecnych niewiadomych.
- Wynik słowa jest agregacją spójnych analiz: dopuszczony homonim zachowuje accept słowa mimo odrzucenia lub unresolved innej analizy.
- Raport odmawia brakujących wariantów/payloadów, niezgodnego SHA lub statusu. Bufor powodów ma limit256; przetwarzamy uporządkowany strumień i reguły jednego słowa, bez listy wszystkich analiz w pamięci.

## Open Questions / Risks
- To raport zapisanej diagnostyki, nie pełnego słownika. Full_qualification_pending i INCOMPLETE pozostają; reports nadal pending.
- Wersja zapisanej oceny pozostaje źródłem raportu. Bieżący kod explain i starszy snapshot ocen mają osobne wersje; nie nadpisujemy wcześniejszych build.
- Pełne G3/G4/G5/G6, raporty jakości/indeks i verify/export nadal wymagają domknięcia;8/36 bez zmian.

## Weryfikacja

[Runtime](unresolved-runtime.json): cała rzeczywista projekcja obecnych konstruktorów ma219713 analiz i213636 kluczy w każdym wariancie. BROAD:37809 odrzuconych analiz i181904 unresolved; STANDARD:61815 odrzuconych i157898 unresolved. Wszystkie analizy mają nadal niewiadome polityki; znane odmowy nie zacierają tych luk. Brak accept jest zgodny z diagnostycznym zakresem.

Dwa odczyty raportu zajęły41,604s, wliczając powtórzenie; hash bazy przed/po identyczny i mode=ro. Cztery testy: brak funkcji→implementacja; brak pliku build→integracja; sprawdzono współdzielone payloady, dwa homonimy jednego klucza, powtórzone warunki, odmowę/unknown równocześnie, zmieniony hash/status, brak wariantu/payloadu i dwa identyczne build. Nie promowano gotowości.160/160testów generatora,5/5audytu; preflight14wejść i10konfiguracji po policyv10 OK.
