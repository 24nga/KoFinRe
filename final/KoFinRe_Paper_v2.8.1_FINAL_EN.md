# KoFinRe-QA: An Automated Quality Assessment Framework for Korean SW/IT Requirements

## Korean Adaptation of the English NLP Tool Paska, Alignment with Six Requirements-Engineering Standards, Multi-Domain Dataset Construction, and Quantitative Validation

> **KoFinRe-QA: A Framework for Korean Requirements Quality Assessment**
> *An NLP-Ensemble and LLM-Correction Approach Aligned with Paska / IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS*
>
> The acronym preserves the tool's historical naming, which originated in the financial domain; in this paper, however, the framework is redefined as a quality-assessment rubric applicable to **Korean requirements in general — public, private, and multi-domain**.
>
> **Document version**: Final v2.8.1 (2026-07-06) — consistency-reviewed edition of the v2.8 integrated draft. English translation of the Korean original (`KoFinRe_Paper_v2.8.1_FINAL.md`).

---

## Abstract

While natural-language requirements quality tools and datasets such as Paska and PURE have been available for English, the Korean SW/IT requirements domain lacks all four of the following: (1) public datasets, (2) automated assessment tools, (3) a smell taxonomy specialized for Korean writing conventions, and (4) alignment with international and national requirements-engineering standards. This study proposes the **KoFinRe-QA Framework**, a domain-agnostic **quality-assessment rubric for Korean requirements** that fills these four gaps simultaneously.

The framework consists of five stages: (i) multi-format text extraction (HTML/HWP/PDF/DOCX/RTF/XLSX), (ii) a **19-smell Korean taxonomy** (6 Paska-mapped + 4 Korea-specific + 5 from ISO 29148/INCOSE/EARS + 4 from CMMI/NCS), (iii) 5-detector ensemble detection, (iv) quantitative evaluation with 6 standard reports, and (v) LLM/heuristic correction. It was validated on **five datasets spanning multiple domains**: 56 unrefined public-finance RFPs (D1), 30 structured RFP requirements (D2), 79 English PURE SRS documents as a baseline (D3), 257 anonymized requirements from a real company's four modules (D4), and **a public multi-domain RFP case collection of 14 documents (healthcare, legal, food & drug, U-City, education, DB construction, etc.) totaling 4,075 requirements (D5)**. Precision-tuning reduced automatic likely-false-positives from **26% to 3.9% (−22pp)**, and a four-way baseline comparison quantitatively confirmed that **Rule-only performs best with Macro-F1 0.278** (LLM-assisted ties with Rule-only because it ran in dry-run mode). The D5 evaluation detected **smells in 87.5%** of requirements, with the dominant patterns being **S18 Missing Traceability ID (69.7%), S2 Incomplete (26.2%), and S5 Missing Actor (16.6%)** — demonstrating that Korean SI writing conventions dominate regardless of domain. Within D5, we further found that the **form-formality effect (−82pp) is 3.7 times larger than the domain-change effect (+22pp)**. Standards-alignment coverage evolved from **~20% (v1.0) → 28% (v2.0) → 55% (v2.7) → ~70% (v2.8)**; CMMI compliance rose from **5/9 to 8/9** principles, and NCS constraint-category classification support expanded from **0/5 to 5/5**. The tool is released as open source (<https://github.com/24nga/KoFinRe>) together with a five-step ethical/legal workflow for handling real corporate data and a reproducible multi-domain sample experiment at [`experiments/rfp_2013_sample/`](https://github.com/24nga/KoFinRe/tree/main/experiments/rfp_2013_sample).

**Keywords:** Korean Requirements Engineering, Multi-domain Requirements Quality, Requirement Smell, Paska, IEEE 830, ISO 29148, INCOSE, EARS, CMMI REQM/RD, NCS Constraint Categories, NLP Ensemble, LLM Correction, Anonymization

---

## 1. Introduction

### 1.1 Background
In Korean SW/IT projects — public, private, and financial alike — the quality of requirements written at the RFP stage directly determines project outcomes. Ambiguous wording, incomplete specifications, compound obligations, unclear necessity, infeasible absolutes, missing traceability IDs, and unclassified constraints are consistently reported as root causes of post-hoc disputes across domains. This study defines **Korean requirements-writing conventions themselves**, rather than any particular domain, as the object of assessment, and validates a domain-agnostic rubric.

### 1.2 Problem Definition
Applying English-language automated assessment tools directly to Korean RFPs faces six barriers:

| # | Barrier | Impact |
|---|---|---|
| 1 | Paska's allennlp dependency — no Windows or Korean support | Tool cannot run |
| 2 | Korean SOV word order; subject omission is grammatical | English detection rules do not fit |
| 3 | Korean SI writing conventions (declarative "handa," noun compounding) | Mismatch with English smell patterns |
| 4 | Korea-specific formats: HWP, full-width bullets | No standard extraction tools |
| 5 | No public Korean requirements dataset | Research cannot be reproduced or compared |
| 6 | No alignment with the six requirements-engineering standards (IEEE 830 / ISO 29148 / INCOSE / EARS / CMMI / NCS) | Academic and industrial standards unreflected |

### 1.3 Research Questions

- **RQ1**: What criteria allow reliable extraction of requirement candidates from Korean RFPs/SRSs?
- **RQ2**: How can the Paska smell taxonomy, Korean writing conventions, and the six requirements-engineering standards be integrated into a single definition?
- **RQ3**: Does an ensemble of multiple Korean-NLP analyzers improve smell-detection performance?
- **RQ4**: Which writing-defect types occur most frequently in Korean requirements, and are they observed consistently across domains?
- **RQ5**: Can LLM-based correction reduce smells while preserving the original meaning?

### 1.4 Contributions (7)

1. **A 19-smell Korean taxonomy**: 6 Paska-mapped (S1·S3·S5·S6·S8·S9) + 4 Korea-specific (S2·S4·S7·S10) + 5 from ISO/INCOSE/EARS (S11–S15) + 4 from CMMI/NCS (S16–S19) — a domain-agnostic general rubric
2. **KoFinRe, a 5-detector ensemble tool**: Regex / Morph (kiwipiepy) / Chunk / Dictionary / LLM with rule-priority voting
3. **Alignment with six requirements-engineering standards**: IEEE 830 (8 characteristics) / ISO 29148 (9 characteristics) / INCOSE (11 defects) / EARS (5 patterns) / CMMI REQM·RD (9 principles) / NCS (5 constraint categories)
4. **Five validation datasets across domains**: public finance (D1·D2) + English baseline (D3) + anonymized real-company data (D4) + **the public multi-domain RFP case collection D5 (healthcare, legal, food & drug, U-City, education, DB construction, etc.)**
5. **Multi-domain generalization evidence**: D5 quantitatively confirms that Korean SI writing conventions dominate regardless of domain (87.5% smell rate; Top 3: S18·S2·S5), plus the **form formality > domain** finding (effect ratio 3.7×)
6. **An ethical/legal workflow**: a five-step processing standard for real corporate data
7. **Open-source release**: <https://github.com/24nga/KoFinRe> (MIT License) + web evaluator + PDF bundle + the reproducible [`experiments/rfp_2013_sample/`](https://github.com/24nga/KoFinRe/tree/main/experiments/rfp_2013_sample)

---

## 2. Related Work

### 2.1 English Requirements Datasets and Tools

- **PURE** (Ferrari 2017): 79 public SRS documents; used as the D3 baseline in this study
- **Paska** (Veizaga 2024): allennlp constituency parsing + Stanford POS tagger + Java smell detector; 9 smells with Rimay pattern recommendations

### 2.2 Requirements Quality — Six Standards

| Standard | Scope | Core content |
|---|---|---|
| **IEEE 830-1998** | Good SRS characteristics | Correct, unambiguous, complete, consistent, ranked, verifiable, modifiable, traceable (8) |
| **ISO/IEC/IEEE 29148:2018** | Extended requirement quality | 9 characteristics (Necessary, Singular, Feasible, Verifiable, Implementation-free, etc.) |
| **INCOSE Guide** | Writing defects | 11 defects (Negative, Speculative, Universal Qualifier, etc.) |
| **EARS** (Mavin 2009) | Writing patterns | 5 patterns (Ubiquitous, Event-driven, State-driven, Optional, Unwanted) |
| **CMMI** (V2.0 REQM·RD) | Requirements management & development | 9 principles (Necessary, Feasible, Traceable, etc.) |
| **NCS** (Korean National Competency Standards) | Constraint classification | 5 categories (TECH, BIZ, COMP, OPS, SEC) |

### 2.3 Korean NLP / LLM-based Software Engineering

- Korean NLP-based requirements classification (Cho 2020)
- Generative-AI-based UML transformation (Cho 2024)
- Korean controlled natural language (no prior work found)

### 2.4 Differentiation of This Study

| Dimension | Prior work | This study |
|---|---|---|
| Language | English-centric | Full Korean support |
| Domain | Single SW field or single sector | **Public + private, multi-domain** (finance, healthcare, legal, food & drug, U-City, education, DB construction, etc.) |
| Smell taxonomy | Paska's 9 (English) | **19 Korean smells + six-standard alignment** |
| Standards alignment | Weak | Quantitative mapping to IEEE / ISO / INCOSE / EARS / CMMI / NCS |
| Data | 1–2 datasets | **5 integrated datasets** (unrefined & structured public + English baseline + anonymized corporate + public multi-domain cases) |
| Real-company handling | Unestablished | Five-step ethical/legal workflow |
| Tooling | Single detector | 5-detector ensemble + heuristic/LLM correction + web evaluator + reproducible experiment folder |

---

## 3. The KoFinRe-QA Framework (Proposed Method)

### 3.1 Overview

```
RFP documents → ① Extraction → ② Smell definition (19) → ③ Ensemble detection → ④ Quantitative evaluation → ⑤ LLM/heuristic correction
```

### 3.2 Stage 1 — Text Extraction

#### 3.2.1 Multi-format input handling
| Format | Tool |
|---|---|
| HTML | BeautifulSoup (auto-detects UTF-8/CP949/EUC-KR) |
| HWP | Hancom Office COM automation (Windows) |
| PDF | pdfplumber |
| DOCX | python-docx |
| RTF | striprtf |
| XLSX | openpyxl (structured requirement specifications — direct parsing of ID/category/name/description columns) |

#### 3.2.2 Signature-based file identification
Korean public-agency websites frequently return PDF or HWP binaries under the filename `page.html`. We re-identify the true format via 8 magic-byte patterns (PDF/OLE2/HWP_ALT/ZIP/HTML/RTF/UNKNOWN).

#### 3.2.3 Sentence segmentation
- Korean/English sentence terminators (`. ! ? 。`)
- Semicolons (`;`) — sub-requirement splitting
- Form pipes (`|`) — splitting combined cells in SI specification forms (new in v2.2)
- Full-width bullets (`◇□■○●▶▪◐`) → converted to semicolons

#### 3.2.4 Precision requirement filter (6 cut categories)
| Filter | Blocked content |
|---|---|
| HARD_NOISE | COPYRIGHT, sitemaps, page navigation |
| BID_NOISE | Bidder terms, integrity pacts, procurement law boilerplate |
| META_START | Lines starting with project name / contact info |
| LEADING_NOISE | Bullet/roman-numeral fragments |
| EVAL_CRITERIA | Scoring rules ("shall be evaluated…") |
| LEGAL_DOMAIN | Tenant/deposit phrasing with no system nouns |

Outputs: `sentence_candidates.csv`, `requirement_candidates.csv`, `exclusion_reason.csv`, `extraction_log.json`.

### 3.3 Stage 2 — Smell Taxonomy (19 smells, v2.8)

#### 3.3.1 Full classification table

| Code | Name | Quality attribute | Source standard | Introduced |
|---|---|---|---|---|
| S1 | Non-atomic Requirement | Atomicity / Singular | Paska, ISO 29148, CMMI | v1.0 |
| S2 | Incomplete Requirement | Completeness | Korea-specific (SI forms) | v2.0 |
| S3 | Ambiguous Term | Unambiguity | Paska, IEEE 830, INCOSE | v1.0 |
| S4 | Weak Obligation | Verifiability | Korea-specific (declarative "handa") | v1.0 |
| S5 | Missing Actor | Completeness | Paska | v1.0 |
| S6 | Missing Quantification | Testability | Paska, ISO 29148 | v1.0 |
| S7 | Undefined Acronym | Traceability | Korea-specific (frequent English acronyms) | v2.0 |
| S8 | Coordination Ambiguity | Unambiguity | Split from Paska | v2.0 |
| S9 | Passive / Agentless Expression | Clarity | Paska | v1.0 |
| S10 | Unverifiable Requirement | Verifiability | Korea-specific + IEEE 830 | v2.0 |
| **S11** | **Implementation Bias** | **Implementation-free** | **ISO 29148, INCOSE** | v2.7 |
| **S12** | **Negative Statement** | **Positive form** | **INCOSE** | v2.7 |
| **S13** | **Speculation** | **Definiteness** | **INCOSE Speculative** | v2.7 |
| **S14** | **Missing Persona/Beneficiary** | **Stakeholder clarity** | **EARS, IEEE 830** | v2.7 |
| **S15** | **Pronoun/Reference Ambiguity** | **Reference clarity** | **INCOSE Pronoun** | v2.7 |
| **S16** | **Necessity Unclear** | **Necessary** | **CMMI REQM** | **v2.8** |
| **S17** | **Infeasible Absolute** | **Feasible** | **CMMI RD, ISO 29148** | **v2.8** |
| **S18** | **Missing Traceability ID** | **Traceable** | **CMMI REQM** | **v2.8** |
| **S19** | **Unclassified Constraint** | **Constraint classification** | **NCS 5 categories** | **v2.8** |

#### 3.3.2 Detection patterns for the four new v2.8 smells (CMMI/NCS-based)

| Code | Core pattern | Positive example | Negative example (clean) |
|---|---|---|---|
| **S16** Necessity Unclear | "선호하는" (*preferred*), "강제로" (*forcibly*), "임의로 정한" (*arbitrarily decided*), "독단적" (*unilateral*), "개발(팀\|자)이 (선호\|결정)" (*dev team prefers/decides*) | "개발팀이 **선호하는** 폰트를 **강제로** 사용" (*forcibly use the font the dev team prefers*) | "사용자 인증 강화를 위해 MFA 적용" (*apply MFA to strengthen user authentication*) |
| **S17** Infeasible Absolute | `100\s*%\s*(availability\|accuracy\|perfection\|guarantee)`, `99\.99{3,}\s*%`, "장애 0건" (*zero failures*), "응답시간 0초" (*0-second response*), "완벽한" (*perfect*) | "100% 가용성 보장" (*guarantee 100% availability*), "0초 이내," "완벽한 보안," "99.9999%" | "월 가용성 99.9% 이상" (*monthly availability ≥ 99.9%*) |
| **S18** Missing Traceability ID | Strong obligation present + no ID pattern + no source/rationale | "본 시스템은 사용자 인증 기능을 제공하여야 한다." (*The system shall provide user authentication.*) | "**FUNC-AUTH-001** 본 시스템은…" / "**보안정책에 따라** 인증 제공" (*per the security policy*) |
| **S19** Unclassified Constraint | Constraint signal ("제약\|제한\|준수\|한정\|허용\|금지") present + zero matches in the TECH/BIZ/COMP/OPS/SEC dictionaries | "본 사업은 일부 제약을 받아야 한다" (*this project is subject to certain constraints*) | "Linux 환경에서 운영" (*operate on Linux*) — TECH match |

#### 3.3.3 NCS 5-category constraint dictionaries (S19 support)

| Category | Dictionary keywords (excerpt) |
|---|---|
| **TECH** | OS, operating system, platform, framework, RHEL, Red Hat, Java, Linux, JDK, Spring, … |
| **BIZ** | budget, schedule, milestone, launch date, deadline, limit, approval chain, organization, … |
| **COMP** | personal data, PII, GDPR, Personal Information Protection Act, supervisory regulations, … (the generic verb "준수/comply" is excluded as too broad) |
| **OPS** | 24 hours, 365 days, non-stop, scheduled maintenance, operating hours, … |
| **SEC** | MFA, multi-factor authentication, encryption, AES, SHA, audit log, key management, … |

### 3.4 Stage 3 — NLP Ensemble Detection

#### 3.4.1 Five detectors

| Detector | Role | Implementation |
|---|---|---|
| **RegexDetector** | Explicit pattern matching (S1–S19) | 50+ regexes with HIGH/MED/LOW confidence |
| **MorphDetector** | Morphology, sentence-final endings, particles | kiwipiepy (Kiwi C++), Sejong POS tagset |
| **ChunkDetector** | Actor–action–object estimation | Noun-phrase/verb heuristics |
| **DictionaryDetector** | Domain dictionaries | Korean financial-institution & acronym whitelists |
| **LLMDetector** | Auxiliary judgment | Anthropic Claude API with dry-run fallback |

#### 3.4.2 Three voting schemes

- **majority**: more than half agree
- **rule-priority** (default): RegexDetector HIGH takes precedence; otherwise combine other detectors
- **confidence-weighted**: weighted average ≥ threshold

### 3.5 Stage 4 — Quantitative Evaluation (3 categories)

| Category | Metrics |
|---|---|
| **Detection** | Precision, Recall, F1, FPR, FNR, Cohen's Kappa, Macro-F1, Micro-F1 |
| **Quality** | Smell Density, Coverage, Average per Requirement, Severe Ratio, Extraction Yield, Validity Rate |
| **Correction** | Smell Reduction Rate, Quality Score Gain, Semantic Preservation, Over-correction, Atomicity/Testability Improvement |

Six reports: `extraction_report.md`, `smell_report.md`, `evaluation_report.md`, `correction_report.md`, `dataset_card.md`, `run_log.json`.

### 3.6 Stage 5 — Correction (dual mode)

#### 3.6.1 LLM correction (6 principles)
1. Preserve the original meaning
2. Never add information absent from the original
3. Atomicity (one requirement = one function)
4. Replace vague wording with verifiable wording
5. Make actor, condition, action, object, and outcome explicit
6. Record before/after differences and any added information

#### 3.6.2 Heuristic correction (when no LLM is available)
Regex-substitution based: S1 splitting / S3 `[SPECIFY: …]` markers / S4 declarative→obligative / S8 `[ENUMERATE EXPLICITLY]` / **S16 `[JUSTIFICATION NEEDED]` / S17 `[REALISTIC FIGURE NEEDED]` / S18 `[ID/SOURCE NEEDED]` / S19 `[SPECIFY CONSTRAINT CATEGORY]`** (new in v2.8).

---

## 4. Experimental Setup

### 4.1 Five Datasets (MECE, multi-domain)

| Code | Data | Domain | Size | Source | Availability |
|---|---|---|---:|---|---|
| **D1** | Unrefined public-finance RFPs | Finance | 56 projects, 4,917 sentences* | Bulletin boards of 12 public agencies | Public (metadata) |
| **D2** | Structured RFP | Finance | 30 reqs, 140 sub-reqs | Curated CSV | Public (with author consent) |
| **D3** | PURE English SRS | General SW | 79 documents, 1,200-req sample | PROMISE | Public |
| **D4** | Real company, 4 modules (FA·BG·CI·CM) | Capital finance | 257 reqs | A Korean capital-finance company | **🔒 Local only** |
| **D5** | **2013 detailed-requirements procurement RFP cases** | **Multi-domain** ⭐ | **14 documents / 4,075 reqs** | Public procurement case collection | **Public** (`experiments/rfp_2013_sample/`) |

> \* D1 sentence counts differ by pipeline version: 3,210 sentences in the v1 extraction (used for the filter pass-rate in §6.1) vs. 4,917 in the v2 re-extraction. The table shows the v2 figure.
>
> **D5 multi-domain composition** — healthcare (Seoul Medical Center, COMWEL, MFDS e-CTD), legal (Incheon Airport immigration biometrics), legislation (Ministry of Government Legislation), DB construction (National Archives, Ministry of Patriots & Veterans Affairs), U-City (Gyeongsangbuk-do), education (Daegu), cloud (KIAT), procurement (PPS website), and maintenance — **the key validation data for removing single-domain bias and demonstrating generalization.**

### 4.2 Evaluation Metrics
See §3.5 (Detection / Quality / Correction).

### 4.3 Baselines (4 methods)
| Method | Composition |
|---|---|
| Rule-only | RegexDetector alone |
| NLP-only | MorphDetector + ChunkDetector |
| LLM-assisted | Regex + LLM OR (dry-run in this experiment — may diverge from Rule with live calls) |
| Ensemble | 5 detectors + rule-priority voting |

### 4.4 Ethical/Legal Processing (D4 only)
| Step | Treatment |
|---|---|
| 1. Regex anonymization | Masking 8 identifier types: company, person, employee ID, phone, e-mail, URL, dates, external partners |
| 2. LOCAL_ONLY isolation | Outside the git repo (`real_reqs_anonymized_LOCAL_ONLY.zip`) |
| 3. Residual-risk monitoring | Counting 4+-letter acronyms and letter+digit IDs |
| 4. Leak checks | git grep 5+ rounds (6 company/acronym/code tokens — masked in this paper) — all 0 hits |
| 5. Statistics-only sharing | 0 verbatim quotes in this paper; statistics and anonymized short patterns only |

---

## 5. Results

### 5.1 Data Collection & Extraction (re: RQ1)

| Dataset | Attempted | Extracted | Yield | Notes |
|---|---:|---:|---:|---|
| D1 | 56 | 14 (25%) | 25% | Site authentication blocks |
| D2 | 30 reqs (curated CSV) | 30 (100%) | 100% | Direct CSV — no extraction stage needed |
| D3 | 79 | 76 (96%) | 96% | Standard English environment |
| D4 | 257 reqs (structured) | 257 (100%) | 100% | Direct XLSX columns |
| **D5** | **14 files (13 HWP + 1 XLSX)** | **14 (100%)** | **100%** | **Hancom COM + openpyxl; 10,899 sentence candidates → 3,409 requirement candidates + 666 structured XLSX = 4,075** |

### 5.2 Smell Detection — Five Datasets Combined (re: RQ2, RQ4)

| Smell | D3 English 1,200 | D1 unrefined 75 | D2 structured 30 | D4 real company 257 | **D5 multi-domain 4,075** |
|---|---:|---:|---:|---:|---:|
| Passive (S9) | **27.5%** | 8.0% | 10.0% | 1% | 1.6% |
| Non-atomic (S1) | 13.8% | 2.7% | 0% | **0%** | 1.8% |
| Missing quantification (S6) | 1.3% | 6.7% | 6.7% | 2% | 6.2% |
| Ambiguous term (S3) | n/a | 30.7% | 26.7% | 4% | 6.0% |
| **Missing actor (S5)** | n/a | **32.0%** | 26.7% | **81%** | **16.6%** |
| **Weak obligation (S4)** | n/a | 0% | 30.0% | 23% | 0.1% |
| Undefined acronym (S7) | n/a | 1.3% | 3.3% | 11% | 4.2% |
| **Incomplete (S2)** | n/a | n/a | n/a | **91%** | **26.2%** |
| Speculation (S13, v2.7) | n/a | n/a | n/a | n/a | **11.5%** |
| Pronoun ambiguity (S15, v2.7) | n/a | n/a | n/a | n/a | **10.6%** |
| **Missing traceability ID (S18, v2.8)** ⭐ | n/a | n/a | n/a | n/a | **69.7%** |
| Unclassified constraint (S19, v2.8) | n/a | n/a | n/a | n/a | 2.8% |
| **Overall smell rate** | 46.6% | 65.3% | 56.7% | **79.4%** (v2.3)† | **87.5%** |

> n/a = not evaluated at that point in time (pre-v2.0 or pre-v2.7). † D4 varies by tuning version: 93.4% (v2.1.1) → 77.0% (v2.2) → 79.4% (v2.3); the table shows the latest v2.3 figure.

### 5.2.1 D5 Multi-domain Validation — Key Results

**Top 5 detections (three v2.7/v2.8 additions enter the Top 5)**

| Rank | Code | Name | Count | Introduced |
|---|---|---|---:|:-:|
| 1 | **S18** | **Missing Traceability ID** | **2,842 (69.7%)** | **v2.8** |
| 2 | S2 | Incomplete | 1,068 (26.2%) | v2.0 |
| 3 | S5 | Missing Actor | 675 (16.6%) | v1.0 |
| 4 | **S13** | **Speculation** | **470 (11.5%)** | **v2.7** |
| 5 | **S15** | **Pronoun Ambiguity** | **430 (10.6%)** | **v2.7** |

**Top 3 co-occurring smell pairs** — defects are combinational, not isolated

| Combination | Count |
|---|---:|
| S2 Incomplete + S13 Speculation | 447 |
| S15 Pronoun Ambiguity + S18 Missing Traceability ID | 421 |
| S2 Incomplete + S18 Missing Traceability ID | 414 |

**Effect of form formality** — comparison inside D5

| Document type | Smell rate | Notes |
|---|---:|---|
| PPS website XLSX functional requirements (structured; IDs + separated columns) | **17.3%** | Cleanest |
| HWP flat body text | 99–100% | No ID or source traceability |

→ Quantitative confirmation that **form formality is a stronger quality factor than domain**.

### 5.2.2 Finance vs. Public Multi-domain — Direct Comparison

D1·D2·D4 (three finance datasets, 362 reqs) vs. D5 (public multi-domain, 4,075 reqs):

| Comparison axis | Value |
|---|---:|
| Volume | Finance 362 vs. public 4,075 (×11.3) |
| S5 Missing Actor — Top 3 in 4/4 datasets | 32% / 27% / 81% / 17% |
| Public-specific S18 Missing Traceability ID | **69.7%** (near 0 in finance data, which carries form IDs) |
| Share of v2.7/v2.8 additions in the D5 Top 5 | **3/5 (60%)** — S13·S15·S18 |
| Form-change effect (inside D5, HWP→XLSX) | **−82pp** |
| Domain-change effect (D1 finance → D5 public) | +22pp |
| **Form effect / domain effect ratio** | **3.7× — form matters more than domain** |

**Conclusion**: Differences in form formality (flat HWP vs. structured XLSX) affect quality more than differences in domain (finance/healthcare/legal/U-City/…). The dominant patterns of Korean SI writing conventions (actor omission, declarative endings) are consistent across domains, and adding the public domain **quantitatively validated the v2.7/v2.8 taxonomy additions** (60% of the Top 5).

Full comparison (all-19 distributions, 8-section analysis, 4 key conclusions): [`DOMAIN_COMPARISON.md`](./DOMAIN_COMPARISON.md).

### 5.3 Taxonomy Evolution — Cumulative Coverage of the Six Standards

| Version | Smells | IEEE 830 (8) | ISO 29148 (9) | INCOSE (11) | EARS (5) | CMMI (9) | NCS (5) | **Overall** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v1.0 | 7 | 3 | 3 | 2 | 0 | 3 | 0 | ~20% |
| v2.0 | 10 | 5 | 5 | 4 | 0 | 5 | 0 | ~28% |
| v2.6 | 10 | 5 | 5 | 4 | 0 | 5 | 0 | 28% |
| v2.7 | 15 | 7 | 7 | 8 | 2 | 5 | 0 | **55%** |
| **v2.8** | **19** | **8** | **8** | **8** | **2** | **8** | **5** | **~70%** |

> Newly satisfied in v2.8 — CMMI Necessary (S16) / Feasible (S17) / Traceable (S18) / all five NCS categories TECH·BIZ·COMP·OPS·SEC (S19) / ISO 29148 Necessary (S16).

### 5.4 CMMI 9-Principle Mapping (as of v2.8)

| Principle | CMMI area | v2.6 | v2.7 | **v2.8** | Mapped smells |
|---|---|:-:|:-:|:-:|---|
| Necessary | REQM | ✗ | ✗ | **✓** | **S16** |
| Singular | RD | ✓ | ✓ | ✓ | S1 |
| Unambiguous | RD | ✓ | ✓ | ✓ | S3 + S8 + S15 |
| Verifiable | RD | ✓ | ✓ | ✓ | S4 + S6 + S10 |
| Consistent | REQM | ✗ | ✗ | ✗ | (planned for v2.9 — S20) |
| Complete | RD | ✓ | ✓ | ✓ | S2 + S5 + S14 |
| Implementation-free | RD | ✗ | ✓ | ✓ | S11 |
| Traceable | REQM | ⚠ | ⚠ | **✓** | S7 + **S18** |
| Feasible | RD | ✗ | ✗ | **✓** | **S17** |
| **Satisfied** | — | **5/9** | **5/9** | **8/9** | +3 |

### 5.5 NCS 5 Constraint Categories — S19 Classification Support

| Category | Mapping | Dictionary size | Example match |
|---|---|---:|---|
| TECH | S19 + CONSTRAINT_TECH | 25+ keywords | "operate on RHEL 8" → TECH |
| BIZ | S19 + CONSTRAINT_BIZ | 12+ keywords | "deadline is June 2026" → BIZ |
| COMP | S19 + CONSTRAINT_COMP | 10+ keywords | "comply with the Personal Information Protection Act" → COMP |
| OPS | S19 + CONSTRAINT_OPS | 8+ keywords | "24×365 non-stop operation" → OPS |
| SEC | S19 + CONSTRAINT_SEC | 15+ keywords | "apply MFA and AES-256 encryption" → SEC |

### 5.6 v2.2/v2.3 Ablation (same D4 dataset)

| Metric | v2.1.1 | v2.2 (chunk fix) | v2.3 (kiwipiepy) | Cumulative Δ |
|---|---:|---:|---:|---:|
| Smell rate | 93.4% | 77.0% | 79.4% | **−14 pp** |
| **Automatic likely-FP** | **26%** | — | **3.9%** | **−22 pp** ⭐ |
| S2 Incomplete | 235 | 181 | 181 | −54 |
| S5 Missing Actor | 209 | 159 | 161 | −48 |
| S4 Weak Obligation | 58 | 58 | 113 | +55 (higher accuracy) |

### 5.7 Four-way Baseline Comparison (re: RQ3)
On the 50-item R1_sim gold set:

| Method | Macro-F1 | Micro-F1 | Detections |
|---|---:|---:|---:|
| **Rule-only** | **0.278** | **0.837** | 21/50 (42%) |
| NLP-only | 0.060 | 0.182 | 48/50 (96%) |
| LLM-assisted (dry-run)‡ | 0.278 | 0.837 | 21/50 (42%) |
| Ensemble (5 detectors) | 0.244 | 0.254 | 50/50 (100%) |

> ‡ LLM-assisted ran in dry-run mode (no API calls), hence identical to Rule-only. Live API calls may diverge; this is future work for v2.9.

### 5.8 Heuristic Correction Demo (re: RQ5, extended in v2.8)

| Original (Korean, glossed) | Detected | Corrected |
|---|---|---|
| 이력 정보를 저장한다 (*stores history data* — declarative) | S4 | 이력 정보를 저장**해야 한다** (*shall store*) |
| 시스템은 효율적으로 운영되어야 한다 (*the system shall operate efficiently*) | S3, S9, S10 | 시스템은 **[SPECIFY: measurement criterion]** 운영되어야 한다 |
| 보고서는 매월 신속히 생성되고, 관리자에게 통보된다 (*reports are promptly generated monthly and notified*) | S3, S4 | 보고서는 매월 **[SPECIFY: time criterion]** 생성되고, 관리자에게 통보**되어야 한다** |
| 개발팀이 선호하는 폰트를 강제로 사용해야 한다 (*shall forcibly use the font the dev team prefers*) | **S16** | **[JUSTIFICATION NEEDED]** 폰트를 사용해야 한다 |
| 본 시스템은 100% 가용성을 보장해야 한다 (*shall guarantee 100% availability*) | **S17** | 본 시스템은 **[REALISTIC FIGURE NEEDED: e.g., 99.9%]** 가용성을 유지해야 한다 |
| 본 시스템은 사용자 인증 기능을 제공하여야 한다 (*shall provide user authentication*) | **S18** | **[FUNC-AUTH-XXX / SOURCE NEEDED]** 본 시스템은 사용자 인증 기능을 제공하여야 한다 |
| 본 사업은 일부 제약을 받아야 한다 (*subject to certain constraints*) | **S19** | 본 사업은 **[SPECIFY CATEGORY: TECH/BIZ/COMP/OPS/SEC]** 제약을 받아야 한다 |

### 5.9 Unit Test Results
- Full suite: **60/61 passing** (the 1 remaining failure is an acronym-whitelist edge case known since v2.1)
- v2.7 new-smell tests (`tests/test_new_smells.py`): 16/16 passing
- **v2.8 CMMI/NCS tests** (`tests/test_cmmi_smells.py`): **18/18 passing**
  - TestS16NecessityUnclear × 3 (preferred font / arbitrary decision / business-justified)
  - TestS17FeasibilityConcern × 5 (100% / 0 s / "perfect" / 99.9999% / realistic 99.9%)
  - TestS18MissingTraceabilityID × 3 (no ID / FUNC-AUTH-001 / source cited)
  - TestS19ConstraintCategory × 2 (unclassifiable / TECH classified)
  - TestKoreanPatternsHelpers × 5 (TECH/BIZ/COMP/OPS/SEC classifier functions)

---

## 6. Discussion — Answers to the RQs

### 6.1 RQ1 (extraction criteria)
Seven obligation-ending forms (Korean equivalents of "shall": ~여야 한다 / 함 / 됨 / 할 수 있어야 / 반드시 / 필수 / ~토록 한다) + 6 exclusion-rule categories + automatic boilerplate detection (text repeated across 5+ projects) enable precise filtering. On the D1 v1 extraction, 3,210 → 75 sentences passed (2.3%), and 65.3% of those 75 carried true smells — a higher pass-rate precision than English Paska (46.6%). On D5, the same filter passed 10,899 HWP sentences → 3,409 (31.3%), demonstrating scalability to procurement documents with high requirement density.

### 6.2 RQ2 (smell definition — extended in v2.8)
Paska's 9 smells were extended into a **19-smell Korean taxonomy aligned with six standards**:

| Step | Added smells | Source |
|---|---|---|
| v1.0 → v2.0 | S2/S4/S7/S10 (Korea-specific) | SI forms, declarative endings, English acronyms |
| v2.7 | S11/S12/S13/S14/S15 | ISO 29148 + INCOSE + EARS |
| **v2.8** | **S16/S17/S18/S19** | **CMMI REQM·RD + NCS 5 categories** |

S16 (necessity), S17 (feasibility), and S18 (traceability) directly raise CMMI compliance from **5/9 to 8/9** principles, and S19 provides **0/5 → 5/5** NCS constraint-category classification support.

### 6.3 RQ3 (ensemble effect) ⭐
**Rule-only is best for the Korean requirements domain.** In the four-way comparison, Macro-F1 was 0.278 (Rule) vs. 0.060 (NLP) vs. 0.244 (Ensemble) — LLM-assisted ties with Rule because it ran dry-run; a live-call comparison remains future work. The clarity of formulaic Korean requirement phrasing makes heuristics efficient, while NLP and the Ensemble tend to over-detect. **The v2.8 additions S16–S19 are all rule-based precision patterns, reinforcing the Rule-only superiority hypothesis.** In the D5 multi-domain evaluation, a single RegexDetector pass evaluated all 14 documents / 4,075 requirements with no per-domain tuning.

### 6.4 RQ4 (frequent defects + multi-domain generalization + coverage)
**The dominant patterns of Korean requirements-writing conventions are domain-independent**:

| Dominant pattern | D1 finance unrefined | D2 finance structured | D4 capital real | **D5 public multi-domain** |
|---|---:|---:|---:|---:|
| Missing Actor (S5) | 32.0% | 26.7% | 81% | **16.6%** |
| Incomplete (S2) | — | — | 91% | **26.2%** |
| Weak Obligation (S4) | 0% | 30.0% | 23% | 0.1% |
| Missing Traceability ID (S18) | — | — | — | **69.7%** |

→ Clearly distinct from the Passive-voice dominance of English SRSs (D3, 27.5%); Korean SOV order, grammatical subject omission, and declarative endings are observed consistently across domains.

**Domain variance vs. form formality**: inside D5, the gap between structured XLSX (17.3%) and flat HWP (99–100%) exceeds the gap across the D1–D5 domains. → **The key quality factor is not domain but form formality and the absence of ID/source traceability.**

Standards coverage: **~20% (v1.0) → 28% (v2.6) → 55% (v2.7) → ~70% (v2.8)**. Only CMMI Consistent (S20) remains for full 9/9 CMMI compliance. All five NCS constraint categories are supported as of v2.8.

### 6.5 RQ5 (LLM correction + v2.8 heuristic extension)
The LLM adapter (`AnthropicCaller`) provides a 6-principle prompt and a dry-run fallback. To save API cost and time, heuristic correction is provided in parallel — v2.8 adds four new markers for S16–S19 (`[JUSTIFICATION NEEDED]` / `[REALISTIC FIGURE NEEDED]` / `[ID/SOURCE NEEDED]` / `[SPECIFY CONSTRAINT CATEGORY]`). Automated evaluation of semantic preservation and over-correction with live LLM calls is future work for v2.9.

### 6.6 Overall Implications
- **Tooling**: heuristics are efficient for Korean requirements; standards alignment provides academic and industrial credibility
- **Multi-domain generalization**: dominant Korean SI patterns are consistent across the five datasets (finance, capital, healthcare, legal, education, U-City, DB construction, etc.) — **usable as a general rubric, not a domain-specific one**
- **Form formality first**: within D5, structured XLSX (17.3%) vs. flat HWP (99–100%) exceeds cross-domain differences (effect ratio 3.7×) — **the top-ROI quality lever in Korean requirements engineering is form standardization**
- **Standards**: CMMI 8/9 + NCS 5/5 + ISO 29148 8/9 + INCOSE 8/11 + EARS 2/5 + IEEE 830 8/8 → overall ~70%
- **Authoring**: author education and standardization matter more than tooling (see `IMPROVEMENT_RECOMMENDATIONS.md`)
- **Data**: industry–academia collaboration on structured datasets is decisive for follow-up research
- **Ethics**: the five-step workflow for real corporate data is reusable by future Korean RE research

---

## 7. Threats to Validity

### 7.1 Internal Validity
- The R1_sim 50-item gold set used in the v2.5 baseline comparison is heuristic-derived, creating **possible bias in favor of Rule-only**. The LLM-assisted tie with Rule (dry-run) stems from the same cause.
- The v2.8 detector tests use 18 synthetic examples — P/R on real datasets is unmeasured.
- **S14 (Missing Persona) detected 0% on D5** — suspected detector-calibration issue where SYSTEM_ACTOR terms (system, server, …) are over-credited as personas. The persona dictionary and the system-actor dictionary need to be separated and re-tuned (v2.9).
- One long-standing unit-test failure remains (acronym-whitelist edge case, present since v2.1).

### 7.2 External Validity
- D1–D4 lean toward finance/capital — **D5 secures generalization across 9+ domains (healthcare, legal, education, DB construction, U-City, etc.)**, but defense, telecom, and autonomous-driving remain unvalidated.
- D4 is a single-point-in-time artifact from one Korean capital-finance company — limited industry representativeness (mitigated when combined with D5).
- D5 consists of 2013 procurement cases — a 13-year gap may under-represent recent changes in writing conventions.
- The NCS 5-category dictionaries use generic SI vocabulary — per-domain refinement (e.g., healthcare) is needed.

### 7.3 Construct Validity
- The 19 smells cannot be claimed to fully cover Korean RFP quality — CMMI Consistent (S20) and three remaining EARS patterns are not yet implemented.
- S18 traceability is limited to five ID-pattern families — proprietary in-house formats may be missed. Given that "no IDs in HWP narrative text" is itself conventional, the 69.7% figure may warrant severity adjustment (form-type-conditional weighting is future work).
- Smell rates across D1 (unrefined) and D4·D5 (structured/procurement) use different denominators (filter-passed requirement candidates), so absolute cross-dataset comparisons require caution.
- Metrics such as "semantic preservation" partly rely on rater subjectivity.

### 7.4 Conclusion Validity
- No 200-item human-rater gold set yet — true Precision/Recall/F1 remains future work.
- R1_sim sample size of 50 — statistical significance needs reinforcement.
- The "~70%" coverage figure is this study's own mapping — no external audit.

---

## 8. Conclusion and Future Work

### 8.1 Conclusion
This study proposed the **domain-agnostic Korean requirements quality-assessment rubric KoFinRe-QA Framework** to close the four gaps (dataset, tooling, taxonomy, standards alignment) in automated Korean SW/IT requirements assessment, and validated it on **five datasets against six standards**. Key results:

1. A **19-smell Korean taxonomy** (6 Paska-mapped + 4 Korea-specific + 5 ISO/INCOSE/EARS + 4 CMMI/NCS)
2. The **5-detector ensemble tool KoFinRe** (open source + web evaluator + PDF bundle + reproducible experiment folder)
3. **D4 real-company anonymized validation** — tuning reduced automatic likely-FPs from 26% to 3.9%
4. **D5 public multi-domain validation** — 14 documents / 4,075 requirements, 87.5% smell rate, Top 3: S18·S2·S5 (Korean SI conventions dominate regardless of domain)
5. **The form formality > domain finding** — form effect (−82pp) is 3.7× the domain effect (+22pp)
6. **Six-standard alignment** — ~20% (v1.0) → ~70% (v2.8); CMMI 5/9 → 8/9; NCS 0/5 → 5/5
7. **RQ3 answer**: Rule-only is best for Korean (Macro-F1 0.278) — reinforced by the v2.8 rule-based additions
8. **RQ4 answer**: Korean requirements quality issues stem not from refinement level or domain but from **linguistic-cultural writing conventions plus form formality**
9. A **five-step ethical/legal workflow** standard, plus the **reproducible experiment folder** (`experiments/rfp_2013_sample/`) as a comparison baseline for future research

### 8.2 Future Work
| Direction | Task | Target |
|---|---|---|
| Human-rater dataset | 200 human-labeled items + Cohen's kappa + true P/R/F1 | v3.0 |
| LLM correction validation | Live Stage-5 calls with ANTHROPIC_API_KEY + quantitative semantic-preservation evaluation + re-run LLM-assisted baseline | v2.9 |
| Consistency smell (S20) | Embedding-based cross-requirement conflict detection → full CMMI 9/9 | v2.9 |
| S14 detector calibration | Separate persona dictionary from system-actor dictionary (D5 0% issue) | v2.9 |
| EARS advisor (S21) | Recommend Ubiquitous/Event/State/Optional/Unwanted patterns | v3.0 |
| Form-formality index | Define form_formality_score (weighted S18·S15·S5) — form-conditional smell severity | v3.0 |
| Domain expansion | Remaining domains (defense, telecom, manufacturing, autonomous driving) + temporal comparison with 2020s-era public RFPs | v3.1 |
| Korean Rimay | Korean-equivalent controlled-natural-language patterns | v3.1 |
| Dataset scale | 1,000+ structured items via industry–academia collaboration | v3.2 |

---

## References

[1] A. Ferrari, G. O. Spagnolo, and S. Gnesi, "PURE: A Dataset of Public Requirements Documents," *IEEE International Requirements Engineering Conference*, 2017.

[2] A. Veizaga, S. Y. Shin, and L. C. Briand, "Automated Smell Detection and Recommendation in Natural Language Requirements," *IEEE Transactions on Software Engineering*, 2024.

[3] A. Veizaga, M. Alferez, D. Torre, M. Sabetzadeh, and L. C. Briand, "On Systematically Building a Controlled Natural Language for Functional Requirements," *Empirical Software Engineering*, 2021.

[4] IEEE, "IEEE Recommended Practice for Software Requirements Specifications," *IEEE Std 830-1998*.

[5] ISO/IEC/IEEE, "Systems and Software Engineering — Life Cycle Processes — Requirements Engineering," *ISO/IEC/IEEE 29148:2018*.

[6] INCOSE, "Guide to Writing Requirements," International Council on Systems Engineering, v4.

[7] A. Mavin, P. Wilkinson, A. Harwood, and M. Novak, "Easy Approach to Requirements Syntax (EARS)," *IEEE 17th International Requirements Engineering Conference*, 2009.

[8] CMMI Institute, "CMMI for Development V2.0 — Requirements Management (REQM) and Requirements Development (RD) Practice Areas," ISACA, 2018.

[9] Human Resources Development Service of Korea, "NCS (National Competency Standards) — Information Technology Requirements Analysis," 2024.

[10] B. S. Cho and S. W. Lee, "A Comparative Study on Requirements Analysis Techniques using Natural Language Processing and Machine Learning," *Journal of The Korea Society of Computer and Information*, 2020.

[11] E. S. Cho, "A Technique for UML-based System Development Using Generative AI," *Journal of The Korea Society of Computer and Information*, 2024.

[12] Y. H. Kim, "A Generative AI-Based Personalized Programming Education System Integrating Adaptive Rubric Assessment," *Journal of The Korea Society of Computer and Information*, 2025.

[13] M. S. Lee, "A Comparative Study on the Performance of GPT-4o-mini, Claude 4 Sonnet, and Gemini 2.5 Flash Models by Prompt Type Based on Prompt Runner," *Journal of The Korea Society of Computer and Information*, 2026.

[14] V. Ivanov, M. Sadovykh, and A. Naumchev, "Extracting Software Requirements from Unstructured Documents," *arXiv preprint*, 2022.

[15] F. Khayashi, B. Jamasb, R. Akbari, and P. Shamsinejadbabaki, "Deep Learning Methods for Software Requirement Classification: A Performance Study on the PURE Dataset," *arXiv preprint*, 2022.

---

## Appendix

### A. Artifact Directory Standard (v2.8.1)

```
KoFinRe/
├── kofinre/                # Core package
│   ├── detectors/          # 5 detectors (all of S1–S19)
│   ├── extraction/         # Stage 1 (HWP/PDF/DOCX/RTF/HTML/XLSX)
│   ├── io/                 # CSV/Excel
│   ├── llm_adapters/       # Anthropic
│   ├── correction.py       # LLM correction
│   ├── correction_heuristic.py  # Heuristic correction (incl. S16–S19 markers)
│   ├── korean_patterns.py  # Korean patterns + CMMI/NCS dictionaries (v2.8)
│   ├── smell_taxonomy.yaml # Formal 19-smell definitions (source_standard, introduced_in)
│   ├── ensemble.py
│   ├── metrics.py
│   ├── reporting.py
│   └── validation.py
├── docs/                   # Living documents (v2.8)
│   ├── PAPER_FINAL.md             # This paper (v2.8.1, Korean)
│   ├── CMMI_NCS_COMPARISON.md     # CMMI/NCS analysis
│   ├── DOMAIN_COMPARISON.md       # Finance vs. public multi-domain comparison
│   ├── JOURNEY.md                 # Full journey (13 steps)
│   └── UPDATE.MD                  # Changelog
├── old/                    # Historical snapshots by era
│   ├── PAPER_DRAFT.md             # v2.1-era draft (10 smells)
│   ├── FRAMEWORK_GAP_ANALYSIS.md  # v2.0-era gap analysis
│   └── STANDARDS_COMPARISON.md    # v2.7-era IEEE/ISO/INCOSE/EARS gaps
├── experiments/            # Reproducible sample experiments
│   └── rfp_2013_sample/           # D5: stage1 extraction + stage3 evaluation artifacts
├── final/                  # Frozen submission package (v2.8.1, KO + EN)
├── scripts/                # CLI + PDF bundler + D5 pipeline
│   ├── run_extraction.py / run_detection.py
│   ├── extract_rfp2013_xlsx.py / evaluate_rfp2013.py
│   └── build_pdf_bundle.py
├── examples/               # Usage examples
├── tests/                  # Unit tests (60/61)
│   ├── test_detectors.py
│   ├── test_new_smells.py         # S11–S15 (16 tests)
│   ├── test_cmmi_smells.py        # S16–S19 (18 tests)
│   └── test_metrics.py
├── web/index.html          # Browser evaluator (SheetJS, synced to 19 smells)
└── legacy/                 # v1 archive
```

### B. Security Processing Verification
- 6-identifier leak checks passed 6+ times (six company/system tokens — masked in this paper)
- Backup ZIPs isolated 3 times (LOCAL_ONLY marked)
- Zero git commits of D4 raw or anonymized data
- Pre-push leak re-check for v2.8: six company/acronym/code tokens (masked here) — **0 hits**
- D5 is a public procurement case collection, so anonymization is unnecessary — however, original HWP/XLSX binaries are excluded from the repository (extracted CSVs and statistics only)

### C. Reproducibility
- Repository: <https://github.com/24nga/KoFinRe>
- Dependencies: `pip install -r requirements.txt` (includes kiwipiepy; HWP extraction requires Windows + Hancom Office + pywin32)
- Verification: `python -m unittest discover tests` + `python examples/basic_usage.py`
- **D5 reproduction**: the four-step recipe in [`experiments/rfp_2013_sample/README.md`](https://github.com/24nga/KoFinRe/tree/main/experiments/rfp_2013_sample) (CP949 ZIP extraction → HWP extraction → XLSX extraction → v2.8 evaluation)
- Companion documents:
  - [`JOURNEY.md`](../docs/JOURNEY.md) — full journey (v1.0 → v2.8)
  - [`UPDATE.MD`](../docs/UPDATE.MD) — changelog
  - [`CMMI_NCS_COMPARISON.md`](./CMMI_NCS_COMPARISON.md) — 11-section v2.8 standards mapping
  - [`DOMAIN_COMPARISON.md`](./DOMAIN_COMPARISON.md) — 9-section finance vs. public comparison
  - [`../old/STANDARDS_COMPARISON.md`](../old/STANDARDS_COMPARISON.md) — v2.7-era IEEE/ISO/INCOSE/EARS gaps (historical)
- Web evaluator: open `web/index.html` in a browser — upload, evaluate, and download XLSX with no server

### D. MECE Verification
Verification that the paper's structure has no overlaps and no gaps:

| Section | Role | Overlap |
|---|---|---|
| §1 Introduction | Problem, RQs, contributions | ✓ independent |
| §2 Related Work | Prior work, six standards, differentiation | ✓ independent |
| §3 Framework | 5-stage proposal + 19-smell taxonomy | ✓ independent |
| §4 Setup | 5 datasets, metrics, baselines, ethics | ✓ independent |
| §5 Results | Quantitative results + D5 multi-domain + domain comparison + coverage | ✓ independent |
| §6 Discussion | Answers to 5 RQs + implications | ✓ independent |
| §7 Validity | 4 threat classes (incl. honest detector-calibration reporting) | ✓ independent |
| §8 Conclusion | 9 results, 9 future directions | ✓ independent |
| References | 15 citations | — |
| Appendix | 5 supplements | — |

Full coverage with no omissions. The v2.8 taxonomy additions, six-standard alignment, and D5 multi-domain validation are consistently integrated across §2.2 / §3.3 / §4.1 / §5.2–5.5 / §6.2–6.4 / §7.2 / §8.1.

### E. Key v2.8 Code Excerpts

```python
# kofinre/korean_patterns.py (new in v2.8)
NECESSITY_RED_FLAGS = re.compile(
    r'(?:선호하는|선호도|마음에\s*드는|강제로\s*(?:사용|적용)'      # preferred / forcibly use
    r'|임의로\s*(?:정한|정의)|독단적|개발(?:팀|자)이\s*(?:선호|결정|정한))'  # arbitrarily decided / dev-team preference
)
INFEASIBLE_ABSOLUTE = re.compile(
    r'(?:100\s*%\s*(?:가용|정확|성공|완벽|보장|만족|동작|처리|적용)'   # 100% availability/accuracy/...
    r'|99\.99{3,}\s*%|장애\s*(?:발생\s*)?0(?:건|회)?|응답시간\s*0\s*초|완벽한)'  # zero failures / 0-second / perfect
)
REQ_ID_PATTERN = re.compile(
    r'\b[A-Z]{2,5}[\-_][A-Z]{2,5}[\-_]\d{3,5}\b'      # FUNC-AUTH-001
    r'|\b(?:REQ|FR|NFR|FUNC|SR|UR|BR|CR)[\-_]\d{3,5}\b'
)
CONSTRAINT_TECH = {'OS', '운영체제', '플랫폼', '프레임워크', 'RHEL', 'Red Hat', ...}
CONSTRAINT_BIZ  = {'예산', '일정', '마일스톤', '오픈일', '마감', '한도', ...}
CONSTRAINT_COMP = {'개인정보', 'PII', 'GDPR', '개인정보보호법', '감독규정', ...}
CONSTRAINT_OPS  = {'24시간', '365일', '무중단', '정기점검', ...}
CONSTRAINT_SEC  = {'MFA', '다중인증', '암호화', 'AES', '감사로그', ...}
```

```python
# kofinre/detectors/regex_detector.py (new S16–S19 in v2.8)
# S16 Necessity-unclear
nec_red, nec_term = kp.has_necessity_red_flag(s)
res.set("S16", nec_red, Confidence.HIGH if nec_red else 0.0, nec_term)

# S17 Feasibility
infeasible, inf_term = kp.has_infeasible_absolute(s)
res.set("S17", infeasible, ...)

# S18 Missing-traceability-ID
has_id = bool(kp.find_req_id(s))
has_source = kp.has_source_rationale(s)
has_obligation = kp.STRONG_OBLIGATION.search(s) is not None
missing_trace = has_obligation and not has_id and not has_source
res.set("S18", missing_trace, ...)

# S19 Constraint-category
cats = kp.classify_constraint_category(s)
has_constraint_signal = bool(re.search(r'(제약|제한|준수|한정|허용|금지)', s))
constraint_unclear = (has_constraint_signal and len(cats) == 0)
res.set("S19", constraint_unclear, ...)
```
