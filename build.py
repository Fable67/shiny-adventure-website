#!/usr/bin/env python3
"""Static site generator for the Pali Dictionary.

Reads term JSON files from a data directory and generates a complete static HTML/CSS/JS site
suitable for GitHub Pages hosting.

Usage:
    python3 build.py --data-dir <path-to-terms> --out <output-dir> [--data-repo-url <url>]

Example:
    python3 build.py --out dist
"""

import sys
import argparse
import time
import json
from pathlib import Path
from datetime import datetime

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from generator.loader import TermLoader
from generator.linking import TermLinker
from generator.render import HTMLRenderer
from generator.search_index import SearchIndexBuilder


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_static_files(src_dir: Path, out_dir: Path) -> None:
    """Copy static CSS and JS files to output directory."""
    static_src = src_dir / "src" / "static"
    if not static_src.exists():
        print(f"Warning: Static directory not found at {static_src}")
        return
    
    for subdir in ["css", "js"]:
        src_subdir = static_src / subdir
        if src_subdir.exists():
            dst_subdir = ensure_dir(out_dir / subdir)
            for file in src_subdir.glob("*"):
                if file.is_file():
                    content = file.read_text(encoding="utf-8")
                    (dst_subdir / file.name).write_text(content, encoding="utf-8")


def write_html_file(output_dir: Path, rel_path: str, content: str) -> None:
    """Write HTML content to file, creating directories as needed."""
    file_path = output_dir / rel_path
    ensure_dir(file_path.parent)
    file_path.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a static Pali dictionary website from JSON term data."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent / "data" / "shiny-adventure" / "terms",
        help="Path to terms/ directory (default: ./data/shiny-adventure/terms)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "dist",
        help="Output directory (default: ./dist)"
    )
    parser.add_argument(
        "--data-repo-url",
        type=str,
        default="https://github.com/timedrapery/shiny-adventure",
        help="URL to the data repository (for footer link, default: https://github.com/timedrapery/shiny-adventure)"
    )
    
    args = parser.parse_args()
    
    print(f"🔨 Pali Dictionary Static Site Generator")
    print(f"📂 Data directory: {args.data_dir}")
    print(f"📁 Output directory: {args.out}")
    print(f"🔗 Data repo URL: {args.data_repo_url}")
    print()
    
    build_start = time.time()
    
    # Verify data directory exists
    if not args.data_dir.exists():
        print(f"❌ Error: Data directory not found: {args.data_dir}")
        sys.exit(1)
    
    # Ensure output directory
    output_dir = ensure_dir(args.out)
    
    # Load all terms
    print("📖 Loading terms...")
    loader = TermLoader(args.data_dir)
    all_terms = loader.load_all_terms()
    major_terms = loader.get_major_terms(all_terms)
    minor_terms = loader.get_minor_terms(all_terms)
    tag_counts = loader.get_all_tags(all_terms)
    
    print(f"   ✓ Loaded {len(all_terms):,} terms ({len(major_terms)} major, {len(minor_terms):,} minor)")
    print(f"   ✓ Found {len(tag_counts)} unique tags")
    
    # Create linker for resolving related_terms
    print("🔗 Building term linkage...")
    linker = TermLinker(all_terms)
    unresolved_count = linker.count_unresolved_across_all()
    print(f"   ✓ Linker ready; {unresolved_count} related_term strings unresolved (will render as plain text)")
    
    # Create renderer
    renderer = HTMLRenderer(linker=linker, data_repo_url=args.data_repo_url)
    
    # Build search index
    print("🔍 Building search index...")
    search_index = SearchIndexBuilder.build_search_index(all_terms)
    SearchIndexBuilder.write_search_index(search_index, str(output_dir / "search-index.json"))
    print(f"   ✓ Search index: {len(search_index)} entries")
    
    # Generate pages
    pages_generated = 0
    
    # Home page
    print("🏠 Generating home page...")
    home_content = renderer.render_index_page(all_terms, tag_counts, major_terms)
    home_html = renderer.render_page_wrapper(home_content, "Home", page_path="index.html")
    write_html_file(output_dir, "index.html", home_html)
    pages_generated += 1
    
    # Term pages
    print("📄 Generating term pages...")
    terms_dir = ensure_dir(output_dir / "term")
    for i, (norm_term, term_data) in enumerate(sorted(all_terms.items())):
        if (i + 1) % 200 == 0:
            print(f"   ... {i + 1}/{len(all_terms)}")
        
        pali_headword = term_data.get("term", norm_term)
        page_title = f"{pali_headword}"
        
        term_content = renderer.render_term_page(norm_term, term_data, all_terms)
        term_html = renderer.render_page_wrapper(term_content, page_title, page_type="term-page", page_path=f"term/{norm_term}.html")
        write_html_file(output_dir, f"term/{norm_term}.html", term_html)
        pages_generated += 1
    
    print(f"   ✓ Generated {len(all_terms):,} term pages")
    
    # Alphabetical index
    print("📑 Generating alphabetical index...")
    alpha_content = renderer.render_alphabet_index(all_terms)
    alpha_html = renderer.render_page_wrapper(alpha_content, "Alphabetical Index", page_type="index", page_path="alphabet/index.html")
    write_html_file(output_dir, "alphabet/index.html", alpha_html)
    pages_generated += 1
    
    # Tag pages
    print("🏷️  Generating tag pages...")
    tag_index_content = renderer.render_tag_index(tag_counts)
    tag_index_html = renderer.render_page_wrapper(tag_index_content, "Browse Tags", page_type="index", page_path="tags/index.html")
    write_html_file(output_dir, "tags/index.html", tag_index_html)
    pages_generated += 1
    
    for tag, count in sorted(tag_counts.items()):
        term_norms = loader.get_terms_by_tag(tag, all_terms)
        tag_content = renderer.render_tag_page(tag, term_norms, all_terms)
        tag_html = renderer.render_page_wrapper(tag_content, f"Tag: {tag}", page_type="tag-page", page_path=f"tag/{tag}/index.html")
        write_html_file(output_dir, f"tag/{tag}/index.html", tag_html)
        pages_generated += 1
    
    print(f"   ✓ Generated {len(tag_counts)} tag pages + 1 tag index")
    
    # Major terms list
    print("📋 Generating term lists...")
    major_list_content = renderer.render_term_list(
        list(major_terms.keys()),
        all_terms,
        title="Major Terms",
        list_type="major"
    )
    major_list_html = renderer.render_page_wrapper(major_list_content, "Major Terms", page_type="index", page_path="major/index.html")
    write_html_file(output_dir, "major/index.html", major_list_html)
    pages_generated += 1
    
    # All terms list
    all_list_content = renderer.render_term_list(
        list(all_terms.keys()),
        all_terms,
        title="All Terms",
        list_type="terms"
    )
    all_list_html = renderer.render_page_wrapper(all_list_content, "All Terms", page_type="index", page_path="terms/index.html")
    write_html_file(output_dir, "terms/index.html", all_list_html)
    pages_generated += 1
    
    print(f"   ✓ Generated 2 term list pages")
    
    # Copy static assets
    print("📦 Copying static assets...")
    copy_static_files(Path(__file__).parent, output_dir)
    print("   ✓ Static assets copied")
    
    # Build summary
    build_time = time.time() - build_start
    
    print()
    print("=" * 60)
    print(f"✅ Build complete in {build_time:.1f}s")
    print()
    print("📊 Summary:")
    print(f"   Total terms: {len(all_terms):,}")
    print(f"   - Major: {len(major_terms)}")
    print(f"   - Minor: {len(minor_terms):,}")
    print(f"   Tags: {len(tag_counts)}")
    print()
    print("📄 Pages generated:")
    print(f"   Home: 1")
    print(f"   Term details: {len(all_terms):,}")
    print(f"   Alphabetical index: 1")
    print(f"   Tag browse: 1 index + {len(tag_counts)} tag pages")
    print(f"   Term lists: 2 (major + all)")
    print(f"   TOTAL: {pages_generated:,} pages")
    print()
    print("📦 Search index:")
    print(f"   Entries: {len(search_index):,}")
    print(f"   File: search-index.json")
    print()
    print("🔗 Link resolution:")
    print(f"   Unresolved related_terms: {unresolved_count}")
    print(f"   (These will render as plain text, not broken links)")
    print()
    print(f"📁 Output: {output_dir.resolve()}")
    print()
    print("🚀 Ready to deploy to GitHub Pages!")
    print("=" * 60)


if __name__ == "__main__":
    main()
