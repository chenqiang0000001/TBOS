import concurrent.futures, urllib.request, pathlib, sys, json, re
from html import unescape
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent
ITEMS=[
 ('S46','Munger 1994 speech transcript','https://fs.blog/great-talks/a-lesson-on-worldly-wisdom/'),
 ('S47','NIST generative AI profile','https://airc.nist.gov/docs/NIST.AI.600-1.GenAI-Profile.ipd.pdf'),
 ('S48','Proper scoring paper DOI metadata','https://api.crossref.org/works/10.1198/016214506000001437'),
]
def get(item):
 sid,title,url=item; out=dict(id=sid,title=title,url=url)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18) as r:
   if 'pdf' in r.headers.get('Content-Type',''): return dict(out,status=r.status,note='PDF not used')
   raw=r.read(2500000).decode('utf-8',errors='replace');out.update(status=r.status,final_url=r.url)
  if sid=='S48':
   obj=json.loads(raw)['message'];raw=json.dumps({k:obj.get(k) for k in ['title','author','published','DOI','URL','abstract']},ensure_ascii=False,indent=2)
  s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',raw,flags=re.S|re.I)
  s=unescape(re.sub('<[^>]+>',' ',s));s=re.sub(r'[ \t\r\f\v]+',' ',s);s=re.sub(r'\n\s*\n','\n',s)
  (ROOT/(sid+'.txt')).write_text(s,encoding='utf-8');out['chars']=len(s)
 except Exception as e:out['error']=str(e)
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p: results=list(p.map(get,ITEMS))
(ROOT/'sources_final.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:print(json.dumps(r,ensure_ascii=False))
