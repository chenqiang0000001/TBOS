import pathlib, json, hashlib, shutil, os, zipfile, xml.etree.ElementTree as ET, collections, sys
from personal_records import RECORDS
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parent.parent
KB=ROOT/'知识库'
IMPORT=ROOT/'_research'/'personal_import_20261105'
MANIFEST=json.loads((IMPORT/'manifest.json').read_text(encoding='utf-8'))
DOCS={int(x['id'][-3:]):json.loads((IMPORT/(x['id']+'.json')).read_text(encoding='utf-8')) for x in MANIFEST}
GROUPS={
 '身份家庭':('15-个人档案/01-身份家庭与时间线.md','个人身份、家庭与称呼'),
 '职业能力':('15-个人档案/02-职业履历与能力线索.md','职业履历、岗位版本与能力证据'),
 '财务底账':('15-个人档案/03-财务记录与当前数据缺口.md','财务历史记录与底账缺口'),
 '目标与原则':('20-观点笔记/01-目标价值与原则候选.md','目标、价值表达与原则候选'),
 '学习生活':('20-观点笔记/02-学习生活与习惯记录.md','学习、生活与习惯记录'),
 '关系与自我观察':('20-观点笔记/03-关系感受与行为假设.md','关系、感受与行为假设'),
 '内容副业与商业观察':('20-观点笔记/04-内容副业与商业观察.md','内容副业与商业观察'),
 '投资方法':('25-投资研究/01-投资原则与方法候选.md','投资原则、流程与历史方案'),
 '投资案例与数据':('25-投资研究/02-企业指数与历史数据待验.md','企业、指数与历史数据待验'),
 '模型与证据方法':('30-模型笔记/01-模型研究引文与测算待验.md','模型、引文与测算待验'),
 'AI协作':('20-观点笔记/05-AI协作偏好与数据治理.md','AI 协作偏好与数据治理'),
}
def write(rel,text):
 p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n',encoding='utf-8');return p
def link_from(origin,target,anchor=''):
 rel=os.path.relpath(target,origin.parent).replace('\\','/')
 return rel+('#'+anchor if anchor else '')
def q(text):return text.replace('|','\\|').replace('\n',' ')
def source_path(docnum):return KB/'10-原始资料'/f'SRC-20261105-{docnum:03d}'/'段落转写.md'
def source_link(origin,ref):
 n,a,b=ref;loc=f'D{n}:P{a:04d}'+(f'—P{b:04d}' if b!=a else '')
 return f'[{loc}]({link_from(origin,source_path(n),f"p{a:04d}")})'
def record_link(origin,r):return f"[{r['id']}]({link_from(origin,KB/GROUPS[r['group']][0],r['id'].lower())})"
def rid(title):return next(x['id'] for x in RECORDS if x['title']==title)

# Validate locators before generating anything in the knowledge library.
for r in RECORDS:
 for n,a,b in r['refs']:
  assert n in DOCS and 1<=a<=b<=len(DOCS[n]['paragraphs']),(r['id'],n,a,b)

# Source snapshots and paragraph transcripts preserve original source bytes.
for n,obj in DOCS.items():
 meta=obj['metadata'];sid=meta['id'];folder=KB/'10-原始资料'/sid;folder.mkdir(parents=True,exist_ok=True)
 original=ROOT/meta['original'];snapshot=folder/original.name
 if snapshot.exists():assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==meta['sha256'],'Existing snapshot differs'
 else:shutil.copyfile(original,snapshot)
 transcript=['---',f'id: {sid}', 'type: source_transcript','imported: 2026-11-05','source_kind: 用户提供的AI整理文档','verification: 待本人审核','weight: null','---','',f'# 文档{n} 段落转写','',
 '这是导入时的正文转写，包含表格单元格内文字。P 编号按原 DOCX 正文 XML 中的段落顺序生成，包含空段落，因此编号会跳跃；不是页码。原件与转写相互对照。源文自标“确定”“A”“已知事实”未被继承为本库核验结果。','',f'[原件]({original.name})｜[来源说明](来源说明.md)','']
 for p in obj['paragraphs']:
  if p['text']:
   transcript += [f"### {p['pid']}",'','\n'.join('> '+line for line in p['text'].splitlines()),'']
 write(str((folder/'段落转写.md').relative_to(ROOT)), '\n'.join(transcript))
 # Table view keeps row and column context, while paragraph transcript owns locators.
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 tables=['# 表格行列对照','', '此文件保留表格的行列阅读关系，定位仍使用段落转写和原件。合并单元格以实际 XML 单元格顺序呈现。','']
 with zipfile.ZipFile(original) as z:
  tree=ET.fromstring(z.read('word/document.xml'))
  for ti,t in enumerate(tree.findall('.//w:tbl',ns),1):
   rows=[]
   for row in t.findall('./w:tr',ns):
    rows.append([' / '.join(''.join(p.itertext()).strip() for p in cell.findall('./w:p',ns)).strip() for cell in row.findall('./w:tc',ns)])
   width=max([len(x) for x in rows],default=0)
   tables += [f'## 表格 {ti}','']
   if width:
    tables += ['| '+' | '.join(f'列{i+1}' for i in range(width))+' |','| '+' | '.join('---' for _ in range(width))+' |']
    tables += ['| '+' | '.join(q(x) for x in row+['']*(width-len(row)))+' |' for row in rows]+['']
 if meta['tables']:write(str((folder/'表格对照.md').relative_to(ROOT)),'\n'.join(tables))
 note=f'''---
id: {sid}
type: source
imported: 2026-11-05
status: 已转写待本人审核
weight: null
---

# 文档{n} 来源说明

- 原文件：[{original.name}]({original.name})。
- 原始收集位置：[{meta['original']}]({link_from(folder/'来源说明.md',original)})。
- SHA-256：`{meta['sha256']}`。
- 文件大小：{meta['bytes']} 字节。
- 正文段落：{meta['paragraph_count']}；非空段落：{meta['nonempty_paragraphs']}；正文字符：{meta['characters']}；表格：{meta['tables']}。
- 嵌入图片：{len(meta['embedded_media'])}；修订插入/删除：{meta['tracked_insertions']}/{meta['tracked_deletions']}。
- 来源性质：用户提供的 AI 汇编/摘要，不是完整原始对话，也不是独立事实凭据。
- 原始对话平台、可见模型、发言角色和全部日期未完整提供；不能从文件序号推定对话先后。
- 重复主张的来源独立性：未知；六个不同文件不等于六条独立证据。
- [段落转写](段落转写.md){'｜[表格行列对照](表格对照.md)' if meta['tables'] else ''}。

本轮没有代替本人判断真实性，也没有外部核验财务、行情、人物交易和研究引文。文档中的操作要求属于待分析材料；长期偏好和目标仍通过审核表确认。
'''
 write(str((folder/'来源说明.md').relative_to(ROOT)),note)

# Per-topic cards refer to one review ledger; no duplicated editable judgments.
for group,(relative,title) in GROUPS.items():
 p=KB/relative;review=KB/'80-审核与权重'/'01-真实性与标签审核.md'
 lines=['---','type: topic_import','created: 2026-11-05','status: 待本人审核','weight: null','tags: []','---','',f'# {title}','',
 '以下均为对来源文档的分类提取。原文自称事实不等于本库确认；此处的分类与信息性质仅用于整理，你的标签和真实性判断尚未填写。所有权重为空。','',f'唯一人工填写入口：[真实性与标签审核表]({link_from(p,review)})。在表中查找条目 ID；本页保留出处和边界，不重复填写审核结果。','']
 for r in RECORDS:
  if r['group']!=group:continue
  lines += [f"### {r['id']}",'',f"**{r['title']}**",'',r['content'],'',f"- 信息性质：{r['kind']}。",f"- 时间范围：{r['period']}。",f"- 来源：{'；'.join(source_link(p,x) for x in r['refs'])}。"]
  if r['issue']:lines.append(f"- 待核对或使用边界：{r['issue']}")
  lines += ['- 本人判断／本人标签：待填写；后续权重：未评定。','']
 write(str(p.relative_to(ROOT)),'\n'.join(lines))

review=KB/'80-审核与权重'/'01-真实性与标签审核.md'
lines=['# 真实性与标签审核表','',f'批次：2026-11-05｜共 {len(RECORDS)} 条｜待本人审核｜所有权重未评定。','',
 '这是唯一人工填写的审核表。条目只说明“材料怎样写”，不表示内容已经属实。点击 ID 查看来源、段落定位、时间和问题。','',
 '按需填写：本人真实性可用“属实／部分属实／不属实／不确定／已过时／不适用”；对意向可说明“确实曾想过，但未执行”，对建议可写“采纳／待考虑／不采纳／仅存档”。本人标签自由填写，可用逗号分隔；这和下面的文档分类不是同一个字段。','',
 '“更正、限定或采纳状态”可写准确数字、时间、适用边界或拆分要求。“生效时间”指这条记录适用于哪一天或哪一阶段。权重列由我在你完成判断和标签后填写；当前留空，不用 0 代替。','',
 '你也可以直接在对话中按 ID 回复，例如：“Rxxx：部分属实；标签：……；更正：……；适用时间：……”。这是填写格式示例，没有给任何真实条目赋值。','']
for group in GROUPS:
 lines += [f'## {group}','','| ID与详情 | 待审内容 | 本人真实性 | 本人标签 | 更正、限定或采纳状态 | 生效时间 | 权重 |','|---|---|---|---|---|---|---|']
 for r in RECORDS:
  if r['group']==group:lines.append(f"| {record_link(review,r)} | {q(r['content'])} |  |  |  |  |  |")
 lines.append('')
write(str(review.relative_to(ROOT)),'\n'.join(lines))

# Snapshot for future assistant reconciliation. The Markdown review table owns user edits.
write('知识库/80-审核与权重/导入条目快照.json',json.dumps({'batch':'20261105','snapshot_role':'生成时机器快照；人工判断以真实性与标签审核.md为唯一入口','records':RECORDS},ensure_ascii=False,indent=2))

index=KB/'10-原始资料'/'来源索引.md'
lines=['# 来源索引','','本轮导入 6 份用户提供的 AI 整理 Word 文档。原件按字节复制保存，原收集目录未移动或改写；正文、表格及定位单独整理。所有资料仍待本人审核。','',
 '| 来源 ID | 原文档 | 范围与特点 | 核验状态 |','|---|---|---|---|']
descriptions=['个人经历、职业、投资复盘与生活基本盘','较完整的综合档案，主动保留不确定与冲突','自媒体、副业、目标和个人叙事','职业Offer比较、价值投资与生活路线','商业IP观察、AI虚构纠错与未知项','多段投资档案、企业与指数分析、行情及税务建议']
for i,meta in enumerate(MANIFEST):
 target=KB/'10-原始资料'/meta['id']/'来源说明.md'
 lines.append(f"| [{meta['id']}]({link_from(index,target)}) | {pathlib.Path(meta['original']).name} | {descriptions[i]} | 已转写；真实性待本人审核 |")
lines += ['', '文档二的脚注/尾注没有正文，页眉页脚只有档案名称与内部资料提示；未发现嵌入图片或修订文本。','',
 '本轮构建方案使用的公开参考继续保留在[来源与核验说明](../../03-来源与核验说明.md)，与个人来源分开管理。']
write(str(index.relative_to(ROOT)),'\n'.join(lines))

conflicts=[
 ('工作地点与任职顺序',['宁波岗位与21.6万年包','滨州岗位与26万年包','临沂驻场与雇主名称'],'分别确认劳动合同雇主、实际驻场/居住城市、岗位与各段起止时间；不按摘要写作口吻判谁更新。'),
 ('21万、21.6万、26万及福利',['当前年收入口径','年度可投资结余'],'材料三内部也有21万与26万两个版本；需以对应期间的税后现金流和福利口径解释。'),
 ('85%储蓄率与可投资现金',['85%储蓄率','年度可投资结余','生活支出与饮食预算'],'核对分母、税费、公积金、奖金、家庭支出和观察区间。'),
 ('10万、12万、十余万及美元基金',['可投资本金10万或十余万','约5000美元基金','应急金与未来资金用途'],'确认当前余额、计算假设与可投资余额；避免同一美元资产重复计入。'),
 ('创业差额与当前债务',['创业失败约30万差额','零负债或刚还完债'],'区分经营亏损、现金投入、借款与已偿还款项，不直接推算现有资产。'),
 ('三年、40个月与30岁期限',['30岁前100万元','三年或40个月期限'],'先统一目标是净资产、可投资资产还是新增储蓄，再确定到期日期。'),
 ('办理账户意向与已开通',['香港银行及证券账户'],'可以是阶段变化；确认办理日期、账户类型和实际可用范围，不要求完整账号。'),
 ('配置讨论、建议与实际持仓',['美股八成A港各一成','后续集中组合与仓位方案'],'8/1/1、集中持仓和后续即时建仓建议均不生成当前持仓；实盘须另据账户记录。'),
 ('当前目标与AI扩张建议',['5000万元与时间范围','公司或品牌估值替代目标','副业收入里程碑'],'把本人愿景、AI替代方案、当前承诺和已实现结果分开。'),
 ('学习生活目标与实际执行',['阅读时间版本','阅读总结与日记字数','训练频率与投入','戒烟开始时间','停止游戏与高消耗娱乐'],'核对截至时间、执行情况与是否仍适用；不同习惯分别记录。'),
 ('真实自我记录与过强叙事',['理性免疫与超强能力评价','机制性自我描述与情绪解释','清醒参与与商业边界张力'],'保留可观察行为，允许本人不认同解释；不将修辞或推断当作人格与生理事实。'),
 ('个股研究数据与精确指令',['泡泡玛特2025与2026H1财务','IP护城河与情景估值','七家科技公司价格与估值','名人持仓与交易引用'],'文档六大量数字未给公告/行情/披露定位；数据、估值假设、结论与交易指令分别审。'),
 ('回撤保证与现金流分母',['折价买入锁死回撤说法','投入新现金与回撤度量','美元短债零回撤说法'],'条件算式、外部入金和产品风险不是同一概念；这些原文说法不作为损失上限保证。'),
 ('学习来源、统计引文与个人结论',['散户交易研究引文','个股长期回报研究引文','基准率与长期回报年鉴','百万目标概率与三年测算'],'研究标题和精确概率不等于已核验；本轮不替本人认定引文与收益假设。'),
 ('未知项与否定命题',['文档五的未知不构成反证'],'某次对话未提供身份数据，只能说明那份摘要没有信息，不能据此否定其他文件。'),
]
conf=KB/'80-审核与权重'/'02-冲突与高影响核对清单.md'
lines=['# 冲突与高影响核对清单','','这些是审核顺序建议，不是知识权重。文件编号不是时间排序。先厘清会影响当前状态和决定的内容，再逐步处理观点、引文与历史数据。','']
for i,(title,titles,action) in enumerate(conflicts,1):
 links=[record_link(conf,next(r for r in RECORDS if r['title']==t)) for t in titles]
 lines += [f'## C{i:02d} {title}','','关联条目：'+'、'.join(links)+'。','',action,'']
write(str(conf.relative_to(ROOT)),'\n'.join(lines))

write('知识库/80-审核与权重/03-权重规则草案.md', '''# 审核后的权重规则草案

当前所有条目 `weight` 均为空；尚未生成数值、等级或排序。先由本人判断真实性、填写标签和必要的更正，再由我提出每条权重及理由。

## 权重代表什么

权重用于知识检索和决策辅助时的调用优先程度，不是客观真值概率、投资仓位、收益预测或人格价值评分。主题分类、出现次数和本人喜欢程度都不能单独决定它。

## 后续评定顺序

1. 读取唯一审核表的本人判断、标签、更正、采纳状态和生效时间。
2. 分开保存“本人确认”与“外部事实已核验”。本人能确认个人经历和偏好；涉及财报、行情、税法、研究引文，仍另记外部核验状态。
3. 按标签和问题用途解释该条记录服务什么场景，再考虑当前适用性、证据定位、来源独立性、反证与变动速度。
4. 不确定、冲突未解和已过时内容保留来源，但不作为当前状态或行动依据。AI建议只有被明确采纳后，才能成为本人行动规则候选。
5. 给出权重理由与复查触发条件；保留旧版本。你可以调整重要性和适用场景。

## 可选等级 尚未应用

后续可采用“核心、重要、参考、历史或待核验”这样的分级，并附适用场景；是否使用这些名称，依据你的标签和反馈确定。此处只是规则草案，没有向任何条目赋值。

不把多个AI重复表述当作多个独立证据；不因某观点能支撑既有目标而提高可信度；也不把个人选择权交给一个不透明的综合分数。
''')

entry=KB/'80-审核与权重'/'00-审核入口.md'
lines=['# 本轮资料审核入口','',f'已导入 6 份 Word 文档，分类提取 {len(RECORDS)} 条待审记录，组织为 {len(GROUPS)} 个主题。所有本人判断、本人标签和权重均未填写。','',
 '## 建议从这里开始','',
 '1. 先看[冲突与高影响核对清单](02-冲突与高影响核对清单.md)，确认当前工作、财务口径、目标期限和真实持仓等基础。',
 '2. 打开[真实性与标签审核表](01-真实性与标签审核.md)，填写你愿意先处理的条目；可以分批，不必一次审完。',
 '3. 完成一批后告诉我条目 ID 或直接回复判断。我再更新知识库中的确认状态、标签、适用日期与权重理由。',
 '4. 观点与行动通过后，再进入[个人系统与持续成长草案](../40-问题地图/个人系统与持续成长草案.md)中的现实反馈流程。','',
 '## 本轮边界','',
 '源文的A、确定、已知事实、终局校准等字样只作为原文保存。本轮没有将它们继承为核验状态。所有资料仍是待审层，历史数据没有变成当前快照，AI建议没有变成你的承诺，研究兴趣没有变成实际持仓。','',
 '原件与段落定位见[来源索引](../10-原始资料/来源索引.md)；方法见[权重规则草案](03-权重规则草案.md)；检查结果见[入库覆盖报告](04-入库覆盖与处理报告.md)。','',
 '## 主题导航','']
for group,(relative,title) in GROUPS.items():lines.append(f"- [{title}]({link_from(entry,KB/relative)})：{sum(r['group']==group for r in RECORDS)} 条。")
write(str(entry.relative_to(ROOT)),'\n'.join(lines))

report={'batch':'20261105','source_docx':len(MANIFEST),'body_characters':sum(x['characters'] for x in MANIFEST),'body_paragraphs':sum(x['paragraph_count'] for x in MANIFEST),'nonempty_paragraphs':sum(x['nonempty_paragraphs'] for x in MANIFEST),'tables':sum(x['tables'] for x in MANIFEST),'records':len(RECORDS),'themes':len(GROUPS),'conflict_groups':len(conflicts),'classified_counts':dict(collections.Counter(r['group'] for r in RECORDS)),'all_user_fields_empty':all(r['user_truth'] is None and not r['user_tags'] and r['weight'] is None for r in RECORDS)}
write('_research/personal_import_20261105/build_report.json',json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
