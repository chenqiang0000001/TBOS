import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '知识库' / '10-原始资料' / 'SRC-APP-20261105-001'
OUT.mkdir(exist_ok=True)

# Transcribed from the authorized, rendered 同花顺 watchlist table.
# Keep the site's raw display prefixes; they are not exchange validation.
RAW = '''阿特斯太阳能|USACSIQ
诺和诺德|USANVO
安进|USAAMGN
赛默飞世尔|USATMO
联邦快递|USAFDX
艾伯维|USAABBV
阿斯利康|USAAZN
默沙东|USAMRK
诺华|USANVS
强生|USAJNJ
礼来|USALLY
长江电力|SZ600900
中国神华|SZ601088
联合利华|USAUL
通用磨坊|USAGIS
梦龙|USAMICC
怪物饮料|USAMNST
孩之宝|USAHAS
伟易达|HK0303
宝洁|USAPG
H&H国际控股|HK1112
标普500ETF|USAVOO
纳斯达克100指数ETF|USAQQQ
联合健康|USAUNH
超威半导体|USAAMD
名创优品|USAMNSO
名创优品|HK9896
麦当劳|USAMCD
宏桥控股|SZ002379
中国宏桥|HK1378
优步|USAUBER
迪士尼|USADIS
中国海洋石油-R|HK0883
通用汽车|USAGM
中国神华|HK1088
卡骆驰|USACROX
沃尔玛|USAWMT
巴西石油|USAPBR
辉瑞|USAPFE
京东|USAJD
多邻国|USADUOL
雅诗兰黛|USAEL
马拉松原油|USAMPC
埃克森美孚|USAXOM
达美乐比萨|USADPZ
九号公司-WD|SZ689009
中国海油|SZ600938
西方石油|USAOXY
阿斯麦|USAASML
西部数据|USAWDC
康宁|USAGLW
SpaceX|USASPCX
闪迪|USASNDK
SK海力士|USASKHY
卫龙美味|HK9985
中信证券|HK6030
中信证券|SZ600030
同花顺|SZ300033
安踏体育|HK2020
耐克|USANKE
中国海洋石油|HK0883
泡泡玛特|HK9992
舜宇光学科技|HK2382
泸州老窖|SZ000568
五 粮 液|SZ000858
BOSS直聘-W|HK2076
伯克希尔哈撒韦 B|USABRK.B
伯克希尔哈撒韦 A|USABRK.A
蒙牛乳业|HK2319
伊利股份|SZ600887
中海油服|SZ601808
东鹏饮料|HK9980
东鹏饮料|SZ605499
东阿阿胶|SZ000423
农夫山泉|HK9633
戴克斯户外|USADECK
可口可乐|USAKO
比亚迪电子|HK0285
联想控股|HK3396
腾讯控股|HK0700
中芯国际|HK0981
中兴通讯|HK0763
小米集团-W|HK1810
金山软件|HK3888
网易-S|HK9999
财捷|USAINTU
自动数据处理|USAADP
奈飞|USANFLX
奥多比|USAADBE
Paypal Holdings|USAPYPL
特许通讯|USACHTR
富达国民信息服务|USAFIS
赛富时|USACRM
欧朋浏览器|USAOPRA
ServiceNow|USANOW
思科|USACSCO
易昆尼克斯|USAEQIX
拉姆研究|USALRCX
科磊|USAKLAC
IBM|USAIBM
台积电|USATSM
博通|USAAVGO
美光科技|USAMU
特斯拉|USATSLA
英特尔|USAINTC
甲骨文|USAORCL
高通|USAQCOM
苹果|USAAAPL
爱彼迎|USAABNB
Booking Holdings|USABKNG
维萨|USAV
万事达|USAMA
Meta|USAMETA
微软|USAMSFT
亚马逊|USAAMZN
英伟达|USANVDA
谷歌C|USAGOOG
谷歌A|USAGOOGL
拼多多|USAPDD
东方甄选|HK1797
兴业银行|SZ601166
农业银行|HK1288
农业银行|SZ601288
中国银行|HK3988
中国银行|SZ601988
建设银行|HK0939
工商银行|HK1398
招商银行|HK3968
招商银行|SZ600036
建设银行|SZ601939
工商银行|SZ601398
宁波银行|SZ002142
中国中免|SZ601888
中国石化|SZ600028
中国船舶|SZ600150
中国石油|SZ601857
海天味业|SZ603288
蜜雪集团|HK2097
宁德时代|HK3750
华润江中|SZ600750
格力电器|SZ000651
美的集团|SZ000333
长鑫科技|SZ688825
贵州茅台|SZ600519
中国卫星|SZ600118
寒武纪|SZ688256
比依股份|SZ603215
兴瑞科技|SZ002937
雅戈尔|SZ600177
公牛集团|SZ603195
拓普集团|SZ601689
乐歌股份|SZ300729
赛力斯|SZ601127
中国平安|SZ601318
阿里巴巴-W|HK9988
理想汽车-W|HK2015
赣锋锂业|SZ002460
比亚迪|SZ002594
锦浪科技|SZ300763
京东方Ａ|SZ000725
李宁|HK2331
牧原股份|SZ002714
浪潮信息|SZ000977
中国中车|SZ601766
紫金矿业|SZ601899
吉利汽车|HK0175
中芯国际|SZ688981'''

rows = []
for i, line in enumerate(RAW.splitlines(), 1):
    name, raw = line.split('|')
    if raw.startswith('USA'):
        market, code = '美国上市页面条目', raw[3:]
    elif raw.startswith('HK'):
        market, code = '香港市场页面条目', raw[2:]
    else:
        market, code = '境内市场页面条目', raw[2:]
    rows.append(dict(row=i, name_on_page=name, raw_code_on_page=raw,
                     code_for_reference=code, market_bucket=market,
                     instrument_type='ETF' if raw in ('USAVOO', 'USAQQQ') else '股票类页面条目',
                     detail_url='https://stockpage.10jqka.com.cn/' + (raw[3:] if raw.startswith('USA') else raw if raw.startswith('HK') else raw[2:])))
if len(rows) != 167:
    raise ValueError(f'Expected 167 rendered rows, found {len(rows)}')

snapshot = dict(
    id='SRC-APP-20261105-001', observed_on='2026-11-05', timezone='Asia/Shanghai',
    source_url='https://t.10jqka.com.cn/newcircle/user/userPersonal/?from=finance&tab=zx',
    acquisition='用户自行登录后，经浏览器可见页面读取；点击查看更多并等待页面加载',
    scope='本次页面已加载167条记录；未验证是否包含所有客户端分组或全部账号数据',
    not_holdings=True, prices_omitted=True,
    validation='原样转录名称与显示代码；代码、上市状态和柜台币种未逐项独立核实',
    market_counts=dict(Counter(r['market_bucket'] for r in rows)),
    etf_count=sum(r['instrument_type']=='ETF' for r in rows), rows=rows)
(OUT/'自选股快照.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# 同花顺自选股页面转录（167条）','',
       '日期：2026-11-05（北京时间）。范围、来源和使用边界见[来源说明](来源说明.md)。这是自选清单，不是持仓表。显示代码按页面原样保存，不能据此确认交易所、柜台币种或实时行情。','',
       '| 顺序 | 页面名称 | 页面显示代码 |','|---:|---|---|']
lines += [f"| {r['row']} | {r['name_on_page']} | {r['raw_code_on_page']} |" for r in rows]
(OUT/'自选股页面转录.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

print(json.dumps({k:v for k,v in snapshot.items() if k!='rows'},ensure_ascii=False,indent=2))
