# Pochodzenie i atrybucje

## Własne wkłady

Projekt [literaki-slownik](https://github.com/robmar-net/literaki-slownik), autorzy projektu, 2026.
Kod i własne konfiguracje: BSD-2-Clause, [oryginalny tekst angielski](LICENSE).
Polska metryczka: licencja kodu, BSD 2-Clause License; źródło tekstu:
[SPDX](https://spdx.org/licenses/BSD-2-Clause.html). Dokumentacja i własne raporty:
[CC BY 4.0](LICENSE-DOCS.md). Te oznaczenia dotyczą wyłącznie własnych wkładów.

## SGJP — tekstowy eksport dla Morfeusza

Wersja pl.sgjp.sgjp-2026.08.24, plik sg jp-20260823.tab.gz (nazwa techniczna: `sgjp-20260823.tab.gz`).
Źródło: https://download.sgjp.pl/morfeusz/20260823/sgjp-20260823.tab.gz
SHA256: `3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810`.
Zakres zawiadomienia: przypięty pięciopolowy eksport, nie pełna internetowa baza SGJP.
Oryginalne angielskie zawiadomienie z polską metryczką: warunki redystrybucji i wyłączenie odpowiedzialności eksportu.

```text
Copyright © 2007–2026 Marcin Woliński, Zbigniew Bronk, Włodzimierz Gruszczyński, Witold Kieraś, Zygmunt Saloni, Danuta Skowrońska, Robert Wołosz

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY COPYRIGHT HOLDERS “AS IS” AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.
```

Operacje projektu: import bez zmiany surowych pól, rozwinięcie tagów, normalizacja kluczy,
kwalifikacja i rekonstrukcje z jawnymi śladami, raporty. Errata wybranych tagów stanowi
osobną adnotację; surowe zapisy pozostają zachowane. Listy wynikowe będą wskazywać te zmiany.

## KWJP100 — listy frekwencyjne

Źródło danych: Korpus Współczesnego Języka Polskiego (IPI PAN), kwjp100-varia, commit 26d82bd8b906dfed1cfcf8f903b1650b56daeabf, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Audyt i wyliczenia: projekt literaki-slownik; przetworzono format i obliczono statystyki. Autorzy i zalecane cytowanie: https://kwjp.pl/overview.

Używamy 13 list wskazanych w [manifeście źródeł](config/generator/sources.json),
każdej z osobnym SHA256, mianownikiem i rolą corpus_evidence. Warunki dotyczą tych zasobów
repozytorium, nie pełnych tekstów korpusu ani całej witryny. Operacje projektu:
parsowanie, powiązania strukturalne i obliczenia diagnostyczne; brak imputacji częstości,
brak rozszerzania zasobu leksykalnego danymi KWJP.

## NKJP — n-gramy ze zrównoważonego podkorpusu

Dotyczy pakietów, które używają NKJP (POP, POP0). Pakiet LL-PL v29 go nie używa.

- Zasób: „N-grams from the balanced subcorpus of the National Corpus of Polish”, plik `1grams.gz`
  (SHA256 `73af49094621b2f86b594beba783c14aee8c8212f1aff3d61f281ab5d99e3dc9`), https://zil.ipipan.waw.pl/NKJPNGrams.
- Twórca i udostępniający: Zespół Inżynierii Lingwistycznej IPI PAN. Korpus: Narodowy Korpus Języka Polskiego (NKJP).
- Licencja: CC BY, wersja nieokreślona przez udostępniającego. Spełniamy wymagania wszystkich wersji
  1.0–4.0; tekst wersji 4.0: https://creativecommons.org/licenses/by/4.0/. Udostępniający nie podał
  informacji o prawach autorskich ani wyłączenia gwarancji.
- Zmiany: z formy zdejmujemy interpunkcję tylko z brzegów tokenu i zostawiamy kropkę, więc skróty
  (np. `ul.`) nie łączą się ze słowami (`ul`); reguła `nkjp-clean-strip-edges-keep-dot-v1`
  ([ADR-007](docs/adr/ADR-007-metoda-pop-v1.md)). Zliczenia łączymy z formami SGJP i przeliczamy
  na miary popularności. Surowego pliku nie redystrybuujemy.
- Autorzy NKJP i IPI PAN nie popierają tego projektu ani jego wyników. Decyzja: [ADR-006](docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md).

## Pozostałe materiały

Oryginalne dokumenty zewnętrzne, cytaty i materiały dowodowe zachowują wskazane przy nich
źródła, metryczki i warunki. Licencje projektu nie obejmują praw osób trzecich.
Cache, źródłowe archiwa i robocze bazy nie są publikowane w tym repozytorium.
Ten plik nie jest zezwoleniem na redystrybucję dowolnej bazy lub materiału spoza manifestu.
