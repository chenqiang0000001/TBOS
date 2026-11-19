import concurrent.futures
import json
import pathlib
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent
DOIS=[
 ('P01','10.1037/bul0000365'),
 ('P02','10.1037/0033-2909.132.1.1'),
 ('P03','10.1037/a0024950'),
 ('P04','10.1111/bjso.12251'),
 ('P05','10.1073/pnas.1908430116'),
 ('P06','10.1037/a0014996'),
 ('P07','10.1037/pspp0000102'),
 ('P08','10.1177/0956797617739704'),
 ('P09','10.1037/0022-3514.80.6.1011'),
 ('P10','10.1177/0963721413475622'),
 ('P11','10.1037/pspp0000096'),
]
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=18) as res:return json.loads(res.read())

def work(item):
    sid,doi=item
    result={'id':sid,'doi':doi}
    try:
        raw=get('https://api.openalex.org/works/https://doi.org/'+doi)
        (ROOT/(sid+'_openalex.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
        inverted=raw.get('abstract_inverted_index') or {}
        words={pos:word for word,positions in inverted.items() for pos in positions}
        abstract=' '.join(words[x] for x in sorted(words))
        result.update(title=raw.get('title'),abstract=abstract,open_access=raw.get('open_access'),locations=[x.get('landing_page_url') for x in raw.get('locations',[])],pdfs=[x.get('pdf_url') for x in raw.get('locations',[]) if x.get('pdf_url')])
    except Exception as e:result['openalex_error']=str(e)
    try:
        raw=get('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe=''))['message']
        (ROOT/(sid+'_crossref.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
        result['crossref']={k:raw.get(k) for k in ['title','abstract','published','author','URL','link']}
    except Exception as e:result['crossref_error']=str(e)
    (ROOT/(sid+'_metadata.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(work,DOIS))
(ROOT/'academic_metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for x in results:
    print(json.dumps(x,ensure_ascii=False))
