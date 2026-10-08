# Literaki — słownik

**[Wiki projektu](https://github.com/robmar-net/literaki-slownik/wiki)** opisuje w skrócie, jakie słowniki tworzymy, jak filtrujemy słowa i skąd je pobrać.

Dopiero rozpoczynamy prace nad tym projektem. Na razie nie wiemy, co uda się osiągnąć — będziemy stopniowo sprawdzać możliwości i rozwijać pomysł.

Pierwsze prace dotyczą audytu źródeł do słowników języka polskiego: SGJP dla Morfeusza, KWJP100 i unigramów NKJP. Audyt sprawdza pochodzenie, warunki użycia, formaty oraz możliwości zbudowania odtwarzalnego procesu. Nie jest jeszcze gotowym słownikiem.

- [Specyfikacja projektu v3](docs/literaki-niezalezne-slowniki-prompt-v3.md) — materiał wejściowy i zakres pierwszego etapu w rozdziale 15.
- [Prosty język i minimum leksykalne — dalsze kierunki](docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md) — notatka rozpoznawcza o słownikach znajomości; opisane dane pozostają BLOCKED i nie są wejściem obecnego generatora.
- [Raport audytu — zatwierdzony](.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-report.md).
- [Projekt pierwszego generatora — zatwierdzony](.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/high-level-design.md).
- [Rejestr decyzji zakresu i architektury](.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/decision-log.md).
- [Raport końcowy i przekazanie do implementacji](.maister/tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-handoff.md).
- [Odtwarzanie pomiarów i organizacja repozytorium](docs/odtwarzanie-audytu.md).
- [Zasady współpracy](AGENTS.md).

Rozpoczęta implementacja udostępnia import danych oraz diagnostyczne `explain`; pełne listy BROAD/STANDARD pozostają nieukończone. [Instrukcja CLI i ograniczenia](docs/generator/cli.md).

[Dalszy plan pracy i runbook przekazania](docs/plan-dalszych-prac-runbook.md) opisuje wznowienie generatora, benchmark SJP.pl, słowniki popularnych słów oraz profile tematyczne i branżowe.

Istotne artefakty procesu Maister znajdują się w `.maister/` i są wersjonowane. Duże dane źródłowe oraz pliki tymczasowe pozostają poza Git. Warunki źródeł zewnętrznych opisują rejestry audytu; publiczność repozytorium sama nie ustala licencji przyszłych wyników.

Własny kod i konfiguracje: [BSD-2-Clause](LICENSE). Własna dokumentacja i raporty: [CC BY 4.0](LICENSE-DOCS.md). [Pochodzenie i warunki danych zewnętrznych](ATTRIBUTIONS.md) oraz [zasady publikacji](docs/generator/publikacja.md).
