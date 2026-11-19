from pathlib import Path
import importlib.util
import json
from concurrent.futures import ThreadPoolExecutor

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('div_fetch',BASE.parent/'dividend_screen_20261105/fetch.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.ROOT=BASE
jobs=[
 ['VICI_IR','https://investors.viciproperties.com/'],
 ['GLPI_IR','https://investors.glpropinc.com/'],
 ['HESM_IR','https://www.hessmidstream.com/'],
 ['GIS_IR','https://investors.generalmills.com/'],
]
with ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(module.fetch,jobs))
(BASE/'public_fetch_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
 print(json.dumps({k:v for k,v in r.items() if k!='links'},ensure_ascii=False))
 print(json.dumps(r.get('links',[])[:16],ensure_ascii=False))
