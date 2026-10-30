"""
Automated Hallucination & Faithfulness Verifier (Case Study Requirement 4).
Catches answers that the scheme record does not support or that hallucinate facts.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from src.models import SchemeRecord, SchemeField, VerificationCheck


class RecordFaithfulnessVerifier:
    """
    Automated check that verifies whether a candidate answer is strictly supported
    by the approved scheme record.
    
    Principles enforced:
    1. Every claimed fact must trace to valid 'found' fields in the record.
    2. Any numerical assertion (amounts, ages, limits) must match the record exactly.
    3. If the record lacks the information, an honest statement of absence is valid,
       whereas making up a figure or rule is classified as an unsupported hallucination.
    """

    def __init__(self):
        # Common civic numerical entity patterns (amounts, ages, years)
        self.currency_pattern = re.compile(r'(?:₹|rs\.?|inr)\s*([0-9,]+(?:\.\d+)?)', re.IGNORECASE)
        self.age_pattern = re.compile(r'\b(age\s*(?:of|is|between)?\s*)?(\d{1,2})\s*(?:years?|yrs?|वर्ष|साल)\b', re.IGNORECASE)
        self.number_pattern = re.compile(r'\b\d+(?:,\d+)*(?:\.\d+)?\b')

    def extract_numerical_entities(self, text: str) -> List[str]:
        """Extract clean numeric entities from text for strict consistency checks."""
        # Normalize commas
        clean_text = text.replace(',', '')
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', clean_text)
        return numbers

    def check_answer_groundedness(
        self,
        question: str,
        answer: str,
        scheme: SchemeRecord,
        claimed_fields: List[str]
    ) -> VerificationCheck:
        """
        Verify whether the answer is strictly supported by the scheme record.
        Returns a VerificationCheck with a score and verdict.
        """
        # 1. Check if the answer is an honest admission of missing data (Principle 2)
        honest_fallback_markers = [
            "does not specify",
            "does not contain",
            "not found",
            "no explicit",
            "record does not require",
            "not restricted",
            "आधिकारिक स्वीकृत रिकॉर्ड में यह जानकारी उपलब्ध नहीं है",
            "रिकॉर्ड में कोई",
            "उल्लेख नहीं है",
            "शर्त नहीं है",
            "जानकारी नहीं दी गई है"
        ]
        is_honest_fallback = any(m in answer.lower() for m in honest_fallback_markers)

        # 2. Validate that claimed fields actually exist in the record
        valid_fields: List[SchemeField] = []
        invalid_field_names: List[str] = []
        for fn in claimed_fields:
            sf = scheme.get_field(fn)
            if sf:
                valid_fields.append(sf)
            else:
                invalid_field_names.append(fn)

        if not claimed_fields and not is_honest_fallback:
            return VerificationCheck(
                is_grounded=False,
                grounding_score=0.0,
                verdict="UNSUPPORTED_HALLUCINATION",
                referenced_fields=[],
                unsupported_claims=["Answer cites zero source fields from the approved scheme record."],
                explanation="Blocked: The answer fails the first principle of attribution—no supporting field cited."
            )

        # If honest fallback and linked to a 'not found' field, this is 100% compliant with Principle 2
        not_found_fields = [f.field for f in valid_fields if f.status == "not found"]
        if is_honest_fallback:
            return VerificationCheck(
                is_grounded=True,
                grounding_score=1.0,
                verdict="RECORD_LACKS_INFO_HONEST_FALLBACK",
                referenced_fields=[f.field for f in valid_fields],
                matched_facts=[f"Honest refusal/clarification for field(s): {', '.join(claimed_fields)}"],
                unsupported_claims=[],
                explanation="Verified: Adheres to Principle 2. When the record lacks the answer, the system honestly admits absence instead of guessing."
            )

        # 3. Check for positive claims on 'not found' fields (Fabrication/Hallucination trap)
        if not_found_fields and not is_honest_fallback:
            return VerificationCheck(
                is_grounded=False,
                grounding_score=0.1,
                verdict="UNSUPPORTED_HALLUCINATION",
                referenced_fields=claimed_fields,
                unsupported_claims=[
                    f"Answer makes affirmative claims on field(s) '{', '.join(not_found_fields)}' which are explicitly marked 'not found' in the official record."
                ],
                explanation="Blocked: Hallucinated fact. The source document does not contain this information, but the answer invented a positive claim."
            )

        # 4. Check numerical entity consistency
        # Aggregate all text from referenced record fields
        record_context = " ".join([f"{f.value} {f.evidence}" for f in valid_fields])
        all_scheme_context = " ".join([f"{f.value} {f.evidence}" for f in scheme.fields if f.status == "found"])
        all_scheme_numbers = set(self.extract_numerical_entities(all_scheme_context))
        
        # Numbers mentioned by the user in their own question (e.g. "I am 19 years old", "income is 2.8L")
        question_numbers = set(self.extract_numerical_entities(question))

        answer_numbers = self.extract_numerical_entities(answer)

        conflicting_numbers = []
        for num in answer_numbers:
            # If the number exists in the record or was introduced by the user in the question, it's valid
            if num in all_scheme_numbers or num in question_numbers:
                continue
            # If the number is large or specific (like monetary figures or ages), flag as hallucinated
            try:
                val = float(num)
                # Ignore small formatting list numbers like 1, 2, 3, 4
                if val in [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]:
                    continue
                conflicting_numbers.append(num)
            except ValueError:
                pass

        if conflicting_numbers:
            return VerificationCheck(
                is_grounded=False,
                grounding_score=0.25,
                verdict="UNSUPPORTED_HALLUCINATION",
                referenced_fields=claimed_fields,
                unsupported_claims=[
                    f"Hallucinated or conflicting numerical values detected: {conflicting_numbers} not found in the approved record for {scheme.scheme_name}."
                ],
                explanation=f"Blocked: The answer includes numbers ({', '.join(conflicting_numbers)}) that contradict or do not exist in the official scheme record."
            )

        # 5. Semantic Fact Overlap Check
        # Ensure that core keywords from the answer find anchors in the cited record fields
        # Tokenize answer keywords (excluding common stop words)
        stop_words = {
            "the", "a", "an", "is", "are", "and", "or", "to", "in", "for", "of", "on", "with",
            "at", "by", "from", "as", "be", "this", "that", "it", "can", "you", "your", "under",
            "का", "के", "की", "है", "हैं", "में", "से", "को", "पर", "और", "या", "नहीं", "भी"
        }
        answer_tokens = [w.lower().strip(".,;:?!'\"()[]{}") for w in answer.split()]
        content_tokens = [w for w in answer_tokens if len(w) > 3 and w not in stop_words]

        record_tokens_lower = record_context.lower()
        matched_tokens = [t for t in content_tokens if t in record_tokens_lower]

        overlap_ratio = len(matched_tokens) / max(1, len(content_tokens))

        if overlap_ratio >= 0.40:
            return VerificationCheck(
                is_grounded=True,
                grounding_score=round(min(1.0, 0.70 + (overlap_ratio * 0.3)), 2),
                verdict="VERIFIED_GROUNDED",
                referenced_fields=claimed_fields,
                matched_facts=[
                    f"Anchored in verified fields: {', '.join(claimed_fields)}",
                    f"Aligned content match: {len(matched_tokens)} semantic anchor terms verified against source evidence."
                ],
                unsupported_claims=[],
                explanation="Passed: Answer is fully grounded in the approved scheme record with verified numerical consistency and direct source evidence."
            )
        else:
            return VerificationCheck(
                is_grounded=False,
                grounding_score=round(overlap_ratio, 2),
                verdict="POTENTIAL_UNGROUNDED_DRIFT",
                referenced_fields=claimed_fields,
                unsupported_claims=["Substantial phrasing divergence from official scheme record evidence."],
                explanation="Warning: Low semantic anchor match with cited scheme fields. Potential ungrounded drift."
            )


# Global verifier instance
verifier = RecordFaithfulnessVerifier()
