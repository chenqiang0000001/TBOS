import pathlib, sys, re
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent
for sid in ['S37','S38','S40','S44','S27','S48']:
 p=ROOT/(sid+'.txt')
 if p.exists():
  s=p.read_text(encoding='utf-8');print('\n### '+sid+'\n'+s[:2100])
for sid,phrases in {'S08':['Organizational Learning A','Management by Fact '],'S10':['Projects:','Areas:','Resources:','Archives:'],'S11':['Capture','Organize','Distill','Express'],'S40':['six','review','outcome'],'S44':['index','fixed','communication'],'S46':['models','latticework','hammer']}.items():
 p=ROOT/(sid+'.txt')
 if not p.exists():continue
 s=p.read_text(encoding='utf-8');print('\n### '+sid)
 for phrase in phrases:
  hits=list(re.finditer(re.escape(phrase),s,re.I))
  if hits:
   m=hits[0];print(phrase+': '+s[max(0,m.start()-100):m.end()+650].replace('\n',' '))
