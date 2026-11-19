import concurrent.futures
import html
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = [
 ('P01', 'Personality stability and change 2022', 'https://doi.apa.org/doi/10.1037/bul0000365'),
 ('P02', 'Patterns of mean-level change 2006', 'https://doi.apa.org/doi/10.1037/0033-2909.132.1.1'),
 ('P03', 'Life course and life events 2011', 'https://doi.apa.org/doi/10.1037/a0024950'),
 ('P04', 'Psychology of social class 2018', 'https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bjso.12251'),
 ('P05', 'Conscientiousness at work 2019', 'https://www.pnas.org/doi/10.1073/pnas.1908430116'),
 ('P06', 'Personality academic performance 2009', 'https://doi.apa.org/doi/10.1037/a0014996'),
 ('P07', 'Grit meta-analysis 2017', 'https://doi.apa.org/doi/10.1037/pspp0000102'),
 ('P08', 'Growth mindset meta-analyses 2018', 'https://journals.sagepub.com/doi/10.1177/0956797617739704'),
 ('P09', 'Traits as distributions of states 2001', 'https://doi.apa.org/doi/10.1037/0022-3514.80.6.1011'),
 ('P10', 'Narrative identity 2013', 'https://journals.sagepub.com/doi/10.1177/0963721413475622'),
 ('P11', 'BFI-2 author university', 'https://www.colby.edu/psych/personality-lab/'),
 ('P12', 'National school mindset experiment 2019', 'https://www.nature.com/articles/s41586-019-1466-y'),
 ('Q01', 'Search personality meta 2022', 'https://www.google.com/search?q='+urllib.parse.quote('"Personality stability and change" "2022" meta analysis')),
 ('Q02', 'Search social class Manstead', 'https://www.google.com/search?q='+urllib.parse.quote('"Manstead" "2018" "social class"')),
 ('Q03', 'Search mindset meta statistics', 'https://www.google.com/search?q='+urllib.parse.quote('"Sisk" "2018" "365,915"')),
 ('Q04', 'Search conscientiousness statistics', 'https://www.google.com/search?q='+urllib.parse.quote('"Wilmot" "Ones" "2019" "92"')),
]

def fetch(item):
    sid, title, url = item
    info = {'id': sid, 'title': title, 'url': url}
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0', 'Accept':'text/html,application/json'})
        with urllib.request.urlopen(req, timeout=24) as res:
            data = res.read(3500000)
            info.update(status=res.status, final_url=res.url, content_type=res.headers.get('Content-Type',''))
        if 'pdf' in info['content_type']:
            info['pdf_not_processed'] = True
            return info
        raw = data.decode('utf-8', errors='replace')
        (ROOT/(sid+'.html')).write_text(raw, encoding='utf-8')
        links = [{'url':html.unescape(href), 'label':html.unescape(re.sub('<[^>]+>', ' ', label)).strip()} for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', raw, re.S|re.I)]
        (ROOT/(sid+'_links.json')).write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
        text = re.sub(r'<(script|style|noscript)\b[^>]*>.*?</\1>', ' ', raw, flags=re.S|re.I)
        text = re.sub(r'</(?:p|div|section|h[1-6]|li|article|tr)>|<br\s*/?>', '\n', text, flags=re.I)
        text = html.unescape(re.sub('<[^>]+>', ' ', text))
        text = '\n'.join(re.sub(r'\s+', ' ', line).strip() for line in text.splitlines() if line.strip())
        (ROOT/(sid+'.txt')).write_text(text, encoding='utf-8')
        info['characters'] = len(text)
        info['preview'] = text[:350]
    except Exception as e:
        info['error'] = str(e)
    return info

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch,SOURCES))
    (ROOT/'sources_primary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    for result in results:
        print(json.dumps(result,ensure_ascii=False))
