import pathlib,sys,json,re,hashlib,urllib.parse,collections
from personal_records import RECORDS
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent.parent
KB=ROOT/'知识库';batch=ROOT/'_research'/'personal_import_20261105'
manifest=json.loads((batch/'manifest.json').read_text(encoding='utf-8'))
errors=[];links=0;anchors=0;snapshots=0
for meta in manifest:
 original=ROOT/meta['original'];copy=KB/'10-原始资料'/meta['id']/original.name
 for p in [original,copy]:
  if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=meta['sha256']:errors.append('Source bytes changed: '+str(p))
 snapshots+=1
 p=KB/'10-原始资料'/meta['id']/'段落转写.md'
 text=p.read_text(encoding='utf-8')
 obj=json.loads((batch/(meta['id']+'.json')).read_text(encoding='utf-8'))
 count=len(re.findall(r'^### P\d{4}$',text,re.M))
 if count!=meta['nonempty_paragraphs']:errors.append('Transcript coverage '+meta['id'])
 for para in obj['paragraphs']:
  if para['text'] and '\n'.join('> '+x for x in para['text'].splitlines()) not in text:errors.append('Transcript missing '+meta['id']+':'+para['pid'])
for p in ROOT.rglob('*.md'):
 if '_research' in p.parts:continue
 text=p.read_text(encoding='utf-8')
 if '\ufffd' in text:errors.append('Replacement character '+str(p))
 for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',text):
  raw=m.group(1).strip('<>')
  if re.match(r'^[a-zA-Z]+:',raw):continue
  target,_,anchor=raw.partition('#')
  q=(p.parent/urllib.parse.unquote(target)).resolve() if target else p
  links+=1
  if not q.exists():errors.append('Missing target: '+str(p.relative_to(ROOT))+' -> '+raw);continue
  if anchor and re.fullmatch(r'[pr]\d+',anchor,re.I):
   anchors+=1
   if not re.search(r'^### '+re.escape(anchor)+r'\s*$',q.read_text(encoding='utf-8'),re.M|re.I):errors.append('Missing anchor: '+raw)
review=(KB/'80-审核与权重'/'01-真实性与标签审核.md').read_text(encoding='utf-8')
rows=[x for x in review.splitlines() if re.match(r'^\| \[R\d{3}\]',x)]
topic_record_paths={}
for directory in ['15-个人档案','20-观点笔记','25-投资研究','30-模型笔记']:
 for topic_path in (KB/directory).glob('*.md'):
  for record_id in re.findall(r'^### (R\d{3})\s*$',topic_path.read_text(encoding='utf-8'),re.M):
   if record_id in topic_record_paths:errors.append('Duplicate topic record ID '+record_id)
   topic_record_paths[record_id]=topic_path
if len(rows)!=len(topic_record_paths):errors.append('Review row count differs from topic records')
reviewed_ids=[];tagged_ids=[];weighted_ids=[];review_ids=[];rows_with_user_fields=0
for row in rows:
 fields=[field.strip() for field in row.split('|')[1:-1]]
 if len(fields)!=7:errors.append('Review table shape '+row[:60])
 else:
  record_id=re.search(r'R\d{3}',fields[0]).group(0)
  review_ids.append(record_id)
  if fields[2]:reviewed_ids.append(record_id)
  if fields[3]:tagged_ids.append(record_id)
  if fields[6]:weighted_ids.append(record_id)
  if any(fields[2:]):rows_with_user_fields+=1
if len(review_ids)!=len(set(review_ids)):errors.append('Duplicate review row ID')
if set(review_ids)!=set(topic_record_paths):errors.append('Review record ID mismatch')
if not {r['id'] for r in RECORDS}.issubset(review_ids):errors.append('Original import record missing')
snapshot=json.loads((KB/'80-审核与权重'/'导入条目快照.json').read_text(encoding='utf-8'))
if len({r['id'] for r in RECORDS})!=len(RECORDS):errors.append('Duplicate record ID')
if {r['id'] for r in snapshot['records']}!={r['id'] for r in RECORDS}:errors.append('Initial import snapshot IDs changed')
if not all(r['weight'] is None and r['user_truth'] is None and not r['user_tags'] for r in snapshot['records']):errors.append('Initial import snapshot unexpectedly modified')
for r in RECORDS:
 for n,a,b in r['refs']:
  obj=json.loads((batch/f'SRC-20261105-{n:03d}.json').read_text(encoding='utf-8'))
  if not obj['paragraphs'][a-1]['text']:errors.append('Link starts at empty source paragraph '+r['id'])
result={'source_snapshots_verified':snapshots,'initial_import_records':len(RECORDS),'additional_user_records':len(topic_record_paths)-len(RECORDS),'review_records':len(rows),'theme_count':len(set(topic_record_paths.values())),'local_links_checked':links,'source_and_record_anchors_checked':anchors,'originals_unchanged':not any('Source bytes changed' in e for e in errors),'review_rows_with_user_judgment':len(reviewed_ids),'reviewed_ids':reviewed_ids,'review_rows_without_user_judgment':len(rows)-len(reviewed_ids),'review_rows_with_user_tags':len(tagged_ids),'review_rows_with_weights':len(weighted_ids),'all_review_fields_and_weights_empty':rows_with_user_fields==0,'initial_import_snapshot_kept_unreviewed':not any('Initial import snapshot' in e for e in errors),'errors':errors}
(batch/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if errors:sys.exit(1)
