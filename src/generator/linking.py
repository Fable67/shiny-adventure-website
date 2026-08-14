"""Utilities for resolving related_terms and generating normalized forms."""

import re
import unicodedata
from typing import Dict, Tuple, Optional, Any


class TermLinker:
    """Resolves related_terms strings to actual term entries with flexible matching."""

    def __init__(self, all_terms: Dict[str, Dict[str, Any]]):
        """Initialize with a dictionary of all terms.
        
        Args:
            all_terms: Dictionary mapping normalized_term -> term data.
        """
        self.all_terms = all_terms
        # Build reverse lookup: pali form (with diacritics) -> normalized_term
        self.pali_to_normalized: Dict[str, str] = {}
        # Build also a dediacriticized version lookup
        self.dediacriticized_to_normalized: Dict[str, str] = {}
        
        for norm_term, term_data in all_terms.items():
            pali = term_data.get("term", "")
            if pali:
                self.pali_to_normalized[pali] = norm_term
                # Also store the dediacriticized version
                dediac = self._dediacriticize(pali)
                if dediac and dediac != pali:
                    self.dediacriticized_to_normalized[dediac] = norm_term
                # And lowercase version of both
                self.dediacriticized_to_normalized[dediac.lower()] = norm_term

    def _dediacriticize(self, text: str) -> str:
        """Remove diacritics from text (Pali macrons/dots).
        
        Converts NFD (decomposed) and removes combining marks.
        """
        nfd = unicodedata.normalize("NFD", text)
        result = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
        return result

    def _slugify(self, text: str) -> str:
        """Convert text to a slug (lowercase, dashes, alphanumeric)."""
        text = self._dediacriticize(text).lower()
        text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
        return text

    def resolve_related_term(self, related_term_str: str) -> Optional[str]:
        """Resolve a related_term string to a normalized_term if possible.
        
        Tries multiple matching strategies:
        1. Exact match on normalized_term
        2. Exact match on term (Pali with diacritics)
        3. Case-insensitive exact match on term
        4. Match on dediacriticized version (case-insensitive)
        5. Match on slugified version (case-insensitive)
        
        Args:
            related_term_str: The related term string from a term's related_terms list.
        
        Returns:
            The normalized_term if found, None otherwise.
        """
        related_term_str = related_term_str.strip()
        
        # Strategy 1: Direct normalized_term match
        if related_term_str in self.all_terms:
            return related_term_str
        
        # Strategy 2: Exact match on Pali term
        if related_term_str in self.pali_to_normalized:
            return self.pali_to_normalized[related_term_str]
        
        # Strategy 3: Case-insensitive match on Pali term
        for pali, norm_term in self.pali_to_normalized.items():
            if pali.lower() == related_term_str.lower():
                return norm_term
        
        # Strategy 4: Match dediacriticized form
        dediac_lookup = self._dediacriticize(related_term_str).lower()
        if dediac_lookup in self.dediacriticized_to_normalized:
            return self.dediacriticized_to_normalized[dediac_lookup]
        
        # Strategy 5: Try as a slug
        slug_lookup = self._slugify(related_term_str)
        if slug_lookup in self.all_terms:
            return slug_lookup
        
        # No match found
        return None

    def resolve_related_terms(self, related_terms: list) -> Tuple[list, list]:
        """Resolve a list of related_term strings.
        
        Args:
            related_terms: List of related_term strings from term data.
        
        Returns:
            Tuple of (resolved_list, unresolved_list).
            - resolved_list: list of dicts with keys 'normalized_term' and 'term'
            - unresolved_list: list of strings that couldn't be resolved
        """
        resolved = []
        unresolved = []
        
        for related_str in related_terms:
            normalized = self.resolve_related_term(related_str)
            if normalized:
                term_data = self.all_terms[normalized]
                resolved.append({
                    "normalized_term": normalized,
                    "term": term_data.get("term", normalized),
                })
            else:
                unresolved.append(related_str)
        
        return resolved, unresolved

    def count_unresolved_across_all(self) -> int:
        """Count total unresolved related_terms across all terms.
        
        Returns:
            Total count of related_terms that couldn't be resolved.
        """
        total_unresolved = 0
        for term_data in self.all_terms.values():
            _, unresolved = self.resolve_related_terms(term_data.get("related_terms", []))
            total_unresolved += len(unresolved)
        return total_unresolved
