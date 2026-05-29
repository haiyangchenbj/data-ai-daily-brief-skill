# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.3.3] - 2026-05-29

### Added
- **Step 4.5: Mandatory Format Pre-flight** — generate-then-assert workflow that forces the LLM to output three statistics (N1=item count, N2=WeChat summary count, N3=section count) plus all assertions (N1>0, N1==N2, N3==5, English section titles, no bold/numbers in 3-points, verdict ≤120 chars). Any ❌ → return to Step 3 for regeneration; patching in review stage is forbidden.
- **Appendix A: MD Format Contract** — single-source format specification (A.1 title & opening / A.2 section titles / A.3 item structure / A.4 WeChat summary uniqueness / A.5 self-check formula) referenced by Step 3, Step 4.5, and Step 5. Eliminates rule duplication across multiple chapters.
- **Appendix B: Failure Handling** — complete failure path coverage (B.1 generation crash → regenerate / B.2 candidate insufficient → expand search or downgrade / B.3 automation vs manual gating differences).
- **Section 0: Rule Maintenance Protocol** — "locate → optimize → record" anti-patch-piling discipline. Mandatory before any future PROMPT change: locate existing rules first, prefer optimizing original clauses over adding new ones, and synchronize changelog + MEMORY records.
- **N1>0 assertion** — explicit guard against the "N1=0 ∧ N2=0 → N1==N2 ✅ false-pass" loophole; forensic-tested on the 2026-05-29 crash MD that triggered the refactor.

### Changed
- **3-layer architecture** — flat structure → 1. Editorial Principles (norms) / 2. Section Definitions (content) / 3. Workflow (process) + 2 appendices. Rules no longer scatter across multiple chapters.
- **Unified 6-dimension mapping** — three inconsistent versions (5/6/7 dimensions across v4.2 lines 53/196/339) consolidated into one definition: cost / performance / architecture / governance / engineering efficiency / procurement & market landscape.
- **Step 5 Review reduced from format+business mixed checks to 7 business-only items** — format completeness fully delegated to Step 4.5 machine pre-check; Step 5 focuses on timeliness / dedup / section admission / source quality / content quality / search coverage / restraint.
- **Section 9 hard constraints absorbed into Appendix A** — original 9 hard constraints split by dimension and merged into Appendix A.1-A.5; cross-chapter duplication with Step 5 fully eliminated.

### Fixed
- **Failed CN policy site searches replaced with keyword search** — `site:caict.ac.cn OR site:ccidreport.com OR site:cesi.cn` (which v4.2 itself annotated as "indexing is poor, cannot be used as the only means") replaced with direct keyword search.
- **Cross-month date arithmetic flaw** — the `today - 3 days` formula for "last Friday" calculation (which fails on month boundaries) replaced with mandatory calendar/`date` command lookup.
- **3-points reverse-example self-contradiction** — the v4.2 negative example accidentally used the bold formatting it was trying to forbid; reworded.
- **Generation-stage drift loophole** — review-stage repair was previously implicitly trusted to fix generation crashes (e.g. 2026-05-29 fully missing item numbers + WeChat summaries); now explicitly forbidden in Appendix B.1 and Hard Rule #5/#8.

### Preserved (zero-deletion guarantee)
- All v4.2 712-line rules, search queries, vendor lists, open-source project lists, analyst lists, source requirements, section definitions/admission criteria/templates/item-count limits, boundary case table, positive/negative example tables, historical lessons (2026-03-23 timeliness lesson, 2026-05-29 format crash lesson) are preserved verbatim — only relocated and deduplicated. Daily brief item selection, section assignment, count distribution, and text templates remain consistent with v4.2.

### Forensic Validation
v4.3 Step 4.5 was tested against the 2026-05-29 crash MD (which v4.2 review failed to catch) and identified all 7 violations with 100% coverage: zero numbered items, all WeChat summaries missing, 3-points containing bold formatting + USD amounts + GA/round labels, verdict 143 chars (>120), and `## 🔥 ...` forbidden title variant.

---

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
