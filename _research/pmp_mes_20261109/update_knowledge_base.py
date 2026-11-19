from pathlib import Path
import json, re, hashlib, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent
cache = {}
originals = {}

def read(rel):
    if rel not in cache:
        p = ROOT / rel
        originals[rel] = p.read_bytes()
        cache[rel] = p.read_text(encoding='utf-8')
    return cache[rel]

def replace(rel, old, new, count=1):
    text = read(rel)
    if text.count(old) != count:
        raise ValueError(f'{rel}: expected {count} matches for {old[:70]!r}, got {text.count(old)}')
    cache[rel] = text.replace(old, new)

def append(rel, value):
    cache[rel] = read(rel).rstrip() + '\n\n' + value.strip() + '\n'

SOURCE = '[本人学历与职责澄清](../10-原始资料/SRC-USER-20261109-001/本人确认原文.md)'
ACTION = '知识库/60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md'

def update_record(rel, rid, note, replacements=()):
    text = read(rel)
    match = re.search(r'^### '+re.escape(rid)+r'\s*\n.*?(?=^### R\d{3}\s*$|\Z)', text, re.M|re.S)
    if not match:
        raise ValueError(rid)
    block = match.group(0)
    marker = '\n- 信息性质：'
    if marker not in block:
        raise ValueError(rid+' information marker')
    block = block.replace(marker, '\n**本人补充与适用边界（2026-11-09）：** '+note+'依据'+SOURCE+'。\n'+marker, 1)
    for old, new in replacements:
        if block.count(old) != 1:
            raise ValueError(rid+' '+old)
        block = block.replace(old, new, 1)
    cache[rel] = text[:match.start()] + block + text[match.end():]

identity = '知识库/15-个人档案/01-身份家庭与时间线.md'
replace(identity, 'status: 待本人审核', 'status: 学历部分获本人确认，其余历史信息待审')
replace(identity, '以下均为对来源文档的分类提取。原文自称事实不等于本库确认；此处的分类与信息性质仅用于整理，你的标签和真实性判断尚未填写。所有权重为空。', '本页保留来源文档的分类提取；R003已补充本人2026-11-09的学历确认，其他未经确认的信息仍待审。本人标签与所有知识权重为空。')
update_record(identity, 'R003', '本人确认2019年全日制大专毕业，2022年函授本科毕业，只有本科毕业证、没有学士学位证。学校、专业与证书未独立核验；PMP教育等值类别待官方确认。', [
    ('- 信息性质：源文转述。', '- 信息性质：学历形式、毕业年份与学位状态本人确认；其他细节待审。'),
    ('- 时间范围：历史记录；当前适用性待本人确认。', '- 时间范围：历史摘要与2026-11-09本人补充。'),
    ('- 待核对或使用边界：学校、专业、起止日期与本科完成状态未核对。', '- 待核对或使用边界：学校、专业、入学日期和证书未核对；不把函授本科写成全日制本科或已获学士学位。'),
    ('- 本人判断／本人标签：待填写；后续权重：未评定。', '- 本人部分确认已回写唯一审核表；本人标签待填写，后续权重未评定。')])

career = '知识库/15-个人档案/02-职业履历与能力线索.md'
update_record(career, 'R009', '本人确认2016年开始工作、做过多个行业；没有逐一确认原摘要列举的行业、任职年月及成果。', [
    ('- 信息性质：经历转述。', '- 信息性质：2016年开始跨行业工作本人确认；具体行业清单仍为待审摘要。'),
    ('- 本人判断／本人标签：待填写；后续权重：未评定。', '- 本人部分确认已回写唯一审核表；本人标签待填写，后续权重未评定。')])
update_record(career, 'R010', '本人确认近几年从事MES测试与实施，但未确认完整软件测试起止年月，旧摘要“约6年”仍待核对。')
update_record(career, 'R011', '近几年从事MES测试与实施，目标为MES/MOM项目经理；本人明确未负责实施计划、客户需求、跨部门协调、人员分工、进度控制、变更或验收，不能提供相关证明。岗位目标不等于已有管理经验。')
replace(career, '具体管理权限和能力熟练度仍未说明。', '职责边界已由2026-11-09本人补充限定，能力熟练度仍需具体案例核对。')
update_record(career, 'R012', '本人明确未负责人员分工、跨部门协调及上述项目管理事项，不能提供相关证明；旧“团队管理”表述不能作为已确认能力。功能/性能测试、JMeter、Java、腾讯云等具体技能仍未逐项确认。', [
    ('- 信息性质：能力转述。', '- 信息性质：技能线索待审；管理表述的使用范围按本人澄清限定。'),
    ('- 本人判断／本人标签：待填写；后续权重：未评定。', '- 管理职责限定已回写唯一审核表；其余技能仍待审，本人标签与后续权重未填写。')])
update_record(career, 'R020', '职业目标明确为MES/MOM项目经理，正在评估PMP；转岗及报考时间未确定。既有宁波、杭州与美国长期意向沿用11月5日记录。')
update_record(career, 'R124', '本人明确没有负责验收管理等上述事项；“项目在上线验收阶段、本人做全模块测试与实施”不能转写为主导项目验收。')

profile = '知识库/15-个人档案/00-当前状态与长期方向.md'
replace(profile, 'updated: 2026-11-05', 'updated: 2026-11-09')
replace(profile, 'sources: [SRC-USER-20261105-001, SRC-USER-20261105-002, SRC-USER-20261105-003, SRC-USER-20261105-004]', 'sources: [SRC-USER-20261105-001, SRC-USER-20261105-002, SRC-USER-20261105-003, SRC-USER-20261105-004, SRC-USER-20261109-001]')
replace(profile, '截至2026-11-05（北京时间）。依据', '本页最近更新2026-11-09；本轮新确认学历、职责边界与职业目标，财务、薪酬、地点及作息仍为2026-11-05自述快照，未据本次答复自动刷新。依据')
replace(profile, '及[人民币可用资金与近期支出补充](../10-原始资料/SRC-USER-20261105-004/本人确认原文.md)更新。', '、[人民币可用资金与近期支出补充](../10-原始资料/SRC-USER-20261105-004/本人确认原文.md)及'+SOURCE+'更新。')
replace(profile, '| 当前职业与职责 | MES测试，负责软件全模块的测试与实施 | 职级、团队规模与管理权限尚未说明 |', '| 当前职业与职责 | MES测试，负责软件全模块的测试与实施 | 本轮明确未负责实施计划、客户需求、跨部门协调、人员分工、进度控制、变更或验收管理；正式职级和团队规模待核对 |')
replace(profile, '| 当前项目阶段 | MES项目上线验收阶段 | 尚未记为已通过验收或本人已任项目经理 |', '| 当前项目阶段 | MES项目上线验收阶段 | 阶段来自11月5日自述；参与验收期不等于负责验收管理，未记为已通过验收 |\n| 学历与学位 | 2019年全日制大专毕业；2022年函授本科毕业，无学士学位证 | 2026-11-09本人补充；学校、专业及证书未独立核验，PMP教育等值类别待官方确认 |\n| 工作时间线 | 2016年开始跨行业工作，近几年从事MES测试与实施 | 2026-11-09本人补充；具体任职年月和旧摘要“6年”待核对 |\n| 项目管理培训与证明 | 暂无项目管理培训，不能提供上述管理经历证明 | 2026-11-09本人补充；尚不能证明PMP合格经验月数 |')
replace(profile, '| 人民币可用现金 | 约5000元 | 最新本人直接回复，指可随时使用的人民币资金，不等于完整资产表 |', '| 人民币可用现金 | 约5000元 | 2026-11-05快照，非11月9日新余额；不等于完整资产表 |')
replace(profile, '| 职业发展 | 从MES测试向MES项目经理方向发展 | 发展意向，尚非当前职务 |', '| 职业发展 | 从MES测试与实施向MES/MOM项目经理方向发展，准备研究PMP | 2026-11-09明确；发展意向，尚非当前职务或已满足报考资格 |')
replace(profile, '- MES验收期适合积累问题、协调、实施与验收的真实交付记录，具体采用何项行动仍待本人选择。', '- 职业建议以争取真实工作包责任、执行与反馈为主，详见[PMP与MES/MOM项目经理转型方案](../60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)；未实际承担的协调与验收管理不能作为已有经历。')
append(profile, '| 2026-11-09 | 明确全日制大专2019年毕业、函授本科2022年毕业但无学士学位；2016年起工作、近年MES测试实施；暂无管理培训且未负责所列管理事项，目标扩展至MES/MOM项目经理 | '+SOURCE+'；具体任职月份与PMP学历等值仍待核对 |')
replace(profile, '\n\n| 2026-11-09 |', '\n| 2026-11-09 |')

review = '知识库/80-审核与权重/01-真实性与标签审核.md'
review_rows = {
 'R003': ('部分属实：学历形式、毕业年份与学位状态本人确认', '2019年全日制大专毕业；2022年函授本科毕业，无学士学位证；学校、专业和证书未独立核验，PMP教育等值类别待官方确认。'),
 'R009': ('部分属实：2016年起跨行业工作本人确认', '2016年开始工作，做过多个行业；原摘要列举的各行业、日期与成果未逐项确认。'),
 'R011': ('部分属实：MES测试实施及发展方向本人确认', '近几年从事MES测试与实施，目标为MES/MOM项目经理；未负责实施计划、客户需求、跨部门协调、人员分工、进度控制、变更或验收；具体能力需案例核对。'),
 'R012': ('部分限定：管理表述不能作为已确认能力', '本人明确未负责人员分工、跨部门协调及所列项目管理事项，不能提供相关证明；旧团队管理表述不据此认可，其余技术技能仍待审。'),
 'R020': ('部分属实：现行职业规划已确认', '目标扩展为MES/MOM项目经理，准备研究PMP；宁波杭州与美国长期意向沿用11月5日记录，未确定报考或转岗时间。'),
 'R124': ('本人确认：测试实施职责与管理边界', '项目上线验收期及全模块测试实施来自11月5日自述；11月9日明确未负责验收管理等所列管理事项，不能写成主导验收。')
}
text = read(review)
for rid, (judgment, correction) in review_rows.items():
    pattern = r'^\| \['+rid+r'\].*$'
    match = re.search(pattern, text, re.M)
    if not match:
        raise ValueError('missing review '+rid)
    fields = [x.strip() for x in match.group().split('|')[1:-1]]
    if len(fields) != 7 or fields[3] or fields[6]:
        raise ValueError('review shape or existing tag/weight '+rid)
    fields[2], fields[4], fields[5] = judgment, correction, '2026-11-09本人补充；原状态日期分别保留'
    text = text[:match.start()] + '| ' + ' | '.join(fields) + ' |' + text[match.end():]
cache[review] = text
replace(review, '后续[人民币可用资金与近期支出补充]', '最新'+SOURCE+'已回写R003、R009、R011、R012、R020、R124；新增3条已有本人反馈，未新增R编号。\n\n后续[人民币可用资金与近期支出补充]')

count_files = [
 '00-开始这里.md','04-首批资料分析与审核说明.md','知识库/00-系统导航.md',profile,
 '知识库/80-审核与权重/00-审核入口.md',review,'知识库/80-审核与权重/04-入库覆盖与处理报告.md'
]
for rel in count_files:
    t = read(rel)
    # Only current count statements; dated historical verification entries stay intact.
    if rel.endswith('04-入库覆盖与处理报告.md'):
        old = '当前128条中，16条已有本人判断、补充或适用性更正（R011、R014、R015、R016、R020、R021、R024、R032、R035、R048、R085、R124—R128），112条尚未填写本人判断。'
        new = '当前128条中，19条已有本人判断、补充或适用性更正（R003、R009、R011、R012、R014、R015、R016、R020、R021、R024、R032、R035、R048、R085、R124—R128），109条尚未填写本人判断。'
        replace(rel, old, new)
        replace(rel, '当前仍为128条、11个主题；16条已有本人反馈、补充或更正，112条尚无本人判断；', '当时仍为128条、11个主题；16条已有本人反馈、补充或更正，112条尚无本人判断；')
    else:
        t = t.replace('16条已有本人', '19条已有本人').replace('累计16条已回写', '累计19条已回写').replace('112条尚未填写本人判断', '109条尚未填写本人判断')
        cache[rel] = t

entry = '00-开始这里.md'
replace(entry, '更新日期：2026-11-05（北京时间）。', '更新日期：2026-11-09；各项事实保留其原始适用日期。')
replace(entry, '最新：[当前状态与长期方向]', '职业新补充：[PMP资格与MES/MOM项目经理转型方案]('+ACTION+')。已明确函授本科只有毕业证、无学士学位及实际管理职责边界；给出官方资格核对、90天工作包路线和真实经历表达模板。方案为建议，尚非本人行动承诺。\n\n当前档案：[当前状态与长期方向]')
replace(entry, '职业向MES项目经理发展，长期工作地倾向宁波、杭州，长期规划美国移民。', '职业目标已于11月9日明确为MES/MOM项目经理；薪酬、地点、作息等沿用11月5日快照，长期工作地倾向宁波、杭州，长期规划美国移民。')
nav = '知识库/00-系统导航.md'
replace(nav, '## 使用入口\n', '## 使用入口\n\n- [PMP与MES/MOM项目经理转型](60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)：学历与经验条件核对、90天工作包路线、真实表达及转岗机会成本；建议版。\n')
replace(nav, '8. [候选方案评估](90-模板/T08-候选方案评估.md)', '8. [候选方案评估](90-模板/T08-候选方案评估.md)\n9. [真实项目职责与能力证据](90-模板/T09-真实项目职责与能力证据.md)')

source_index = '知识库/10-原始资料/来源索引.md'
replace(source_index, '\n\n## 授权应用页面观察', '\n| [SRC-USER-20261109-001](SRC-USER-20261109-001/本人确认原文.md) | 大专与函授本科毕业年份、无学士学位、2016年起工作、近年MES测试实施、暂无培训及明确的管理职责边界、MES/MOM项目经理目标 | 本人直接陈述；学历与证明未独立核验，回写既有记录，不增加R编号 |\n\n## 授权应用页面观察')
append(source_index, '## 后续公开职业研究\n\n- [2026-11-09 PMP与MES/MOM项目经理转型](../60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)：S01—S05列明PMI现行全球资格、经验解释、FAQ、CAPM和中国区访问边界；[本地核验说明](../../_research/pmp_mes_20261109/来源与核验说明.md)可追溯。本轮未取得中国学历等值书面确认或杭州宁波招聘详情样本。')

dashboard = '知识库/40-问题地图/个人系统运行面板-建议版.md'
replace(dashboard, 'created: 2026-11-05', 'created: 2026-11-05\nupdated: 2026-11-09')
replace(dashboard, '本人已确认方向：目前从事MES测试，向MES项目经理发展', '本人已确认方向：目前从事MES测试与实施，目标已扩展为MES/MOM项目经理，正在评估PMP')
replace(dashboard, '| 当前薪酬条件 |', '| 学历、培训与职责边界 | 2026-11-09 | 全日制大专2019年毕业；函授本科2022年毕业无学士学位；暂无管理培训，未负责所列项目管理事项 | 见[最新本人来源](../10-原始资料/SRC-USER-20261109-001/本人确认原文.md)，PMP教育等值及合格经验月数尚未认定 |\n| 当前薪酬条件 |')
replace(dashboard, '| 主项目，建议最多1个 | 待选择 | 待填写 | 待填写 | 待填写 | 待填写 |', '| 主项目候选，待本人采用 | 争取一个有授权的MES交付工作包，形成真实职责和反馈记录 | 整理一个现有测试实施案例，与经理讨论可承担的范围 | 可从现有阅读时间中每周划出6—8小时，尚未承诺 | 采用后按周回顾，90天为首轮建议 | [PMP与MES/MOM转型方案](../60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)；未登记为已获授权或已完成 |')

gaps = '06-待补数据与系统构建研究路线.md'
replace(gaps, '| D03 已部分补齐 | 当前项目的具体问题与权限 | 已知上线验收阶段、全模块测试与实施；剩余为自己可决定和需协调的事项、一个影响交付的问题及已有反馈 |', '| D03 已补职责边界 | 当前项目的具体问题与权限 | 已知全模块测试实施；11月9日明确未负责计划、需求、跨部门协调、分工、进度、变更或验收；剩余为一个真实测试实施案例、现有权限与主管可授予的工作包 |')
replace(gaps, '| D04 随职业项目补 | 目标项目经理角色与能力证据 | 更倾向厂商交付、实施项目管理或甲方项目管理；已有需求、计划、协调、验收等经验各举一例，没有就留空 |', '| D04 学历与管理缺口已补 | 目标项目经理角色与能力证据 | 已确认大专2019、函授本科2022毕业无学士学位，暂无培训及所列管理经历；剩余为目标甲乙方类型、任职项目起止年月和实际职责升级机会，不再要求重复提供已明确没有的经历 |')
replace(gaps, 'D01、D02、D03、D05、D07已有明确补充，不再从头重问。', 'D01、D02、D03、D04、D05、D07已有明确补充，不再从头重问。11月9日新增[PMP与MES/MOM转型方案]('+ACTION+')；学历等值待官方确认，首轮以真实工作包与反馈为重点。')

append('07-本次补充分析与知识库更新.md', '## 2026-11-09 职业职责口径更新\n\n本人进一步明确：2019年大专、2022年函授本科毕业，无学士学位；近年MES测试与实施，未负责所列计划、需求、协调、分工、进度、变更或验收管理，暂无培训且不能提供相关证明。前文“验收交付案例”是行动建议，不能读作已有管理经历。后续以[PMP与MES/MOM转型方案]('+ACTION+')及[最新本人原文](知识库/10-原始资料/SRC-USER-20261109-001/本人确认原文.md)限定使用范围。')
replace('04-首批资料分析与审核说明.md', '更新：2026-11-05已依据两轮本人回复及澄清，新增5条独立记录，当前共128条；', '更新：截至2026-11-09，原123条另新增5条独立记录，仍共128条；学历及职责边界的新补充回写既有条目；')
append('知识库/80-审核与权重/00-审核入口.md', '## 2026-11-09 职业增量\n\n'+SOURCE+'已回写R003、R009、R011、R012、R020、R124。学历、开始工作年份及管理表述共新增3条已有反馈，当前19条有本人反馈、109条尚无本人判断；具体技能与历史细节仍待审。新增[PMP与MES/MOM转型方案](../60-行动项目/ACT-20261109-001-PMP与MES-MOM项目经理转型.md)，方案不代表已采纳或已完成。')
append('知识库/80-审核与权重/04-入库覆盖与处理报告.md', '## 2026-11-09 职业补充\n\n新增本人来源SRC-USER-20261109-001，回写R003、R009、R011、R012、R020、R124，正式条目仍为128条；19条已有本人反馈，109条尚未填写。学历、跨行业工作起点与管理表述限定为本次新增反馈，部分记录的其余历史细节继续待审。新增职业方案、真实项目模板和PMI公开页面核验记录；本人标签及权重继续留空。')

# Validate all expected counts before writing; no new R records are created.
rows = [line for line in read(review).splitlines() if re.match(r'^\| \[R\d{3}\]', line)]
judged = [line for line in rows if line.split('|')[3].strip()]
if len(rows) != 128 or len(judged) != 19:
    raise ValueError((len(rows), len(judged)))

changed = []
for rel, text in cache.items():
    p = ROOT / rel
    encoded = text.encode('utf-8')
    if encoded == originals[rel]:
        continue
    backup = BATCH / 'before_update' / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    if backup.exists():
        raise ValueError('backup already exists; stop before overwriting '+rel)
    backup.write_bytes(originals[rel])
    p.write_text(text, encoding='utf-8', newline='\n')
    changed.append({'file': rel, 'sha256_before': hashlib.sha256(originals[rel]).hexdigest(),
                    'sha256_after': hashlib.sha256(p.read_bytes()).hexdigest()})
(BATCH/'knowledge_base_update_manifest.json').write_text(json.dumps(changed, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'updated_files':len(changed), 'review_records':len(rows), 'with_user_feedback':len(judged), 'without_user_judgment':len(rows)-len(judged)}, ensure_ascii=False))
