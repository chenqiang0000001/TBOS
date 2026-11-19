from pathlib import Path
import json, re, collections, hashlib, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
OUT = ROOT / '知识库/25-投资研究/自选分组维护-20261105'
OUT.mkdir(exist_ok=True)
snapshot_path = ROOT / '知识库/10-原始资料/SRC-APP-20261105-001/自选股快照.json'
snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
visible = json.loads((BASE/'current_visible_watchlist.json').read_text(encoding='utf-8'))
visible_pairs = {(x['text'].splitlines()[0].strip(),x['url']) for x in visible['rows']}
visible_code_pairs = {(x['text'].splitlines()[-1].strip(),x['url']) for x in visible['rows']}

groups = {
    '老登·成熟现金流': [3,6,7,8,9,10,12,14,15,19,20,28,37,45,64,65,67,68,69,70,74,77,87,92,96,100,108,111,112,121,122,123,124,125,126,127,128,129,130,131,132,137,140,141,142,144,150,154],
    '小登·高预期验证': [41,62,104,120,138,145,146,153,156],
    '周期·经营修复': [1,5,18,21,24,29,30,32,34,35,36,38,39,42,43,44,47,48,50,51,53,56,57,58,60,63,71,79,81,82,90,91,103,105,133,134,135,136,149,157,159,160,161,162,163,164,165,166,167],
    'ETF·基准': [22,23],
    '待核·证券身份': [16,33,52,54,143],
}
assigned = [x for v in groups.values() for x in v]
assert len(assigned) == len(set(assigned))
groups['中登·持续成长'] = sorted(set(range(1,168))-set(assigned))
order = ['老登·成熟现金流','中登·持续成长','小登·高预期验证','周期·经营修复','ETF·基准','待核·证券身份']
group_by_row = {i:g for g,indices in groups.items() for i in indices}
default_reason = {
    order[0]:'成熟业务与现金创造；观察每股现金流、返还纪律和资本配置',
    order[1]:'持续成长与再投资；观察增长质量、竞争优势和每股回报',
    order[2]:'长期预期、模式延续或转型兑现较关键；不代表已核实当前估值',
    order[3]:'主要观察问题是行业周期、经营修复、资产与负债变化',
    order[4]:'组合基准；ETF与单家公司分开，不认定满足6%股息门槛',
    order[5]:'证券身份、柜台或长期可比资料待核；不据旧信息判断其上市状态',
}
notes = {}
def note(indices, text):
    for i in indices: notes[i] = text
note([3,6,7,8,9,10], '成熟医疗企业；仅按公开财务与治理归类，现金覆盖和负债仍待核')
note([2,11], '增长与利润集中度影响再投资回报；仅作财务分类，不涉及科研判断')
note([4], '设备与服务业务；观察订单、利润率及投入回报')
note([1,159], '光伏相关周期；观察供需、价格、资产减值和投资后现金流')
note([5], '物流网络成熟，但利润受需求与成本周期影响；观察修复兑现')
note([13,35], '煤炭与能源周期；本期高分红不能直接外推为永久收益')
# 13不在上面的周期集合时，显式纠正，避免以默认余集误归成长。
for i in [13,61]:
    groups[group_by_row[i]].remove(i)
    groups['周期·经营修复'].append(i)
    group_by_row[i] = '周期·经营修复'
note([15], '成熟食品品牌；第三方显示股息率6.81%，普通股息及回购仍待核')
note([16], 'MICC/梦龙：本轮尚未核实发行人、上市证券身份与可比历史')
note([19], '成熟电子消费业务；初筛7.60%，分红覆盖、关税与实际回购待核')
note([18,32,36,42,60,133,161], '消费或服务经营修复；观察销量、品牌、利润率与现金转化')
note([21], '消费健康业务；优先核实杠杆、现金转化和资本配置')
note([24,39], '成熟医疗经营修复；只跟踪公开财务、负债和返还持续性')
note([26,27], '同一发行人的美股与港股分别保留；业务研究合并，证券税费分开')
note([29,30], '铝业链相关周期；两家证券不是同一可互换证券，不按名称相似删除')
note([33], '名称含-R却显示HK0883；可能涉及柜台/币种或页面映射，暂不与另一条合并')
note([34,156,166], '汽车行业竞争与经营兑现；按主要观察问题区分修复和新模式验证')
note([38,44,47,48,61,134,136], '能源价格与资本开支周期；区分油气、炼化和政府/控制方影响')
note([43], 'MPC为炼油及相关业务，区别于上游油气；观察炼油利润与资本配置')
note([41], '增长、用户留存与变现兑现较关键；分类不等于估值结论')
note([49,98,99,101], '成熟半导体设备/制造业务持续成长；同时跟踪资本开支周期')
note([50,53,103], '存储供需和价格周期；分拆/股份历史须分别保留')
note([51], '材料与光通信需求周期；观察订单兑现、利润与资本开支回报')
note([52], 'SPCX/SpaceX：本轮未完成发行人、股份及上市身份核验，不作上市状态推断')
note([54], 'SKHY/SK海力士：本轮未核实该页面所代表证券、挂牌地与股份类别')
note([56,57,58], '资本市场活跃度与交易周期；券商和行情软件并非同一商业模式')
note([62], '品牌IP延续、渠道增长与需求波动待验证；不是按市值归小登')
note([63,78,82], '电子与通信制造：观察客户集中、订单周期和投入回报')
note([64,65,144], '成熟白酒品牌；观察渠道库存、终端需求和每股自由现金流')
note([67,68], '同一资本配置平台的A/B股份均保留；集中度按发行人合并')
note([69,70], '成熟乳品消费业务；观察品牌、渠道、利润与现金返还')
note([71], '油田服务需求与资本开支周期，区别于油气资源股')
note([72,73], '东鹏饮料A/H分别保留，业务与发行人风险合并观察')
note([74,140], '成熟消费健康业务；观察经营现金流、渠道和资本配置')
note([79,149], '多元持股/资产配置，需穿透投资与房地产敞口及负债')
note([81,167], '中芯国际A/H证券分别保留；经营研究合并，价格和税费分开')
note([83], '消费电子平台与新业务再投资；关注分部现金流和资本回报')
note([86,89,93,95,106,114], '企业软件/平台持续成长；观察续费、利润、现金转化及稀释股数')
note([90,91], '成熟支付/通信业务修复；观察竞争、客户与自由现金流变化')
note([104], '汽车业务与长期新业务预期并存；关注投入与经营兑现')
note([108], '成熟硬件/服务生态与现金返还；关注单位回报、竞争和股数变化')
note([111,112], '成熟支付网络；观察跨境业务、监管、费率和每股现金流')
note([117,118], 'Alphabet A/C不同投票权股份均保留；不因同一发行人删除')
note(list(range(121,133)), '成熟银行业务；观察信用成本、资本充足、每股净资产与分红，不套工业FCF')
note([135,164], '装备制造订单与交付周期；仅作证券财务归类')
note([138], '加盟网络与单店经济延续待验证；不据上市时间或市值决定分类')
note([139,158], '制造平台持续成长；观察竞争、客户、资本开支和每股回报')
note([141,142,150], '成熟制造品牌与渠道；观察竞争、现金返还和留存资金回报')
note([143], '688825/长鑫科技：本轮未完成证券身份与长期可比历史核验')
note([145,146], '订单或长期增长预期兑现较关键；仅作公开经营财务观察')
note([147,148,151,152], '制造业务成长与订单转化；观察客户集中、现金流和再投资回报')
note([153], '汽车业务转型兑现；观察竞争、盈利质量与投入后现金流')
note([154], '成熟保险与金融业务；观察偿付能力、资本配置和股东返还')
note([157,165], '资源价格与产能投资周期；观察成本、现金流和并购纪律')
note([160], '面板供需与折旧周期；观察投资后现金流')
note([162], '农产品价格与资本开支周期；本轮只作证券经营财务分组')
note([163], '服务器订单与利润周期；观察客户集中、应收和现金转化')

issuer_clusters = {
 'MINISO':['US:MNSO','HK:09896'], 'Berkshire':['US:BRK.A','US:BRK.B'],
 'Alphabet':['US:GOOG','US:GOOGL'], 'CNOOC':['HK:00883','CN:600938'],
 'Shenhua':['CN:601088','HK:01088'], 'CITIC_Securities':['HK:06030','CN:600030'],
 'Eastroc':['HK:09980','CN:605499'], 'SMIC':['HK:00981','CN:688981'],
 'ABC':['HK:01288','CN:601288'], 'BOC':['HK:03988','CN:601988'],
 'CCB':['HK:00939','CN:601939'], 'ICBC':['HK:01398','CN:601398'],
 'CMB':['HK:03968','CN:600036']
}
issuer_by_key={k:g for g,ks in issuer_clusters.items() for k in ks}
plan=[]
for r in snapshot['rows']:
    market='US' if r['market_bucket'].startswith('美国') else ('HK' if r['market_bucket'].startswith('香港') else 'CN')
    code=r['code_for_reference'].strip()
    if market=='HK': code=code.zfill(5)
    key=f'{market}:{code}'
    unresolved=r['row']==33
    if unresolved: key+=':柜台待核-R'
    plan.append({**r,'market_for_plan':market,'normalized_code':code,'security_key':key,
      'primary_group':group_by_row[r['row']],'classification_status':'分析暂定，非本人标签或买入评级',
      'classification_reason':notes.get(r['row'],default_reason[group_by_row[r['row']]]),
      'issuer_cluster': 'CNOOC_柜台待核' if unresolved else issuer_by_key.get(key,key),
      'current_rendered_confirmed':(r['raw_code_on_page'],r['detail_url']) in visible_code_pairs,
      'app_execution_status':'未执行：当前网页无分组入口，待可操作客户端',
      'user_tags':None,'knowledge_weight':None})
assert len(plan)==167 and len({r['security_key'] for r in plan})==167
counts=collections.Counter(r['primary_group'] for r in plan)
assert sum(r['current_rendered_confirmed'] for r in plan)==85
status={
 'observed_on':'2026-11-05','app_execution_status':'未执行；不是已应用的同花顺分组',
 'required_group_name':'分红','historical_rows':167,'current_rendered_confirmed':85,
 'remaining_historical_rows_status':'本轮未渲染核对，不认定已删除或缺失',
 'primary_group_counts':dict(counts),
 'deduplication':{'exact_duplicate_with_same_confirmed_identity':0,
   'unresolved_collisions':[{'code':'HK0883','rows':[33,61],'reason':'-R名称与页面代码不一致，保留两条待核'}],
   'same_issuer_different_security':'保留A/H、ADR与普通股、不同股份类别；按发行人合并风险',
   'delete_actions':[], 'existing_app_group_memberships':'未取得，不能声称已清理跨组重复'},
 'source_sha256':hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
 'issuer_clusters':issuer_clusters,'rows':plan
}
(OUT/'全部自选分组执行计划.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# 全部自选分组清单（执行前）','',
 '日期：2026-11-05。**同花顺账号内尚未执行。** 本表是分析暂定分组，不是本人真实性标签、知识权重、持仓或买入评级。',
 '', '历史快照共167条；本轮网页重新渲染确认85条，余82条未在本轮渲染核对，不能认定已删除。分类依据是企业成熟度、再投资与最主要观察问题，未为167家公司逐项重新验证2026估值与财报。',
 '', '[执行状态与研究说明](../09-港美股分红扩展与自选分组维护-20261105.md) · [机器执行计划](全部自选分组执行计划.json)',
 '', '## 主分组数量','', '| 主分组 | 条目数 |','|---|---:|']
for g in order:lines.append(f'| {g} | {counts[g]} |')
lines += ['', '每条证券仅有一个主分组；“分红”是独立风格观察组，允许有意交叉。真实重复仅在同一市场、证券、股份类别及柜台币种一致后去重。',
 '', '## 去重与发行人风险','',
 '当前快照有1组代码冲突：第33与61条都显示HK0883，但第33条名称带“-R”。柜台/币种尚未核实，保留两条。未发现其他完全相同的归一证券键；这不代表已经检查或清理同花顺现有各组成员。',
 '', 'BRK.A/BRK.B、GOOG/GOOGL、名创优品美港两地、银行A/H等是不同证券，保留。宏桥控股002379与中国宏桥01378不按名称相似合并。原页SZ600xxx等前缀只保留为来源字段，不据此判断真实交易所。',
 '', '| 同一发行人风险簇 | 分别保留的证券 |', '|---|---|']
for issuer,ks in issuer_clusters.items():lines.append(f'| {issuer} | {"、".join(ks)} |')
for g in order:
    lines += ['',f'## {g}','', '| 原序号 | 证券键 / 名称 | 本轮渲染 | 分类依据与待核点 |','|---:|---|---|---|']
    for r in plan:
        if r['primary_group']==g:
            lines.append(f"| {r['row']} | {r['security_key']} {r['name_on_page']} | {'已确认' if r['current_rendered_confirmed'] else '未核'} | {r['classification_reason']} |")
(OUT/'全部自选分组清单.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

priority={
 'US':['VZ','EPD','MPLX','VICI','HESM','GLPI','GIS','WES','ET','PAA','KNTK','USAC','BNL','FCPT','GTY','FLO','ARCC','MAIN'],
 'HK':['0941','0883','6823','0728','0762','0576','1052','0683','0303','1044','1999','3998','2313','0220','1378','1308','0823']
}
ordinary_verified={'US:VZ':'沿用08：分红、近期实际回购已核；多年与文化待核',
 'US:EPD':'沿用08：分派、实际回购已核；MLP税务待个人确认',
 'US:MPLX':'沿用08：分派、实际回购已核；投资后现金缺口限制评级',
 'US:VICI':'本轮核实分红；回购仅授权，未确认实际执行',
 'US:HESM':'本轮核实分派与Q1实际回购；2027分派指引持平，交易/税制待核',
 'HK:00941':'沿用08：H1未回购；不满足已核稳定回购要求',
 'HK:06823':'本轮核实分派；H1无回购，AFF分派覆盖约1倍',
 'HK:00883':'沿用08：油价周期，H1仅债券回购；普通分红可变',
 'HK:00823':'沿用08：年度DPU下降，移至修复观察，不进首批分红组'}
universe=[]
for market,filename in [('US','us_dividend_screen_raw.json'),('HK','hk_dividend_screen_raw.json')]:
    raw=json.loads((BASE/filename).read_text(encoding='utf-8'))
    for row in raw['rows']:
        code=row['symbol'].zfill(5) if market=='HK' else row['symbol']
        key=f'{market}:{code}'
        m=re.search(r'(\d+(?:\.\d+)?)%',row['displayed_dividend_yield'])
        y=float(m.group(1)) if m else None
        flag=ordinary_verified.get(key,'仅第三方初筛；普通分红、回购、覆盖与治理均待核')
        if market=='US' and code in ['ARCC','MAIN']:flag='BDC进阶池；核对基础/补充分派、信用损失与NAV，不进首批分红组'
        if market=='US' and code in ['AGNC','NLY','ARR','ORC']:flag='高杠杆按揭REIT；不因高息进入稳定分红组'
        if market=='US' and code in ['TDG','ORI','FIZZ']:flag='需优先排除特别股息影响；暂不认定普通股息率达6%'
        if y is not None and y>=20:flag='极高收益率异常核查：价格、特别分派、减息/退出等均待核；不自动入组'
        universe.append({**row,'market':market,'security_key':key,'displayed_yield_numeric_pct':y,
            'priority_for_next_verification':row['symbol'] in priority[market], 'verification_status':flag,
            'strict_four_conditions_passed':False,'app_added':False})
assert len(universe)==741 and len({r['security_key'] for r in universe})==741
(OUT/'港美股6%以上初筛底表.json').write_text(json.dumps({
 'observed_on':'2026-11-05','source':'https://stockanalysis.com/stocks/screener/',
 'scope':'该数据商Exchange Country筛选范围，非所有全球证券或全部合格稳定分红股；Over 6%不等于覆盖恰好6.00%的边界记录',
 'counts':{'US':314,'HK':427},'qualification':'第三方显示值，不能当作741项均满足四项条件',
 'rows':universe},ensure_ascii=False,indent=2),encoding='utf-8')
ul=['# 港美股股息率6%以上初筛底表','',
 '日期：2026-11-05。来源：[StockAnalysis免费筛选器](https://stockanalysis.com/stocks/screener/)。美国314项、香港427项，共741项；逐页读取免费20行分页。',
 '', '**这是该数据商筛选范围的完整分页底表，不是741家合格稳定分红企业，也不是港美所有证券无遗漏的证明。** 口径为Exchange Country和Dividend Yield Over 6%，包含ADR、不同股份类别、基金等；可能混入特别股息、已经降息和异常报价。恰好6.00%的边界记录、未被该商收录或数据缺失的证券不保证覆盖。',
 '', '原显示字段保留；如“.6.13%”仅解析百分号前的有效数值，不改原始JSON。第三方收益率与发行人普通分红复算不同的，以各自时点及口径分别记录。没有把回购金额加进现金股息率。',
 '', '[研究结论](../09-港美股分红扩展与自选分组维护-20261105.md) · [可检索JSON](港美股6%以上初筛底表.json)',
 '', '## 优先核验队列','', '| 市场 | 代码 | 公司 | 第三方显示率 | 本轮状态 |', '|---|---|---|---:|---|']
for r in universe:
    if r['priority_for_next_verification']:
        ul.append(f"| {r['market']} | {r['symbol']} | {r['name']} | {r['displayed_dividend_yield']} | {r['verification_status']} |")
for market,label in [('US','美国挂牌筛选范围：314项'),('HK','香港挂牌筛选范围：427项')]:
    ul+=['',f'## {label}','', '| 代码 | 名称 | 原显示率 | 核验状态 |','|---|---|---:|---|']
    for r in universe:
        if r['market']==market:ul.append(f"| {r['symbol']} | {r['name']} | {r['displayed_dividend_yield']} | {r['verification_status']} |")
(OUT/'港美股6%以上初筛底表.md').write_text('\n'.join(ul)+'\n',encoding='utf-8')

div_keys=['US:VZ','US:EPD','US:MPLX','US:HESM','US:VICI','HK:00941','HK:06823']
div_plan={
 'group_name':'分红','app_execution_status':'未执行：待支持分组且已登录的客户端',
 'meaning':'分红研究观察组；不代表四项全部通过、收益稳定保证或买入名单',
 'strict_qualified_members':[],
 'planned_observation_members':[{'security_key':k,'reason':ordinary_verified[k],
    'in_historical_watchlist':any(x['security_key']==k for x in plan),
    'app_added':False} for k in div_keys],
 'exclude_from_first_batch':['HK:00823（DPU下降）','HK:00883（周期与分红稳定性待核）','US:ARCC/MAIN（BDC单列）','其余仅初筛项目均不自动添加'],
 'transaction_actions':[], 'deletion_actions':[]}
(OUT/'分红组待执行清单.json').write_text(json.dumps(div_plan,ensure_ascii=False,indent=2),encoding='utf-8')

q=(BASE/'verified_candidates_quotes.txt').read_bytes()
quote_rows={}
for ticker in ['usVICI','usHESM','hk06823']:
    line=q.split(('v_'+ticker+'="').encode())[1].split(b'";')[0]
    f=line.split(b'~')
    quote_rows[ticker]={'price':float(f[3]),'price_timestamp':f[30].decode('ascii'),
                        'source':'https://qt.gtimg.cn/q=usVICI,usHESM,hk06823'}
for ticker,base in [('usVICI',1.84),('usHESM',3.194),('hk06823',.8277)]:
    quote_rows[ticker].update(cash_basis=base,pretax_yield_pct=base/quote_rows[ticker]['price']*100,
                             mechanical_6pct_price=base/.06)
quote_rows['usVICI']['basis']='最新季息0.46×4，未来维持的假设'
quote_rows['usHESM']['basis']='最新季分派0.7985×4，未来维持的假设'
quote_rows['hk06823']['basis']='2025末期0.4797+2026中期0.3480；后者支付未再独立核实'
(BASE/'additional_yield_calculations.json').write_text(json.dumps(quote_rows,ensure_ascii=False,indent=2),encoding='utf-8')
validation={'historical_rows':len(plan),'unique_planned_security_keys':len({x['security_key'] for x in plan}),
 'current_visible_confirmed':sum(x['current_rendered_confirmed'] for x in plan),'primary_group_counts':dict(counts),
 'preliminary_rows':len(universe),'us_rows':sum(x['market']=='US' for x in universe),'hk_rows':sum(x['market']=='HK' for x in universe),
 'preliminary_unique_keys':len({x['security_key'] for x in universe}),'dividend_observation_members':len(div_keys),
 'all_strictly_qualified':0,'actual_app_writes':0,'source_unchanged_sha256':hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
 'personal_labels_or_weights_written':False}
(BASE/'group_plan_verification.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=False,indent=2))
