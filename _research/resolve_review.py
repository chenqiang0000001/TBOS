import pathlib, urllib.request, re, sys
from html import unescape
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path(__file__).resolve().parent
url='https://aisel.aisnet.org/misq/vol25/iss1/'
with urllib.request.urlopen(url,timeout=15) as r:s=r.read().decode('utf-8',errors='replace')
for m in re.finditer(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>',s,re.S|re.I):
 text=unescape(re.sub('<[^>]+>',' ',m.group(2)))
 if 'Knowledge Management' in text:
  target=m.group(1);print(target+' '+text)
  with urllib.request.urlopen(target,timeout=15) as r:raw=r.read().decode('utf-8',errors='replace')
  text=unescape(re.sub('<[^>]+>',' ',re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',raw,flags=re.S|re.I)))
  text=re.sub(r'\s+',' ',text)
  (root/'S49.txt').write_text(text,encoding='utf-8')
  (root/'S49_url.txt').write_text(target,encoding='utf-8')
  at=text.find('Abstract');print(text[at:at+3200])
