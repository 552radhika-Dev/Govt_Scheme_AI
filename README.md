# Haqdarshak Scheme AI: Citizen Welfare FAQ Generator
**AI/ML Engineer Case Study Assignment · Scenario A3**

[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-12%20Passed-emerald.svg)](https://github.com/552radhika-Dev/Govt_Scheme_AI)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Haqdarshak%20Evaluation-orange.svg)](#)

---

## ⚡ How to Run the Project (Quick Start)

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Steps to Run Locally

```bash
# Step 1: Clone the repository
git clone https://github.com/552radhika-Dev/Govt_Scheme_AI.git
cd Govt_Scheme_AI

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run automated test suite (Verifies 12 tests)
python -m pytest tests/ -v

# Step 4: Start the web application
python run.py
```

### 3. Open in Browser
Once running, open your browser and navigate to:
👉 **[http://127.0.0.1:8080](http://127.0.0.1:8080)** (or `http://localhost:8080`)

---

## 🔗 Quick Links
- **GitHub Repository:** [https://github.com/552radhika-Dev/Govt_Scheme_AI](https://github.com/552radhika-Dev/Govt_Scheme_AI)
- **Live Local App:** [http://127.0.0.1:8080](http://127.0.0.1:8080)
- **Offline Submission Zip:** `Govt_Scheme_AI_submission.zip` (available in root directory)

---

## 💡 Simple Explanations: Core Principles & Assumptions

### 1. What Problem Are We Solving?
Rural citizens and community agents (*Haqdarshaks*) repeatedly ask questions about 5,000+ government welfare schemes. 
In government welfare, **a confident wrong answer is dangerous**:
- Telling an ineligible person they qualify leads to wasted travel, application fees, and disillusionment.
- Telling an eligible person they are disqualified deprives a poor family of critical money or rations.

We built an AI FAQ Assistant that strictly answers **only from the approved scheme record**, cites the exact document source, and **honestly says "I do not know" when a rule is not in the record**.

---

### 2. Main Assumptions Made (And Why)

1. **The Scheme Record is 100% Ground Truth:**
   - *Assumption:* If a detail (like an income ceiling or age limit) is not written in the official scheme record, the AI treats it as **unknown**.
   - *Why:* The AI must never guess or use generic internet knowledge for official government rules.
2. **Two User Personas (Citizen vs Community Agent):**
   - *The Citizen:* Needs an instant bottom-line answer in simple words (`✅ Yes, you qualify`).
   - *The Community Agent:* Needs the exact government clause and page number to defend the citizen's application at the block/tehsil office.
3. **Offline & Self-Contained First:**
   - *Assumption:* Field workers frequently face bandwidth limits or lack paid API credits.
   - *Why:* The system runs deterministic verification and semantic matching locally without requiring external paid API keys.

---

### 3. What We Deliberately Left Out (And Why)

1. **Open-Ended Generative "Guessing":**
   - *Left out:* Allowing an LLM to extrapolate or "make up" plausible answers when uncertain.
   - *Why:* Free-form generative AI often hallucinates plausible rules (e.g. guessing age 18 when the rule says 21). In welfare, strict honest refusal is much safer.
2. **Heavy Database Infrastructure (Postgres/Docker):**
   - *Left out:* Complex SQL database servers.
   - *Why:* Validated JSON records and in-memory caches allow any evaluator or field agent to run the code on a laptop in seconds without database configuration.
3. **Voice / Speech Engines:**
   - *Left out:* Audio speech-to-text models.
   - *Why:* Kept the repository focused squarely on the core AI/ML challenges: **strict groundedness, attribution, and hallucination prevention**.

---

## 🎙️ Walkthrough Questions & Plain-English Answers

### Q1. One decision you made, and the option you decided against?
- **Decision Made:** **Strict Extractive Grounding with Honest Fallbacks.** When an answer is missing or unsupported, the AI explicitly states: *"The official approved record does not contain this information."*
- **Option Decided Against:** **Open Conversational Generative RAG.** Decided against letting the AI fill in gaps from memory, because false positives cause direct financial and emotional harm to poor families.

---

### Q2. Where does your work fall short, and how would someone notice?
- **Where it falls short:**
  1. *Regional Rural Dialects:* The Hindi answers use standard Khari Boli Hindi. While correct, it can feel formal to citizens speaking rural dialects (like Ahirani, Varhadi, or Bhojpuri).
  2. *Last-Minute Circulars:* State departments frequently amend rules via local WhatsApp circulars. A brand-new extension announced yesterday won't be known until the record is updated.
- **How someone would notice:** A rural field agent will notice that the Hindi phrasing sounds formal like a textbook, or an applicant might bring a local gazette notification with an amended deadline not yet in the central knowledge base.

---

### Q3. How did you check the quality of Hindi answers, especially if not fluent?
We implemented a **4-pillar automated quality checker** in Python (`src/hindi_checker.py`):
1. **Civic Welfare Glossary Audit:** An automated dictionary check ensuring core government terms are translated accurately (e.g., Direct Benefit Transfer $\to$ *प्रत्यक्ष लाभ अंतरण*, Domicile $\to$ *अधिवास प्रमाणपत्र*, Beneficiary $\to$ *लाभार्थी*).
2. **Script Purity & Leakage Check:** Regex check verifying that Devanagari Unicode coverage exceeds 85% and no untranslated English words leak into the response.
3. **Sentence Length & Readability:** Programmatically verified that sentences stay under 18 words to ensure high readability for low-literacy citizens.
4. **Back-Translation Verification:** Translated Hindi back to English to verify that the core factual eligibility criteria remained unchanged.
5. **Human-in-the-Loop Review:** Designed a workflow where 5% of drafts are reviewed by native-speaking women field agents (*Haqdarshaks*) before production deployment.

---

### Q4. An answer is accurate but hard to follow for someone with low literacy. How do you balance accuracy and clarity?
We built the **3-Tier Progressive Disclosure Framework**:
- **Tier 1 — The Bottom Line (Instant Visual Clarity):** Starts with an unmistakable visual icon and one direct sentence:
  - `✅ हाँ, आप पात्र हैं` (Yes, you are eligible)
  - `❌ नहीं, आप पात्र नहीं हैं` (No, you are not eligible)
  - `💰 ₹1,500 हर महीने सीधे बैंक खाते में` (₹1,500 every month in your bank)
- **Tier 2 — Actionable 3-Point Bullets:** Replaces legal jargon with everyday spoken terms (e.g., instead of *"सक्षम प्राधिकारी द्वारा निर्गत अधिवास प्रमाण पत्र"*, say *"15 साल पुराना राशन कार्ड या स्कूल की टीसी"*).
- **Tier 3 — Collapsible Official Evidence Drawer:** Retains the exact government resolution number and source clause in an expandable drawer for the community agent to verify.

---

### Q5. Model Selection & Cost per Scheme
- **Recommended Model:** **Gemini 1.5 Flash** or **GPT-4o-mini** (with structured JSON mode).
- **Token Budget per Scheme:** ~3,500 input tokens + ~1,800 output tokens (~5,300 tokens total).
- **Cost per Scheme:** **~₹0.30 INR ($0.0035 USD)** per scheme record.
- **Cost for 5,000 Schemes:**
  - Generating the complete national catalog of **5,000 schemes costs only ~₹1,500 INR (~$18 USD)**.
  - Ongoing monthly verification updates: **under ₹100 INR (~$1.20 USD) per month**.

---

## 📋 The 6-Part Scheme Field Specification

Every scheme record in `data/` implements the 6-part schema required by the Case Study brief:
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

When information is absent from official guidelines, it is recorded explicitly with status `"not found"`:
```json
{
  "scheme_ref": "SCHEME-CENTRAL-PMK-001",
  "field": "income_ceiling",
  "value": "",
  "evidence": "Absence verification: Review of Operational Guidelines Section 4 (pp. 5-7), Doc-Ref: AGRI-GOI-PMK-2023, captured 2024-09-10",
  "confidence": "high",
  "status": "not found",
  "note": "The scheme does not impose an annual family income ceiling; disqualification is strictly tax-payer and role-based."
}
```

---

## 🧪 Automated Unit Test Suite

Run all tests with:
```bash
python -m pytest tests/ -v
```

Output (12/12 passing in < 0.4s):
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

## 📁 Repository Directory Structure

```
Govt_Scheme_AI/
├── README.md                      # Complete documentation & walkthrough explanations
├── requirements.txt               # Dependencies (fastapi, uvicorn, pydantic, pytest)
├── run.py                         # One-line application launcher (starts on port 8080)
├── .gitignore                     # Git ignore rules
│
├── data/
│   ├── pm_kisan_record.json       # PM-KISAN scheme record (6-part schema)
│   ├── ladki_bahin_record.json    # Maharashtra Ladki Bahin record (6-part schema)
│   └── faq_catalog.json           # 20 Curated Bilingual FAQs with field citations
│
├── src/
│   ├── app.py                     # FastAPI REST server & static router
│   ├── models.py                  # Pydantic schemas (SchemeField, FAQItem, etc.)
│   ├── knowledge_base.py          # Scheme record loader & provenance tracker
│   ├── faq_engine.py              # Bilingual Q&A engine with strict fallback
│   ├── verifier.py                # Silent hallucination & faithfulness checker
│   └── hindi_checker.py           # 4-pillar Hindi quality verification module
│
├── static/
│   ├── index.html                 # Clean, user-focused 2-column web UI
│   ├── style.css                  # Modern, responsive styling system
│   └── app.js                     # Interactive client logic & language switcher
│
└── tests/
    ├── test_knowledge_base.py     # Schema compliance tests
    ├── test_verifier.py           # Hallucination guardrail tests
    └── test_faq_engine.py         # Bilingual Q&A & fallback tests
```

---

## 👥 Submission Information
- **Assignment:** Haqdarshak AI/ML Engineer Case Study (Scenario A3)
- **GitHub Repository:** [https://github.com/552radhika-Dev/Govt_Scheme_AI](https://github.com/552radhika-Dev/Govt_Scheme_AI)
