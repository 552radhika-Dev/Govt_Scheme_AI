"""
FastAPI Application for Haqdarshak Scheme AI Citizen FAQ Generator & Knowledge Workbench.
Provides REST APIs for:
- Browsing approved scheme records in the 6-part field format
- Pre-curated 8-10 Bilingual FAQs per scheme
- Interactive citizen chat with field-level attribution and strict fallback
- Automated hallucination & faithfulness verification
- Programmatic Hindi quality auditing
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.models import (
    SchemeRecord,
    SchemeField,
    FAQItem,
    ChatRequest,
    ChatResponse,
    VerificationCheck
)
from src.knowledge_base import kb
from src.faq_engine import faq_engine
from src.verifier import verifier
from src.hindi_checker import hindi_checker


app = FastAPI(
    title="Haqdarshak Scheme Knowledge Base & Citizen FAQ AI",
    description="Grounded Bilingual Welfare FAQ Generation and Verification System",
    version="1.0.0"
)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class VerifyRequest(BaseModel):
    scheme_id: str
    question: str
    answer: str
    claimed_fields: List[str]


class HindiAuditRequest(BaseModel):
    english_text: str
    hindi_text: str


@app.get("/api/schemes")
def get_schemes():
    """List all approved scheme records in the knowledge base."""
    return kb.list_schemes()


@app.get("/api/schemes/{scheme_id}")
def get_scheme_details(scheme_id: str):
    """Retrieve complete scheme record with all fields conforming to the 6-part schema."""
    scheme = kb.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme


@app.get("/api/schemes/{scheme_id}/faqs")
def get_scheme_faqs(scheme_id: str):
    """Get the 8-10 bilingual FAQs for a scheme with field provenance."""
    scheme = kb.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return kb.get_faqs_for_scheme(scheme_id)


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Process a citizen/agent question against the approved scheme record.
    Returns grounded answer, cited fields, evidence snippets, and automated verification check.
    """
    return faq_engine.query_scheme(request)


@app.post("/api/verify", response_model=VerificationCheck)
def verify_answer_endpoint(req: VerifyRequest):
    """
    Automated check that catches unsupported answers or hallucinations (Requirement 4).
    """
    scheme = kb.get_scheme(req.scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return verifier.check_answer_groundedness(
        question=req.question,
        answer=req.answer,
        scheme=scheme,
        claimed_fields=req.claimed_fields
    )


@app.post("/api/hindi-audit")
def hindi_audit_endpoint(req: HindiAuditRequest):
    """
    Evaluate Hindi answer quality, terminology consistency, and readability.
    Directly demonstrates walkthrough answer on Hindi QA without fluency.
    """
    return hindi_checker.evaluate_hindi_answer(req.english_text, req.hindi_text)


@app.get("/api/walkthrough-notes")
def get_walkthrough_notes():
    """Return the structured answers to the assignment walkthrough questions."""
    return {
        "scenario": "A3 · Citizen FAQ Generator",
        "decisions": {
            "decision_made": "Strict extractive & NLI-verified grounding with a fail-safe fallback ('Record does not contain this information') over open generative RAG.",
            "option_decided_against": "Open-ended generative chat that attempts to interpolate or extrapolate answers using parametric LLM memory.",
            "rationale": "In citizen welfare schemes, a confident hallucination (e.g. telling an ineligible family to travel 50 km with wrong papers, or falsely promising ₹10,000) causes tangible harm, financial loss, and disillusionment. Strict adherence to Principle 2 ('If you cannot show a source, leave the field empty and say why, rather than filling it in') is mandatory."
        },
        "limitations": {
            "where_it_falls_short": "1. Field-based records represent structured summaries rather than raw, messy circulars with uncodified footnotes. 2. Standard Khari Boli Hindi can occasionally feel formal to citizens speaking regional rural dialects (e.g., Ahirani, Varhadi, Bhojpuri).",
            "how_someone_would_notice": "A community field agent (Haqdarshak) in rural Maharashtra or Bihar testing voice queries in local dialect will notice the formal grammar, or a citizen asking about an edge-case clause amended yesterday in a sub-circular not yet incorporated in the record."
        },
        "hindi_quality_check": {
            "methodology": "How we checked Hindi quality without native fluency:",
            "steps": [
                "1. Domain Civic Glossary Alignment: Enforced strict mapping of official welfare vocabulary (e.g., DBT, RoR/Khatauni, Domicile, Beneficiary, Aadhaar).",
                "2. Automated Script & Leakage Verification: Programmatic audit verifying Devanagari Unicode completeness (≥85%) and zero untranslated English jargon.",
                "3. Readability & Sentence Length Heuristics: Maintained average sentence length under 18 words to prevent legalistic cognitive overload.",
                "4. Back-Translation Semantic Consistency: Automated translation cycles to ensure factual claims retain identical meaning in reverse.",
                "5. Haqdarshak Community Agent Human-in-the-Loop Pilot: Staged rollout where bilingual women field agents review sample batches before production release."
            ]
        },
        "literacy_vs_accuracy": {
            "balance_strategy": "Progressive Disclosure Framework (3 Tiers):",
            "tier_1": "The Bottom Line (Instant Answer): A single clear sentence starting with a clear icon (✅ हाँ, आप पात्र हैं / ❌ नहीं, आप पात्र नहीं हैं / 💰 ₹6,000 हर साल).",
            "tier_2": "Actionable Bullets: Exactly 3-4 bullet points highlighting only what the citizen must bring or do, using everyday terms (e.g., 'जमीन के कागज' instead of 'भू-अभिलेख स्वत्व प्रमाण').",
            "tier_3": "Collapsible Official Evidence Drawer: Complete legal clause, Government Resolution reference, and field citations for the Haqdarshak community agent to verify if challenged."
        },
        "ai_model_pricing": {
            "model": "Gemini 1.5 Flash / GPT-4o-mini (Dual Extractive + NLI Verification Pipeline)",
            "input_tokens_per_scheme": "~3,500 tokens (Standard Scheme Record + Guidelines)",
            "output_tokens_per_scheme": "~1,800 tokens (10 Bilingual FAQs + Citations)",
            "cost_per_scheme_inr": "Approximately ₹0.25 to ₹0.40 per scheme (under 0.5 cents USD)",
            "annual_knowledge_base_cost_5000_schemes": "₹2,000 for 5,000 schemes initial draft generation; verification re-runs under ₹500/month."
        }
    }


# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def serve_ui():
        return FileResponse(STATIC_DIR / "index.html")
