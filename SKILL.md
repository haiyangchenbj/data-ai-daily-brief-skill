---
name: data-ai-daily-brief
version: "3.0"
description: |
  AI-powered industry intelligence daily brief generator. This skill automatically searches,
  filters, writes, and delivers structured daily briefings for any industry.
  Default configuration covers Data+AI (data platforms, lakehouse, streaming, governance, etc.),
  but can be customized for FinTech, HealthTech, Cybersecurity, DevTools, or any domain.
  Trigger keywords: daily brief, 日报, industry report, 行业日报, data+ai report, 数据平台日报,
  全球日报, industry newsletter, intelligence brief, 情报简报.
allowed-tools:
  - read_file
  - write_to_file
  - replace_in_file
  - execute_command
  - web_search
  - web_fetch
disable: false
---

# AI 行业情报日报生成器

一个 AI 驱动的行业情报日报生成技能，自动搜集、过滤、编写并推送高质量的行业日报。默认以 Data+AI 行业为例，可通过配置文件切换至任何行业。

## 工作流程

当用户请求生成日报时，按以下步骤执行：

### Step 1: 确认配置

1. 读取工作区中的 `daily-brief-config.json` 配置文件（如果存在）
2. 如不存在，使用 `scripts/init_config.py` 初始化默认配置
3. 确认目标日期（默认当天）和输出渠道

### Step 2: 信息采集与过滤

使用 web_search 工具，按以下优先级和过滤规则采集信息：

#### 核心原则

**数据平台优先，严格过滤。** 每条信息必须能明确回答：这会影响企业数据平台的产品路线、架构设计、成本结构、治理方式、运维效率或 Agent 在数据场景的落地吗？如果不能明确回答「是」，一律不纳入。

**信息宁缺毋滥。** 绝不因为某个板块条目过少而降低准入标准。日报的价值在于精准，不在于条数多。

#### 搜索策略（三阶段）

**阶段一：一手来源定向搜索（必须执行）**

针对第一优先级厂商，逐一搜索其官方渠道：

英文搜索：
1. `site:databricks.com OR site:snowflake.com OR site:aws.amazon.com announcement`
2. `site:cloud.google.com OR site:azure.microsoft.com data platform announcement`
3. `site:github.com (apache/iceberg OR apache/spark OR apache/flink OR trinodb/trino) release`
4. `site:prnewswire.com OR site:businesswire.com data platform OR data lake OR data warehouse`
5. `site:prnewswire.com OR site:businesswire.com (funding OR acquisition OR IPO) data platform`

中文搜索：
1. `site:cloud.tencent.com OR site:help.aliyun.com 数据 发布`
2. `site:volcengine.com OR site:huaweicloud.com 数据 公告`
3. `site:caict.ac.cn OR site:ccidreport.com OR site:cesi.cn 数据 发布 报告`

**投融资定向搜索（必须执行）**：
1. `(Databricks OR Snowflake OR Confluent OR ClickHouse OR dbt) funding OR acquisition OR IPO`
2. `data platform OR data infrastructure funding round`
3. `数据平台 OR 大数据 融资 OR 收购 OR 上市`
4. `(Databricks OR Snowflake OR Palantir OR Elastic OR Cloudera) earnings OR revenue OR quarterly results`

**阶段二：扩展搜索（补充覆盖）**

英文：
1. `"data platform" OR "data infrastructure" release announcement {date_range}`
2. `Databricks OR Snowflake OR "data lakehouse" announcement {date_range}`
3. `Apache Iceberg OR Hudi OR Paimon OR "Delta Lake" release {date_range}`
4. `"data governance" OR "data catalog" OR "data quality" announcement {date_range}`
5. `Gartner OR Forrester OR IDC "data platform" OR "data analytics" {date_range}`
6. `ClickHouse OR DuckDB OR StarRocks OR Doris release update {date_range}`

中文：
1. `数据平台 OR 数据基础设施 发布 公告`
2. `湖仓一体 OR 数据湖 OR 数据治理 新品`
3. `阿里云 OR 腾讯云 OR 华为云 数据 发布`

**阶段三：来源溯源（强制执行）**

对阶段二中通过媒体报道发现的信息，必须使用 web_fetch 或追加 site: 搜索追溯到一手来源。无法找到一手来源的信息标注「⚠️ 待验证」或降级到 Watchlist。

**搜索覆盖硬性要求**：必须对所有第一优先级厂商至少执行一次定向搜索。

#### 覆盖范围与时效性（红线规则）

**工作日（周二至周五）** 严格只覆盖过去 24 小时内（日报日期前一天 08:00 至当天 08:00 CST）首次公开发布的信息。

**周一特殊规则：** 时效性窗口扩展为 72 小时（上周五 08:00 CST 至周一 08:00 CST），覆盖周五至周日三天。周一日报总量上限从 10-14 条放宽至 14-20 条。周一日报标题标注为《Data+AI 全球日报 | YYYY-MM-DD（含周末）》。

⚠️ **时效性红线——以下情况一律不得纳入：**
- 原始发布日期早于当期时效窗口的信息
- 已在此前日报中出现过的信息
- 产品发布日期在数天甚至数周前的旧公告
- 会议/峰会日程等已提前公布、非今日首次披露的常态信息

✅ **时效性判定方法：**
1. 查看原始页面的发布日期（publish date）
2. 发布日期不在当期窗口内 → 直接排除
3. 日报撰写前，先列出候选信息的发布日期清单，逐条确认

#### 聚焦领域

大数据、数据平台、数据基础设施、数据治理、数据工程、数据智能平台、湖仓架构、查询引擎、流批处理、向量检索基础设施、开源数据生态。

AI 相关信息**仅在明确影响数据平台**时才纳入。

#### 严格排除

- 纯 AI 新闻（纯模型发布、纯 benchmark、纯消费级 AI 产品）
- AI 产业中与数据平台无直接关系的动态
- 财经媒体、大众媒体的二手报道和分析
- 搬运号、标题党、无来源转述

#### 厂商关注优先级

**第一优先级：** AWS、Google Cloud、Microsoft Azure、Databricks、Snowflake、阿里云、腾讯云、华为云、字节跳动火山引擎

**第二优先级：** Confluent、MongoDB、Elastic、ClickHouse、Cloudera、Starburst/Trino、dbt Labs、Fivetran、Airbyte、Dataiku、Palantir、百度智能云、京东云

**仅在与数据平台直接相关时：** NVIDIA、Intel、AMD

#### 开源项目

Iceberg、Hudi、Paimon、Delta Lake、Trino、Spark、Flink、Ray、Airflow、Kafka、dbt、ClickHouse、DuckDB、Milvus、Weaviate、Lance/LanceDB、StarRocks、Doris、SeaTunnel、Amoro 等。

#### 投融资信息源参考

**重点跟踪厂商：** Databricks、Snowflake、Google Cloud、AWS、阿里云大数据、Elastic、Cloudera、华为云大数据、Palantir

**信息源：** SiliconANGLE Big Data、DBTA (Database Trends and Applications)、InfoQ 大数据、PR Newswire、Business Wire、SEC EDGAR（美股财报）、各公司 IR 页面

#### 分析师机构

**全球头部：** Gartner、Forrester、IDC、a16z、Sequoia、Bessemer

**国内研究机构：** 信通院、赛迪研究院、电子标准院、艾瑞咨询、亿欧智库

**头部券商研报：** 国内外头部券商中与数据平台直接相关的核心论点和数据

#### 信源要求

**仅接受一手来源：** 官网、官方博客、release notes、GitHub 仓库、原始发言（X/LinkedIn/博客）、earnings call 原始记录、分析师机构报告、PR Newswire/Business Wire 新闻稿

**不接受：** 财经媒体二手分析（分析师报告除外）

### Step 3: 编写日报

基于已筛选出的有效信息，生成一份面向数据平台从业者的专业日报。

#### 信息置信度分层

**Level A：已确认事实** — 有公司官网、官方博客、GitHub release、财报文件、活动实录等一手来源确认。→ 可进入 A / B / C / D。

**Level B：高可信二手确认** — 有 Reuters、Bloomberg、TechCrunch 等可靠媒体报道，但暂无一手文件。→ 可谨慎进入 A / C，但必须标注「媒体报道/未见公司正式文件」。未正式确认事件优先放 E。

**Level C：间接信号 / 未证实传闻** — 社交媒体爆料、社区讨论、未合并 PR 猜测。→ 只能进 E. Watchlist。

#### 去重规则

同一条信息只能归入一个主板块，优先级：A > B > C > D > E。若已作为 A 板块核心事件，不再在 B/C/D 重复展开。

**去重自检（强制步骤）：** 完成全部板块编写后，列出所有事件/来源/产品名称，检查跨板块重复。同一事件出现在两个以上板块 → 保留优先级最高的板块，其余删除或仅用一句引用（≤15字）。

#### 标题与开头

标题格式：`# Data+AI 全球日报 | YYYY-MM-DD`（周一标注「含周末」）

**开头固定结构：**
```markdown
**今日最重要的3点：**
1. [一句趋势判断，写方向而非完整事件，15-30 字]
2. [一句趋势判断，写方向而非完整事件，15-30 字]
3. [一句趋势判断，写方向而非完整事件，15-30 字]

**总判断：** [用 1-2 句话给出当天最值得带走的行业判断，≤120字，必须落到数据平台演进方向、投入重点或市场变化]
```

**重要区分：**「今日最重要的3点」不是 Top Signals 的摘要版，也不是 3 条事件标题。它是跨事件提炼出的 3 个「今天该带走的变化方向」。

**硬约束：**
- 每条判断 15-30 字（不需要撑满，能说清楚即可），不得包含产品名全称、版本号、具体数字
- 好的判断应该能让读者理解"发生了什么方向的变化"以及"so what"

**总判断约束：**
- ≤120 字，不需要撑满，简洁优先
- 必须是方向性判断，不可重复3点或 A 板块的事件细节

**自检方法：** 写完3点后，遮住 A 板块，只看3点。如果读者能从3点中直接还原出 A 板块每条的标题和核心数字，说明3点写得太像摘要了，需要重写。

#### 正文板块

**A. Top Signals（3条）**

当天最重要的已发生事件，必须有一手来源。每条包含：
```markdown
### 1. 事件标题
**来源：** [具体出处](链接)
**摘要：** 2-3 句
**为什么对数据平台重要：** xxx
> 企微摘要：xxx
```

**B. Product & Tech（0-6条，宁缺毋滥）**

严格限定为数据平台相关的产品与技术动态。
- 允许：云厂商数据产品发布/更新、开源数据项目 release、数据框架/引擎/工具链新版本
- 不允许：政策文件、股市行情、券商研报、AI模型发布（除非直接集成到数据平台产品中）

每条包含：事件标题、来源、摘要（1-2句）、对数据平台的影响判断、**企微摘要**

**C. Views & Research（0-5条）**

收录两类高价值信息：关键人物的原始观点，以及高公信力机构的正式研究。
- **人物观点：** 创始人、CEO、CTO 等在采访、演讲、博客、X、LinkedIn 中的原始表达
- **机构研究：** Gartner / Forrester / IDC / 信通院 / 赛迪 / 头部券商的官方报告

每条包含：人物/机构名称、来源、核心观点、映射到数据平台的判断、**企微摘要**

**D. Capital & Corporate（0-4条，宁缺毋滥）**

收录与数据平台领域直接相关的资本与公司事件，使用 inline 类型标签：
1. **【投融资】** — 融资轮次、战略投资、估值变化
2. **【财报发布】** — 季度/年度业绩、营收增长、关键业务指标
3. **【IPO】** — IPO 申请、上市定价、首日表现
4. **【收购兼并】** — 收购、合并、资产剥离

每条包含：
```markdown
### 1. 【投融资】事件标题
**来源：** [具体出处](链接)
**核心数据：** 融资金额/估值/营收/增长率
**摘要：** 2-3 句
**对数据平台的影响：** xxx
> 企微摘要：xxx
```

**E. Watchlist（1-3条）**

收录三类信息：
- **【预告】** 即将发生的重要事件
- **【降级】** 有价值但不满足 A-D 准入标准的信息
- **【跟踪】** 已发生事件的后续影响仍待验证

每条包含：关注项标题、来源、为什么值得继续看、需要等待什么信号确认、**企微摘要**

#### 企微摘要字段规则（所有板块通用）

每条新闻在所有详细字段之后，必须附加一行：`> 企微摘要：一句话语义压缩`

规则：
- **对整段内容做语义压缩**，30-80 字
- 必须是独立成句、信息自足的完整句子
- 不包含链接、不包含来源标注
- **仅出现在 Markdown 文件中**，HTML 文件中不展示

#### 输出要求

- 输出中文，专业、简洁、克制
- 每条信息必须有：来源（具体链接或出处）、摘要、影响判断
- 总量控制在 10-14 条（周一为 14-20 条），宁少勿滥
- 不杜撰数据

### Step 4: 生成输出文件

1. **Markdown 文件**：`Data+AI全球日报_{date}.md`
   - 每条新闻包含 `> 企微摘要：xxx` 行
2. **HTML 文件**：参考 `assets/report-template.html` 模板样式，生成美观的 `Data+AI全球日报_{date}.html`
   - HTML 中每条信息的来源带有可点击的超链接
   - 投融资板块使用类型标签（彩色标记区分投融资/财报/IPO/收购兼并）
   - **不包含企微摘要行**

### Step 5: Review & 修正

生成文件后、推送前，必须执行一轮完整 review。review 不通过不得进入 Step 6 推送。

**Review 检查项：**
1. **时效性合规** — 逐条核对发布日期是否在时效窗口内
2. **跨板块去重** — 同一事件出现在两个以上板块 → 合并
3. **板块准入合规** — 逐条检查是否符合所在板块准入标准
4. **信源质量** — 每条是否有明确一手来源链接
5. **格式完整性** — 企微摘要行、来源/摘要/影响三要素、3点是否为趋势判断（15-30字）、总判断是否 ≤120 字且不重复事件细节
6. **宁缺毋滥** — 各板块条数是否在规定范围内

### Step 6: 推送（按配置）

根据 `daily-brief-config.json` 中的配置，执行推送。支持以下 **9 大渠道**：

#### 国内渠道

1. **企业微信**：`scripts/send_wecom.py`
   - 先发精简摘要版（<4096字节），再发完整版 HTML 文件
   - **摘要采用3层优先级填充**：层级1（标题+今日变化+总判断）→ 层级2（板块标题+新闻标题）→ 层级3（一句话摘要，按剩余空间填充）
   - **摘要中不带任何链接**，保持纯文本阅读体验，来源仅以文字标注
   - **所有来源链接仅在 HTML 完整版中呈现**
   - 支持防重复推送锁，避免同一日期重复推送
   - 配置：群机器人 Webhook URL → `WECOM_WEBHOOK_URL`

2. **钉钉**：`scripts/send_dingtalk.py`
   - 支持 Markdown 消息 + 链接消息，支持加签安全验证
   - 配置：群机器人 Webhook → `DINGTALK_WEBHOOK_URL`，可选加签 → `DINGTALK_SECRET`
   - 限制：每分钟最多 20 条消息

3. **飞书**：`scripts/send_feishu.py`
   - 支持富文本（post）和交互卡片（含按钮）两种模式
   - 配置：群机器人 Webhook → `FEISHU_WEBHOOK_URL`，可选签名 → `FEISHU_SECRET`
   - 卡片模式：`--card --link-url <URL>`
   - 限制：每分钟 5 条，每小时 100 条

#### 国际渠道

4. **Slack**：`scripts/send_slack.py`
   - 使用 Block Kit 富消息格式，支持按钮链接
   - 配置：Incoming Webhook URL → `SLACK_WEBHOOK_URL`

5. **Discord**：`scripts/send_discord.py`
   - 使用 Embed 消息格式，支持文件上传
   - 配置：Webhook URL → `DISCORD_WEBHOOK_URL`
   - 限制：Embed 描述 4096 字符，每秒 5 次

6. **Telegram**：`scripts/send_telegram.py`
   - 通过 Bot API 推送 HTML 格式消息，支持文件上传
   - 配置：Bot Token → `TELEGRAM_BOT_TOKEN`，Chat ID → `TELEGRAM_CHAT_ID`
   - 限制：消息 4096 字符，每秒 30 条

7. **Microsoft Teams**：`scripts/send_teams.py`
   - 支持 Adaptive Card（推荐）和旧版 MessageCard 格式
   - 配置：Incoming Webhook → `TEAMS_WEBHOOK_URL`
   - 旧版兼容：`--legacy`

#### 通用渠道

8. **邮件**：`scripts/send_email.py`
   - SMTP 邮件推送，HTML 正文 + 纯文本备选
   - 配置：`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO`

9. **GitHub Pages**：`scripts/deploy_github.py`
   - 部署到 GitHub Pages 作为公开访问的网页，自动归档历史版本
   - 配置：`GITHUB_TOKEN`, `GITHUB_USER`

## 自定义指南

### 修改关注领域

编辑 `daily-brief-config.json` 中的 `customization` 字段，可自定义：
- 关注的行业领域（默认 Data+AI）
- 厂商优先级列表
- 开源项目列表
- 输出语言和格式

### 添加推送渠道

在 `daily-brief-config.json` 的 `adapters` 中启用渠道并填入配置：

| 渠道 | 配置键 | 类型 | 主要环境变量 |
|------|--------|------|-------------|
| 企业微信 | `wechatwork` | Webhook | `WECOM_WEBHOOK_URL` |
| 钉钉 | `dingtalk` | Webhook | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` |
| 飞书 | `feishu` | Webhook | `FEISHU_WEBHOOK_URL`, `FEISHU_SECRET` |
| Slack | `slack` | Webhook | `SLACK_WEBHOOK_URL` |
| Discord | `discord` | Webhook | `DISCORD_WEBHOOK_URL` |
| Telegram | `telegram` | Bot API | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Teams | `teams` | Webhook | `TEAMS_WEBHOOK_URL` |
| 邮件 | `email` | SMTP | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` |
| GitHub | `github` | API | `GITHUB_TOKEN`, `GITHUB_USER` |

### 调整定时任务

修改 `daily-brief-config.json` 中的 `cron` 配置：
```json
{
  "schedule": "0 8 * * 1-5",
  "timezone": "Asia/Shanghai"
}
```
