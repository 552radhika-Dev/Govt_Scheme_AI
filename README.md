# Haqdarshak Scheme Knowledge Base: Citizen FAQ Generator & AI Safety Guardrail
**AI/ML Engineer Case Study Assignment · Scenario A3**

[![Tests](https://img.shields.io/badge/Unit%20Tests-12%20Passed-emerald.svg)](https://github.com/552radhika-Dev/Govt_Scheme_AI)
[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Proprietary%20%2F%20Haqdarshak%20Evaluation-orange.svg)](#)

---

## 📌 Executive Summary

At Haqdarshak, millions of Indian citizens rely on community agents (*Haqdarshaks*) to identify and access welfare entitlements across 5,000+ central and state schemes. In civic welfare, **a confident wrong answer is catastrophic**: telling an ineligible family they qualify causes wasted travel, lost wages, and disillusionment; incorrectly telling an eligible family they are disqualified denies them critical livelihood support.

This repository implements **Scenario A3: Citizen FAQ Generator**, strictly adhering to Haqdarshak's two core operational principles:
1. **Human-in-the-Loop Principle:** Whatever AI produces is a draft; all live answers are grounded solely in verified, approved scheme records.
2. **Strict Provenance & Zero-Guess Principle:** Every factual claim points directly back to its source field and official evidence excerpt. If the record lacks information, the system **honestly states its absence rather than guessing**.

---

## 🚀 Live Interactive Demo & Web Interface

The project includes a full-featured, responsive web workbench and citizen chat interface:
- **URL:** [http://127.0.0.1:8080](http://127.0.0.1:8080) (or `http://localhost:8080`)
- **Scheme Explorer:** Browse approved scheme records rendered in the exact **6-part field format** (`scheme_ref`, `field`, `value`, `evidence`, `confidence`, `status`, `note`).
- **Interactive Bilingual Chat:** Real-time conversational interface answering in English and Hindi (हिन्दी).
- **Low-Literacy Toggle:** 1-click toggle to switch between *Standard Mode* and *Low-Literacy Mode* (icon-based, bottom-line simplified answers for rural citizens).
- **AI Safety & Hallucination Inspector (Requirement 4):** Live visual display showing the entailment score, referenced fields, and instant interception of simulated hallucination attacks.
- **Walkthrough Modal:** One-click in-app reference for all 4 presentation questions.

---

## 🛠️ Quickstart & How to Run

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git

### Installation & Launch
```bash
# 1. Clone repository
git clone https://github.com/552radhika-Dev/Govt_Scheme_AI.git
cd Govt_Scheme_AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run unit test suite (12 tests verifying grounding, verification, & fallback)
python -m pytest tests/ -v

# 4. Launch the application
python run.py
```
Open your browser and navigate to **[http://127.0.0.1:8080](http://127.0.0.1:8080)**.

---

## 📂 Architecture & Data Models

### 1. The 6-Part Scheme Field Specification
Every scheme record strictly implements the field schema defined in the Case Study brief:
```json
{
  "scheme_ref": "SCHEME-CENTRAL-PMK-001",
  "field": "benefit_amount",
  "value": "₹6,000 per financial year",
  "evidence": "Section 3 'Benefit Structure': 'Under the Scheme, an amount of Rs. 6,000/- per year is transferred to farmer families...', p. 4, Doc-Ref: AGRI-GOI-PMK-2023, captured 2024-09-10",
  "confidence": "high",
  "status": "found",
  "note": null
}
```

When a field is missing from official guidelines (e.g., `income_ceiling` for PM-KISAN, or `caste_requirement` for Ladki Bahin), it is explicitly recorded as:
```json
{
  "scheme_ref": "SCHEME-CENTRAL-PMK-001",
  "field": "income_ceiling",
  "value": "",
  "evidence": "Absence verification: Review of Operational Guidelines Section 4 (pp. 5-7), Doc-Ref: AGRI-GOI-PMK-2023, captured 2024-09-10",
  "confidence": "high",
  "status": "not found",
  "note": "The scheme does not impose an annual income ceiling; disqualification is strictly role/tax-payer based."
}
```

### 2. Implemented Welfare Schemes
1. **Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)**
   - *Scope:* Central Sector Scheme (Agriculture & Farmers Welfare)
   - *Key Rules:* Direct DBT of ₹6,000/yr (3 installments of ₹2,000); requires land ownership title; excludes institutional landholders, income tax payers, government employees, and pensioners with pension ≥ ₹10,000.
2. **Mukhyamantri Majhi Ladki Bahin Yojana**
   - *Scope:* State Government of Maharashtra (Women & Child Development)
   - *Key Rules:* Monthly DBT of ₹1,500 for resident women aged 21–65; annual family income ≤ ₹2.5 Lakh; yellow/orange ration card flexibility; 4-wheeler vehicle exclusion with explicit exemption for agricultural tractors.

---

## 🛡️ Requirement 4: Automated Hallucination & Faithfulness Verifier

The verifier (`src/verifier.py`) acts as an automated safety guardrail that inspects candidate answers before they reach community agents or citizens:

1. **Attribution Check:** Answers must cite verified fields from the approved scheme record.
2. **Affirmative-on-Absent Interception:** If a field is marked `not found`, any affirmative claim (e.g. inventing an income cap of ₹3.5L) is immediately blocked with verdict `UNSUPPORTED_HALLUCINATION`.
3. **Numerical & Entity Consistency:** Extracts currency amounts, age bounds, and frequencies. Conflicting numbers (e.g., ₹25,000 instead of ₹6,000) are flagged and rejected.
4. **Semantic Entailment:** Validates semantic keyword anchors against the record's source evidence.
5. **Honest Fallback Validation:** If an answer admits that the record does not contain the answer, the verifier assigns a 1.0 score under verdict `RECORD_LACKS_INFO_HONEST_FALLBACK`.

### Hallucination Attack Simulation
You can trigger test attacks directly in the UI:
- **Fake Amount Attack:** Injects a claim that the government provides a bonus of ₹25,000 and a solar pump $\to$ **Intercepted and blocked**.
- **Not Found Field Attack:** Asserts a positive income limit for PM-KISAN $\to$ **Intercepted and blocked**.

---

## 🎙️ 10-Minute Walkthrough: Presentation Notes & Q&A

### 1. One decision you made, and the option you decided against
- **Decision Made:** **Strict Extractive & NLI-Grounded Verification with Deterministic Fallbacks.** We restricted FAQ answers strictly to verified fields in the approved scheme record, with an explicit refusal when information is absent.
- **Option Decided Against:** **Open-Ended Generative LLM RAG.** We rejected allowing an LLM to "fill in the gaps" using its parametric memory. While open generation feels smoother conversational, it routinely hallucinates plausible-sounding eligibility criteria (e.g., guessing an age limit of 18 when the rule says 21, or inventing income thresholds). In welfare entitlements, false positives cause severe hardship.

### 2. Where your work falls short, and how someone would notice
- **Where it falls short:**
  1. *Sub-circular & Gazette Amendments:* Our scheme records are modeled as structured canonical fields. In reality, state departments release frequent amendments via government resolutions (GRs) and WhatsApp circulars that may temporarily override base rules (e.g., extending a deadline by 15 days).
  2. *Dialectal Nuance:* The Hindi answers use standard Khari Boli Hindi. While grammatically sound, they may sound formal to rural citizens accustomed to regional dialects (e.g., Ahirani, Varhadi, or Bhojpuri).
- **How someone would notice:** A rural Haqdarshak field agent in a village would notice if a citizen asks in local colloquial dialect and receives formal textbook Hindi, or if a citizen brings a local taluka-level circular with an extension that has not yet been merged into the central knowledge base.

### 3. The main assumptions you made, and why
- **Assumption 1: Scheme Record as Ground Truth.** We assume that if a piece of information is missing from the approved record, it must be treated as unknown—even if external general knowledge suggests an answer. This enforces Haqdarshak's Principle 2.
- **Assumption 2: Dual User Persona.** We assume two end users: the *last-mile citizen* (needs low-cognitive-load, bottom-line answers) and the *Haqdarshak agent* (needs the official clause and legal citation to defend the application).
- **Assumption 3: Offline Operability.** We designed the engine to run deterministic verification locally without mandatory third-party external API keys, ensuring reliable deployment in bandwidth-constrained rural environments.

### 4. Also Explain: How you checked the quality of the Hindi answers, especially if you are not fluent
We implemented a **4-pillar programmatic evaluation pipeline** (`src/hindi_checker.py`):
1. **Civic Welfare Terminology Alignment:** Maintained a bilingual domain dictionary of 20+ core civic terms (e.g., DBT $\to$ प्रत्यक्ष लाभ अंतरण / सीधे बैंक खाते में, Domicile $\to$ अधिवास प्रमाणपत्र, Beneficiary $\to$ लाभार्थी). The test suite automatically fails any Hindi translation that drops or mistranslates these terms.
2. **Script Integrity & Leakage Check:** Automated regex auditing verifying that Devanagari Unicode coverage exceeds 85% and that untranslated English jargon (outside standard abbreviations like CSC or DBT) does not leak into the response.
3. **Readability & Cognitive Load Heuristic:** Programmatically measured average sentence length (target $\le$ 18 words) and Devanagari danda punctuation spacing to prevent dense, Sanskritized bureaucratic phrasing.
4. **Back-Translation Semantic Consistency:** Ran English $\to$ Hindi $\to$ English roundtrip checks to verify that core eligibility assertions retained identical semantic meaning without drift.
5. **Human-in-the-Loop Field Agent Review:** Designed a staged sampling workflow where bilingual community agents review 5% of drafts before promotion to production.

### 5. A Question About How You Work: An answer is accurate but hard to follow for someone with low literacy. How do you balance accuracy and clarity?
We solve this using our **3-Tier Progressive Disclosure Framework**:
- **Tier 1 — The Bottom Line (Instant Visual Clarity):** A single sentence starting with an unmistakable visual indicator:
  - `✅ हाँ, आप पात्र हैं` (Yes, you are eligible)
  - `❌ नहीं, आप पात्र नहीं हैं` (No, you are not eligible)
  - `💰 ₹1,500 हर महीने सीधे बैंक खाते में` (₹1,500 every month in your bank)
- **Tier 2 — Actionable 3-Point Bullets:** Replace legal jargon with everyday language (e.g., instead of *"सक्षम प्राधिकारी द्वारा निर्गत अधिवास प्रमाण पत्र"*, say *"15 साल पुराना राशन कार्ड या स्कूल की टीसी"*).
- **Tier 3 — Collapsible Official Evidence Drawer:** Retain the exact legal clause, Government Resolution number, and source quote in a collapsible drawer. The citizen gets simple clarity, while the Haqdarshak field agent has the exact legal citation to advocate on their behalf.

---

## 💰 AI Model Selection & Cost-per-Scheme Analysis

If powered by an external LLM for initial draft generation and verification:
- **Recommended Model:** **Gemini 1.5 Flash** or **GPT-4o-mini** (with structured JSON output mode).
- **Token Budget per Scheme:**
  - Input (Scheme circular text + formatting instructions): ~3,500 tokens
  - Output (10 Bilingual FAQs + Citations + Fallbacks): ~1,800 tokens
- **Estimated Cost per Scheme:**
  - Gemini 1.5 Flash: **~₹0.28 to ₹0.35 INR ($0.0035 USD)** per scheme record.
- **Scaling to 5,000 Schemes:**
  - Total initial catalog generation: **~₹1,500 to ₹1,800 INR (~$18–$22 USD)**.
  - Ongoing monthly updates (assuming 5% of schemes update each month): **~₹90 INR (~$1.10 USD) per month**.

---

## 🧪 Test Suite & Verification Results

All 12 automated tests run in `< 0.5s`:
```
tests/test_faq_engine.py::test_faq_count_per_scheme PASSED
tests/test_faq_engine.py::test_query_pm_kisan_english PASSED
tests/test_faq_engine.py::test_query_pm_kisan_hindi PASSED
tests/test_faq_engine.py::test_query_low_literacy_mode PASSED
tests/test_faq_engine.py::test_strict_fallback_on_unsupported_query PASSED
tests/test_knowledge_base.py::test_schemes_loaded PASSED
tests/test_knowledge_base.py::test_pm_kisan_field_schema_compliance PASSED
tests/test_knowledge_base.py::test_ladki_bahin_field_schema_compliance PASSED
tests/test_verifier.py::test_verifier_passes_grounded_answer PASSED
tests/test_verifier.py::test_verifier_validates_honest_fallback PASSED
tests/test_verifier.py::test_verifier_catches_fake_number_hallucination PASSED
tests/test_verifier.py::test_verifier_catches_affirmative_claim_on_not_found_field PASSED
============================= 12 passed in 0.33s =============================
```

---

## 👥 Authorship & Submission Details
- **Candidate:** AI/ML Engineer Applicant
- **Organization:** Haqdarshak Empowerment Solutions
- **Repository:** [https://github.com/552radhika-Dev/Govt_Scheme_AI](https://github.com/552radhika-Dev/Govt_Scheme_AI)
