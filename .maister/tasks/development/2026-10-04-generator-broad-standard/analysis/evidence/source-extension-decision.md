# Uzupełniające wejścia dowodowe — decyzja

## TL;DR
Obecne SGJP/KWJP nie wystarczają do potwierdzenia wszystkich growych warunków konstrukcji.
Proponujemy uzupełnić dane dowodowe bez tworzenia nowych leksemów i bez zmiany zasad gry.
To rozszerzenie aktywnych wejść projektu, nie zgoda na korzystanie z SJP lub benchmarku.

## Key Decisions
- Reguły gry pozostają wiążące. Nie proponujemy pomijania poświadczenia kontrakcji ani automatycznej akceptacji niewiadomych.
- Dodanie nowego artefaktu danych wymaga jawnej roli, wersji, hasha, warunków pozyskania/użycia i odpowiedniego rozszerzenia manifestu. Dotychczasowy kontrakt produkcyjny ma jeden eksport SGJP i 13 list KWJP.
- Nie zmieniamy zamrożonego research, wcześniejszych baz ani list działającej gry.

## Open Questions / Risks
- Nie ma gwarancji, że dodatkowy audyt dostarczy wszystkich potrzebnych danych. Nierozstrzygnięcia wpływające na zakres nadal blokują K4/K5.
- Dokumentacja teorii i miary korpusowe nie zastępują wymaganej metryki/opracowania słownikowego.
- Do domknięcia pozostają także kwalifikatory i hosty mobilnych zakończeń; ta decyzja ich nie rozstrzyga.

## Konkretny zakres A — rekomendacja
Zbadać oficjalne metadane internetowego SGJP dotyczące pochodzenia/opracowania haseł oraz dodatkowe niezależne poświadczenia słownikowe całych kontrakcji. Przed użyciem danych ustalić warunki i wersję; materiały o nieustalonych warunkach zostają BLOCKED. Dopuścić do manifestu wyłącznie artefakty z pozytywnym audytem, w roli uzupełniających dowodów dla jednostek/konstrukcji z istniejących leksemów SGJP. Nie rozszerzać zasobu leksemów, nie pobierać list ani werdyktów SJP/OSPS/PoliMorf. Zmianę schematu manifestu i testy odmowy ująć w zatwierdzanym doprecyzowaniu planu.

Nowa notatka użytkownika `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` dotyczy przyszłych słowników znajomości i nie jest częścią tego rozszerzenia. Wymienione w niej dane pozostają BLOCKED zgodnie z notatką; nie importujemy ich ani nie używamy do kalibracji.

## Alternatywa B
Nie rozszerzać teraz wejść. Kontynuować wyłącznie niezależne prace techniczne; brakujące poświadczenia pozostają unresolved. Taki wynik nie jest pełnym VERIFIED ani ukończeniem wymaganego generatora. Przed pełnym wydaniem trzeba wrócić do rozstrzygnięcia źródeł.

## Dlaczego decyzja jest potrzebna
To nowy rodzaj danych konstrukcyjnych poza zatwierdzonym manifestem, a nie zwykły dokument objaśniający. Maister Development wymaga zatrzymania przy rozszerzeniu zakresu. Executor wymaga pytania przed zmianą zakresu lub przyjęciem materialnego niepowodzenia. Dlatego po utrwaleniu dostępnych dowodów i testów wracamy po jedną decyzję A/B, bez ponownego głosowania nad niezmiennością zasad gry.
