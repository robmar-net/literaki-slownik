# Udokumentowane warianty małej i wielkiej litery

## TL;DR
Wdrożono zatwierdzony dowód BROAD dla wznak. Dalszy przegląd ortografii ujawnił brak poprawnych małoliterowych wariantów niektórych istniejących leksemów w eksporcie SGJP.
Zatwierdzone A: osobny kandydat pisowni wyłącznie z dosłownym dowodem normy i dokładnym źródłem, bez zmiany źródłowego rekordu.
To rozszerzenie modelu rekonstrukcji, wymagające decyzji; nie zmienia reguł gry ani nie dopuszcza samoczynnego lower.

## Key Decisions
- Zatwierdzona norma2026 pozostaje. [RJP §8.1.2 pkt3–4, s.43](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf#page=43) obejmuje miasta, dzielnice, osiedla i wsie wspólnym obowiązkiem dużej litery. Nie trzeba między nimi wybierać innej normy.
- Osobna uwaga dopuszcza małą lub wielką literę nieoficjalnych nazw etnicznych. Tego wyjątku nie można rozszerzać na wszystkie etnonimy, nazwy własne czy skrótowce.
- Przypięty eksport ma Angol/Angol/subst:sg:nom:m1/nazwa_pospolita/pot.,etn. w wierszu9040 oraz Jugol/Jugol/subst:sg:nom:m1/nazwa_pospolita/pusty kwalifikator w wierszu358226. Oba zapisy normy małoliterowej mają jawne przykłady RJP, lecz nie występują w SGJP jako osobne małoliterowe analizy.
- Angol jest jednocześnie formą nazwy kraju Angola; reguła nie przechodzi na tę analizę. Osobny szkop ma także nazwiskowe homonimy; one zachowują własną ocenę.
- kitajec nie występuje w zamkniętym lookup źródła; nie dodajemy nowego leksemu z dokumentu RJP. makaroniarz, szkop i żabojad mają już własne małoliterowe analizy w SGJP, nie wymagają tego obejścia.

## Open Questions / Risks
- Obecny model odrębnej ortografii nie tworzy formy tylko dlatego, że source.lower() pasuje do alfabetu. Norma, znaczenie i dokładne źródło muszą być dowiedzione.
- Pełna klasa mieszkańców nadal nierozpoznana: etn. nie jest jej kompletnym indeksem; warszawianka/krakowianka mają zwykłe nazwa_pospolita i puste kwalifikatory. Bawarka/bawarka ilustrują niebezpieczeństwo przeniesienia klasy na herbaciany homonim.
- Pełny ID nie gwarantuje jednej semantyki. Dowód tylko konkretnego użycia; nieznane możliwości zachowane. Finalna delta list nadal niepoliczalna przed pełną macierzą.

## Zatwierdzony projekt A

A — rekomendowane: dodać osobny typ udokumentowanego wariantu ortograficznego istniejącej analizy. Pierwsze przypadki wyłącznie literalne formy podstawowe angol i jugol, bez automatycznego generowania fleksji. Kandydat zawiera cały rekord źródłowy, źródłowy zapis, nowy zapis, przypięty dokument i ID użycia. Źródłowe sgjp_record/interpretation i ich pisownia pozostają nietknięte.

Kandydat z istniejących relacji derivation_candidate/component/analysis, bez nowego leksemu lub migracji; trace określa zmianę ortograficzną, nie dopisanie końcówki. Język, gra, profil i zakres oceniane dla tej jednej kompletnej analizy. Dowód małej litery nie zwalnia z innych kryteriów; UNKNOWN nadal blokuje końcową akceptację. Źródłowy zapis wielką literą zachowuje odrębną ocenę. Nie oznaczamy pełnego pokrycia wszystkich znaczeń.

Test-first: brak reguły dla nazwy kraju/homonimu/niedopasowanego użycia, hash/wiersz/pola/dokument, brak jawnego przykładu odmowa, niezależność oryginału i wariantu, powtarzalny zapis oraz explain w obu wariantach. Raport rozlicza te kandydaty jako osobną klasę. Dalsza fleksja lub rozszerzenie zamkniętej populacji wymaga osobnego źródłowego przeglądu, nie analogii po sufiksie.

B — zachować dotychczasowy model i poczekać na niezależną dopuszczoną małoliterową analizę. Obecna obserwacja nie tworzy kandydata; brak tych form pozostaje wykazaną luką, nie dowodem błędności ani domknięciem wydania.

## Kontrola źródłowa

[Powtarzalny raport](capitalization-coverage.json), [skrypt readonly](capitalization-coverage-probe.py): dwie identyczne reprodukcje, source SHA eksportu3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810, oryginalna baza bez zmian. Pełna populacja zaobserwowanych etn.:83 pełne ID,84 kombinacje metadanych,967 kompaktowych interpretacji. To nie pełna populacja etnonimów ani mieszkańców.12 zamkniętych zapytań dokumentacyjnych ze wszystkimi źródłowymi homonimami; brak aktywacji danych czytnika.

RJP: przypięty wcześniej PDF SHA87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e, ponownie sprawdzony w publicznym dokumencie. Publikujemy własny opis i źródłowe identyfikatory, nie słownik z dokumentu. Nie zastosowano SJP/OSPS/PoliMorf lub community ani nie kontaktowano innych grup.

## Dlaczego pytamy

[AGENTS.md](../../../../../../AGENTS.md) wymaga omówienia zmian kryteriów/składu przed wdrożeniem. Skill maister-implementation-plan-executor wymaga: „At a material deviation or recovery decision […] ask […] and pause”. A dodaje nowy typ kandydata pisowni do zatwierdzonych konstruktorów, dotąd opartych na dołączaniu źródłowych segmentów. Dlatego projekt, przykłady i kontrole są gotowe do przeglądu przed zmianą kodu.

## Zatwierdzenie

A zatwierdzone przez użytkownika; zapis 2026-10-05T16:49:33Z. Wdrożenie zgodnie z zamkniętym zakresem, bez zmiany reguł gry.
