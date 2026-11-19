import concurrent.futures, urllib.request, urllib.parse, xml.etree.ElementTree as ET, json, pathlib
QUERIES=[
 '段永平 新浪博客 做对的事情 把事情做对 原文',
 '段永平 2025 2024 访谈 能力圈 不懂不做 网易',
 'site.stripe.press poor charlie almanack mental models',
 'site.linkingyourthinking.com LYT kit download',
 'site.km.nasa.gov knowledge policy lessons learned',
 'site.johnnydecimal.com introduction structure',
]
def run(q):
 try:
  url='https://www.bing.com/search?format=rss&q='+urllib.parse.quote(q)
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=20) as r: root=ET.fromstring(r.read())
  return {'query':q,'results':[{'title':x.findtext('title'),'link':x.findtext('link'),'description':x.findtext('description')} for x in root.findall('.//item')[:6]]}
 except Exception as e:return {'query':q,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(run,QUERIES))
pathlib.Path(__file__).with_name('search_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for result in results: print(json.dumps(result,ensure_ascii=False))
