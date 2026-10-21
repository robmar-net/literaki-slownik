Pierwsze wydanie **POP00**: **259 779 form**, **13 896 leksemów** odziedziczonych z POP0 pop-v3.
O 128 984 formy mniej niż POP0 (33,18%). Każdy wybrany leksem zachował co najmniej jedną formę.

Metoda [pop00-v1 / ADR-009](https://github.com/robmar-net/literaki-slownik/blob/pop00-v1/docs/adr/ADR-009-pop00-v1.md):
- chroniona zwykła odmiana, także bez pełnego zapisu w liście korpusowej;
- nijaka pierwsza/druga osoba odpada jako analiza; druga zachowana analiza może uratować napis;
- wybrane grupy imiesłowów, zaprzeczonych gerundiów, stopniowania i konstrukcji wymagają co najmniej 0,1 IPM dokładnego zapisu KWJP orth/all;
- POP00 ⊆ POP0 ⊆ STANDARD. To słownik znajomości; integracja z grą jest osobnym zadaniem.

| zostaje | odpada |
|---|---|
| kotach, czytajcie, zrobiłem, byłam, bym | remontowałoś, przeczytałobym |
| czytany, najmilszy, nieczytanie | czytanymi, najmilszemu, nieczytaniami |

Kontrola: **461 testów**, dwa niezależne przebiegi z identycznymi bajtami wszystkich 11 plików,
pełny diff względem zatwierdzonej sondy 0/0, niezależny kontroler odtwarzający decyzje z bazy
oraz **891 pozycji technicznego przeglądu** z indywidualnymi śladami źródłowymi.

Pliki:
- POP00.txt.gz — posortowana lista UTF-8, małe litery, jedna forma w wierszu;
- pop00-v1-pakiet.tar.gz — lista, pełne decyzje dla wszystkich form POP0, podsumowanie, próbka, manifest, atrybucje, warunki i ograniczenia;
- pop00-v1-review.json — przegląd techniczny związany hashami z tym pakietem;
- release-manifest.json i SHA256SUMS — tożsamość kodu/źródeł i sumy plików;
- SHA256SUMS-rozpakowane — hash listy po rozpakowaniu.

SHA256 rozpakowanego POP00.txt: 332739e84a9ab4391c5cc14c2dd668eedbb960fab8251f4d2f71c4ab5bd76ad7.

**Ograniczenia:** próg i podział form są pierwszą zatwierdzoną polityką. Odpadają też poprawne,
zrozumiałe, lecz rzadkie odmiany. Brak wiersza KWJP nie oznacza częstości zero.
Przegląd techniczny nie jest badaniem znajomości słów przez graczy; nie zmierzono wpływu na partie.

Formy SGJP zachowują BSD-2-Clause z pełną atrybucją. KWJP: CC BY 4.0; wybór leksemów
odziedziczono z POP0, także z jego warunkami NKJP (CC BY, wersja nieokreślona, ADR-006).
Surowe dane NKJP nie są dołączone. Pełne zawiadomienia i opis zmian w ATTRIBUTIONS.md i TERMS.md pakietu.

[Wiki POP00](https://github.com/robmar-net/literaki-slownik/wiki/Slownik-POP00) · [Zadanie #10](https://github.com/robmar-net/literaki-slownik/issues/10)
