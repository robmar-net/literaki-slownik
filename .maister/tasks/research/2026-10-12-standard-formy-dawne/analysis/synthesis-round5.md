# Synteza rundy 5: granica POP

## TL;DR

Pełne pomiary wyjaśniają koszt i stabilność 27 wariantów na dwóch STANDARD.
Próbka 300 haseł nie wskazuje naturalnej granicy 70k, 80k ani progu 0,05.
Samo pokrycie korpusu ukrywa duże różnice składu i decyzje o brakach danych.
Rekomendacja dotyczy kierunku kryterium; żadnej wartości ani wdrożenia nie zatwierdzono.

## Key Decisions

- Skorygować wcześniejsze zalecenie zachowania 60k. Poprawny mechanizm limitu nie dowodzi poprawności jego wartości.
- Oddzielić stabilizację od poszerzenia. Stała punktacja obecnego cięcia usuwa zbadane wypychanie, lecz nie potwierdza właściwej granicy POP.
- Przed kolejną kalibracją uzgodnić zakres POP i traktowanie terminów, rejestrów, derywatów, braków oraz homonimów. Nie wybierać progu na podstawie kilku wygodnych przykładów.

## Open Questions / Risks

- Oceny rejestru mają 22/30 zgodnych klas w powtórnym przeglądzie. Różne źródła i różna ostrożność częściowo wyjaśniają pozostałe osiem; nie usuwają niepewności.
- Brak własnego KWJP rośnie od 14% w paśmie 50–60k do 51% w 60–70k i 85% w 70–80k. To luka konkretnego rodzaju dowodu, a nie automatyczny błąd słownika.
- Nie badano znajomości przez graczy. Konteksty wybrano z pierwszej strony, agenci użyli tego samego modelu; część źródeł ma obserwowane ograniczenia dostępu.

## Łańcuch wnioskowania

| Dowód | Wniosek | Granica wniosku |
|---|---|---|
| Limit 70k daje +197 684 form, 80k +409 433 względem 60k | Zwiększenie limitu ma duży wpływ na skład | Mały zysk pokrycia nie ocenia przydatności tych form |
| W pasmach 60–70k i 70–80k jest odpowiednio 9 i 10 ocen ogólnych na 40 | Nie ma skoku wskazującego dokładną granicę 70k | Oceny ogólne nie są badaniem rozpoznawalności, ograniczone nie są odrzuceniami |
| Odbąknąć i bezołowiówka mają poprawne konteksty, a pozostają poza 80k i 0,05 | Jedna granica obecnej punktacji pomija także zwykłe słowa | To kontrprzykłady, nie dowód, że należy przyjąć wszystkie pozycje poniżej |
| Siejba wchodzi przy 70k i 0,05; uherski przy 80k ma obcy dowód | Większy limit oraz próg wymagają kontroli sensu i rejestru | Zły dowód nie oznacza nieistnienia słowa lub automatycznej zmiany STANDARD |
| Stałe obecne cięcie: ta sama lista baseline, +2372/0 przy dodatkach | Można usunąć konkurencję o miejsca bez szerokiej ekspansji | Grupowanie, nowe źródła i przycinanie nadal mogą zmieniać listę |
| Dwa filtry ARF≥3 / ARF/F≥0,1 mają to samo pokrycie, różnią się o 345 639 form | Polityka braków nie jest technicznym detalem | Fallback nie dowodzi rozproszenia słów bez własnych danych |

Pełne liczby, źródła i rekomendacja: [raport](../outputs/pop-calibration.md). Pomiar sprawdzono [niezależnym kodem](findings/round5/measurement-review.md); definicje i literatura mają osobny [audyt źródeł](findings/round5/methodology-sources.md).

## Rozbieżności i pewność

Zachowano pierwotne 300 ocen oraz 30 ocen koordynatora. W pięciu rozbieżnościach tory korzystały z dodatkowych źródeł, których nie miał koordynator: przedryndać, lnica, miodokwiat, ostojowy, pyrex. Pilarz ujawnia nieostrą granicę zawodu ogólnego i terminu. Fermentownia i zgorzknialec mają wstępne oceny bez kontekstów. W tych przypadkach niska pewność lub odmienna klasa pozostają widoczne; nie zastąpiono ich pozornym konsensusem. [Pełne zestawienie](findings/round5/quality-summary.json).

Odczyt pierwotnych stron po utrwaleniu klas stanowi osobną kontrolę źródeł. Ograniczony dostęp nie został przemianowany na pełny odczyt. Korekty interpretacji historycznego szampitra i pęcy opisano w rejestrze dostępu toru B; nie są podstawą wyboru progu. To ważne rozróżnienie: potwierdzenie znaczenia lub dawnej rejestracji nie potwierdza dzisiejszego szerokiego obiegu.

Wysoka pewność liczb opiera się na pełnych zbiorach i odtworzeniu. Średnia pewność ocen językowych wynika z próbkowania, nieostrych kategorii i ograniczonych dowodów. Nie wyliczono trafności całego POP ani progu „znane x% graczy”.

## Decyzja pozostająca po badaniu

Przyjąć wyniki jako podstawę omówienia kryterium albo wskazać konkretną lukę wymagającą dalszego badania. Opcjonalny brainstorming i projekt nie były zamawiane. Skład słowników, parametry produkcyjne, wydanie i wdrożenie pozostają bez zmian.
