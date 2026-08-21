# 产品开发策略 Brief Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一个以预包装烘焙为核心、采用渐进式披露和“三圈定位”模型的产品开发策略 Brief Skill，并整理为可公开分享的 GitHub 仓库。

**Architecture:** Skill 入口负责模式路由和阶段状态；`references/` 保存可按需读取的稳定判断规则；项目状态保存为 JSON；动态调研只记录来源和证据，不把动态事实硬编码进知识库；内部案例与共享记忆只保留本地升级接口，不进入公开仓库。

**Tech Stack:** Python 3.11+、标准库 JSON/argparse/pathlib/unittest、Markdown、可选 `lark-cli` 飞书文档能力、Git/GitHub CLI。

---

## 公开范围和安全边界

- GitHub 仓库只公开通用方法、规则、测试夹具、脱敏示例和使用说明。
- 不公开历史客户名称、经营数字、内部文件路径、共享记忆原文、API Key、Token、Cookie 或本机凭证。
- `internal_cases/` 只放公开仓库的说明文件，不放真实内部案例；内部案例更新机制只公开接口和字段规范。
- 动态市场、竞品、平台和价格数据不提交为长期事实；项目级调研证据默认放在用户自己的项目目录。

## 文件结构

```text
产品开发策略 skill 项目/
├── SKILL.md
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── scripts/
│   ├── main.py
│   ├── router.py
│   ├── state_manager.py
│   ├── validator.py
│   ├── research_log.py
│   └── modes/
│       ├── __init__.py
│       ├── workshop.py
│       ├── diagnose.py
│       └── quick_start.py
├── references/
│   ├── 00-知识基座说明.md
│   ├── 01-知识路由表.md
│   ├── 02-三圈定位总则.md
│   ├── 03-可做：市场机会与趋势.md
│   ├── 04-想做：客户意愿与战略承接.md
│   ├── 05-能做：供应链能力与伸手可及.md
│   ├── 06-三圈交集与策略取舍.md
│   ├── 07-方法模型选择与误用边界.md
│   ├── 08-策略诊断与评分标准.md
│   ├── 09-案例与失败模式索引.md
│   ├── 10-动态调研与多来源证据规则.md
│   └── 11-品类扩展接口.md
├── templates/
│   ├── brief.json
│   └── strategy-confirmation.json
├── examples/
│   └── 脱敏三圈示例.json
├── internal_cases/
│   └── README.md
├── tests/
│   ├── test_router.py
│   ├── test_state_manager.py
│   ├── test_validator.py
│   ├── test_research_log.py
│   └── test_modes.py
└── docs/superpowers/
    ├── specs/2026-08-21-产品开发策略Brief知识基座设计.md
    └── plans/2026-08-21-产品开发策略Brief-Skill实施计划.md
```

## Task 1: 初始化仓库和公开安全边界

**Files:**
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `README.md`
- Create: `requirements.txt`
- Create: `internal_cases/README.md`
- Modify: none

- [ ] **Step 1: 初始化 Git 仓库并建立主分支**

Run:

```bash
git init -b main
```

Expected: 输出空仓库初始化信息，`git branch --show-current` 返回 `main`。

- [ ] **Step 2: 写入公开范围和敏感文件忽略规则**

`.gitignore` 必须至少包含：

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
env/
.env
*.env
*.key
*.pem
*.token
*.sqlite3
*.db
project_state.json
product-strategy.json
research/raw/
internal_cases/raw/
```

- [ ] **Step 3: 写入 MIT 许可证、公开 README 和内部案例边界说明**

README 必须说明：三圈定位、预包装烘焙范围、渐进式披露、动态多来源调研、GitHub 公共仓库不含内部案例，以及如何本地安装和运行测试。

`internal_cases/README.md` 必须明确：真实内部案例只在用户本机或受控项目目录维护，公开仓库只保留字段规范，不提交客户名称、经营数据或共享记忆原文。

- [ ] **Step 4: 运行敏感文件扫描**

Run:

```bash
rg -n -i 'api[_ -]?key|token|password|secret|cookie|client_secret|gho_[A-Za-z0-9]+' . --glob '!docs/superpowers/plans/**'
```

Expected: 只允许命中说明中的抽象字段名或 `[REDACTED]`，不得出现真实凭证和内部客户材料。

- [ ] **Step 5: 提交初始化变更**

```bash
git add .gitignore LICENSE README.md requirements.txt internal_cases/README.md
git commit -m "chore: initialize public skill repository"
```

## Task 2: 提炼并写入渐进式知识基座

**Files:**
- Create: `references/00-知识基座说明.md`
- Create: `references/01-知识路由表.md`
- Create: `references/02-三圈定位总则.md`
- Create: `references/03-可做：市场机会与趋势.md`
- Create: `references/04-想做：客户意愿与战略承接.md`
- Create: `references/05-能做：供应链能力与伸手可及.md`
- Create: `references/06-三圈交集与策略取舍.md`
- Create: `references/07-方法模型选择与误用边界.md`
- Create: `references/08-策略诊断与评分标准.md`
- Create: `references/09-案例与失败模式索引.md`
- Create: `references/10-动态调研与多来源证据规则.md`
- Create: `references/11-品类扩展接口.md`

- [ ] **Step 1: 将设计规格拆成运行时入口、核心门禁和阶段规则**

每份文件只负责一个判断层；每份文件开头写明“何时读取”和“何时不读取”。`01-知识路由表.md` 必须区分本 Skill 的“定位三圈”和现有烘焙 Skill 的“机会调研三圈”。

- [ ] **Step 2: 写入三圈定位规则**

`02-三圈定位总则.md` 必须包含：

```text
可做 ∩ 想做 ∩ 能做 = 该做
```

并明确四类反例：只有趋势、只有客户意愿、只有供应链能力、三圈证据冲突时均不能直接进入正式推荐。

- [ ] **Step 3: 写入客户现实承接规则**

`04-想做` 覆盖战略意愿、资源投入意愿、风险接受度和决策人；`05-能做` 覆盖当前产线、设备、工艺、供应商、人员、改造负担和“踮踮脚尖”四级状态。

- [ ] **Step 4: 写入多来源动态调研规则**

`10-动态调研与多来源证据规则.md` 必须写明 Tavily、国外搜索引擎/官网/零售页面、国内小红书/抖音/天猫等来源的适用场景，并把平台热度限制为趋势信号，不直接当销量事实。

- [ ] **Step 5: 写入模型路由和诊断规则**

`07` 至少覆盖 JTBD、STP、RWW、渠道—规格—价带、单位经济、产品角色/生命周期和 Stage-Gate；`08` 必须让严重缺口优先于总分。

- [ ] **Step 6: 运行知识基座结构检查并提交**

Run:

```bash
test "$(find references -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')" -eq 12
rg -n '可做 ∩ 想做 ∩ 能做|Tavily|小红书|抖音|天猫|共享记忆|机会调研三圈' references
```

Expected: 12 个参考文件，关键规则均能检索到。

```bash
git add references
git commit -m "feat: add progressive three-circle knowledge base"
```

## Task 3: 建立 JSON 状态、Brief 门禁和三圈校验

**Files:**
- Create: `templates/brief.json`
- Create: `templates/strategy-confirmation.json`
- Create: `scripts/state_manager.py`
- Create: `scripts/validator.py`
- Create: `tests/test_state_manager.py`
- Create: `tests/test_validator.py`

- [ ] **Step 1: 写失败测试覆盖最低字段和三圈状态**

测试至少覆盖：缺少八项 Brief 字段时拒绝进入策略；`目标保质期类型` 非短保/中保/长保时拒绝；三圈任一圈缺证据时状态为 `pending`；只有三圈交集成立时才允许 `recommended`。

- [ ] **Step 2: 实现原子 JSON 保存、读取、历史记录和版本字段**

`StateManager` 使用 `pathlib.Path` 和临时文件替换保存；顶层至少包含 `meta`、`brief`、`three_circle`、`outputs`、`history`。保存时更新 `updated_at`，不得写入 Token 或内部原始资料。

- [ ] **Step 3: 实现 Brief 与三圈校验器**

`validate_brief(data)` 返回结构化结果：`valid`、`missing_fields`、`invalid_fields`、`warnings`；`validate_three_circle(data)` 返回每圈状态、交集状态、阻断原因和下一步验证项。

- [ ] **Step 4: 运行单元测试**

```bash
python3 -m unittest tests.test_state_manager tests.test_validator -v
```

Expected: 全部 PASS。

- [ ] **Step 5: 提交状态和校验模块**

```bash
git add templates scripts/state_manager.py scripts/validator.py tests/test_state_manager.py tests/test_validator.py
git commit -m "feat: add brief and three-circle state validation"
```

## Task 4: 实现渐进式路由和三个 MVP 模式

**Files:**
- Create: `SKILL.md`
- Create: `scripts/router.py`
- Create: `scripts/main.py`
- Create: `scripts/modes/__init__.py`
- Create: `scripts/modes/workshop.py`
- Create: `scripts/modes/diagnose.py`
- Create: `scripts/modes/quick_start.py`
- Create: `tests/test_router.py`
- Create: `tests/test_modes.py`

- [ ] **Step 1: 写路由失败测试**

测试输入分别路由到 workshop、diagnose、quick_start；明确“对标”和“迭代”只返回预留状态，不误称为已实现。

- [ ] **Step 2: 实现关键词和上下文路由**

`detect_mode(user_input, context)` 先判断显式模式，再按确认状态、已有 JSON 和章节意图判断；默认进入 workshop。路由结果必须包含 `mode`、`reason`、`required_references`。

- [ ] **Step 3: 实现工作坊模式**

工作坊按“Brief → 可做 → 想做 → 能做 → 三圈交集 → 策略确认”推进；每次只返回一个问题，缺口未解决时不进入下一门。

- [ ] **Step 4: 实现诊断模式**

诊断报告至少包含：三圈状态、缺失证据、逻辑问题、严重度、建议动作和是否允许进入正式策略。总分只能作为辅助信息。

- [ ] **Step 5: 实现快速启动模式**

快速启动只压缩提问数量，不跳过 Brief 和三圈门槛；输出 `draft` 或 `pending` 状态，不把未验证内容写成 `recommended`。

- [ ] **Step 6: 写入 SKILL.md**

主文件只保留触发说明、模式入口、渐进式读取规则、状态边界和命令示例；详细判断放在 `references/`，避免入口文件膨胀。

- [ ] **Step 7: 运行路由和模式测试**

```bash
python3 -m unittest discover -s tests -v
```

Expected: 所有已实现模式测试通过；对标/迭代测试明确返回 `reserved`。

- [ ] **Step 8: 提交 MVP**

```bash
git add SKILL.md scripts tests
git commit -m "feat: implement workshop diagnose and quick-start modes"
```

## Task 5: 实现多来源调研记录和内部案例升级接口

**Files:**
- Create: `scripts/research_log.py`
- Modify: `scripts/state_manager.py`
- Modify: `references/09-案例与失败模式索引.md`
- Modify: `references/10-动态调研与多来源证据规则.md`
- Create: `tests/test_research_log.py`

- [ ] **Step 1: 写调研记录失败测试**

测试来源类型、日期、URL、证据类别和禁止外推字段缺失时拒绝保存；同一来源 ID 重复写入时保持幂等。

- [ ] **Step 2: 实现研究记录器**

`ResearchLog.add_source()` 保存项目级证据记录；支持 `tavily`、`foreign_web`、`official`、`xiaohongshu`、`douyin`、`tmall`、`other` 来源类型；不保存登录 Cookie、Token 或页面密码。

- [ ] **Step 3: 实现内部案例索引接口**

只实现本地案例卡的字段校验和版本记录；共享记忆召回由运行时 Agent 调用，脚本不复制云端原文，也不自动把记忆线索升级为正式案例。

- [ ] **Step 4: 运行研究记录测试并提交**

```bash
python3 -m unittest tests.test_research_log -v
git add scripts/research_log.py scripts/state_manager.py references/09-案例与失败模式索引.md references/10-动态调研与多来源证据规则.md tests/test_research_log.py
git commit -m "feat: add multi-source research and case iteration hooks"
```

## Task 6: 脱敏示例、完整验收和公开发布包

**Files:**
- Create: `examples/脱敏三圈示例.json`
- Modify: `README.md`
- Create: `CHANGELOG.md`
- Create: `发布检查清单.md`

- [ ] **Step 1: 写脱敏三圈示例**

示例只使用虚构品类、虚构客户和虚构数据，覆盖三圈交集成立、趋势好但客户不想做、客户想做但能做等级为 major_investment 三个案例。

- [ ] **Step 2: 运行完整测试和命令行烟测**

```bash
python3 -m unittest discover -s tests -v
python3 scripts/main.py --input '我想快速做一个预包装烘焙新品策略' --project-path ./examples/烟测项目
```

Expected: 测试全部通过；烟测只生成脱敏项目状态，不生成飞书文档、不访问外部平台、不输出凭证。

- [ ] **Step 3: 执行公开发布审计**

检查：

```bash
rg -n -i '客户名称|内部项目|手机号|邮箱|api[_ -]?key|token|password|secret|cookie|/Users/|gho_' . --glob '!.git/**'
```

内部项目名、绝对路径和真实凭证不得出现在公开代码、示例和 README 中；设计文档可以保留抽象方法，但公开仓库不能包含真实内部案例内容。

- [ ] **Step 4: 生成发布检查清单并确认工作树**

```bash
git status --short
git diff --check
git log --oneline --decorate -8
```

- [ ] **Step 5: 创建公开 GitHub 仓库并推送**

先确认仓库名为 `product-strategy-brief-skill`；使用 GitHub CLI 创建公开仓库并推送：

```bash
gh repo create product-strategy-brief-skill --public --source=. --remote=origin --push
```

如果该仓库名已存在，停止并读取当前远端状态，不覆盖已有仓库；改用用户明确指定的新名称。

- [ ] **Step 6: 公开仓库线上验收**

```bash
git remote -v
gh repo view --json nameWithOwner,isPrivate,url,defaultBranchRef
```

Expected：远端是公开仓库、默认分支为 `main`、README 和 Skill 文件可见；不在回复中展示 Token 或其他敏感内容。

## 实施完成定义

只有同时满足以下条件，才报告本次 MVP 完成：

- 12 份渐进式知识基座参考文件存在且路由可读；
- Brief、三圈状态、证据和历史记录可保存并校验；
- workshop、diagnose、quick_start 三个模式可运行；
- 多来源调研记录器和内部案例升级接口通过测试；
- 脱敏反例测试覆盖三圈不重叠情况；
- 本地测试、`git diff --check` 和发布审计通过；
- GitHub 公开仓库创建成功并在线可见；
- 对标学习和策略迭代明确标记为第二阶段预留，不冒充已完成。
