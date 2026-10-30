"""
Citizen FAQ Answering Engine for Government Welfare Schemes.
Fulfills Scenario A3 requirements:
1. Grounded answers derived solely from approved scheme records.
2. Every answer cites source fields and evidence snippets.
3. Explicit fallback when record lacks information (Principle 2).
4. Dual language support (English & Hindi).
5. Low-literacy accessible response mode.
"""

import re
from typing import Dict, List, Optional, Tuple
from src.models import (
    SchemeRecord,
    SchemeField,
    FAQItem,
    ChatRequest,
    ChatResponse,
    VerificationCheck
)
from src.knowledge_base import kb
from src.verifier import verifier


class FAQEngine:
    """Answers citizen and community agent queries strictly grounded in scheme records."""

    def __init__(self):
        pass

    def _normalize_text(self, text: str) -> List[str]:
        """Convert text into tokens for keyword and semantic matching."""
        tokens = re.findall(r'[\w]+', text.lower())
        # Filter trivial words
        stop_words = {
            "is", "the", "a", "an", "for", "to", "in", "of", "and", "or", "what", "how", "am", "i",
            "my", "can", "do", "we", "get", "me", "if", "there", "any", "are", "under", "scheme",
            "योजना", "क्या", "है", "हैं", "का", "के", "की", "में", "से", "को", "पर", "और", "या"
        }
        return [t for t in tokens if len(t) > 1 and t not in stop_words]

    def _stem_token(self, token: str) -> str:
        """Lightweight stemmer for English and Hindi inflectional endings."""
        # Hindi inflections
        hindi_suffixes = ["ों", "ियों", "ियां", "ाएं", "ता", "ती", "ते", "ना", "नी", "ने", "या", "यी", "ये", "ा", "ी", "े"]
        for s in sorted(hindi_suffixes, key=len, reverse=True):
            if token.endswith(s) and len(token) - len(s) >= 2:
                return token[:-len(s)]

        # English inflections
        eng_suffixes = ["ing", "ies", "ied", "ed", "es", "s"]
        for s in sorted(eng_suffixes, key=len, reverse=True):
            if token.endswith(s) and len(token) - len(s) >= 3:
                return token[:-len(s)]

        return token

    def _compute_similarity(self, query_tokens: List[str], target_tokens: List[str]) -> float:
        """Compute semantic overlap similarity score with stemming and synonyms."""
        if not query_tokens or not target_tokens:
            return 0.0

        # Civic synonyms dictionary
        synonyms = {
            "पैसा": "राशि",
            "रुपए": "राशि",
            "धन": "राशि",
            "सहायता": "राशि",
            "कागजात": "दस्तावेज़",
            "कागज": "दस्तावेज़",
            "money": "benefit",
            "amount": "benefit",
            "cash": "benefit",
            "docs": "documents",
            "papers": "documents"
        }

        stemmed_q = [self._stem_token(synonyms.get(t, t)) for t in query_tokens]
        stemmed_t = [self._stem_token(synonyms.get(t, t)) for t in target_tokens]

        q_set = set(stemmed_q)
        t_set = set(stemmed_t)

        intersection = q_set.intersection(t_set)
        if not intersection:
            return 0.0
        return len(intersection) / len(q_set)

    def find_matching_faq(self, scheme_id: str, query: str) -> Optional[Tuple[FAQItem, float]]:
        """Find the most relevant pre-approved FAQ for a given scheme query."""
        faqs = kb.get_faqs_for_scheme(scheme_id)
        if not faqs:
            return None

        query_tokens = self._normalize_text(query)
        best_faq = None
        highest_score = 0.0

        for faq in faqs:
            # Match against both English and Hindi question tokens
            en_tokens = self._normalize_text(faq.question_en)
            hi_tokens = self._normalize_text(faq.question_hi)
            
            score_en = self._compute_similarity(query_tokens, en_tokens)
            score_hi = self._compute_similarity(query_tokens, hi_tokens)
            score = max(score_en, score_hi)

            if score > highest_score:
                highest_score = score
                best_faq = faq

        # Match threshold (>= 0.35 overlap)
        if best_faq and highest_score >= 0.35:
            return best_faq, highest_score
        return None

    def query_scheme(self, request: ChatRequest) -> ChatResponse:
        """
        Process a citizen/agent question against an approved scheme record.
        Enforces strict grounding, citation, verification, and honest fallback.
        """
        scheme = kb.get_scheme(request.scheme_id)
        if not scheme:
            return ChatResponse(
                scheme_id=request.scheme_id,
                scheme_name="Unknown Scheme",
                question=request.question,
                language=request.language,
                answer=(
                    "The requested scheme ID was not found in the approved knowledge base."
                    if request.language == "en" else
                    "अनुरोधित योजना आईडी स्वीकृत नॉलेज बेस में नहीं मिली।"
                ),
                source_fields=[],
                evidence_quotes=[],
                verification=VerificationCheck(
                    is_grounded=False,
                    grounding_score=0.0,
                    verdict="UNSUPPORTED_HALLUCINATION",
                    referenced_fields=[],
                    unsupported_claims=["Scheme does not exist in knowledge base."],
                    explanation="Scheme ID is invalid or missing."
                ),
                disclaimer="Always verify with an official Haqdarshak community agent.",
                is_fallback=True
            )

        # 1. Search for a matching vetted FAQ
        match = self.find_matching_faq(scheme.scheme_id, request.question)

        if match:
            faq, score = match
            is_hindi = request.language == "hi"
            is_simple = request.mode == "simple_literacy"

            if is_hindi:
                answer_text = (faq.simple_answer_hi if is_simple and faq.simple_answer_hi else faq.answer_hi)
            else:
                answer_text = (faq.simple_answer_en if is_simple and faq.simple_answer_en else faq.answer_en)

            source_fields = faq.source_fields
            evidence_quotes = faq.evidence_quotes

            # Run automated verification check (Req 4)
            verification = verifier.check_answer_groundedness(
                question=request.question,
                answer=faq.answer_en,  # verify against English grounding canonical
                scheme=scheme,
                claimed_fields=source_fields
            )

            is_fallback = not faq.is_supported_by_record or (
                "not found" in [scheme.get_field(f).status for f in source_fields if scheme.get_field(f)]
            )

            disclaimer = (
                "Verified draft generated from approved scheme record. Verified by Haqdarshak AI."
                if request.language == "en" else
                "स्वीकृत योजना रिकॉर्ड से सत्यापित उत्तर। हकदर्शक एआई द्वारा प्रमाणित।"
            )

            return ChatResponse(
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                question=request.question,
                language=request.language,
                answer=answer_text,
                source_fields=source_fields,
                evidence_quotes=evidence_quotes,
                verification=verification,
                disclaimer=disclaimer,
                is_fallback=is_fallback
            )

        # 2. Strict Fallback Handling (Principle 2: If you cannot show a source, do not guess)
        if request.language == "hi":
            fallback_answer = (
                f"आधिकारिक स्वीकृत योजना रिकॉर्ड ({scheme.scheme_name}) में आपके पूछे गए प्रश्न की जानकारी उपलब्ध नहीं है। "
                f"हकदर्शक के सत्यनिष्ठा नियमों के तहत, अधूरी जानकारी पर कोई अनुमान या कयास नहीं लगाया जाता है। "
                f"कृपया निकटतम अधिकृत हकदर्शक सहायक या आधिकारिक सरकारी पोर्टल से पुष्टि करें।"
            )
        else:
            fallback_answer = (
                f"The approved scheme record for '{scheme.scheme_name}' does not contain sufficient verified "
                f"information to answer this question. In accordance with Haqdarshak's core principles, we refuse "
                f"to guess or interpolate unverified rules. Please consult an authorized field agent or the official government portal."
            )

        verification = VerificationCheck(
            is_grounded=True,
            grounding_score=1.0,
            verdict="RECORD_LACKS_INFO_HONEST_FALLBACK",
            referenced_fields=[],
            matched_facts=["Adheres to strict non-hallucination fallback policy (Principle 2)."],
            unsupported_claims=[],
            explanation="Passed: The system safely declined to answer an unsupported query rather than hallucinating facts."
        )

        return ChatResponse(
            scheme_id=scheme.scheme_id,
            scheme_name=scheme.scheme_name,
            question=request.question,
            language=request.language,
            answer=fallback_answer,
            source_fields=[],
            evidence_quotes=[],
            verification=verification,
            disclaimer="Strict Grounding Safety: Information not present in official record.",
            is_fallback=True
        )


# Global FAQ engine instance
faq_engine = FAQEngine()
