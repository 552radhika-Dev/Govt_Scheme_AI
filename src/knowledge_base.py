"""
Knowledge Base Repository for Approved Government Scheme Records.
Loads and validates records complying with Haqdarshak's 6-part field schema.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from src.models import SchemeRecord, SchemeField, FAQItem


class KnowledgeBase:
    """In-memory Knowledge Base managing approved Scheme Records and FAQs."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent / "data"
        self._schemes: Dict[str, SchemeRecord] = {}
        self._faqs: List[FAQItem] = []
        self.reload()

    def reload(self) -> None:
        """Load or reload all scheme records and FAQ catalogs from disk."""
        self._schemes.clear()
        self._faqs.clear()

        # Load PM-KISAN
        pmk_path = self.data_dir / "pm_kisan_record.json"
        if pmk_path.exists():
            with open(pmk_path, "r", encoding="utf-8") as f:
                pmk_data = json.load(f)
                self._schemes[pmk_data["scheme_id"]] = SchemeRecord(**pmk_data)

        # Load Majhi Ladki Bahin
        mlb_path = self.data_dir / "ladki_bahin_record.json"
        if mlb_path.exists():
            with open(mlb_path, "r", encoding="utf-8") as f:
                mlb_data = json.load(f)
                self._schemes[mlb_data["scheme_id"]] = SchemeRecord(**mlb_data)

        # Load FAQ Catalog
        faq_path = self.data_dir / "faq_catalog.json"
        if faq_path.exists():
            with open(faq_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)
                self._faqs = [FAQItem(**item) for item in catalog.get("faqs", [])]

    def get_scheme(self, scheme_id: str) -> Optional[SchemeRecord]:
        """Fetch scheme record by scheme ID."""
        return self._schemes.get(scheme_id)

    def list_schemes(self) -> List[Dict[str, str]]:
        """List summary of all available approved schemes."""
        return [
            {
                "scheme_id": s.scheme_id,
                "scheme_name": s.scheme_name,
                "state_or_central": s.state_or_central,
                "state_name": s.state_name or "All India",
                "version": s.version,
                "last_approved_date": s.last_approved_date,
                "approved_by": s.approved_by,
                "fields_count": str(len(s.fields))
            }
            for s in self._schemes.values()
        ]

    def get_faqs_for_scheme(self, scheme_id: str) -> List[FAQItem]:
        """Get pre-curated 8-10 FAQs for a specific scheme."""
        return [f for f in self._faqs if f.scheme_id == scheme_id]

    def get_faq_by_id(self, faq_id: str) -> Optional[FAQItem]:
        """Find FAQ by ID."""
        for f in self._faqs:
            if f.faq_id == faq_id:
                return f
        return None


# Global singleton instance
kb = KnowledgeBase()
