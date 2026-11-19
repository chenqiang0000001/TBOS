from pathlib import Path
import hashlib, json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent
cache, originals = {}, {}

def read(rel):
    if rel not in cache:
        p = ROOT / rel
        originals[rel] = p.read_bytes()
        cache[rel] = p.read_text(encoding='utf-8')
    return cache[rel]

def replace(rel, old, new):
    text = read(rel)
    if text.count(old) != 1:
        raise ValueError(f'{rel}: expected one match, got {text.count(old)} for {old[:80]}')
    cache[rel] = text.replace(old, new, 1)

def append(rel, text):
    cache[rel] = read(rel).rstrip() + '\n\n' + text.strip() + '\n'

def insert_record_note(rel, rid, text):
    content = read(rel)
    match = re.search(r'^### '+re.escape(rid)+r'\s*\n.*?(?=^### R\d{3}\s*$|\Z)', content, re.M|re.S)
    if not match:
        raise ValueError(rid)
    block = match.group()
    block = block.replace('\n- 信息性质：', '\n**本人补充（2026-11-10）：** '+text+'\n\n- 信息性质：', 1)
    cache[rel] = content[:match.start()] + block + content[match.end():]

SRC = '[入职、组织归属与转岗邀请](../10-原始资料/SRC-USER-20261110-001/本人确认原文.md)'
DEC = 'DEC-20261110-001-产研资源池转铝深加工实施.md'
profile = '知识库/15-个人档案/00-当前状态与长期方向.md'
replace(profile, 'updated: 2026-11-09', 'updated: 2026-11-10')
replace(profile, 'SRC-USER-20261109-001]\n', 'SRC-USER-20261109-001, SRC-USER-20261110-001]\n')
replace(profile, '本页最近更新2026-11-09；本轮新确认学历、职责边界与职业目标，财务、薪酬、地点及作息仍为2026-11-05自述快照，未据本次答复自动刷新。', '本页最近更新2026-11-10；本轮明确9月底入职、产研中心资源池归属及铝深加工转实施提议。学历和真实管理职责边界沿用11月9日确认，财务、薪酬、地点及作息仍为11月5日自述快照；拟转岗条件尚未明确，未记为已转岗。')
replace(profile, '及[本人学历与职责澄清](../10-原始资料/SRC-USER-20261109-001/本人确认原文.md)更新。', '、[本人学历与职责澄清](../10-原始资料/SRC-USER-20261109-001/本人确认原文.md)及'+SRC+'更新。')
replace(profile, '| 公司所在地 | 滨州 | 与当前出差地分开记录 |', '| 入职时间 | 9月底 | 2026-11-10本人补充，具体日未提供；不推导试用期或合同安排 |\n| 当前部门与资源归属 | 属于产研中心，测试归属资源池 | 2026-11-10本人补充，具体内部汇报矩阵未核对 |\n| 项目与实际工作归属 | 在铝深加工部门工作，项目归属铝深加工 | 与人事部门归属及地理工作地点分开记录 |\n| 公司所在地 | 滨州 | 与当前出差地分开记录 |')
replace(profile, '| 当前职业与职责 | MES测试，负责软件全模块的测试与实施 | 本轮明确未负责实施计划、客户需求、跨部门协调、人员分工、进度控制、变更或验收管理；正式职级和团队规模待核对 |', '| 当前职业与职责 | MES测试，负责软件全模块的测试与实施 | 11月9日明确未负责所列项目管理事项；11月10日转实施仍为提议，尚未登记为新职责已生效 |\n| 转岗提议及条件 | 项目经理希望本人转实施并转入铝深加工；原实施转产品 | 薪酬、职责、项目数量、工时均未明确；本人尚未作决定 |\n| 产研管理发展机会 | 领导口头看好本人管理发展 | 暂无具体职责、岗位与时间表 |')
replace(profile, '| 工作节奏 | 不加班、双休 | 当前自述；后续变化时更新 |', '| 工作节奏 | 11月5日自述不加班、双休 | 转岗后可能加班是11月10日担忧，具体工时未明确；不据此改写已发生事实 |')
replace(profile, '## 投资现状、计划与理念', '## 转岗判断的证据边界\n\n项目经理所说“产研不稳定容易裁员、新项目都在铝深加工”属于他人说法，尚未通过编制、预算或项目清单核验；不登记为裁员事实或转岗后更稳定的保证。分析与谈条件清单见[转铝深加工实施决策记录](../50-决策记录/'+DEC+')。\n\n## 投资现状、计划与理念')
append(profile, '| 2026-11-10 | 明确9月底入职、产研测试资源池与铝深加工项目关系；记录转实施及部门提议、转岗条件未明确，产研管理期待仅口头；本人尚未决定 | '+SRC+'；部门稳定性及项目分布属于待核对说法 |')
replace(profile, '\n\n| 2026-11-10 |', '\n| 2026-11-10 |')

career = '知识库/15-个人档案/02-职业履历与能力线索.md'
insert_record_note(career, 'R015', '本人确认9月底入职；属于产研中心，测试归属资源池，实际工作与项目归属铝深加工。转实施与部门调整尚未决定；具体日、职级及转岗待遇未明确。依据'+SRC+'。')
replace(career, '- 待核对或使用边界：税前口径已明确；入职日期、职级、薪酬构成、福利计价及税后实际到账仍未说明。', '- 待核对或使用边界：已明确9月底入职及税前口径；具体入职日、职级、薪酬构成、福利计价和税后到账仍待核对。')
insert_record_note(career, 'R016', '当前组织归属产研中心测试资源池，项目与实际工作在铝深加工；项目经理邀请转实施并转部门。本人确认薪酬、职责、项目数量与工时尚未明确，产研领导管理期待仅口头；未登记为已经转岗。依据'+SRC+'。')

review = '知识库/80-审核与权重/01-真实性与标签审核.md'
text = read(review)
updates = {
 'R015': '本人确认9月底入职，属产研中心测试资源池，工作与项目在铝深加工；既有税前26万元、包吃住沿用11月5日记录。具体日、测试主管头衔和转岗待遇未确认。',
 'R016': '本人确认产研中心资源池与铝深加工项目的关系；项目经理提出转实施及部门，条件均未明确，尚未决定。产研不稳定及新项目分布为经理说法；领导管理期待仅口头。'
}
for rid, correction in updates.items():
    match = re.search(r'^\| \['+rid+r'\].*$', text, re.M)
    if not match:
        raise ValueError(rid)
    fields = [x.strip() for x in match.group().split('|')[1:-1]]
    if len(fields) != 7 or fields[3] or fields[6]:
        raise ValueError('row shape or existing tag/weight '+rid)
    fields[4], fields[5] = correction, '2026-11-10补充；既有薪酬地点等保留原日期'
    text = text[:match.start()] + '| ' + ' | '.join(fields) + ' |' + text[match.end():]
cache[review] = text
replace(review, '这是唯一人工填写的审核表。', '2026-11-10的'+SRC+'已回写R015、R016；仅更新既有反馈，仍为128条中19条有本人反馈，未新增标签或权重。\n\n这是唯一人工填写的审核表。')

index = '知识库/10-原始资料/来源索引.md'
replace(index, '\n\n## 授权应用页面观察', '\n| [SRC-USER-20261110-001](SRC-USER-20261110-001/本人确认原文.md) | 9月底入职；产研测试资源池与铝深加工项目关系；转实施提议，条件未明确，管理期待仅口头 | 本人陈述与他人说法分开；部门稳定性未核验，尚未作出转岗决定；回写既有R015、R016 |\n\n## 授权应用页面观察')
append(index, '## 个人职业决策支持\n\n- [2026-11-10 产研资源池转铝深加工实施](../50-决策记录/'+DEC+')：仅依据本人当前陈述与既有职业目标形成条件性建议；未核验公司内部预算、人事或裁员信息，不把谈判建议登记为已获同意。')

root_entry = '00-开始这里.md'
replace(root_entry, '更新日期：2026-11-09；', '更新日期：2026-11-10；')
replace(root_entry, '职业新补充：', '当前职业选择：[产研资源池转铝深加工实施](知识库/50-决策记录/'+DEC+')。已补9月底入职及组织归属；转岗条件未明确、产研管理期待仅口头。分析有条件倾向转实施，先谈范围、资源、工时与待遇；本人尚未决定。\n\n职业新补充：')
nav = '知识库/00-系统导航.md'
replace(nav, '## 使用入口\n', '## 使用入口\n\n- [产研资源池转铝深加工实施：是否转岗](50-决策记录/'+DEC+')：拆分岗位与部门，核对稳定性说法、六项条件、过渡方案和机会成本；本人尚未决定。\n')

dashboard = '知识库/40-问题地图/个人系统运行面板-建议版.md'
replace(dashboard, 'updated: 2026-11-09', 'updated: 2026-11-10')
replace(dashboard, '| 学历、培训与职责边界 |', '| 组织关系与转岗选择 | 2026-11-10 | 9月底入职；归产研中心测试资源池，项目与实际工作在铝深加工；受邀转实施与部门 | 条件均未明确、尚未决定；部门稳定性属待核对说法，见[决策记录](../50-决策记录/'+DEC+') |\n| 学历、培训与职责边界 |')
replace(dashboard, '| 主项目候选，待本人采用 | 争取一个有授权的MES交付工作包，形成真实职责和反馈记录 | 整理一个现有测试实施案例，与经理讨论可承担的范围 | 可从现有阅读时间中每周划出6—8小时，尚未承诺 | 采用后按周回顾，90天为首轮建议 | [PMP与MES/MOM转型方案](../60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)；未登记为已获授权或已完成 |', '| 近期职业决策，尚未决定 | 比较留产研与转铝深加工实施的具体安排 | 与双方负责人讨论，形成一页待遇、任务、资源、工时和成长条件表 | 建议先做两次短沟通与条件核对，不新增固定学习承诺 | 转岗条件明确后；若公司允许试运行则按约定周期复核 | [转岗决策记录](../50-决策记录/'+DEC+')；[PMP与MES/MOM路线](../60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)继续作为长期参考 |')

plan = '知识库/60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md'
append(plan, '## 2026-11-10 实际岗位机会更新\n\n本人补充9月底入职、归产研测试资源池，项目与实际工作在铝深加工；项目经理邀请转实施及部门。目前薪酬、职责、项目数量、工时均未明确，产研领导的管理期待也仅为口头。该邀请为本方案的潜在实践机会，尚不等于已转岗或已有管理授权；具体选择见[转岗决策记录](../50-决策记录/'+DEC+')。')

# Validate and preserve all pre-existing review judgments, tags and weights except the stated corrections.
rows = [line for line in read(review).splitlines() if re.match(r'^\| \[R\d{3}\]', line)]
assert len(rows) == 128
assert sum(bool(line.split('|')[3].strip()) for line in rows) == 19
assert all(not line.split('|')[4].strip() and not line.split('|')[7].strip() for line in rows)
backups = BATCH / 'before_update'
for rel in cache:
    if (backups / rel).exists():
        raise ValueError('one-shot update already backed up '+rel)
manifest = []
for rel, value in cache.items():
    p = ROOT / rel
    backup = backups / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_bytes(originals[rel])
    p.write_text(value, encoding='utf-8', newline='\n')
    manifest.append({'file':rel, 'sha256_before':hashlib.sha256(originals[rel]).hexdigest(), 'sha256_after':hashlib.sha256(p.read_bytes()).hexdigest()})
(BATCH/'update_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'updated_files':len(manifest),'formal_records':128,'records_with_user_feedback':19,'tags_and_weights_unchanged':True},ensure_ascii=False))
