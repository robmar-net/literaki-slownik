"""Odtwarza pomocniczą próbkę kontekstów i liczby NKJP; bez tekstów w wynikach Git."""
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent / 'findings'
sys.path.insert(0, str(ROOT))
from literaki_slownik.pop import read_nkjp


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


path = ROOT / 'cache/nkjp/1grams.gz'
assert digest(path) == '73af49094621b2f86b594beba783c14aee8c8212f1aff3d61f281ab5d99e3dc9'
words = set('desperacja ekscytacją niezbędnik familia odzienie surdut aliści jakoż iże nazad trzykroć sek ali'.split())
result = read_nkjp(path, 'strip-edges-keep-dot', words)
result = {k:v for k,v in result.items() if k not in {'merged','path'}}
result['source'] = 'https://zil.ipipan.waw.pl/NKJPNGrams'
result['source_sha256'] = digest(path)
(OUT/'nkjp-examples.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')

path = ROOT/'tmp/kwjp-halfm-samples.tar.gz'
assert digest(path) == 'aedad77022508fe10d0d537e6a082884b8e7a97d4836a184ff744a5261db55b1'
rx = re.compile(r'\b(?:desperacj\w*|ekscytacj\w*|niezbędnik\w*|famili\w*|odzien\w*|surdut\w*|aliści|jakoż|iże|nazad|trzykroć)\b', re.I)
judgments = {
 '136430': ('żywe_nacechowane', 'Rodzina w narracji o współczesnym życiu; fikcja.'),
 '136715': ('historyczny_desygnat', 'Ubranie w powieści historycznej; to nie dowodzi neutralnego rejestru.'),
 '136888': ('nacechowane', 'Eseistyczny opis używa odzienia; nie rozstrzyga jego neutralności.'),
 '208998': ('nietrafienie', 'familijne jest innym leksemem; wyłączone z 12 właściwych trafień.'),
 '136485': ('stylizacja', 'Scena z tronem i strażnikami; słowo odzienie jest częścią nacechowanej narracji.'),
 '136594': ('stylizacja', 'iże w stylizowanej wypowiedzi bohatera, obok gwarowych i dawnych środków.'),
 '228537': ('żywe_nacechowane', 'familia oznacza rodzinę w narracji fikcyjnej.'),
 '142821': ('żywe', 'desperacji w wywiadzie o szukaniu szkoły, gatunek fakt.'),
 '140696': ('żywe', 'ekscytację w opisie oddziaływania barw, gatunek fakt.'),
 '138284': ('żywe', 'desperacji w recenzji filmu; próbka przypisana do fikcji mimo recenzenckiej treści.'),
 '136342': ('żywe_nacechowane', 'familii w metaforycznym określeniu środowiska Radia Maryja, biografia.'),
 '136252': ('dawny_język', 'jakoż obok onych/nieochędożone/absentować w pracy historycznej; prawdopodobny cytat, wymaga pełnego tekstu do potwierdzenia.'),
 '136378': ('niejednoznaczne', 'Niezbędnik w nawiasie i wielką literą; odsyłacz/nazwa, brak dowodu zwykłego użycia.'),
}
hits = []
count = 0
with tarfile.open(path) as archive:
    for member in archive:
        if not member.isfile():
            continue
        count += 1
        record = json.load(archive.extractfile(member))
        for index, sample in enumerate(record.get('samples', [])):
            matched = rx.findall(sample['text'])
            if matched:
                category, note = judgments[record['meta']['id']]
                hits.append({'file':member.name, 'sample_index':index, 'matches':matched,
                  'bibliography':record['meta'], 'review':category, 'note':note})
(OUT/'context-review.json').write_text(json.dumps({'source':
 'https://github.com/ipipan/kwjp100-varia/tree/26d82bd8b906dfed1cfcf8f903b1650b56daeabf/KWJP%C2%BDM',
 'source_sha256':digest(path), 'files_inspected':count,'hits':hits,
 'scope':'Własny jakościowy przegląd małej publicznej próbki, bez statystycznej ekstrapolacji i bez redystrybucji tekstów.'},ensure_ascii=False,indent=2)+'\n')
print('NKJP i konteksty: gotowe;', count, 'plików,', len(hits), 'trafień regex.')
