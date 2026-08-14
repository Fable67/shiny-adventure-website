"""Generates a JSON search index for client-side searching."""

import json
from typing import Dict, List, Any


class SearchIndexBuilder:
    """Builds a JSON search index for all terms."""

    @staticmethod
    def build_search_index(all_terms: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build a searchable index of all terms.
        
        Args:
            all_terms: Dictionary mapping normalized_term -> term data.
        
        Returns:
            List of index entries, each containing:
            - normalized_term: for linking
            - term: Pali headword
            - preferred_translation: main translation
            - definition: short definition
            - entry_type: "major" or "minor"
            - tags: list of tags
            - part_of_speech: e.g. "noun", "verb"
        """
        index = []
        
        for normalized_term, term_data in sorted(all_terms.items()):
            entry = {
                "normalized_term": normalized_term,
                "term": term_data.get("term", ""),
                "preferred_translation": term_data.get("preferred_translation", ""),
                "definition": term_data.get("definition", ""),
                "entry_type": term_data.get("entry_type", "minor"),
                "tags": term_data.get("tags", []),
                "part_of_speech": term_data.get("part_of_speech", ""),
            }
            index.append(entry)
        
        return index

    @staticmethod
    def write_search_index(index: List[Dict[str, Any]], output_path: str) -> None:
        """Write search index to a JSON file.
        
        Args:
            index: List of index entries.
            output_path: Path to write the JSON file.
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
