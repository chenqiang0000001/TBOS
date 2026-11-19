import pathlib, zipfile, xml.etree.ElementTree as ET, hashlib, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/'_research'/'personal_import_20261105'
OUT.mkdir(exist_ok=True)
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W='{'+NS['w']+'}'
order={'一':1,'二':2,'三':3,'四':4,'五':5,'六':6}
files=sorted((ROOT/'AI对话信息收集').glob('*.docx'),key=lambda p:order.get(p.stem[-1],99))
manifest=[]
for idx,p in enumerate(files,1):
 raw=p.read_bytes(); sid=f'SRC-20261105-{idx:03d}'
 with zipfile.ZipFile(p) as z:
  tree=ET.fromstring(z.read('word/document.xml'))
  paras=[]
  for n,para in enumerate(tree.findall('.//w:body//w:p',NS),1):
   # Preserve text order and explicit line breaks; exclude deleted revision text.
   items=[]
   for elem in para.iter():
    if elem.tag==W+'t':items.append(elem.text or '')
    elif elem.tag in (W+'br',W+'cr'):items.append('\n')
    elif elem.tag==W+'tab':items.append('\t')
   text=''.join(items).strip()
   style=para.find('./w:pPr/w:pStyle',NS)
   style=style.get(W+'val','') if style is not None else ''
   paras.append({'pid':f'P{n:04d}','style':style,'text':text})
  embedded=[x for x in z.namelist() if x.startswith('word/media/')]
  metadata={'id':sid,'original':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'paragraph_count':len(paras),'nonempty_paragraphs':sum(bool(x['text']) for x in paras),'characters':sum(len(x['text']) for x in paras),'tables':len(tree.findall('.//w:tbl',NS)),'embedded_media':embedded,'tracked_insertions':len(tree.findall('.//w:ins',NS)),'tracked_deletions':len(tree.findall('.//w:del',NS)),'extra_text_parts':[x for x in z.namelist() if re.search(r'(footnotes|endnotes|comments|header|footer)\d*\.xml$',x)]}
 (OUT/(sid+'.json')).write_text(json.dumps({'metadata':metadata,'paragraphs':paras},ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/(sid+'.txt')).write_text('\n\n'.join(f"[{x['pid']}] {x['text']}" for x in paras if x['text']),encoding='utf-8')
 manifest.append(metadata)
 print(json.dumps(metadata,ensure_ascii=False))
 print('OUTLINE')
 headings=[]
 for x in paras:
  t=x['text']
  if t and (re.search('heading|标题',x['style'],re.I) or (len(t)<100 and re.match(r'^(#{1,6}\s|第[一二三四五六七八九十\d]+[章节部分]|[一二三四五六七八九十]+[、.．]|\d+(?:\.\d+)*[.、．\s]|[（(][一二三四五六七八九十\d]+[）)])',t))):
   headings.append(f"[{x['pid']}] {t}")
 print('\n'.join(headings[:150]))
 print('FIRST PARAGRAPHS\n'+'\n'.join(f"[{x['pid']}] {x['text'][:250]}" for x in paras if x['text'])[:1600])
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
