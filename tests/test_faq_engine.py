"""
Tests for Citizen FAQ Answering Engine and Bilingual Processing.
"""

import pytest
from src.models import ChatRequest
from src.knowledge_base import kb
from src.faq_engine import faq_engine


def test_faq_count_per_scheme():
    """Verify each scheme has at least 8-10 curated bilingual FAQs."""
    pmk_faqs = kb.get_faqs_for_scheme("SCHEME-CENTRAL-PMK-001")
    mlb_faqs = kb.get_faqs_for_scheme("SCHEME-STATE-MAH-MLB-002")

    assert len(pmk_faqs) >= 8
    assert len(mlb_faqs) >= 8

    for faq in pmk_faqs + mlb_faqs:
        assert faq.question_en and faq.question_hi
        assert faq.answer_en and faq.answer_hi
        assert len(faq.source_fields) > 0


def test_query_pm_kisan_english():
    """Test standard citizen question in English."""
    req = ChatRequest(
        scheme_id="SCHEME-CENTRAL-PMK-001",
        question="What documents are needed to apply for PM-KISAN?",
        language="en",
        mode="standard"
    )
    resp = faq_engine.query_scheme(req)

    assert "Aadhaar" in resp.answer
    assert "documents_required" in resp.source_fields
    assert resp.verification.is_grounded is True


def test_query_pm_kisan_hindi():
    """Test citizen question in Hindi."""
    req = ChatRequest(
        scheme_id="SCHEME-CENTRAL-PMK-001",
        question="पीएम-किसान में कितना पैसा मिलता है?",
        language="hi",
        mode="standard"
    )
    resp = faq_engine.query_scheme(req)

    assert "₹6,000" in resp.answer
    assert "benefit_amount" in resp.source_fields or "benefit_frequency" in resp.source_fields


def test_query_low_literacy_mode():
    """Test simplified response mode for low-literacy citizens."""
    req = ChatRequest(
        scheme_id="SCHEME-STATE-MAH-MLB-002",
        question="Can a 19 year old girl apply?",
        language="en",
        mode="simple_literacy"
    )
    resp = faq_engine.query_scheme(req)

    assert "❌ No" in resp.answer
    assert "21" in resp.answer


def test_strict_fallback_on_unsupported_query():
    """Test strict Principle 2 fallback when information is absent from record."""
    req = ChatRequest(
        scheme_id="SCHEME-CENTRAL-PMK-001",
        question="Can I get subsidized airline flight tickets under PM-KISAN?",
        language="en",
        mode="standard"
    )
    resp = faq_engine.query_scheme(req)

    assert resp.is_fallback is True
    assert "does not contain sufficient verified information" in resp.answer
    assert resp.verification.verdict == "RECORD_LACKS_INFO_HONEST_FALLBACK"
