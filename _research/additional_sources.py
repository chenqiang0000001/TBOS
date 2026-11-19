import concurrent.futures, urllib.request, urllib.parse, pathlib, sys, json, re
from html import unescape
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent
ITEMS=[
 ('S37','Alavi Leidner knowledge management review','https://aisel.aisnet.org/misq/vol25/iss1/2/'),
 ('S38','Crossref scholarly metadata','https://api.crossref.org/works/10.2307/3250961'),
 ('S39','Gneiting Raftery scoring rules paper','https://stat.uw.edu/research/tech-reports/strictly-proper-scoring-rules-prediction-and-estimation'),
 ('S40','Farnam Street decision journal','https://fs.blog/decision-journal/'),
 ('S41','Derek Sivers public book notes','https://sive.rs/book'),
 ('S42','Duan search Sogou','https://www.sogou.com/web?query='+urllib.parse.quote('段永平 做对的事情 把事情做对 浙大 访谈')),
 ('S43','Duan search Baidu','https://www.baidu.com/s?wd='+urllib.parse.quote('段永平 浙江大学 2025 访谈 投资')),
 ('S44','Luhmann translated original essay','https://luhmann.surge.sh/communicating-with-slip-boxes'),
 ('S45','Poor Charlie electronic book','https://www.stripe.press/poor-charlies-almanack/introduction'),
]
def get(item):
 sid,title,url=item; out=dict(id=sid,title=title,url=url)
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18) as r:
   raw=r.read(2500000).decode('utf-8',errors='replace');out.update(status=r.status,final_url=r.url)
  links=re.findall(r'href=[\"\']([^\"\']+)',raw)
  if sid=='S38':
   obj=json.loads(raw)['message']; raw=json.dumps({k:obj.get(k) for k in ['title','author','published','DOI','URL','abstract','link']},ensure_ascii=False,indent=2)
  s=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',raw,flags=re.S|re.I)
  s=unescape(re.sub('<[^>]+>',' ',s));s=re.sub(r'[ \t\r\f\v]+',' ',s);s=re.sub(r'\n\s*\n','\n',s)
  (ROOT/(sid+'.txt')).write_text(s,encoding='utf-8');out['chars']=len(s)
  (ROOT/(sid+'_links.json')).write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf-8')
 except Exception as e:out['error']=str(e)
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as p: results=list(p.map(get,ITEMS))
(ROOT/'sources_additional.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:print(json.dumps(r,ensure_ascii=False))
