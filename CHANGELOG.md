# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] - 2026-04-02

### Added
- Phase 1 Chinese search: keyword search for CAICT (信通院)、CCID (赛迪)、National Data Administration (国家数据局) policy sources
- Phase 1 funding search: Crunchbase News、TechCrunch、CB Insights macro capital sources
- Phase 2 Chinese search: iResearch (艾瑞)、EqualOcean (亿欧) reports; partnership/integration search for ecosystem news
- Information sources list: + Crunchbase News、CB Insights、PitchBook News、TechCrunch Venture
- Analyst institutions: + Futurum Group、Constellation Research、Wikibon/SiliconANGLE Research
- New category "Policy & Standards Institutions" (国家数据局、工信部)
- C-Board admission: policy & standards content type
- Importance ranking rules for search expansion
- WeChat/HTML differentiated item counts (WeChat: A≤3/B≤6/C≤5/D≤4/E≤3, HTML: +2-3 each)

### Changed
- Domestic institution search: site search (caict.ac.cn etc.) downgraded to auxiliary, keyword search added as primary
- Phase 2 search scope: + partner ecosystem search

### Fixed
- Search strategy coverage gap causing 18-report analysis: D-board 44%、C-board 39%、B-board 33% empty; missed Q1 2026 global VC $297B report and Wiliot-Databricks partnership

---

## [3.0.0] - 2026-03-20

### Added
- Major restructuring: merge C+D into C (Views & Research)
- New D-board: Capital & Corporate
- Confidence levels for all news items
- Self-check for duplicates
- Review step with 3-point trend judgment (15-30 chars) with "so what"
- Verdict constraint (≤120 chars)
- Funding search strategy
- Item count control: 10-14 items (14-20 on Mondays)

### Changed
- Impact analysis format
- Output template structure

---

## [2.0.0] - 2026-03-15

### Added
- Multi-channel delivery support (Slack, Teams, email, WeChat, DingTalk, Feishu, Discord, Telegram)
- Configurable templates per channel
- Auto-formatting for HTML output

---

## [1.0.0] - 2026-03-10

### Added
- Initial release
- Core daily brief generation workflow
- Web search, filtering, writing pipeline
