import pathlib, sys, re
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path(__file__).resolve().parent
terms={
 'S01':['12.','information','goals','paradigm'],
 'S02':['feedback','humble','learning'],
 'S03':['circle of competence','boundaries'],
 'S06':['effort','growth mindset','fixed'],
 'S08':['Systems Perspective','Organizational Learning','Management by Fact','Learning'],
 'S10':['Projects','Areas','Resources','Archives','actionability'],
 'S11':['Capture','Organize','Distill','Express'],
 'S12':['Evergreen','atomic','concept','oriented'],
 'S14':['kit','download','Obsidian'],
 'S15':['ten','category','area'],
 'S18':['Six Patterns','topography','growth','imperfection'],
 'S19':['CSV','Markdown','recreate','export'],
 'S20':['Brier score','binary','strictly proper'],
 'S21':['voluntary','Govern','MAP','MEASURE','MANAGE'],
 'S24':['mistakes','owner earnings'],
 'S25':['effort','mindset'],
}
for sid, phrases in terms.items():
 p=root/(sid+'.txt')
 if not p.exists():continue
 s=p.read_text(encoding='utf-8'); print('\n### '+sid)
 if len(s)<4000: print(s);continue
 for phrase in phrases:
  m=re.search(re.escape(phrase),s,re.I)
  if m: print(phrase+': '+s[max(0,m.start()-180):m.end()+750].replace('\n',' '))
