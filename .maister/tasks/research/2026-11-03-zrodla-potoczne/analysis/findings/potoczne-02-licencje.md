# potoczne-02: licencje źródeł potocznych (cytaty)

## TL;DR
- Czystą licencję tekstu i daty mają: **strony dyskusji plwiki** (CC BY-SA 4.0, podpisy z datą), **Common Voice PL** (CC0, ale tekst nie jest potoczny). BAN-PL wycofany decyzją użytkownika 2026-11-04 (autorzy chronią archiwa hasłem przed automatycznym zbieraniem); liczby usunięte.
- Licencja niekomercyjna: hate_speech_pl (CC BY-NC-SA), Spokes (CC BY-NC 3.0, **nowy fakt** wobec #16), blogi CLARIN-PL (CC BY-NC-SA / BY-NC-ND).
- Bez licencji tekstu: OpenSubtitles (OPUS: tylko prośba o link i cytowanie), fora SpeakLeash („conditional license”, „(c) …”), PolEval 2019 (licencja „unknown”).
- Regulamin zabrania: Reddit (scraping, trening ML bez zgody właścicieli), X (scraping; dalej wolno dawać tylko ID wpisów). Mowa BIGOS i PELCRA na HF: bramka → odpada.

## Kluczowe decyzje
- Licencję tekstu oceniam osobno od licencji opakowania (zasada z #16). Opakowanie MIT pakietu SpeakLeash nie obejmuje tekstów forów.
- „conditional license” i „(c) host” traktuję jak brak licencji tekstu: wolno najwyżej liczyć lokalnie (TDM, do oceny w kat. 2), nie publikować tekstu.

## Otwarte pytania i ryzyka
- OpenSubtitles: napisy to tłumaczenia filmów chronionych prawem autorskim, robione przez użytkowników. SpeakLeash podaje dla swojej kopii „Public Domain; CC BY-SA 3.0; Free Art License 1.3”. Ta licencja nie ma oparcia w OPUS ani na karcie HF („unknown”); wygląda na przepisaną z innego zbioru.
- Spokes: rekord CLARIN-PL dotyczy usługi (wyszukiwarki, `toolService`), nie wprost pliku korpusu. Czy CC BY-NC obejmuje cytowanie wyników — niepewne.
- Nie sprawdzałem regulaminów poszczególnych forów (kafeteria.pl i in.).

## Cytaty (odczyt 2026-11-03)

| Źródło | Cytat dosłowny | URL |
|---|---|---|
| OPUS OpenSubtitles | „IMPORTANT: If you use the OpenSubtitle corpus: Please, add a link to http://www.opensubtitles.org/ to your website and to your reports and publications produced with the data! I promised this when I got the data from the providers of that website!” Licencji brak. | https://opus.nlpl.eu/legacy/OpenSubtitles-v2018.php |
| HF Helsinki-NLP/open_subtitles | `license: - unknown`; „Licensing Information: [More Information Needed]” | https://huggingface.co/datasets/Helsinki-NLP/open_subtitles |
| SpeakLeash, open_subtitles_pl_corpus | `"license": "Public Domain; Creative Commons Attribution-ShareAlike 3.0; Free Art License 1.3"`, `"Source data collected from https://opus.nlpl.eu/OpenSubtitles-v2018.php"` | https://d6t0.c15.e2-2.dev/speakleash-ds-pub/datasets_text/open_subtitles_corpus.manifest |
| SpeakLeash, forum_kafeteria_pl_corpus (wzór dla forów) | `"license": "conditional license"`; „Although the robots.txt file allows for the data collection, it may not provide full rights to use them, especially if the data is copyrighted. Before using this data to train a model, it is recommended to familiarize yourself with the terms and conditions of the site…” | https://d6t0.c15.e2-2.dev/speakleash-ds-pub/datasets_text/forum_kafeteria_pl_corpus.manifest |
| SpeakLeash, pakiet | Repozytorium kodu: MIT (API GitHub `license.spdx_id = MIT`). Dotyczy kodu, nie danych. | https://github.com/speakleash/speakleash |
| PolEval 2019 zad. 6 (tweety) | Karta HF: `license: - unknown`, „[More Information Needed]”. Strona zadania: „The entries will contain tweets collected from openly available Twitter discussions.” | https://huggingface.co/datasets/poleval/poleval2019_cyberbullying ; http://2019.poleval.pl/index.php/tasks/task6 |
| hate_speech_pl | `license: - cc-by-nc-sa-3.0`; „According to Metashare, the dataset is licensed under CC-BY-NC-SA, but the version is not mentioned.” | https://huggingface.co/datasets/community-datasets/hate_speech_pl |
| PolEmo 2.0 | HF `clarin-pl/polemo2-official`: `license:cc-by-sa-4.0`; CLARIN-PL hdl 11321/710: „Creative Commons - Attribution 4.0 International (CC BY 4.0)” | https://huggingface.co/datasets/clarin-pl/polemo2-official ; http://hdl.handle.net/11321/710 |
| Common Voice, tekst zdań | „The majority of our sentence text in `/server/data` comes directly from user submissions in our Sentence Collector … and are released under a CC0 public domain Creative Commons license.” | https://github.com/common-voice/common-voice (README) |
| Wikipedia, strony dyskusji | Zrzut `plwiki-20261101-pages-meta-current*.xml.bz2`; tekst Wikipedii: CC BY-SA 4.0 (warunki Wikimedia). | https://dumps.wikimedia.org/plwiki/20261101/ |
| **Spokes (nowy fakt)** | Rekord CLARIN-PL: „Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0)”; „The underlying corpus contains more than 2 million words of time-aligned transcriptions of casual spoken discourse. The service is available both as a web application and as a REST service.” | http://hdl.handle.net/11321/47 |
| Mowa Wrocławia lat 80. | „Creative Commons - Attribution 4.0 International (CC BY 4.0)”; nagrania z lat 80. | http://hdl.handle.net/11321/548 |
| Blogs_2018 (CLARIN-PL) | „Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)”, „Teksty z blogów książkowych” | http://hdl.handle.net/11321/456 |
| Korpus forum klientów banku | „Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY-NC-ND 3.0)” (2017) | http://hdl.handle.net/11321/417 |
| Komentarze YouTube (próbny) | „Attribution-NonCommercial-NoDerivs 3.0 Unported (CC BY-NC-ND 3.0)” (2016) | http://hdl.handle.net/11321/485 |
| Reddit Data API Terms (Last Revised July 20, 2026) | „no other rights or licenses are granted or implied, including any right to use User Content for other purposes, such as for training a machine learning or AI model, without the express permission of rightsholders in the applicable User Content.” oraz „If you are interested in using the Data APIs for commercial purposes, research in excess of rate limits … you will need to enter into a separate agreement with Reddit.” | https://redditinc.com/policies/data-api-terms |
| Reddit User Agreement (Effective July 1, 2026) | „we conditionally grant permission to crawl the Services in accordance with the parameters set forth in our robots.txt file, but scraping the Services without Reddit's prior written consent is prohibited” | https://redditinc.com/policies/user-agreement |
| X Developer Agreement | „If you provide X Content to third parties, including downloadable datasets or via an API, you may only distribute Post IDs, Direct Message IDs, and/or User IDs” | https://developer.x.com/en/developer-terms/agreement-and-policy |
| X Terms of Service (Effective October 9, 2026) | „crawling or scraping the Services in any form, for any purpose without our prior written consent is expressly prohibited” | https://x.com/en/tos |
| BIGOS v2, PELCRA for BIGOS | HF: `amu-cai/pl-asr-bigos-v2` `gated: auto` (CC BY-SA 4.0); `pelcra/pl-asr-pelcra-for-bigos` `gated: auto` (CC BY-NC-ND 4.0). Bramka = konto → odpada. | https://huggingface.co/api/datasets?search=pl-asr-bigos |
