import concurrent.futures
import html
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding='utf-8')

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ignored = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.ignored += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript'):
            self.ignored = max(0, self.ignored - 1)
    def handle_data(self, data):
        if not self.ignored and data.strip():
            self.parts.append(data.strip())

ROOT = pathlib.Path(__file__).with_name('reading_notes_20261109')
ROOT.mkdir(exist_ok=True)
SOURCES = [
    ('R01', 'Meadows: Leverage Points', 'https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/'),
    ('R02', 'Bank of England: Money creation in the modern economy', 'https://www.bankofengland.co.uk/quarterly-bulletin/2014/q1/money-creation-in-the-modern-economy'),
    ('R03', 'FINRA: Investing with borrowed funds', 'https://www.finra.org/investors/insights/investing-borrowed-funds-no-shares-your-risk'),
    ('R04', 'Brown et al: Meta-analysis of empirical estimates of loss aversion', 'https://www.aeaweb.org/articles?id=10.1257/jel.20221698'),
    ('R05', 'Nobel: Contract theory scientific background 2016', 'https://www.nobelprize.org/uploads/2018/06/advanced-economicsciences2016.pdf'),
    ('R06', 'Lazear: Performance Pay and Productivity', 'https://www.nber.org/papers/w5672'),
    ('R07', 'Bloom et al: Does Management Matter? Evidence from India', 'https://www.nber.org/papers/w16658'),
    ('R08', 'OECD: Hours worked', 'https://www.oecd.org/en/data/indicators/hours-worked.html'),
    ('R09', 'Cerasoli et al: Intrinsic motivation and extrinsic incentives jointly predict performance', 'https://doi.org/10.1037/a0035661'),
    ('R10', 'Cesarini et al: Wealth and labor supply Swedish lotteries', 'https://www.aeaweb.org/articles?id=10.1257/aer.20151589'),
]
QUERIES = [
    'Brown Imai Vieider Camerer 2024 meta analysis loss aversion 607 estimates 2.1',
    'Cerasoli Nicklin Ford 2014 intrinsic motivation extrinsic incentives performance quantity quality meta analysis',
    'Cesarini Lindqvist Notowidigdo Ostling wealth labor supply Swedish lotteries 2017 labor earnings',
    'Walasek Mullett Stewart 2024 meta analysis loss aversion risky contexts 102740',
]

def fetch(source):
    sid, title, url = source
    row = {'id': sid, 'title': title, 'url': url}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=25) as response:
            content = response.read()
            row.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type', ''))
        if 'pdf' in row['content_type'] or content[:4] == b'%PDF':
            (ROOT / (sid + '.pdf')).write_bytes(content)
            try:
                from pypdf import PdfReader
                text = '\n'.join(page.extract_text() or '' for page in PdfReader(ROOT / (sid + '.pdf')).pages)
            except Exception as error:
                text = str(error)
        else:
            raw = content.decode('utf-8', errors='replace')
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(raw, 'html.parser')
                for tag in soup(['script', 'style', 'noscript', 'nav', 'footer', 'header']):
                    tag.decompose()
                text = soup.get_text('\n', strip=True)
            except ImportError:
                parser = TextParser()
                parser.feed(raw)
                text = '\n'.join(parser.parts)
        (ROOT / (sid + '.txt')).write_text(text, encoding='utf-8')
        row['chars'] = len(text)
        row['preview'] = text[:450]
    except Exception as error:
        row['error'] = str(error)
    return row

def search(query):
    row = {'query': query}
    try:
        import xml.etree.ElementTree as ET
        url = 'https://www.bing.com/search?format=rss&q=' + urllib.parse.quote(query)
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=25) as response:
            root = ET.fromstring(response.read())
        row['results'] = [{'title': node.findtext('title'), 'url': node.findtext('link'), 'description': node.findtext('description')} for node in root.findall('.//item')[:5]]
    except Exception as error:
        row['error'] = str(error)
    return row

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        sources = list(pool.map(fetch, SOURCES))
        searches = list(pool.map(search, QUERIES))
    (ROOT / 'sources.json').write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'searches.json').write_text(json.dumps(searches, ensure_ascii=False, indent=2), encoding='utf-8')
    for row in sources + searches:
        print(json.dumps(row, ensure_ascii=False))
