# Świadoma zmiana 02: zaimki.pl, RJP, poradnie

## TL;DR
- **zaimki.pl** (Rada Języka Neutralnego) ma publiczne API JSON bez logowania: 5296 rzeczowników w trzech rodzajach, 412 terminów i 164 rady inkluzywne. Licencja to **OQL v1.4**, z zakazami: wielkie korporacje, policja i wojsko, „bigoted purposes”, odsprzedaż „even if laundered through machine learning”. To nie jest licencja otwarta w sensie OSI/CC, więc ocena: **do decyzji** (na dziś tylko dowód ręczny).
- Wulwy nie ma w słowniku rzeczowników zaimki.pl. Pojawia się tylko w uzasadnieniu dwóch rad, gdzie zalecane jest słowo „srom”.
- **RJP**: stanowisko o feminatywach z 25.11.2019 (model `-ka`, `-ini/-yni` dobry, „ministra” nietypowa) i opinia o neutralności płciowej ogłoszeń (2026, po art. 183ca § 3 KP z 24.12.2025). Wulwy RJP nie omawia. Prawa zastrzeżone, więc **tylko dowód ręczny**. Dla nas RJP to **źródło reguły** (np. „feminatyw na `-ka` od nazwy zawodu jest systemowy”), nie źródło słów.
- Poradnie (PWN, UW, UWr, UZ): nie znalazłem porady o wulwie. Ocena: **tylko dowód ręczny**, po jednej poradzie.

## Kluczowe decyzje
- RJP 2019 i opinię z 2026 cytujemy w karcie jako uzasadnienie klasy „feminatyw systemowy”, nie jako dowód pojedynczego słowa.
- zaimki.pl nie trafia do żadnej automatycznej warstwy, dopóki użytkownik nie oceni zgodności OQL z projektem (kod BSD-2, dokumentacja CC BY 4.0).

## Otwarte pytania i ryzyka
- OQL: zakaz „Be a big corporation” i zakazy celu użycia przechodzą na odbiorców. Wbudowanie danych w listy, które Literaki redystrybuuje, mogłoby obciążyć te listy warunkami OQL. To ocena, nie porada prawna.
- Dane zaimki.pl są społecznościowe i w dużej części **normatywne** (propozycje, np. neutratywy `psycholoże`, `socjologum`), a nie dokumentacja użycia. Tylko 8 z 2439 feminatywów spoza SGJP ma wypełnione pole `sources`.
- Opinia RJP z 2026 nie ma daty na stronie. Datę wziąłem z `lastmod` w mapie witryny (2026-04-15).

## zaimki.pl (odczyt 2026-11-03)
- Stopka każdej strony: „Kod źródłowy oraz treści są udostępnione na licencji OQL”. Licencja: https://zaimki.pl/license, „Opinionated Queer License v1.4, © Copyright Andrea Vos, Collective »Neutral Language Council«”.
- Cytaty z OQL:
  - „The User must give appropriate credit to the Licensor, provide a copy of this license or a … link to oql.avris.it/license/v1.4, and indicate whether and what kind of changes were made.”
  - „No one may use this Work for prejudiced or bigoted purposes …”
  - Lista „You cannot”: „Be a big corporation”, „Be law enforcement or military”, „Just blatantly resell it (even if laundered through machine learning)”.
- `robots.txt` blokuje tylko `/@*`, `/u/*`, `/card/@*` i GPTBot. Nie ma `tdmrep.json` (404).
- API bez logowania: `https://zaimki.pl/api/nouns` (1,77 MB, 5296 haseł), `/api/terms` (412), `/api/inclusive` (164). Pliki są w `scratchpad/potoczne/swiadoma/dl-zaimki/`.
- Wulwa występuje tylko w dwóch radach `inclusive`:
  - rada odróżniająca srom (wulwę) od pochwy;
  - rada sprzeciwiająca się traktowaniu wulwy i pochwy jako symbolu słabości.
- Kontrola dodatnia: psycholożka, ministra, chirurżka i kardiolożka są w `nouns` (klucze psycholog, minister, chirurg, kardiolog).
- Pomiar względem SGJP 20261018 (forma jednowyrazowa, liczba pojedyncza):

| rodzaj | haseł | brak w SGJP |
|---|---|---|
| żeński | 4860 | 2448 (unikalnych 2439) |
| męski | 4688 | 1223 |
| neutralny (neutratywy) | 5781 | 4154 |

- Przykłady żeńskie spoza SGJP: cyrkowczyni, lewicowczyni, poufalczyni, starowierczyni, tanatopraktorka, genderystka, kidultka. 122 z nich są też w tezaurusie DS (np. chirurżka, kardiolożka, fundraiserka, fashionistka). Neutratywy (`-cze`, `-um`) to propozycje, nie słowa w użyciu.

## RJP (odczyt 2026-11-03; stopka „© Copyright by Rada Języka Polskiego PAN”)
- Stanowisko z 25.11.2019: https://rjp.pan.pl/stanowisko-rady-jezyka-polskiego-przy-prezydium-pan-w-sprawie-zenskich-form-nazw-zawodow-i-tytulow-przyjete-na-posiedzeniu-plenarnym-rady-25-listopada-2019-r/
  - Rada uznaje, że polszczyzna potrzebuje możliwie pełnej symetrii męskich i żeńskich nazw osób (parafraza).
  - Nazwy żeńskie tworzone samą zmianą końcówki (ministra, doktora, dziekana) Rada uznaje za nietypowe dla polskiego słowotwórstwa (parafraza).
  - Przyrostek `-ini/-yni` jest popularny (przykłady Rady: naukowczyni, gościni); chirurżka według Rady nie powinna razić.
- Stanowisko z 19.03.2012 (wcześniejsze): https://rjp.pan.pl/stanowisko-rady-jezyka-polskiego-w-sprawie-zenskich-form-nazw-zawodow-i-tytulow-przyjete-na-posiedzeniu-plenarnym-rady-19-marca-2012-roku/
- Opinia o neutralności płciowej ogłoszeń (`lastmod` 2026-04-15): https://rjp.pan.pl/opinia-rjp-w-sprawie-neutralnosci-plciowej-w-ogloszeniach-o-naborze-na-stanowisko/
  - Bodźcem jest art. 183ca § 3 KP, obowiązujący od 24.12.2025: „ogłoszenia o naborze na stanowisko oraz nazwy stanowisk były neutralne pod względem płci”.
  - O osobatywach (np. osoba studencka): według Rady to na razie zwyczaj środowiskowy, jeszcze nie standard języka publicznego (parafraza).
  - **Wniosek dla nas:** przepis z 2025 r. przyspiesza użycie feminatywów w ogłoszeniach, więc w korpusach z lat 2026+ (PPC, sieć) należy się spodziewać wzrostu form na `-ka`.
- Wulwy, sromu ani nazw części ciała w wyszukiwarce RJP nie znalazłem (`?s=wulwa`, `?s=srom` bez trafień w treści). REST API RJP zwraca „UNAUTHORIZED”, więc użyłem zwykłej wyszukiwarki strony.

## Poradnie i słowniki feminatywów
- PWN (sjp.pwn.pl/poradnia): oceniona w #16. URL wyszukiwania `szukaj/wulwa.html` zwraca 404. WebSearch nie zwrócił porady o wulwie.
- UWr, UZ, „Poradnik Językowy” UW: WebSearch nie znalazł porady o wulwie.
- „Słownik nazw żeńskich polszczyzny”, red. A. Małocha-Krupa (WUWr 2015, 683 s., ISBN 978-83-229-3465-4): tylko druk, bez otwartego PDF. Ocena: **tylko dowód ręczny** (strona, wydanie).
- Poradnik ASP Kraków „Feminatywy w Akademii. Słowniczek” (2024, PDF): https://www.asp.krakow.pl/wp-content/uploads/2024/04/Feminatywy_w_Akademii_Slowniczek.pdf. Licencji nie sprawdziłem. Ocena: **tylko dowód ręczny**.

## Ocena
| źródło | licencja | pobieranie | ocena |
|---|---|---|---|
| zaimki.pl (API) | OQL v1.4 (zakazy celu i podmiotu) | JSON bez logowania | **do decyzji** (dziś tylko dowód ręczny) |
| RJP: stanowiska i opinie | © RJP PAN | HTML | **tylko dowód ręczny** (reguła, nie słowo) |
| poradnie (PWN, UW, UWr, UZ) | prawa zastrzeżone | HTML | **tylko dowód ręczny** |
| Słownik nazw żeńskich (2015) | druk | brak | **tylko dowód ręczny** |
