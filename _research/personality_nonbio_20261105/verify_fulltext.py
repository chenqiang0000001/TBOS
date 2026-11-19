import concurrent.futures
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from fetch_evidence import ROOT

sys.stdout.reconfigure(encoding='utf-8')
def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=22) as res:return res.read()

def fulltext(item):
    sid,pmc=item
    url='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML'
    info={'id':sid,'url':url}
    try:
        raw=get(url)
        (ROOT/(sid+'.xml')).write_bytes(raw)
        root=ET.fromstring(raw)
        blocks=[]
        for elem in root.iter():
            if elem.tag in ['article-title','title','p','table','table-wrap-foot']:
                text=' '.join(''.join(elem.itertext()).split())
                if text:blocks.append(text)
        (ROOT/(sid+'.txt')).write_text('\n'.join(blocks),encoding='utf-8')
        info['paragraphs']=len(blocks)
        info['preview']=blocks[:3]
    except Exception as e:info['error']=str(e)
    return info
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(fulltext,[('P05B','PMC6859351'),('P04B','PMC5901394')]))
(ROOT/'sources_fulltext.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for x in results:print(json.dumps(x,ensure_ascii=False))

query='Buhler Mund Zimmermann Wrzus Roberts life events personality meta analysis'
url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':query,'rows':5})
try:
    items=json.loads(get(url))['message']['items']
    (ROOT/'life_events_search2.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
    for x in items:print(json.dumps({k:x.get(k) for k in ['title','DOI','published','abstract']},ensure_ascii=False))
except Exception as e:print('lookup error: '+str(e))
