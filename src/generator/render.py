"""HTML rendering and page generation."""

import html
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from .linking import TermLinker


class HTMLRenderer:
    """Renders terms and pages to HTML."""

    def __init__(self, linker: Optional[TermLinker] = None, data_repo_url: str = "https://github.com/YOUR_ORG/shiny-adventure"):
        """Initialize renderer.
        
        Args:
            linker: TermLinker instance for resolving related terms.
            data_repo_url: URL to the data repository (for footer link).
        """
        self.linker = linker
        self.data_repo_url = data_repo_url

    def escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return html.escape(text) if text else ""

    def render_page_wrapper(self, content: str, title: str = "Pali Dictionary",
                           page_type: str = "page", page_path: str = "index.html") -> str:
        """Wrap content in a full HTML page structure.
        
        Args:
            content: The main content HTML.
            title: Page title.
            page_type: CSS class for body (for styling hooks).
            page_path: The output-relative path of the page being rendered (e.g. "index.html", "term/dukkha.html", "tag/core-doctrine/index.html").
        
        Returns:
            Complete HTML document.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.escape_html(title)} — Pali Dictionary</title>
    <link rel="stylesheet" href="{self._rel_url('css/style.css', page_path)}">
</head>
<body class="{page_type}">
    <header class="site-header">
        <div class="header-content">
            <h1><a href="{self._rel_url('index.html', page_path)}">Pali Dictionary</a></h1>
            <p class="tagline">A structured Pali-English lexicon</p>
        </div>
    </header>
    
    <main>
{content}
    </main>
    
    <footer class="site-footer">
        <p>Pali Dictionary — Generated from <a href="{self.escape_html(self.data_repo_url)}">shiny-adventure data</a></p>
    </footer>
    
    <script src="{self._rel_url('js/app.js', page_path)}"></script>
    <script src="{self._rel_url('js/search.js', page_path)}"></script>
</body>
</html>"""

    def _rel_url(self, target: str, from_path: str) -> str:
        """Compute relative URL from one page to another.
        
        Args:
            target: Target file path (e.g. "css/style.css", "index.html", "term/dukkha.html")
            from_path: Source file path (e.g. "index.html", "term/dukkha.html", "tag/core-doctrine/index.html")
        
        Returns:
            Relative URL path.
        """
        from_parts = from_path.strip("/").split("/")
        target_parts = target.strip("/").split("/")
        
        # How many directories up do we need to go from from_path to reach root?
        if from_path == "index.html":
            up_count = 0
        else:
            # Remove filename from from_path to get directory depth
            up_count = len(from_parts) - 1
        
        # Build relative path
        rel_parts = [".."] * up_count + target_parts
        return "/".join(rel_parts)

    def render_index_page(self, all_terms: Dict[str, Dict[str, Any]],
                         tag_counts: Dict[str, int],
                         major_terms: Dict[str, Dict[str, Any]]) -> str:
        """Render the home page.
        
        Args:
            all_terms: All terms.
            tag_counts: Tag -> count mapping.
            major_terms: Major terms dict.
        
        Returns:
            HTML content (without wrapper).
        """
        total_count = len(all_terms)
        major_count = len(major_terms)
        minor_count = total_count - major_count
        tag_count = len(tag_counts)
        
        featured_terms = sorted(major_terms.items(), key=lambda x: x[0])[:6]
        featured_html = ""
        for norm_term, term_data in featured_terms:
            featured_html += f"""        <div class="term-preview">
            <h3><a href="{self._rel_url(f'term/{norm_term}.html', 'index.html')}">{self.escape_html(term_data.get('term', norm_term))}</a></h3>
            <p class="translation">{self.escape_html(term_data.get('preferred_translation', ''))}</p>
            <p class="definition">{self.escape_html(term_data.get('definition', '')[:80])}...</p>
        </div>
"""
        
        return f"""        <section class="home-hero">
            <div class="hero-content">
                <p>A comprehensive, structured Pali-English lexicon with rich semantic links, translation policies, and doctrinal context.</p>
                <div class="search-box">
                    <input type="search" id="search-input" placeholder="Search {total_count:,} terms...">
                    <div id="search-results" class="search-results"></div>
                </div>
            </div>
        </section>
        
        <section class="stats">
            <div class="stat">
                <div class="stat-number">{total_count:,}</div>
                <div class="stat-label">Terms</div>
            </div>
            <div class="stat">
                <div class="stat-number">{major_count}</div>
                <div class="stat-label">Major</div>
            </div>
            <div class="stat">
                <div class="stat-number">{minor_count:,}</div>
                <div class="stat-label">Minor</div>
            </div>
            <div class="stat">
                <div class="stat-number">{tag_count}</div>
                <div class="stat-label">Tags</div>
            </div>
        </section>
        
        <section class="browse-links">
            <h2>Browse</h2>
            <div class="link-grid">
                <a href="{self._rel_url('alphabet/index.html', 'index.html')}" class="browse-link">Alphabetical Index</a>
                <a href="{self._rel_url('tags/index.html', 'index.html')}" class="browse-link">Browse by Tag</a>
                <a href="{self._rel_url('major/index.html', 'index.html')}" class="browse-link">Major Terms ({major_count})</a>
                <a href="{self._rel_url('terms/index.html', 'index.html')}" class="browse-link">All Terms ({total_count:,})</a>
            </div>
        </section>
        
        <section class="featured">
            <h2>Featured Terms</h2>
            <div class="featured-grid">
{featured_html}            </div>
        </section>
"""

    def render_term_page(self, normalized_term: str, term_data: Dict[str, Any],
                        all_terms: Dict[str, Dict[str, Any]]) -> str:
        """Render a single term's detail page.
        
        Args:
            normalized_term: The normalized_term of this term.
            term_data: The term's data dict.
            all_terms: All terms (for resolving related_terms).
        
        Returns:
            HTML content (without wrapper).
        """
        pali = self.escape_html(term_data.get("term", normalized_term))
        pos = self.escape_html(term_data.get("part_of_speech", ""))
        entry_type = term_data.get("entry_type", "minor")
        status = term_data.get("status", "draft")
        preferred_trans = self.escape_html(term_data.get("preferred_translation", ""))
        literal_meaning = term_data.get("literal_meaning")
        definition = term_data.get("definition", "")
        notes = term_data.get("notes")
        
        # Build HTML
        content = f"""        <article class="term-page">
            <header class="term-header">
                <h1 class="term-pali">{pali}</h1>
                <div class="term-meta">
                    <span class="badge badge-{entry_type}">{entry_type.title()}</span>
                    <span class="badge badge-status badge-{status}">{status.title()}</span>
                    <span class="part-of-speech">{pos}</span>
                </div>
            </header>
            
            <section class="term-translation">
                <h2>Translation</h2>
                <p class="preferred-translation">{preferred_trans}</p>
"""
        
        if literal_meaning:
            content += f"""                <p class="literal-meaning"><em>Literal:</em> {self.escape_html(literal_meaning)}</p>
"""
        
        content += f"""            </section>
            
            <section class="term-definition">
                <h2>Definition</h2>
                <p>{self.escape_html(definition)}</p>
            </section>
"""
        
        # Alternative and discouraged translations
        alt_trans = term_data.get("alternative_translations", [])
        disc_trans = term_data.get("discouraged_translations", [])
        
        if alt_trans or disc_trans:
            content += """            <section class="term-translations">
                <h2>Translations</h2>
"""
            if alt_trans:
                content += """                <div class="alternative-translations">
                    <h3>Alternative Translations</h3>
                    <ul>
"""
                for trans in alt_trans:
                    content += f"                        <li>{self.escape_html(trans)}</li>\n"
                content += """                    </ul>
                </div>
"""
            if disc_trans:
                content += """                <div class="discouraged-translations">
                    <h3>Discouraged Translations</h3>
                    <ul>
"""
                for trans in disc_trans:
                    content += f"                        <li>{self.escape_html(trans)}</li>\n"
                content += """                    </ul>
                </div>
"""
            content += """            </section>
"""
        
        # Notes
        if notes:
            content += f"""            <section class="term-notes">
                <h2>Notes</h2>
                <p>{self.escape_html(notes)}</p>
            </section>
"""
        
        # Context rules
        context_rules = term_data.get("context_rules", [])
        if context_rules:
            content += """            <section class="term-context-rules">
                <h2>Context Rules</h2>
                <table class="rules-table">
                    <thead>
                        <tr>
                            <th>Context</th>
                            <th>Rendering</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for rule in context_rules:
                context = self.escape_html(rule.get("context", ""))
                rendering = self.escape_html(rule.get("rendering", ""))
                rule_notes = self.escape_html(rule.get("notes", ""))
                content += f"""                        <tr>
                            <td>{context}</td>
                            <td><code>{rendering}</code></td>
                            <td>{rule_notes}</td>
                        </tr>
"""
            content += """                    </tbody>
                </table>
            </section>
"""
        
        # Example phrases
        example_phrases = term_data.get("example_phrases", [])
        if example_phrases:
            content += """            <section class="term-examples">
                <h2>Example Phrases</h2>
                <div class="examples">
"""
            for example in example_phrases:
                pali_ex = self.escape_html(example.get("pali", ""))
                trans_ex = example.get("translation")
                source_ex = example.get("source")
                notes_ex = example.get("notes")
                
                content += f"""                    <div class="example">
                        <p class="pali"><em>{pali_ex}</em></p>
"""
                if trans_ex:
                    content += f"""                        <p class="translation">{self.escape_html(trans_ex)}</p>
"""
                if source_ex:
                    content += f"""                        <p class="source">— {self.escape_html(source_ex)}</p>
"""
                if notes_ex:
                    content += f"""                        <p class="notes">{self.escape_html(notes_ex)}</p>
"""
                content += """                    </div>
"""
            content += """                </div>
            </section>
"""
        
        # Sutta references
        sutta_refs = term_data.get("sutta_references", [])
        if sutta_refs:
            content += """            <section class="term-suttas">
                <h2>Sutta References</h2>
                <div class="suttas">
"""
            for ref in sutta_refs:
                content += f"""                    <span class="sutta-ref">{self.escape_html(ref)}</span>
"""
            content += """                </div>
            </section>
"""
        
        # Related terms
        related_terms = term_data.get("related_terms", [])
        if related_terms and self.linker:
            resolved, unresolved = self.linker.resolve_related_terms(related_terms)
            if resolved or unresolved:
                content += """            <section class="term-related">
                <h2>Related Terms</h2>
                <div class="related">
"""
                for rel in resolved:
                    norm = self.escape_html(rel["normalized_term"])
                    term = self.escape_html(rel["term"])
                    rel_url = self._rel_url(f"term/{rel['normalized_term']}.html", f"term/{normalized_term}.html")
                    content += f"""                    <a href="{rel_url}" class="related-term-link">{term}</a>
"""
                for unres in unresolved:
                    content += f"""                    <span class="related-term-unresolved">{self.escape_html(unres)}</span>
"""
                content += """                </div>
            </section>
"""
        
        # Tags
        tags = term_data.get("tags", [])
        if tags:
            content += """            <section class="term-tags">
                <h2>Tags</h2>
                <div class="tags">
"""
            for tag in tags:
                tag_escaped = self.escape_html(tag)
                tag_url = self._rel_url(f"tag/{tag}/index.html", f"term/{normalized_term}.html")
                content += f"""                    <a href="{tag_url}" class="tag-link">{tag_escaped}</a>
"""
            content += """                </div>
            </section>
"""
        
        # Authority basis and translation policy (major entries)
        if entry_type == "major":
            auth_basis = term_data.get("authority_basis", [])
            if auth_basis:
                content += """            <section class="term-authority">
                <h2>Authority Basis</h2>
                <div class="authority-items">
"""
                for auth in auth_basis:
                    source = self.escape_html(auth.get("source", ""))
                    scope = self.escape_html(auth.get("scope", ""))
                    priority = auth.get("priority", "")
                    kind = auth.get("kind", "")
                    auth_notes = auth.get("notes", "")
                    
                    content += f"""                    <div class="authority-item">
                        <p class="source"><strong>{source}</strong></p>
                        <p class="scope"><em>{scope}</em></p>
"""
                    if priority:
                        content += f"""                        <p class="priority">Priority: {self.escape_html(priority)}</p>
"""
                    if kind:
                        content += f"""                        <p class="kind">Kind: {self.escape_html(kind)}</p>
"""
                    if auth_notes:
                        content += f"""                        <p class="notes">{self.escape_html(auth_notes)}</p>
"""
                    content += """                    </div>
"""
                content += """                </div>
            </section>
"""
            
            trans_policy = term_data.get("translation_policy", {})
            if trans_policy:
                content += """            <section class="term-policy">
                <h2>Translation Policy</h2>
                <div class="policy-content">
"""
                for key, value in trans_policy.items():
                    if value:
                        key_display = key.replace("_", " ").title()
                        content += f"""                    <div class="policy-item">
                        <h3>{key_display}</h3>
                        <p>{self.escape_html(value)}</p>
                    </div>
"""
                content += """                </div>
            </section>
"""
        
        content += """            <nav class="term-nav">
                <a href="javascript:history.back()" class="nav-link">← Back</a>
            </nav>
        </article>
"""
        
        return content

    def render_alphabet_index(self, all_terms: Dict[str, Dict[str, Any]]) -> str:
        """Render an alphabetical index page.
        
        Args:
            all_terms: All terms.
        
        Returns:
            HTML content (without wrapper).
        """
        # Group by first character
        groups: Dict[str, List[Tuple[str, Dict]]] = {}
        for norm_term, term_data in sorted(all_terms.items()):
            pali = term_data.get("term", norm_term)
            first_char = pali[0].upper() if pali else "?"
            if first_char not in groups:
                groups[first_char] = []
            groups[first_char].append((norm_term, term_data))
        
        content = """        <section class="alphabet-index">
            <h1>Alphabetical Index</h1>
            <div class="letters-nav">
"""
        for letter in sorted(groups.keys()):
            content += f"""                <a href="#{letter}" class="letter-link">{letter}</a>
"""
        content += """            </div>
            
            <div class="term-list">
"""
        for letter in sorted(groups.keys()):
            content += f"""                <h2 id="{letter}">{letter}</h2>
                <ul>
"""
            for norm_term, term_data in groups[letter]:
                pali = self.escape_html(term_data.get("term", norm_term))
                trans = self.escape_html(term_data.get("preferred_translation", ""))
                entry_type = term_data.get("entry_type", "minor")
                url = self._rel_url(f"term/{norm_term}.html", "alphabet/index.html")
                content += f"""                    <li>
                        <a href="{url}" class="term-link">{pali}</a>
                        <span class="badge badge-{entry_type}">{entry_type}</span>
                        <span class="trans">{trans}</span>
                    </li>
"""
            content += """                </ul>
"""
        content += """            </div>
        </section>
"""
        return content

    def render_tag_index(self, tag_counts: Dict[str, int]) -> str:
        """Render the tag browse index page.
        
        Args:
            tag_counts: Tag -> count mapping.
        
        Returns:
            HTML content (without wrapper).
        """
        sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
        
        content = """        <section class="tag-index">
            <h1>Browse by Tag</h1>
            <div class="tags-grid">
"""
        for tag, count in sorted_tags:
            tag_escaped = self.escape_html(tag)
            url = self._rel_url(f"tag/{tag}/index.html", "tags/index.html")
            content += f"""                <a href="{url}" class="tag-card">
                    <span class="tag-name">{tag_escaped}</span>
                    <span class="tag-count">{count}</span>
                </a>
"""
        content += """            </div>
        </section>
"""
        return content

    def render_tag_page(self, tag: str, term_norms: List[str],
                       all_terms: Dict[str, Dict[str, Any]]) -> str:
        """Render a single tag's browse page.
        
        Args:
            tag: The tag name.
            term_norms: List of normalized_terms with this tag.
            all_terms: All terms.
        
        Returns:
            HTML content (without wrapper).
        """
        tag_escaped = self.escape_html(tag)
        
        content = f"""        <section class="tag-page">
            <h1>Tag: {tag_escaped}</h1>
            <p class="tag-count">Entries: {len(term_norms)}</p>
            
            <div class="term-list">
"""
        
        for norm_term in sorted(term_norms):
            if norm_term not in all_terms:
                continue
            term_data = all_terms[norm_term]
            pali = self.escape_html(term_data.get("term", norm_term))
            trans = self.escape_html(term_data.get("preferred_translation", ""))
            entry_type = term_data.get("entry_type", "minor")
            url = self._rel_url(f"term/{norm_term}.html", f"tag/{tag}/index.html")
            
            content += f"""                <div class="term-item">
                    <h3><a href="{url}" class="term-link">{pali}</a></h3>
                    <p class="trans">{trans}</p>
                    <span class="badge badge-{entry_type}">{entry_type}</span>
                </div>
"""
        
        content += """            </div>
        </section>
"""
        return content

    def render_term_list(self, term_norms: List[str], 
                        all_terms: Dict[str, Dict[str, Any]],
                        title: str = "All Terms",
                        list_type: str = "all") -> str:
        """Render a list of terms (e.g. major or all).
        
        Args:
            term_norms: List of normalized_terms.
            all_terms: All terms.
            title: Page title.
            list_type: Type of list (for styling/path).
        
        Returns:
            HTML content (without wrapper).
        """
        content = f"""        <section class="term-list-page">
            <h1>{self.escape_html(title)}</h1>
            <p class="entry-count">Total: {len(term_norms):,}</p>
            
            <div class="term-list">
"""
        
        for norm_term in sorted(term_norms):
            if norm_term not in all_terms:
                continue
            term_data = all_terms[norm_term]
            pali = self.escape_html(term_data.get("term", norm_term))
            trans = self.escape_html(term_data.get("preferred_translation", ""))
            entry_type = term_data.get("entry_type", "minor")
            url = self._rel_url(f"term/{norm_term}.html", f"{list_type}/index.html")
            
            content += f"""                <div class="term-item">
                    <h3><a href="{url}">{pali}</a></h3>
                    <span class="badge badge-{entry_type}">{entry_type}</span>
                    <p class="trans">{trans}</p>
                </div>
"""
        
        content += """            </div>
        </section>
"""
        return content
