"""Loads and validates Pali term JSON files from disk."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


class TermLoader:
    """Loads and parses term JSON files from major/ and minor/ directories."""

    def __init__(self, data_dir: Path):
        """Initialize loader with a path to the terms/ directory.
        
        Args:
            data_dir: Path to terms/ directory containing major/ and minor/ subdirs.
        """
        self.data_dir = Path(data_dir)
        self.major_dir = self.data_dir / "major"
        self.minor_dir = self.data_dir / "minor"

    def load_all_terms(self) -> Dict[str, Dict[str, Any]]:
        """Load all term files from both major and minor directories.
        
        Returns:
            Dictionary mapping normalized_term -> term data (dict).
            Skips invalid JSON files with a warning.
        """
        terms = {}
        
        for entry_type, term_dir in [("major", self.major_dir), ("minor", self.minor_dir)]:
            if not term_dir.exists():
                print(f"Warning: {term_dir} does not exist, skipping {entry_type} terms")
                continue
            
            for json_file in sorted(term_dir.glob("*.json")):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        term_data = json.load(f)
                    
                    # Basic validation: check that normalized_term matches filename
                    filename_stem = json_file.stem
                    norm_term = term_data.get("normalized_term", "")
                    
                    if norm_term != filename_stem:
                        print(f"Warning: {json_file.name} normalized_term '{norm_term}' "
                              f"does not match filename stem '{filename_stem}', skipping")
                        continue
                    
                    # Verify entry_type matches directory
                    if term_data.get("entry_type") != entry_type:
                        print(f"Warning: {json_file.name} entry_type '{term_data.get('entry_type')}' "
                              f"does not match directory '{entry_type}', skipping")
                        continue
                    
                    # Add to terms dict
                    if norm_term in terms:
                        print(f"Warning: Duplicate normalized_term '{norm_term}', "
                              f"keeping existing entry from {entry_type}")
                        continue
                    
                    terms[norm_term] = term_data
                    
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Failed to load {json_file.name}: {e}")
                    continue
        
        return terms

    def get_major_terms(self, all_terms: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Filter terms to only major entries."""
        return {k: v for k, v in all_terms.items() if v.get("entry_type") == "major"}

    def get_minor_terms(self, all_terms: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Filter terms to only minor entries."""
        return {k: v for k, v in all_terms.items() if v.get("entry_type") == "minor"}

    def get_all_tags(self, all_terms: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """Extract all unique tags and count occurrences.
        
        Returns:
            Dictionary mapping tag -> count.
        """
        tag_counts: Dict[str, int] = {}
        for term_data in all_terms.values():
            for tag in term_data.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts

    def get_terms_by_tag(self, tag: str, all_terms: Dict[str, Dict[str, Any]]) -> List[str]:
        """Get list of normalized_term strings that have a given tag.
        
        Args:
            tag: The tag to filter by.
            all_terms: Dictionary of all terms.
        
        Returns:
            List of normalized_term strings.
        """
        return [norm_term for norm_term, data in all_terms.items()
                if tag in data.get("tags", [])]
