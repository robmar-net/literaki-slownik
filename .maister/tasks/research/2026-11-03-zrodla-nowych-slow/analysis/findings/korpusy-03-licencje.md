# korpusy: cytaty licencji (odczyt 2026-11-03)

## TL;DR
- Pełne CC BY 4.0 dla danych mają ParlaMint 5.0, korpusy LCC do pobrania i KWJP100.
- FineWeb-2 (ODC-By) i HPLT/OSCAR (CC0) licencjonują opakowanie, nie tekst. Prawa do tekstu zostają przy autorach stron.
- Wikimedia: CC BY-SA 4.0 i GFDL.

## Kluczowe decyzje
- Cytaty są dosłowne. Tam, gdzie tekst pochodzi z narzędzia do pobierania stron, oznaczam to.

## Otwarte pytania
- Warunki Common Crawl nie mają osobnej klauzuli o redystrybucji pochodnych. Tę lukę trzeba ocenić przy FineWeb-2 i HPLT.

## Cytaty
- **ParlaMint 5.0**, https://www.clarin.si/repository/xmlui/handle/11356/2004: „Creative Commons - Attribution 4.0 International (CC BY 4.0)”. Opublikowano 2025-07-08. Strona podaje też: „The corpora mostly start in 2015 and extend to mid-2022” (cytat przez WebFetch).
- **Leipzig Corpora Collection**, https://wortschatz.uni-leipzig.de/en/usage (przeglądarka): „The data and applications provided by the project are protected by copyright. They are made available free of charge for private and scientific use under the Creative Commons licence CC BY-NC. Any use beyond the query options provided on the WWW, automated queries (except via our web services) and commercial use of the data are prohibited without the written consent of the project management. The text corpora offered for download are made available under the Creative Commons licence CC BY.” Link „CC BY” prowadzi do `creativecommons.org/licenses/by/4.0/`. Dla nas wiąże zdanie o korpusach do pobrania (CC BY 4.0), a nie CC BY-NC strony i API.
- **FineWeb-2**, `README.md` karty HF: „The dataset is released under the **Open Data Commons Attribution License (ODC-By) v1.0** license. The use of this dataset is also subject to CommonCrawl's Terms of Use.”
- **Common Crawl ToU** (wersja z 2024-03-07), https://commoncrawl.org/terms-of-use, przez WebFetch: „may be subject to separate terms of use or terms of service from the owners of such Crawled Content”; „YOU AGREE TO RESPECT THE COPYRIGHTS AND OTHER APPLICABLE RIGHTS OF THIRD PARTIES”.
- **HPLT v2.0/v3.0**, karta HF `HPLT/HPLT2.0_cleaned` i https://hplt-project.org/datasets/v3.0: „We do not own any of the text from which these text data has been extracted.” / „We license the actual packaging of these text data under the Creative Commons CC0 license ("no rights reserved").” / „It is your responsibility that any use of the data complies with any applicable legal framework, such as, among others, the EU Copyright Directive 2019/790 […]”.
- **OSCAR**, https://oscar-project.org/, przez WebFetch: „We do not own any of the text from which these data has been extracted.” / „We license the actual packaging and annotations of these data under the Creative Commons CC0 license”. API HF: `oscar-corpus/OSCAR-2301` `gated: manual`, `license:cc0-1.0`.
- **CulturaX**: karta niedostępna bez logowania (API HF: `gated: auto`). Cytat wtórny z loadera SEACrowd: „The licence terms for CulturaX strictly follows those of mC4 and OSCAR.”
- **MADLAD-400**, karta HF `allenai/MADLAD-400`: nagłówek YAML `license: odc-by`; sekcja „## License”: „This data is released with the `CC-BY-4.0` license.” To sprzeczność.
- **CC-100**, karta HF `statmt/cc100` (cytat wtórny przez wyszukiwarkę): licencja „unknown”; „by using this, you are also bound by the Common Crawl terms of use in respect of the content contained in the dataset”.
- **KWJP100 varia**, https://github.com/ipipan/kwjp100-varia, README: „na zasadach licencji CC-BY 4.0 (Creative Commons Attribution 4.0)”. Ostatni commit `26d82bd8`, 2026-05-28 (`gh api`).
- **PPC**, https://git.nlp.ipipan.waw.pl/PPC/ppc: „The parliamentary data is public domain.” / „The corpus annotations are available on CC-BY (attribution) licence.”
- **Wikimedia dumps**, https://dumps.wikimedia.org/legal.html: „all original textual content is licensed under the GNU Free Documentation License (GFDL) and the Creative Commons Attribution-Share-Alike 4.0 License”.
- **Google Books Ngram**, https://books.google.com/ngrams/info: „Ngram Viewer graphs and data may be freely used for any purpose”. Polskiego korpusu nie ma.
- **MoncoPL**: licencji nie znalazłem. Artykuł Pęzik 2020, „Filologia Łódzka”, DOI 10.31261/FL.2020.07.11: „jedynym narzędziem do udostępniania tego korpusu użytkownikom zewnętrznym jest wyszukiwarka dostępna w serwisie monco.frazeo.pl”.
- **Spokes**: licencji danych nie znalazłem (strona `spokes.clarin-pl.eu` to aplikacja JS, wiki CLARIN-PL bez treści przez WebFetch).
