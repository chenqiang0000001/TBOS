import pathlib, zipfile, xml.etree.ElementTree as ET, sys
sys.stdout.reconfigure(encoding='utf-8')
root=pathlib.Path(__file__).resolve().parent.parent
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
for p in (root/'AI对话信息收集').glob('*.docx'):
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if any(k in name for k in ['footnotes.xml','endnotes.xml','header1.xml','footer1.xml']):
    try:t=' '.join(ET.fromstring(z.read(name)).itertext()).strip()
    except Exception:t='[unreadable]'
    print(p.name,name,repr(t[:1200]))
