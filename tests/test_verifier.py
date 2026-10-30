"""
Tests for Automated Hallucination & Faithfulness Verifier (Case Study Requirement 4).
"""

import pytest
from src.knowledge_base import kb
from src.verifier import verifier


def test_verifier_passes_grounded_answer():
    """Verify that a legitimate grounded answer passes with high score."""
    scheme = kb.get_scheme("SCHEME-CENTRAL-PMK-001")
    answer = "Beneficiaries receive ₹6,000 per financial year in three equal installments of ₹2,000 each through Direct Benefit Transfer (DBT)."
    
    result = verifier.check_answer_groundedness(
        question="How much benefit do farmers get?",
        answer=answer,
        scheme=scheme,
        claimed_fields=["benefit_amount", "benefit_frequency"]
    )

    assert result.is_grounded is True
    assert result.verdict == "VERIFIED_GROUNDED"
    assert result.grounding_score >= 0.70
    assert len(result.unsupported_claims) == 0


def test_verifier_validates_honest_fallback():
    """Verify that honest admission of missing info adheres to Principle 2."""
    scheme = kb.get_scheme("SCHEME-CENTRAL-PMK-001")
    answer = "The official approved PM-KISAN scheme record does not specify an annual income ceiling."

    result = verifier.check_answer_groundedness(
        question="What is the income ceiling?",
        answer=answer,
        scheme=scheme,
        claimed_fields=["income_ceiling"]
    )

    assert result.is_grounded is True
    assert result.verdict == "RECORD_LACKS_INFO_HONEST_FALLBACK"
    assert result.grounding_score == 1.0


def test_verifier_catches_fake_number_hallucination():
    """Verify that hallucinated monetary values or conflicting numbers are intercepted."""
    scheme = kb.get_scheme("SCHEME-CENTRAL-PMK-001")
    fake_answer = "All farmers receive a special bonus of ₹25000 per year along with free tractors."

    result = verifier.check_answer_groundedness(
        question="What is the bonus?",
        answer=fake_answer,
        scheme=scheme,
        claimed_fields=["benefit_amount"]
    )

    assert result.is_grounded is False
    assert result.verdict == "UNSUPPORTED_HALLUCINATION"
    assert any("25000" in claim for claim in result.unsupported_claims)


def test_verifier_catches_affirmative_claim_on_not_found_field():
    """Verify that asserting a positive claim on a 'not found' field is flagged as a hallucination."""
    scheme = kb.get_scheme("SCHEME-CENTRAL-PMK-001")
    fake_answer = "The government has strictly capped income at ₹350000 per year."

    result = verifier.check_answer_groundedness(
        question="What is the income cap?",
        answer=fake_answer,
        scheme=scheme,
        claimed_fields=["income_ceiling"]
    )

    assert result.is_grounded is False
    assert result.verdict == "UNSUPPORTED_HALLUCINATION"
