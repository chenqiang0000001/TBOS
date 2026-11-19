import concurrent.futures
import json
import pathlib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent
TITLES = [
    'Personality stability and change A meta-analysis of longitudinal studies Bleidorn 2022',
    'Patterns of mean-level change in personality traits across the life course A meta-analysis of longitudinal studies Roberts Walton Viechtbauer',
    'Stability and change of personality across the life course The impact of age and major life events Specht Egloff Schmukle',
    'The psychology of social class How socioeconomic status impacts thought feelings and behaviour Manstead',
    'A century of research on conscientiousness at work Wilmot Ones',
    'A meta-analysis of the five-factor model of personality and academic performance Poropat',
    'Much ado about grit A meta-analytic synthesis of the grit literature Crede Tynan Harms',
    'To What Extent and Under Which Circumstances Are Growth Mind-Sets Important to Academic Achievement Two Meta-Analyses Sisk',
    'Toward a structure- and process-integrated view of personality Traits as density distributions of states Fleeson',
    'Narrative identity McAdams McLean 2013',
    'The next Big Five Inventory BFI-2 Developing and assessing a hierarchical model with 15 facets Soto John',
    'A national experiment reveals where a growth mindset improves achievement Yeager 2019',
]
SEARCHES = [
    'Bleidorn 2022 personality stability change meta-analysis 189 276 178503 242542',
    'Wilmot Ones 2019 conscientiousness work 92 meta analyses 1.1 million',
    'Poropat 2009 personality academic performance 70000 meta analysis conscientiousness',
    'Sisk 2018 growth mindset meta analyses 365915 effect 0.10 0.08',
    'Specht Egloff Schmukle 2011 personality life events 14718',
    'Manstead psychology social class socioeconomic status 2018 review',
    'Crede Tynan Harms 2017 grit 66807 88 conscientiousness',
    'Soto John BFI-2 official questionnaire 60 items Chinese',
]

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (nonbiological social-science evidence review)', 'Accept': 'application/json,text/html,application/xml'})
    with urllib.request.urlopen(req, timeout=22) as res:
        return res.read(), res.url

def crossref(title):
    try:
        data, _ = get('https://api.crossref.org/works?' + urllib.parse.urlencode({'query.bibliographic': title, 'rows': 2}))
        items = json.loads(data)['message']['items']
        return {'query': title, 'matches': [{k: x.get(k) for k in ['title', 'DOI', 'URL', 'container-title', 'published', 'abstract', 'link', 'resource']} for x in items]}
    except Exception as e:
        return {'query': title, 'error': str(e)}

def search(query):
    try:
        data, _ = get('https://www.bing.com/search?format=rss&q=' + urllib.parse.quote(query))
        root = ET.fromstring(data)
        return {'query': query, 'results': [{k: x.findtext(k) for k in ['title', 'link', 'description']} for x in root.findall('.//item')[:5]]}
    except Exception as e:
        return {'query': query, 'error': str(e)}

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    metadata = list(pool.map(crossref, TITLES))
    searches = list(pool.map(search, SEARCHES))
(ROOT / 'crossref.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'searches.json').write_text(json.dumps(searches, ensure_ascii=False, indent=2), encoding='utf-8')
for result in metadata:
    print(json.dumps(result, ensure_ascii=False))
for result in searches:
    print(json.dumps({'query': result['query'], 'results': result.get('results', [])[:3], 'error': result.get('error')}, ensure_ascii=False))
