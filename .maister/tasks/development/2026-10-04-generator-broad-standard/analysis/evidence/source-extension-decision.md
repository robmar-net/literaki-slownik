# Uzupełniające wejścia dowodowe — decyzja

## TL;DR
Obecne SGJP/KWJP nie wystarczają do potwierdzenia wszystkich growych warunków konstrukcji.
Użytkownik zatwierdził wariant A: audyt i dopuszczenie uzupełniających dowodów, bez tworzenia nowych leksemów i zmiany zasad gry.
Zgoda obejmuje rozszerzenie po pozytywnym audycie. Nie dodano jeszcze nowych aktywnych wejść produkcyjnych.


> Sprostowanie po rozmowie z użytkownikiem: wymaganie filtra SJPDor i późniejszego niezależnego opracowania nie było uzgodnione. Wyniki audytu pozostają aktualne; wcześniejszy opis ich konieczności nie jest bieżącą polityką generatora. Zob. [wyjaśnienie](source-policy-clarification.md).

## Key Decisions
- Reguły gry pozostają wiążące. Nie proponujemy pomijania poświadczenia kontrakcji ani automatycznej akceptacji niewiadomych.
- Dodanie nowego artefaktu danych wymaga jawnej roli, wersji, hasha, warunków pozyskania/użycia i odpowiedniego rozszerzenia manifestu. Dotychczasowy kontrakt produkcyjny ma jeden eksport SGJP i 13 list KWJP.
- Nie zmieniamy zamrożonego research, wcześniejszych baz ani list działającej gry.

## Open Questions / Risks
- Nie ma gwarancji, że dodatkowy audyt dostarczy wszystkich potrzebnych danych. Nierozstrzygnięcia wpływające na zakres nadal blokują K4/K5.
- Dokumentacja teorii i miary korpusowe nie zastępują wymaganej metryki/opracowania słownikowego.
- Do domknięcia pozostają także kwalifikatory i hosty mobilnych zakończeń; ta decyzja ich nie rozstrzyga.

## Konkretny zakres A — rekomendacja
Zbadać oficjalne metadane internetowego SGJP dotyczące pochodzenia/opracowania haseł oraz dodatkowe niezależne poświadczenia słownikowe całych kontrakcji. Przed użyciem danych ustalić warunki i wersję; materiały o nieustalonych warunkach zostają BLOCKED. Dopuścić do manifestu wyłącznie artefakty z pozytywnym audytem, w roli uzupełniających dowodów dla jednostek/konstrukcji z istniejących leksemów SGJP. Nie rozszerzać zasobu leksemów, nie pobierać list ani werdyktów SJP/OSPS/PoliMorf. Gdy powstanie dopuszczony artefakt, rozszerzyć jawnie schemat manifestu i testy odmowy zgodnie z zatwierdzonym zakresem A. Nie tworzyć fikcyjnego wejścia przed audytem.

Nowa notatka użytkownika `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` dotyczy przyszłych słowników znajomości i nie jest częścią tego rozszerzenia. Wymienione w niej dane pozostają BLOCKED zgodnie z notatką; nie importujemy ich ani nie używamy do kalibracji.

## Alternatywa B
Nie rozszerzać teraz wejść. Kontynuować wyłącznie niezależne prace techniczne; brakujące poświadczenia pozostają unresolved. Taki wynik nie jest pełnym VERIFIED ani ukończeniem wymaganego generatora. Przed pełnym wydaniem trzeba wrócić do rozstrzygnięcia źródeł.

## Historia decyzji
To nowy rodzaj danych konstrukcyjnych poza zatwierdzonym manifestem, a nie zwykły dokument objaśniający. Maister Development wymaga zatrzymania przy rozszerzeniu zakresu. Executor wymaga pytania przed zmianą zakresu lub przyjęciem materialnego niepowodzenia. Bramka została zatwierdzona odpowiedzią A, zapisaną w orchestrator-state.yml (2026-10-04T14:40:29Z). Nie oczekujemy ponownej zgody na ten sam audyt.

## Wynik audytu po A
Metadane pochodzenia i dokładnych kategorii istnieją w modelu internetowego SGJP. Publiczny kod Kuźni jest objęty BSD-2-Clause; licencja tego programu nie nadaje licencji bazie internetowej. Nie odnaleziono dopuszczonego przypiętego artefaktu metadanych zgodnego z eksportem 20260823. Chronionego eksportu nie wywoływano. [Raport audytu](sgjp-metadata-audit.json) rozróżnia dowód formatu od BLOCKED danych do builda.

Potrzebny artefakt: projekcja powiązana z pełnym ID leksemu, identyfikatorem snapshotu eksportu, membership SJPDor, dokładną kategorią i udokumentowaną proweniencją redakcyjną. Musi mieć autora/źródło, warunki pozyskania i ponownego użycia, wersję, SHA256 oraz brak wykluczonych zależności. Status redakcyjny lub data modyfikacji nie wystarczają za niezależne opracowanie. Tak samo brak znanego poświadczenia kontrakcji nie dowodzi jej niepoprawności. G3 i pełne wydanie pozostają nieukończone.
