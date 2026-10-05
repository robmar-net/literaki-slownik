# Przegląd dokumentacyjny znaczeń PAN

## TL;DR
Udokumentowano konkretne użycia 14 ze147 przypadków frag:12 z dokumentacji SGJP i2 z obserwacji WSJP. Pełne znaczenia i dopuszczalność nadal nierozstrzygnięte. Dodano odtwarzalny audyt mapowania z ochroną homonimów;156/156 testów przeszło.

## Key Decisions
- Rejestr ekstrakcji pozostaje niezmieniony. Ręczne adnotacje są osobnym [artefaktem](pan-semantic-document-review.json), związanym hashem z jego snapshotem i dokładną tożsamością źródłową, nie samym napisem.
- Dowód opisuje wskazane użycie. Pełny identyfikator SGJP nie gwarantuje pojedynczego znaczenia: [§2.1, s.21](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=21). Z tego powodu nie rozciągamy adnotacji na całą semantykę ID ani inne homonimy.
- Odczytane źródła są obserwacją dokumentacyjną; nie dodano wejść ani reguł do build. Własne zwięzłe adnotacje i bibliografia są publiczne; surowe dokumenty i teksty haseł nie są kopiowane do repo.

## Open Questions / Risks
-133 przypadki nie mają jeszcze takiego przeglądu;147 pozostaje unresolved w kwalifikacji. Dowód14 użyć nie zamyka klasy ani normy2026. [Pokrycie i scenariusz wieku](pan-document-review-coverage.json).
- Brakujące glosy nie zostały odczytane: publiczny czytnik korzysta z anonimowego GET, ale dwa punktowe odczyty search-by-form dla oścież zwróciły502, w tym ponowienie po eskalacji. To ograniczenie tych prób, nie dowód nieistnienia danych. Nie użyto uwierzytelnienia ani dostępu chronionego, nie wykonano masowego pobierania.
- Nowy wybór wieku opisano w [decyzji do omówienia](general-class-age-decision.md). Dalsze nazwy mieszkańców, wyjątki semantyczne, G3–G9 i phase10 nadal wymagają pracy.
- Historyczne próby kontaktu pozostały niewysłane. Nie kontaktujemy się z innymi grupami.

## Mapowanie i sprawdzenie

Adnotacje obejmują osiem użyć frazeologicznych i sześć użyć jako człony nazw. Zachowano osobno roścież:F/roścież:S, de:F/de:S oraz ziem/ziemia; KWJP nie jest źródłem normatywnej poprawności. Nie rozszerzono przykładów dokumentacji na pozostałe wyrazy przez podobieństwo pisowni.

Ponowne pobranie PDF daje identyczny SHA256 jak zatwierdzony cache:3e3d104b1a210e0097c511b36f1440de539413ec64079fba505c47c3bf7684ca. WSJP ma odsyłacze, datę obserwacji i jawny brak hasha upstream; warunki importu danych nadal nieustalone.

Audyt odmawia niezgodnego snapshotu, innego ID/tagu/etykiet/wierszy, duplikatu lub nieistniejącego odsyłacza. Odmawia też twierdzeń all_meanings i accept zamiast unresolved. Cztery testy red(brak skryptu)→green; pełna suita156/156. Dwa odtworzenia mają identyczne bajty. Audyt nie odczytuje ani nie zapisuje źródłowej bazy SQLite.

## Odtworzenie

```sh
python3 scripts/audit_pan_review.py --cases .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/pan-semantic-cases.json --review .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/pan-semantic-document-review.json --output tmp/nowy-przeglad-pan.json
```

Cel musi być nowym plikiem. Przegląd pozostaje osobną warstwą dowodową; nie zastępuje historycznego rejestru ani pełnego odbioru generatora.
