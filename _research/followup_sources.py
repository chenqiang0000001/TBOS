import concurrent.futures, pathlib, sys, json, re, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
from html import unescape
ROOT=pathlib.Path(__file__).resolve().parent
ITEMS=[
 ('S26','Berkshire 2014 Munger letter','https://www.berkshirehathaway.com/letters/2014ltr.pdf'),
 ('S27','Zettelkasten practical overview','https://zettelkasten.de/overview/'),
 ('S28','Obsidian raw help','https://raw.githubusercontent.com/obsidianmd/obsidian-help/master/en/Files%20and%20folders/How%20Obsidian%20stores%20data.md'),
 ('S29','NASA lessons learned official','https://www.nasa.gov/learning-resources/nasa-lessons-learned/'),
 ('S30','NASA knowledge continuity','https://www.nasa.gov/learning-resources/knowledge-management/'),
 ('S31','ISO overview knowledge systems','https://www.iso.org/news/ref2337.html'),
 ('S32','Stripe official book text','https://www.poorcharliesalmanack.com/'),
 ('S33','Duan public account','https://xueqiu.com/1247347556'),
 ('S34','Duan Bloomberg interview search','https://www.google.com/search?q=%E6%AE%B5%E6%B0%B8%E5%B9%B3+2025+%E8%AE%BF%E8%B0%88+%E5%81%9A%E5%AF%B9%E7%9A%84%E4%BA%8B%E6%83%85&udm=14'),
 ('S35','Logseq README','https://raw.githubusercontent.com/logseq/logseq/master/README.md'),
 ('S36','LYT homepage','https://www.linkingyourthinking.com/'),
]
def get(item):
 sid,title,url=item; out=dict(id=sid,title=title,url=url)
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=18) as r: data=r.read(4000000); out.update(status=r.status,final_url=r.url,content_type=r.headers.get('Content-Type',''))
  if 'pdf' in out['content_type']:
   (ROOT/(sid+'.pdf')).write_bytes(data)
   import pymupdf
   doc=pymupdf.open(stream=data,filetype='pdf')
   text='\n'.join(p.get_text() for p in doc)
  else:
   text=data.decode('utf-8',errors='replace')
   text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',text,flags=re.S|re.I)
   text=unescape(re.sub('<[^>]+>',' ',text))
   text=re.sub(r'[ \t\r\f\v]+',' ',text)
   text=re.sub(r'\n\s*\n','\n',text)
  (ROOT/(sid+'.txt')).write_text(text,encoding='utf-8'); out['chars']=len(text)
 except Exception as e:out['error']=str(e)
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=7) as p: results=list(p.map(get,ITEMS))
(ROOT/'sources_followup.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:print(json.dumps(r,ensure_ascii=False))
