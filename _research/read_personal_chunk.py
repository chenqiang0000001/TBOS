import pathlib,json,sys
sys.stdout.reconfigure(encoding='utf-8')
sid=sys.argv[1];start=int(sys.argv[2]);end=int(sys.argv[3])
p=pathlib.Path(__file__).resolve().parent/'personal_import_20261105'/f'SRC-20261105-{int(sid):03d}.json'
obj=json.loads(p.read_text(encoding='utf-8'))
print(obj['metadata']['id'])
for x in obj['paragraphs'][start-1:end]:
 if x['text']:print(f"{x['pid']} {x['text']}")
