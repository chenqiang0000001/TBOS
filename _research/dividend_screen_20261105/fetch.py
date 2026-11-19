import concurrent.futures, datetime, json, re, sys, urllib.request, urllib.parse
from html.parser import HTMLParser
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden=0; self.parts=[]; self.links=[]; self.a=None
    def handle_starttag(self, tag, attrs):
        at=dict(attrs)
        if tag in ('script','style'): self.hidden+=1
        if tag=='a': self.a=[at.get('href',''),'']
    def handle_endtag(self, tag):
        if tag in ('script','style') and self.hidden: self.hidden-=1
        if tag=='a' and self.a: self.links.append(self.a); self.a=None
    def handle_data(self, data):
        if self.hidden: return
        s=' '.join(data.split())
        if s: self.parts.append(s)
        if self.a: self.a[1]+=s+' '

def fetch(job):
    key,url=job
    out=dict(id=key,url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=16) as r:
            raw=r.read(3000000)
            (ROOT/(key+'.raw')).write_bytes(raw)
            meta=re.search(br'charset\s*=\s*[\"\x27]?([A-Za-z0-9_-]+)',raw[:20000],re.I)
            enc=meta.group(1).decode('ascii') if meta else r.headers.get_content_charset() or ('gb18030' if 'gtimg' in url else 'utf-8')
            text=raw.decode(enc,errors='replace')
            out.update(status=r.status,final_url=r.url,encoding=enc)
            if 'html' in (r.headers.get('Content-Type') or '') or '<html' in text[:1000].lower():
                p=Page(); p.feed(text)
                (ROOT/(key+'.html')).write_text(text,encoding='utf-8')
                text='\n'.join(p.parts)
                out['links']=[dict(text=t.strip(),url=urllib.parse.urljoin(r.url,h)) for h,t in p.links if re.search(r'dividend|distribution|repurchas|buyback|2026|2025|quarter|annual|result|earning|financial|stock|report',h+' '+t,re.I)][:100]
            (ROOT/(key+'.txt')).write_text(text,encoding='utf-8')
            out.update(text_length=len(text),excerpt=text[:450])
    except Exception as exc: out['error']=str(exc)
    return out

if __name__=='__main__':
    if len(sys.argv)>1:
        jobs=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        name=Path(sys.argv[1]).stem+'_results.json'
    else:
        jobs=[
          ['QUOTES','https://qt.gtimg.cn/q=usMO,usBTI,usEPD,usMPLX,usVZ,usUPS,hk00303,hk00941,hk00883,hk01088,hk00386,hk00005,hk01308'],
          ['MO','https://investor.altria.com/'],
          ['BTI','https://www.bat.com/investors-and-reporting'],
          ['EPD','https://ir.enterpriseproducts.com/'],
          ['MPLX','https://ir.mplx.com/'],
          ['VZ','https://www.verizon.com/about/investors/stock-information/dividend-history'],
          ['UPS','https://investors.ups.com/'],
          ['VTECH','https://www.vtech.com/en/investors/'],
          ['CM','https://www.chinamobileltd.com/en/ir/dividends.php'],
          ['SINOPEC','https://www.sinopec.com/listco/en/'],
          ['HSBC','https://www.hsbc.com/investors'],
          ['SHENHUA','https://www.csec.com/zgshwwEn/investorRelations/investorRelations.shtml'],
          ['SITC','https://www.sitc.com/en/investor-relations/']
        ]
        name='initial_sources.json'
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(fetch,jobs))
    (ROOT/name).write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    for e in results:
        print(json.dumps({k:v for k,v in e.items() if k!='links'},ensure_ascii=False))
        if 'links' in e: print(json.dumps(dict(id=e['id'],links=e['links'][:9]),ensure_ascii=False))
