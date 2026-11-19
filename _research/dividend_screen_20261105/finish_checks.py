from pathlib import Path
import json
import sys
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
out = BASE / 'pdf_checks'
out.mkdir(exist_ok=True)
files = [
    (BASE / 'CM_2026H1.pdf', [23, 27, 29], 'CM'),
    (ROOT / '_research/cnooc_20261105/2025annual_full.pdf', [2], 'CNOOC_ANNUAL'),
    (ROOT / '_research/cnooc_20261105/2026h1_full.pdf', [24, 26], 'CNOOC_H1'),
]
for path, pages, name in files:
    doc = pdfium.PdfDocument(str(path))
    for number in pages:
        image = doc[number-1].render(scale=1.35).to_pil()
        target = out / f'{name}_p{number}.png'
        image.save(target)
        print(target.relative_to(ROOT))

reader = PdfReader(BASE / 'CM_2026H1.pdf')
for number in [28, 29, 30]:
    print(f'\nCM PDF page {number}\n{reader.pages[number-1].extract_text()}')

rows = [
    dict(ticker='VZ', currency='USD', price=46.17, cash_per_share=0.7075*4, basis='latest_quarter_annualized'),
    dict(ticker='EPD', currency='USD', price=36.71, cash_per_share=0.56*4, basis='latest_quarter_annualized'),
    dict(ticker='EPD', currency='USD', price=36.71, cash_per_share=0.545+0.55+0.55+0.56, basis='trailing_12_months_paid'),
    dict(ticker='MPLX', currency='USD', price=56.25, cash_per_share=1.2111*4, basis='latest_quarter_annualized'),
    dict(ticker='00941', currency='HKD', price=80.75, cash_per_share=2.9003+2.52, basis='latest_two_declared_ordinary_dividends'),
    dict(ticker='00883', currency='HKD', price=23.04, cash_per_share=0.94+0.55, basis='latest_two_declared_ordinary_dividends'),
    dict(ticker='00883', currency='HKD', price=23.04, cash_per_share=1.28, basis='FY2025_declared_ordinary_dividends'),
    dict(ticker='00823', currency='HKD', price=40.96, cash_per_share=2.5361, basis='FY2025_26_DPU'),
    dict(ticker='UPS', currency='USD', price=114.31, cash_per_share=1.64*4, basis='latest_quarter_annualized'),
]
for row in rows:
    row['gross_yield_percent'] = row['cash_per_share']/row['price']*100
    row['price_at_6_percent'] = row['cash_per_share']/0.06
record = dict(
    calculation_date='2026-11-05',
    us_price_timestamp='2026-11-04 16:05:07 America/New_York',
    hk_price_timestamp='2026-11-05 approximately 11:35-11:41 Asia/Hong_Kong; intraday, may be delayed',
    price_source_files=['QUOTES.txt','QUOTES2.txt'],
    cash_source_notes='See 已核实公告摘录.md and the linked knowledge-base report. All yields before tax and costs. Annualization is not a payment promise.',
    rows=rows,
    checks=dict(
        VZ_9M_FCF_dividend_coverage=18/8.8,
        VZ_9M_dividend_and_buyback_share_of_FCF=(8.8+4)/18,
        CM_H1_FCF_dividend_coverage=53.9/54.426,
        MPLX_9M_adjusted_FCF_minus_distributions_billion_USD=1.664-3.277,
    ),
)
(BASE/'yield_calculations.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
