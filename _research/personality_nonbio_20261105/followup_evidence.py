import concurrent.futures
import json
import urllib.parse
import urllib.request
from fetch_evidence import fetch, ROOT

sources=[
 ('P05A','Conscientiousness at work open full text','https://pmc.ncbi.nlm.nih.gov/articles/PMC6859351/'),
 ('P04A','Social class open full text','https://pmc.ncbi.nlm.nih.gov/articles/PMC5901394/'),
 ('P11A','BFI-2 university repository','https://escholarship.org/uc/item/16x6n05t'),
 ('P03A','Life events social panel repository','https://ideas.repec.org/p/diw/diwsop/diw_sp377.html'),
 ('P01A','Personality stability university repository','https://www.zora.uzh.ch/handle/20.500.14742/207266'),
]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(fetch,sources))
(ROOT/'sources_followup.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for result in results:print(json.dumps(result,ensure_ascii=False))

query='Personality trait changes following life events A meta-analysis'
url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.title':query,'rows':2})
try:
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=18) as res:raw=json.loads(res.read())
    items=raw['message']['items']
    (ROOT/'life_events_search.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
    for x in items:print(json.dumps({k:x.get(k) for k in ['title','DOI','published','abstract','author']},ensure_ascii=False))
except Exception as e:print('life events metadata error: '+str(e))
