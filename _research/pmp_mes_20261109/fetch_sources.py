from pathlib import Path
from html.parser import HTMLParser
import urllib.request, urllib.parse, json, sys, datetime
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
BASE=Path(__file__).resolve().parent
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[];self.links=[];self.hidden=0;self.a=None
    def handle_starttag(self,t,a):
        a=dict(a)
        if t in ('script','style'): self.hidden+=1
        if t=='a':self.a=[a.get('href',''),'']
    def handle_endtag(self,t):
        if t in ('script','style') and self.hidden:self.hidden-=1
        if t=='a' and self.a:self.links.append(self.a);self.a=None
    def handle_data(self,s):
        if self.hidden:return
        s=' '.join(s.split())
        if s:self.parts.append(s)
        if self.a:self.a[1]+=s+' '
def fetch(item):
    name,url=item
    out={'id':name,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as r:
            raw=r.read(6000000);ct=r.headers.get('content-type','');enc=r.headers.get_content_charset() or 'utf-8'
            (BASE/(name+'.raw')).write_bytes(raw)
            out.update(status=r.status,final_url=r.url,content_type=ct)
            if 'pdf' in ct:
                (BASE/(name+'.pdf')).write_bytes(raw)
                from pypdf import PdfReader
                doc=PdfReader(BASE/(name+'.pdf'))
                txt='\n\n'.join('PAGE '+str(i+1)+'\n'+(p.extract_text() or '') for i,p in enumerate(doc.pages))
                out['pages']=len(doc.pages)
            else:
                html=raw.decode(enc,errors='replace');(BASE/(name+'.html')).write_text(html,encoding='utf-8')
                p=Extract();p.feed(html);txt='\n'.join(p.parts)
                out['links']=[{'text':t.strip(),'url':urllib.parse.urljoin(r.url,h)} for h,t in p.links]
            (BASE/(name+'.txt')).write_text(txt,encoding='utf-8');out['text_chars']=len(txt)
    except Exception as e:out['error']=str(e)
    return out
if __name__=='__main__':
    jobs=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')) if len(sys.argv)>1 else [
      ['PMI_PMP','https://www.pmi.org/certifications/project-management-pmp'],
      ['PMI_NEW','https://www.pmi.org/certifications/project-management-pmp/new-exam'],
      ['CHINA_EXAM','https://event.chinapmp.cn/']]
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,jobs))
    dest=BASE/((Path(sys.argv[1]).stem if len(sys.argv)>1 else 'initial')+'_results.json')
    dest.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in results:
        print(json.dumps({k:v for k,v in r.items() if k!='links'},ensure_ascii=False))
        if 'links'in r:print(json.dumps([x for x in r['links'] if any(s in (x['text']+' '+x['url']).lower() for s in ['2026','eligib','exam','handbook','audit','application','报考','报名','条件'])][:35],ensure_ascii=False))
