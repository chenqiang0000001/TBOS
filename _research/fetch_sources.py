import concurrent.futures, json, pathlib, re, urllib.request, time
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = [
('S01','Meadows leverage points','https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/'),
('S02','Meadows dancing with systems','https://donellameadows.org/archives/dancing-with-systems/'),
('S03','Berkshire 1996 shareholder letter','https://www.berkshirehathaway.com/letters/1996.html'),
('S04','Poor Charlie official publisher','https://www.stripe.press/poor-charlies-almanack'),
('S05','Duan original public blog','https://blog.sina.com.cn/s/blog_49eea45a0100pffv.html'),
('S06','Dweck growth mindset HBR','https://hbr.org/2016/01/what-having-a-growth-mindset-actually-means'),
('S07','ISO 30401','https://www.iso.org/standard/68683.html'),
('S08','NIST Baldrige values','https://www.nist.gov/baldrige/core-values-and-concepts'),
('S09','NASA knowledge policy','https://km.nasa.gov/knowledge-policy/'),
('S10','PARA original author','https://fortelabs.com/blog/para/'),
('S11','CODE original author','https://fortelabs.com/blog/basboverview/'),
('S12','Andy Matuschak evergreen notes','https://notes.andymatuschak.org/Evergreen_notes'),
('S13','Luhmann archive','https://niklas-luhmann-archiv.de/'),
('S14','LYT starter kit','https://www.linkingyourthinking.com/lyt-kit'),
('S15','Johnny Decimal official','https://johnnydecimal.com/10-19-concepts/11-core/11.01-introduction/'),
('S16','Obsidian storage help','https://help.obsidian.md/Files+and+folders/How+Obsidian+stores+data'),
('S17','Logseq repository','https://api.github.com/repos/logseq/logseq'),
('S18','Digital garden Maggie Appleton','https://maggieappleton.com/garden-history'),
('S19','Notion export official','https://www.notion.com/help/export-your-content'),
('S20','Brier score mathematical definition','https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html'),
('S21','NIST AI risk management','https://www.nist.gov/itl/ai-risk-management-framework'),
('S22','Daniel Miessler Fabric repository','https://api.github.com/repos/danielmiessler/fabric'),
('S23','Ness Labs digital garden','https://nesslabs.com/digital-garden-set-up'),
('S24','Berkshire 1986 letter','https://www.berkshirehathaway.com/letters/1986.html'),
('S25','Mindset publisher','https://www.penguinrandomhouse.com/books/44330/mindset-by-carol-s-dweck-phd/'),
]

def fetch(item):
    sid, title, url = item
    out = dict(id=sid, title=title, url=url)
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; knowledge-system-review/1.0)','Accept':'text/html,application/json'})
        with urllib.request.urlopen(req,timeout=22) as res:
            data=res.read(2500000)
            out.update(status=res.status, final_url=res.url, content_type=res.headers.get('Content-Type',''))
        text=data.decode('utf-8', errors='replace')
        if 'json' in out['content_type']:
            obj=json.loads(text)
            text=json.dumps({k:obj.get(k) for k in ['full_name','description','html_url','homepage','updated_at','pushed_at','archived','default_branch']},ensure_ascii=False,indent=2)
        else:
            text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>',' ',text,flags=re.S|re.I)
            text=re.sub(r'</(p|div|h[1-6]|li|section|article|br)>','\n',text,flags=re.I)
            text=unescape(re.sub('<[^>]+>',' ',text))
            text='\n'.join(re.sub(r'\s+',' ',x).strip() for x in text.splitlines() if x.strip())
        path=ROOT/(sid+'.txt'); path.write_text(text,encoding='utf-8')
        out['chars']=len(text)
    except Exception as e:
        out['error']=str(e)
    return out

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(fetch,SOURCES))
(ROOT/'sources.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results: print(json.dumps(r,ensure_ascii=False))
