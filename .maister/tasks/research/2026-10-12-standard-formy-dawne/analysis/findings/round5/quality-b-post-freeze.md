# Runda 5: źródłowa weryfikacja ocen B po zamrożeniu

## TL;DR

Podjęto próbę otwarcia wszystkich 19 wskazanych URL. Właściwe fragmenty odczytano dla 17 źródeł: 16 pod pierwotnym adresem, jedno przez oficjalny nowy adres PDF AMUR. Dwa własne hasła WSJP (`przedryndać`, `bojownica`) pozostają bez bezpośredniego odczytu mimo ponowień i alternatyw. Nie przedstawiam ich jako zweryfikowanych pełnym odczytem.

Macierz `quality-b.json` i jej klasy pozostały bez zmian. Poniższe ustalenia powstały po zamrożeniu. Szczegółowy rejestr prób, URL, zakresów i ograniczeń: [quality-b-post-freeze.json](quality-b-post-freeze.json).

## Key Decisions

- **przedryndać** — Telefonicznego znaczenia nie usuwam jako nieistniejącego: potwierdza je teraz otwarte hasło zatelefonować jako relację synonimii. Przypisuję nowy właściwy URL zamiast adresu znaczenia podróżnego. Nie wywodzę z samej tej relacji częstości ani kwalifikatora potoczności. Znaczenie podróżne nie uzyskało bezpośredniego potwierdzenia z powodu dostępu.
- **szampiter** — Wycofuję z bieżącej interpretacji automatyczne przypisanie rzeczownikowi kwalifikatora żartobliwości na podstawie nawiasu dotyczącego czasownika szampitrować. Potwierdzone: rzeczownik szampiter=szampan przywołany za SW oraz osobne regionalne szampiter=szampon.
- **bojownica** — W bieżącej syntezie kwalifikacja książk. i pełne hasło nadal mają status tylko indeksowanego wyniku. Zamrożona wysoka pewność nie może być przedstawiana jako zakończona weryfikacja bezpośrednia. Propozycja robocza: niepewne źródłowo do uzyskania właściwego odczytu; bez zmiany klasy historycznej.
- **pęca** — Potwierdzenie nazwy i historycznych rejestracji nie rozstrzyga współczesnego obiegu. Dla decyzji o szerokim POP pozostawić niepewność. Autorstwo i tytuł po otwarciu: Jowita Żurawska-Chaszczewska, Słownik słownictwa rzemiosł skórzanych, Poznań 2010.
- **lunonauta** — Po bezpośrednim odczycie ustalono: Wiesław Krajewski, Urania–PA 5/2009. Nie jest to poświadczenie tekstu z 2026 r.
- **ruptura** — Kwalifikator przest. pozostaje potwierdzony, lecz przykłady WSJP obejmują także późne użycie przenośne w prasie, objaśnione przez redakcję. Nie rozciągać opisu próby KWJP na wszystkie użycia słowa.

## Open Questions / Risks

- Własne hasła `przedryndać` i `bojownica`: `web.open` zwracał Cache miss lub niedostępność; curl zwrócił HTTP 403 również po ponowieniu poza sandboxem. Sprawdzono adresy podglądu, wydruku i wariant z www. Wyniki wyszukiwania pozostają dowodami pośrednimi.
- Znaczenie telefoniczne `przedryndać` ma teraz osobny [odczytany dowód relacji synonimii w WSJP](https://wsjp.pl/haslo/podglad/33898/zatelefonowac). Nie jest to jeszcze odczyt użycia tego czasownika w zdaniu.
- `pęca` i `kozeta`: potwierdzony sens historyczny, niepotwierdzony dzisiejszy zasięg. To nadal istotny brak dla decyzji o POP.
- Trzy PDF: odczyt właściwych fragmentów ekstrakcji tekstu. Obrazów stron nie oceniono; próby dla Sokólskiej i wykazu grzybów zakończyły się błędem Cache miss.
- `profitka`: web timeout, następnie bezpośredni HTTP 200 i odczyt fragmentu z pobranego HTML. Cache i jego hash zapisano w JSON; surowej treści nie publikowano.
- Kwalifikator `rzad./żart.` z artykułu Sokólskiej nie może być bez sprawdzenia przenoszony z czasownika na rzeczownik. Ta korekta nie zmienia zamrożonej klasy, lecz zawęża uzasadnienie.
- Dalsze decyzje powinny uwzględniać te ograniczenia. Zamrożenie ocen zapewnia historię badania, nie usuwa braków dowodowych.

## Odczytane fragmenty

| Hasło | Źródło | Wynik |
|---|---|---|
| przedryndać | [źródło](https://wsjp.pl/haslo/podglad/111647/przedryndac/5263631/500-km) | Znaczenie telefoniczne potwierdza relacja synonimii w odczytanym haśle zatelefonować. Znaczenie podróżne nadal znane z indeksowanego wyniku; wyłączone z wniosków opartych na bezpośrednim odczycie. |
| siejba | [źródło](https://wsjp.pl/haslo/podglad/119994/siejba) | Kwalifikator daw. i znaczenie siewu potwierdzone. Daty wydań 1988/2008 nie unieważniają ograniczenia stylistycznego. |
| kikować | [źródło](https://obserwatorium-mlodziezy.ujk.edu.pl/jednostki/kikowac/) | Anna Wileczek, wpis 11.06.2024: usuwanie z gry/grupy oraz omówienie warszawskiego znaczenia obserwowania. Rozdzielenie sensów jest zasadne. |
| kozeta | [źródło](https://pl.wikisource.org/wiki/M._Arcta_S%C5%82ownik_ilustrowany_j%C4%99zyka_polskiego/K_%28ca%C5%82o%C5%9B%C4%87%29) | Transkrypcja słownika Arcta potwierdza nazwę małej kanapy. Współczesny zakres nadal nierozstrzygnięty. |
| konklawista | [źródło](https://www.przewodnik-katolicki.pl/Archiwum/2004/Przewodnik-Katolicki-48-2004/Historia/Jak-wybierano-papiezy) | Artykuł Małgorzaty Jańczak z 28.10.2004 zawiera formy konklawistów, konklawiści i konklawista, w autorskiej narracji o wyborze papieża. |
| wiroid | [źródło](https://zpe.gov.pl/a/przeczytaj/DQN7i4ibO) | Hasło występuje w objaśnieniu pojęcia i nazwach konkretnych wiroidów. Poświadczenie terminu biologicznego potwierdzone. |
| wiroid | [źródło](https://www.gov.pl/web/piorin/regulowane-agrofagi-niekwarantannowe-dla-unii) | Strona instytucji używa polskich nazw wiroidów wrzecionowatości bulw ziemniaka i karłowatości chmielu. |
| wiwera | [źródło](https://wsjp.pl/haslo/podglad/117600/wiwera) | Potwierdzone hasło zoologiczne i przytoczony przez WSJP tekst prasowy z 29.03.2020. |
| szampiter | [źródło](https://www.poradnikjezykowy.uw.edu.pl/wydania/poradnik_jezykowy.796.2022.07.3-U.Sokolska.pdf) | W omówieniu szampitrować autorka przywołuje rzeczownik szampiter w znaczeniu szampana za Słownikiem warszawskim. |
| szampiter | [źródło](https://smakipowiatupoznanskiego.pl/slownik-gwary-poznanskiej/) | Regionalny słownik rzeczywiście podaje znaczenie szamponu. |
| lunonauta | [źródło](https://www.urania.edu.pl/zasoby/ksiezyc-ludzie-i-slowa.html) | Artykuł Wiesława Krajewskiego, Urania–PA 5/2009: objaśnienie określenia i własne użycie liczby mnogiej lunonauci. |
| superstrat | [źródło](https://wsjp.pl/haslo/podglad/20796/substrat/5157958/w-jezykoznawstwie) | Słownik przytacza zdanie Artura Rejtera z superstrat w opisie relacji języków. |
| profitka | [źródło](https://muzeumkresow.eu/eksponat/lichtarz-3/) | Autorski opis eksponatu zawiera profitką i profitka jako nazwę części lichtarza. |
| strzępiak | [źródło](https://pnbt.gov.pl/pliki-do-pobrania/otworz/a7b93254-3b32-4d4e-b9a5-c6641d00d381.pdf) | Potwierdzone nazwy dziesięciu strzępiaków w wykazie gatunków. |
| ruptura | [źródło](https://wsjp.pl/haslo/podglad/50305/ruptura) | Potwierdzony kwalifikator przest. dla przepukliny. Cytaty pokazują także użycie przenośne w wypowiedzi prasowej z 2003 r. z objaśnieniem redakcji. |
| odwłóczyć | [źródło](https://wsjp.pl/haslo/podglad/124654/odwloczyc) | Kwalifikator przest. i znaczenie odłożenia w czasie potwierdzone. |
| bojownica | [źródło](https://wsjp.pl/haslo/podglad/129634/bojownica) | Własne hasło i kwalifikator książk. nadal są widoczne tylko w wyniku wyszukiwania. Bezpośrednia weryfikacja tej tezy nie powiodła się. |
| pęca | [źródło](https://repozytorium.amu.edu.pl/bitstreams/03e4a6b5-31c3-48e6-ac40-d4aaa4bcc98e/download) | Jowita Żurawska-Chaszczewska, Słownik słownictwa rzemiosł skórzanych, Poznań 2010: pęca jako element sokolniczy, z historycznym wykazem rejestracji. |
| pasywizacja | [źródło](https://informatorects.uw.edu.pl/pl/courses/view?prz_kod=3301-ZJ-WM-JF003) | Nazwa operacji składniowej występuje w dwóch miejscach opisu zajęć. |
