"""
Tests for Scheme Knowledge Base and Schema Compliance.
Verifies that all scheme records adhere strictly to Haqdarshak's 6-part field schema.
"""

import pytest
from src.knowledge_base import kb
from src.models import SchemeRecord, SchemeField


def test_schemes_loaded():
    """Verify both sample schemes are loaded into the knowledge base."""
    schemes = kb.list_schemes()
    assert len(schemes) >= 2
    scheme_ids = [s["scheme_id"] for s in schemes]
    assert "SCHEME-CENTRAL-PMK-001" in scheme_ids
    assert "SCHEME-STATE-MAH-MLB-002" in scheme_ids


def test_pm_kisan_field_schema_compliance():
    """Verify PM-KISAN fields strictly conform to the 6-part schema."""
    pmk = kb.get_scheme("SCHEME-CENTRAL-PMK-001")
    assert pmk is not None
    assert pmk.scheme_name == "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)"

    required_fields = [
        "scheme_name", "department", "benefit_amount", "benefit_frequency",
        "eligibility_conditions", "exclusion_criteria", "documents_required",
        "how_to_apply", "deadline", "official_link", "income_ceiling"
    ]

    for rf in required_fields:
        f = pmk.get_field(rf)
        assert f is not None, f"Missing required field: {rf}"
        assert f.scheme_ref == pmk.scheme_id
        assert f.field == rf
        assert f.evidence is not None and len(f.evidence) > 0
        assert f.confidence in ["high", "medium", "low", 1.0, 0.9]
        assert f.status in ["found", "not found", "conflict"]

    # income_ceiling must have status 'not found'
    inc = pmk.get_field("income_ceiling")
    assert inc.status == "not found"
    assert inc.value == ""
    assert inc.note is not None


def test_ladki_bahin_field_schema_compliance():
    """Verify Majhi Ladki Bahin fields strictly conform to the 6-part schema."""
    mlb = kb.get_scheme("SCHEME-STATE-MAH-MLB-002")
    assert mlb is not None
    assert "Ladki Bahin" in mlb.scheme_name
    assert mlb.state_or_central == "State"
    assert mlb.state_name == "Maharashtra"

    # Check caste_requirement field is marked 'not found'
    caste = mlb.get_field("caste_requirement")
    assert caste is not None
    assert caste.status == "not found"
    assert caste.value == ""
