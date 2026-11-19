import pathlib, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path(__file__).resolve().parent.parent
files=[p for p in root.rglob('*.md') if '_research' not in p.parts]
errors=[]; checked=0
for p in files:
 text=p.read_text(encoding='utf-8')
 if '\ufffd' in text:errors.append(str(p.relative_to(root))+': replacement character')
 for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',text):
  target=m.group(1).strip('<>')
  if re.match(r'^[a-zA-Z]+://',target) or target.startswith('#'):continue
  target=target.split('#')[0]
  if not target:continue
  checked+=1
  if not (p.parent/target).resolve().exists():errors.append(str(p.relative_to(root))+': missing '+target)
 for marker in re.findall(r'\[(S\d+(?:、S\d+)*)\]',text):
  for sid in marker.split('、'):
   if sid not in (root/'03-来源与核验说明.md').read_text(encoding='utf-8'):
    errors.append(str(p.relative_to(root))+': unknown source '+sid)
demo=root/'知识库'/'95-合成演示'
for p in demo.glob('*.md'):
 if '合成' not in p.read_text(encoding='utf-8'):errors.append(str(p)+': missing synthetic label')
result={'markdown_files':len(files),'local_links_checked':checked,'errors':errors,'core_template_count':len(list((root/'知识库'/'90-模板').glob('*.md'))),'synthetic_records':len(list(demo.glob('*.md')))}
print(json.dumps(result,ensure_ascii=False,indent=2))
(root/'_research'/'deliverable_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for sid in ['S41','S38']:
 p=root/'_research'/(sid+'.txt')
 print('\nSOURCE CHECK '+sid+'\n'+p.read_text(encoding='utf-8')[:3000])
if errors:sys.exit(1)
