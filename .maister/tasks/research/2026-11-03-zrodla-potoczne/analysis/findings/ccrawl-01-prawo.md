# ccrawl: prawo — FineWeb-2 i HPLT wobec TDM (dyrektywa 2019/790, pr. aut. art. 26²–26³)

> **Status: do decyzji użytkownika, nie porada prawna.** To odczyt przepisów i licencji przez zbieracza, nie opinia prawnika.

## TL;DR
- **Lokalne liczenie słów** w pobranych próbkach FineWeb-2/HPLT mieści się w definicji eksploracji tekstów i danych (art. 6 ust. 1 pkt 22 pr. aut.). Podstawą jest **art. 26³** (każdy, także cel komercyjny), nie art. 26² (tylko uczelnie, instytuty naukowe i instytucje dziedzictwa). Warunek: brak zastrzeżenia (opt-out) uprawnionego. Kopie wolno trzymać tylko tak długo, jak trzeba do eksploracji.
- **Publikacja liczb** (lemat + liczba, rok, liczba domen) to publikacja informacji wygenerowanej przez TDM, a nie utworu. Przepisy TDM obejmują zwielokrotnienie; wynik w postaci liczb nie powiela tekstu autorów. Ryzyko oceniam jako niskie. Od strony zbioru: ODC-By 4.3 nie wymaga nawet notki dla „Produced Work”; HPLT CC0.
- **Krótkie przykłady (konteksty)** to już zwielokrotnienie i rozpowszechnienie fragmentów utworów. TDM tego nie obejmuje. Zostaje prawo cytatu (art. 29) z warunkami art. 34 (autor i źródło) i art. 35. Rekomendacja: **w repo tylko URL + data + własny opis**, konteksty tylko lokalnie.
- **Opt-out:** Common Crawl respektuje robots.txt w chwili zbierania (karta FineWeb-2), HPLT v3 ma „filtering for robots.txt opt-out”. To nie obejmuje zastrzeżeń zrobionych później ani w TDMRep czy regulaminie. Pomiar zastrzeżeń na hostach próbki: [`ccrawl-04-optout.md`](ccrawl-04-optout.md).

## Kluczowe decyzje
- Projekt (open source, non-profit, BSD/CC BY) nie jest „organizacją badawczą” w rozumieniu art. 26² ani art. 3 dyrektywy. Oceniam go więc wyłącznie według art. 26³ i art. 4 dyrektywy. W tym trybie opt-out wiąże, a art. 7 ust. 1 dyrektywy **nie** unieważnia zastrzeżeń umownych.
- Licencję tekstu (autorzy stron) oceniam osobno od licencji opakowania (ODC-By/CC0), jak w #16.
- Proponowany podział: lokalnie liczyć — tak (art. 26³); publikować liczby i decyzję — tak, z atrybucją zbioru; publikować teksty i konteksty — nie; redystrybuować próbki — nie.

## Otwarte pytania i ryzyka
- Polska ustawa wymaga zastrzeżenia „w formacie przeznaczonym do odczytu maszynowego […] wraz z metadanymi”. Nie wiadomo, czy sądy uznają za taki format zakaz w regulaminie strony (HTML), czy wolny tekst w robots.txt. Brak orzecznictwa (nie szukałem w bazach płatnych).
- Moment zastrzeżenia. Nasze zwielokrotnienie to pobranie shardu w 2026 r. Strona mogła zastrzec TDM po crawlu (2013–2024). Sprawdzenie wszystkich hostów jest niewykonalne. Wykonalne jest sprawdzenie hostów dowodów konkretnego kandydata (kilka–kilkadziesiąt) przed wpisaniem go do karty.
- Art. 34 każe wymienić twórcę i źródło przy każdym dozwolonym użytku. Przy milionach stron wykonalne jest tylko źródło (zbiór + URL). Ustawa łagodzi to zwrotem „powinno uwzględniać istniejące możliwości”.
- Prawo sui generis do baz danych stron (np. słowników online) chroni art. 8a ustawy o ochronie baz danych, z tym samym mechanizmem opt-out. Strony-słowniki (w tym kopie SJP.pl) i tak wykluczamy.

## Przepisy (cytaty dosłowne)

Źródło polskie: tekst jednolity **Dz.U. 2025 poz. 24** (obwieszczenie z 2024-12-06), PDF z API Sejmu `https://api.sejm.gov.pl/eli/acts/DU/2025/24/text.pdf`, odczyt 2026-11-03. Art. 26² i 26³ dodał art. 1 pkt 8 ustawy z 26 lipca 2024 r. (**Dz.U. 2024 poz. 1254**). Nowela weszła w życie **2024-09-20** (ELI `DU/1994/83`, „Akty zmieniające”). Późniejsza zmiana ustawy (Dz.U. 2026 poz. 1296, w życie 2026-11-06) dotyczy tylko art. 22¹ ust. 3, nie TDM. Uwaga: `isap.sejm.gov.pl` zwraca wyzwanie anty-botowe (HTTP 307 + ciasteczka), więc czytałem ten sam PDF przez oficjalne API ELI Sejmu, bez obchodzenia blokady.

- **Art. 6 ust. 1 pkt 22**: „eksploracją tekstów i danych jest ich analiza wyłącznie przy zastosowaniu zautomatyzowanej techniki służącej do analizowania tekstów i danych w postaci cyfrowej w celu wygenerowania określonych informacji, obejmujących w szczególności wzorce, tendencje i korelacje;”
- **Art. 26² ust. 1**: „Instytucje dziedzictwa kulturowego, a także podmioty, o których mowa w art. 7 ust. 1 pkt 1, 2 i 4–8 ustawy z dnia 20 lipca 2018 r. – Prawo o szkolnictwie wyższym i nauce, mogą zwielokrotniać utwory w celu eksploracji tekstów i danych do celów badań naukowych, jeżeli czynności te nie są dokonywane w celu osiągnięcia bezpośredniej lub pośredniej korzyści majątkowej.”
- **Art. 26³**:
  - ust. 1: „Wolno zwielokrotniać rozpowszechnione utwory w celu eksploracji tekstów i danych, chyba że uprawniony zastrzegł inaczej.”
  - ust. 2: „Zastrzeżenia, o którym mowa w ust. 1, dokonuje się wyraźnie i odpowiednio do sposobu, w jaki utwór został udostępniony. W przypadku utworów publicznie udostępnionych w taki sposób, aby każdy mógł mieć do nich dostęp w miejscu i czasie przez siebie wybranym, zastrzeżenia dokonuje się w formacie przeznaczonym do odczytu maszynowego w rozumieniu art. 2 pkt 7 ustawy z dnia 11 sierpnia 2021 r. o otwartych danych i ponownym wykorzystywaniu informacji sektora publicznego (Dz. U. z 2023 r. poz. 1524) wraz z metadanymi.”
  - ust. 3: „Utwory zwielokrotnione zgodnie z ust. 1 mogą być przechowywane wyłącznie w celu eksploracji tekstów i danych, tak długo, jak jest to konieczne do osiągnięcia tego celu.”
- **Art. 29** (cytat): „Wolno przytaczać w utworach stanowiących samoistną całość urywki rozpowszechnionych utworów […] w zakresie uzasadnionym celami cytatu, takimi jak wyjaśnianie, polemika, analiza krytyczna lub naukowa, nauczanie lub prawami gatunku twórczości.”
- **Art. 34**: „Można korzystać z utworów w granicach dozwolonego użytku pod warunkiem wymienienia imienia i nazwiska twórcy oraz źródła. Podanie twórcy i źródła powinno uwzględniać istniejące możliwości.”
- **Art. 35**: „Dozwolony użytek nie może naruszać normalnego korzystania z utworu lub godzić w słuszne interesy twórcy.”
- **Ustawa o ochronie baz danych, art. 8a ust. 1** (dodany art. 2 pkt 3 noweli 2024, PDF `https://api.sejm.gov.pl/eli/acts/DU/2024/1254/text.pdf`): „Wolno zwielokrotniać rozpowszechnione bazy danych w celu eksploracji tekstów i danych, chyba że uprawniony zastrzegł inaczej.” Ust. 2–3 brzmią jak w art. 26³.

Dyrektywa (UE) 2019/790, tekst PL z Cellar (`http://publications.europa.eu/resource/celex/32019L0790`, odczyt 2026-11-03; `eur-lex.europa.eu` zwrócił wyzwanie WAF 202, którego nie obchodziłem):
- **Art. 2 pkt 2**: „„eksploracja tekstów i danych” oznacza zautomatyzowaną technikę analityczną służącą do analizowania tekstów i danych w postaci cyfrowej w celu wygenerowania informacji, obejmujących między innymi wzorce, tendencje i korelacje;”
- **Art. 4 ust. 1–3**: „1. Państwa członkowskie wprowadzają przepisy przewidujące wyjątek lub ograniczenie […] w odniesieniu do zwielokrotnień i pobrań dostępnych zgodnie z prawem utworów i innych przedmiotów objętych ochroną do celów eksploracji tekstów i danych. 2. Zwielokrotnienia i pobrania dokonane zgodnie z ust. 1 mogą być przechowywane tak długo, jak jest to konieczne do celów eksploracji tekstów i danych. 3. Wyjątek lub ograniczenie przewidziane w ust. 1 ma zastosowanie, pod warunkiem że korzystanie z utworów […] nie zostało wyraźnie zastrzeżone przez podmioty uprawnione w odpowiedni sposób, na przykład za pomocą środków nadających się do odczytu maszynowego w przypadku treści, które zostały podane do publicznej wiadomości w internecie.”
- **Art. 7 ust. 1**: „Każde postanowienie umowne sprzeczne z wyjątkami przewidzianymi w art. 3, 5 i 6 jest bezskuteczne.” Art. 4 nie jest tu wymieniony, więc zastrzeżenie umowne skutecznie wyłącza wyjątek z art. 4.
- **Motyw 18** (fragment): „W przypadku treści, które zostały podane do publicznej wiadomości w internecie, za stosowne powinno się wyłącznie uznać zastrzeżenie tych praw za pomocą środków nadających się do odczytu maszynowego, łącznie z metadanymi i warunkami korzystania ze strony internetowej lub usługi. Zastrzeżenie praw do celów eksploracji tekstów i danych nie powinno dotyczyć innych sposobów korzystania.”

## Licencje zbiorów (odczyt 2026-11-03)
- **FineWeb-2**, `https://huggingface.co/datasets/HuggingFaceFW/fineweb-2/raw/main/README.md`: „The dataset is released under the **Open Data Commons Attribution License (ODC-By) v1.0** […]. The use of this dataset is also subject to CommonCrawl's Terms of Use.” Opt-out: „CommonCrawl respects robots.txt at crawl time, but if you are a webmaster and find your website in 🥂 FineWeb2 and would like to have it removed, you may also use the PII removal/opt out form”. Adresy e-mail i IP są zanonimizowane.
- **ODC-By 1.0**, `https://opendatacommons.org/licenses/by/1-0/`: „“Produced Work” – a work (such as an image, audiovisual material, text, or sounds) resulting from using the whole or a Substantial part of the Contents (via a search or other query) from this Database […]”; „4.3 Notice for using output (Contents). Creating and Using a Produced Work does not require the notice in Section 4.2.” Lista „lemat + liczba” jest co najwyżej Produced Work. Atrybucję i tak warto dać w `ATTRIBUTIONS.md`.
- **Common Crawl ToU** („LAST UPDATED: March 7, 2024”), `https://commoncrawl.org/terms-of-use`: „“Crawled Content” […] may be subject to separate terms of use or terms of service from the owners of such Crawled Content.” Lista zakazów obejmuje m.in. „(d) violating the rights of another individual or entity, including but not limited to such party's intellectual property rights” i „(l) collecting or harvesting any personally identifiable information […]”. ToU nie wymagają celu niekomercyjnego. Strona CC ma też „Opt-Out Ledger”.
- **HPLT v3.0**, `https://hplt-project.org/datasets/v3.0`: „We do not own any of the text from which these text data has been extracted.” / „We license the actual packaging of these text data under the Creative Commons CC0 license ("no rights reserved").” Wśród nowości wydania: „Improved filtering for robots.txt opt-out, adult content, and credentials”. Polityka usuwania: „We will comply with legitimate requests by removing the affected sources from the next release of the corpora.”
- **TDMRep** (W3C CG Final Report 2024-02-02, „not a W3C Standard”), `https://www.w3.org/community/reports/tdmrep/CG-FINAL-tdmrep-20240202/`: nagłówek HTTP `tdm-reservation: 1`, `<meta name="tdm-reservation" content="1">`, plik `/.well-known/tdmrep.json`. `1` oznacza zastrzeżenie, `0` brak zastrzeżenia; opcjonalny `tdm-policy` (URL).

## Ocena czynności (do decyzji użytkownika)

| Czynność | Podstawa | Ocena |
|---|---|---|
| Pobranie shardów i lokalne liczenie form | art. 26³ ust. 1 (TDM), ODC-By / CC0, CC ToU | **dozwolone**, jeśli strona nie zastrzegła TDM; kasować po pomiarze (ust. 3) |
| Trzymanie pobrań „na zapas” | art. 26³ ust. 3 | **nie**: tylko na czas pomiaru. Trzymać sumy kontrolne i adresy, nie dane |
| Publikacja w repo: lemat, liczby wg lat, liczba domen, decyzja | informacja (wynik TDM), nie utwór; ODC-By 4.3 | **niskie ryzyko**; atrybucja „FineWeb-2 (ODC-By 1.0) / HPLT v3 (CC0)” |
| Publikacja URL + daty dokumentu dowodowego | fakt, nie utwór | **niskie ryzyko**; sprawdzić opt-out hosta przed wpisem |
| Publikacja krótkiego kontekstu (zdanie) | art. 29 + 34 + 35, nie TDM | **ryzyko średnie**: wymaga autora i źródła, uzasadnionego celu i „samoistnej całości”. Rekomendacja: nie publikować, opisać własnymi słowami |
| Redystrybucja próbek lub list zdań | brak podstawy | **nie** |
| Karta kandydata z danymi osobowymi (nick, imię z forum) | CC ToU (l), RODO | **nie**: w karcie tylko host i data |
