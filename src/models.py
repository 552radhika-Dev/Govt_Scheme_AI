"""
Pydantic Data Models for Haqdarshak Scheme Knowledge Base & FAQ Generator.
Implements the exact 6-part field format specified in the Case Study Brief:
- scheme_ref
- field
- value
- evidence
- confidence
- status
- note
"""

from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field


class SchemeField(BaseModel):
    """Represents a single atomic field in a scheme record per Haqdarshak specification."""
    scheme_ref: str = Field(..., description="Which scheme this belongs to (an ID or source doc)")
    field: str = Field(..., description="Field name, e.g., benefit_amount, deadline, eligibility_conditions")
    value: str = Field(default="", description="The extracted value, or empty string if not found")
    evidence: str = Field(
        ...,
        description="The exact text it came from, where in the source (page/section), source link/ref, and capture date"
    )
    confidence: Union[float, Literal["high", "medium", "low"]] = Field(
        default="high",
        description="How sure the system is: number 0-1, or high/medium/low"
    )
    status: Literal["found", "not found", "conflict"] = Field(
        ...,
        description="found, not found, or conflict (when sources disagree, keep all values and sources)"
    )
    note: Optional[str] = Field(
        default=None,
        description="Optional short reason, e.g., why something could not be mapped or conflict notes"
    )


class SchemeRecord(BaseModel):
    """Approved Scheme Record composed of standard SchemeFields."""
    scheme_id: str
    scheme_name: str
    state_or_central: Literal["Central", "State"]
    state_name: Optional[str] = None
    last_approved_date: str
    approved_by: str
    version: str = "1.0.0"
    fields: List[SchemeField]

    def get_field(self, field_name: str) -> Optional[SchemeField]:
        """Retrieve a specific field by name."""
        for f in self.fields:
            if f.field == field_name:
                return f
        return None

    def get_field_value(self, field_name: str, default: str = "") -> str:
        """Helper to get field string value if found."""
        f = self.get_field(field_name)
        if f and f.status == "found":
            return f.value
        return default


class FAQItem(BaseModel):
    """Bilingual FAQ item with explicit field provenance and grounding status."""
    faq_id: str
    scheme_id: str
    category: str = Field(..., description="e.g. Eligibility, Benefit, Documents, Application, Deadline, Exclusion")
    question_en: str
    question_hi: str
    answer_en: str
    answer_hi: str
    
    # Low-literacy simplified answers (clarity tier)
    simple_answer_en: Optional[str] = None
    simple_answer_hi: Optional[str] = None

    # Provenance attribution to scheme fields
    source_fields: List[str] = Field(
        default_factory=list,
        description="List of field names from the scheme record that ground this answer"
    )
    evidence_quotes: List[str] = Field(
        default_factory=list,
        description="Exact source evidence excerpts from the approved record"
    )

    # Status: whether this FAQ is supported by the record or handles missing info
    is_supported_by_record: bool = True
    grounding_note: Optional[str] = None


class VerificationCheck(BaseModel):
    """Result of automated hallucination & unsupported answer check (Case Study Req 4)."""
    is_grounded: bool
    grounding_score: float = Field(..., ge=0.0, le=1.0, description="0.0 = completely hallucinated, 1.0 = fully grounded")
    verdict: Literal["VERIFIED_GROUNDED", "UNSUPPORTED_HALLUCINATION", "RECORD_LACKS_INFO_HONEST_FALLBACK", "POTENTIAL_UNGROUNDED_DRIFT"]
    referenced_fields: List[str]
    matched_facts: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    explanation: str


class ChatRequest(BaseModel):
    scheme_id: str
    question: str
    language: Literal["en", "hi"] = "en"
    mode: Literal["standard", "simple_literacy"] = "standard"


class ChatResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    question: str
    language: str
    answer: str
    source_fields: List[str]
    evidence_quotes: List[str]
    verification: VerificationCheck
    disclaimer: str
    is_fallback: bool
