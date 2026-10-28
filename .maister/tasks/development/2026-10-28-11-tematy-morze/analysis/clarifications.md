# Doprecyzowania (faza 1)

## TL;DR
Pytań do operatora w fazie 1 nie było. Zakres wynika z ticketu #11, badania 2026-10-27 i poleceń operatora z 2026-10-28.

## Kluczowe decyzje
- Etykiety T1: `mors.`, `żegl.`, `ryb.`, porównywane jako całe atomy, tak jak w projekcie badania (254 leksemy). `geogr.` i `meteor.` nie wchodzą, bo nie ma ich w decyzji D1 (ticket #11).
- Pliki tematów: `config/generator/tematy/<id>.json`, manifest źródeł `config/generator/tematy-sources.json`. To decyzja techniczna (wzór POP00).
- Słowosieć 4.5: używamy pliku `data/work/plwordnet/wordnet_work_4_5.zip`, który jest już pobrany (sha256 `30edc5f8…dcbc`). Przenosimy go do `cache/plwordnet/` i zapisujemy źródło, datę i sumę. IATE TBX 2019 pobieramy.
- Numery ADR w repo: ADR-010 dla metody tematy-v1, ADR-011 dla źródeł. Lokalne numery 001–010 z badania mapujemy na nie.

## Polecenia operatora (2026-10-28)
- Potok wsadowy i deterministyczny, jako podkomenda według wzoru POP00 (#10).
- Dane surowe poza Git, z przypiętymi sumami SHA-256. Zapisać źródło, datę i sumę.
- Bez kontaktu z autorami i innymi grupami. Wikisłownik odroczony.
- Kontrolnie zmierzyć pokrycie T2. Sprawdzić, czy IATE 4821 wciąga żeglugę śródlądową.
- Na bramce: raport przecięć i 30 słów do przeglądu R2. Dalszych tematów nie robimy przed decyzją.
- Artefakty po polsku, zwięźle. Nie wymieniać żadnej gry słownej poza Literaki i Kurnik.
- Po zapisie w `.maister/tasks`: commit i push.
