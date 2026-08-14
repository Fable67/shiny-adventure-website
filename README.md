# Pali Dictionary Static Website

A fast, pure-Python static site generator that transforms the [shiny-adventure](https://github.com/YOUR_ORG/shiny-adventure) Pali dictionary term data into a complete, searchable HTML website suitable for GitHub Pages hosting.

## Features

- ✨ **Fast generation**: ~1000+ terms in seconds, pure Python stdlib (no external dependencies)
- 🔍 **Instant client-side search**: Fuzzy/substring search across all ~1100 terms with no server required
- 📱 **Responsive design**: Mobile-friendly CSS, works on all screen sizes
- 🎨 **Clean typography**: Serif fonts for Pali text, modern sans-serif for interface
- 🔗 **Smart linking**: Resolves related terms with flexible matching (diacriticized Pali forms, slugified ASCII, case-insensitive) — unresolved terms render as plain text, never broken links
- 📑 **Rich pages**: Each term shows definition, translations (preferred/alternative/discouraged), context rules, examples, related terms, sutta references, tags, and more
- 🏷️ **Browse by tag**: Automatic tag index with clickable tag pages
- 📇 **Alphabetical index**: Quick A-Z term lookup
- ⚙️ **GitHub Actions ready**: Includes a workflow file for automated builds and deployment to GitHub Pages

## Directory Structure

```
shiny-adventure-website/
├── README.md                  # This file
├── .gitignore                 # Ignore dist/ and build artifacts
├── build.py                   # Main build script (entry point)
├── src/
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── loader.py          # Loads term JSON files
│   │   ├── linking.py         # Related-term resolution
│   │   ├── render.py          # HTML page rendering
│   │   └── search_index.py    # Search index generation
│   └── static/
│       ├── css/style.css      # Main stylesheet
│       └── js/
│           ├── search.js      # Client-side search logic
│           └── app.js         # General interactivity
├── .github/
│   └── workflows/
│       └── deploy.yml         # GitHub Actions build + deploy workflow
└── dist/                      # Output directory (generated, gitignored)
```

## Usage

### Local Development

Requires **Python 3.6+** (uses only stdlib).

```bash
cd shiny-adventure-website

# Build the site
python3 build.py --data-dir ../shiny-adventure/terms --out dist

# Serve locally for testing (Python 3.7+)
python3 -m http.server 8000 --directory dist

# Visit http://localhost:8000 in your browser
```

### Command-line Options

```bash
python3 build.py \
  --data-dir <path>         # Path to terms/ directory (default: ../shiny-adventure/terms)
  --out <path>              # Output directory (default: ./dist)
  --data-repo-url <url>     # URL to the data repository for footer link (default: https://github.com/YOUR_ORG/shiny-adventure)
```

#### Example with Custom Data Repo URL

```bash
python3 build.py --data-dir ../shiny-adventure/terms --out dist --data-repo-url https://github.com/myorg/mydata-repo
```

#### How Relative Paths Work

This generator uses **relative paths per page**, ensuring the site works regardless of deployment location (GitHub Pages root, project subdirectory, localhost, etc.). All CSS/JS/link references are computed relative to each page's actual location in the output directory. No `<base>` tag or `--base-url` flag needed.

### Build Output

The build script generates:

- **~1 home page** with search box, stats, and featured terms
- **~1100 term pages** (one per term) with rich details
- **1 alphabetical index** with fast A-Z lookup
- **~N tag pages** (one per unique tag) plus a tag index
- **2 term list pages**: major terms + all terms
- **1 search index** (JSON) loaded by client-side search
- **Static assets**: CSS and JavaScript

```
dist/
├── index.html
├── term/
│   ├── paticcasamuppada.html
│   ├── dukkha.html
│   └── ... (~1100 files)
├── alphabet/index.html
├── tags/index.html
├── tag/
│   ├── core-doctrine/index.html
│   ├── core-practice/index.html
│   └── ... (one per tag)
├── major/index.html
├── terms/index.html
├── search-index.json
├── css/style.css
└── js/
    ├── search.js
    └── app.js
```

## Deployment

### Option 1: GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:

1. **On every push to `main`**: Checks out both this repo and the data repo
2. **Builds the site** using `python3 build.py`
3. **Deploys to GitHub Pages** using the Pages artifact upload

**Setup steps:**

1. In `.github/workflows/deploy.yml`, replace `YOUR_ORG/shiny-adventure` with your actual GitHub org/repo slug:
   ```yaml
   - uses: actions/checkout@v4
     with:
       repository: YOUR_ORG/shiny-adventure  # ← Replace this
       path: shiny-adventure
   ```

2. (Optional) In `build.py`, customize `--data-repo-url` if your data repo has a different URL. The default is `https://github.com/YOUR_ORG/shiny-adventure` (appears in the footer of all pages).

3. Enable GitHub Pages in your repo settings:
    - Go to **Settings → Pages**
    - Source: **GitHub Actions** (or **Deploy from a branch** → select the branch, depending on workflow config)

4. Push to `main`, and the workflow will automatically build and deploy the site.

**Note**: The workflow checks out the `shiny-adventure` repo as a sibling. If that repo is private, the workflow will fail unless the checkout uses a personal access token or deploy key. For simplicity, ensure both repos are public, or use a deploy token.

### Option 2: Manual Deployment (Single Repo)

If you prefer a self-contained repo without cross-repo dependencies:

1. **Copy the term JSON files** from `shiny-adventure/terms/` into this repo (e.g., `data/terms/`)
2. **Commit them** to git (no need for `.gitignore` on `data/`)
3. **Update `deploy.yml`** to skip the second checkout and point to the local `data/` directory:
   ```bash
   python3 build.py --data-dir data/terms --out dist
   ```

This is simpler for a standalone GitHub Pages site but requires maintaining a copy of the term data.

### Option 3: Manual Build and Commit

1. Build locally: `python3 build.py --data-dir ../shiny-adventure/terms --out dist`
2. Commit the `dist/` folder
3. Point GitHub Pages to the `dist/` folder (or rename to `docs/` and point there)

**Not recommended** because it bloats the repo with generated HTML; prefer Option 1 (Actions) or Option 2 (vendored data).

## Data Format

This generator reads from the **shiny-adventure** repository's term JSON files. Each term must conform to the [PALI_TERM_SCHEMA.json](../shiny-adventure/schema/PALI_TERM_SCHEMA.json).

### Key Assumptions

- **Major vs. Minor**: Determined by the term's `entry_type` field and its directory (major/ or minor/)
- **File naming**: Each file's stem (filename without `.json`) matches its `normalized_term` field
- **Related terms resolution**: The generator uses flexible matching to resolve `related_terms` strings:
  - Tries direct normalized_term matches
  - Falls back to matching Pali forms (with diacritics), dediacriticized forms, and slugified versions
  - Unresolved terms render as plain text (not broken links)
- **Links**: All links are computed per-page using relative paths, ensuring they work regardless of deployment location (no `<base>` tag needed unless using `--base-url`)

## Building and Styling

### Adding Custom CSS

Edit `src/static/css/style.css`. The stylesheet uses CSS custom properties (variables) for colors and spacing, making it easy to customize. Includes responsive design and optional dark mode support via `prefers-color-scheme`.

### Adding JavaScript

Edit `src/static/js/app.js` (general interactivity) or `src/static/js/search.js` (search logic). Uses vanilla JavaScript only; no frameworks or external libraries.

### Modifying HTML Output

Edit `src/generator/render.py` to change how pages are generated. Each renderer method (`render_term_page`, `render_index_page`, etc.) produces HTML strings. No template files or Jinja2; all templates use simple f-strings for easy review.

## Search Index

The site generates a `search-index.json` file containing all terms with their:
- `normalized_term`
- `term` (Pali with diacritics)
- `preferred_translation`
- `definition`
- `entry_type`
- `tags`
- `part_of_speech`

The client-side `search.js` loads this JSON and performs instant filtering as you type, using a heuristic scoring system that weights exact matches and term matches higher than definition matches.

## FAQ

### Why no external dependencies?

We use only Python stdlib (json, pathlib, re, unicodedata, html, etc.) so the generator:
- Runs in GitHub Actions without pip install steps
- Is trivial to review (no dependency audit needed)
- Works on any system with Python 3.6+

### Why relative paths instead of absolute?

Relative paths ensure the site works regardless of where it's deployed (GitHub Pages root, project page subdirectory, localhost, etc.). The generator computes the correct relative URL from each page's location to reach shared assets (CSS, JS) and other pages. This eliminates the need for a `<base>` tag or `--base-url` flag.

### Can I customize the site layout?

Yes! Edit `src/generator/render.py` (Python rendering logic) and `src/static/css/style.css` (styling). All page templates are f-strings, not a separate template language.

### How do I add a new page type?

1. Add a new render method in `src/generator/render.py` (e.g., `render_custom_page`)
2. Call it from `build.py` in the main generation loop
3. Write the output using `write_html_file(output_dir, "path/to/page.html", html_content)`

### How fast is the build?

On a modern machine, the full build (1100+ terms, tag pages, indexes, search index) takes ~5–10 seconds. Exact time depends on disk I/O and term data richness.

### The search isn't finding my term!

The search uses substring and fuzzy matching. Try:
- Typing part of the English translation (e.g., "suffering" for "dukkha")
- Typing the Pali term (e.g., "dukk" for "dukkha")
- Checking the search-index.json to verify the term was indexed

### Related terms aren't linking!

The generator logs unresolved related terms. Check:
1. Is the target term file present in `major/` or `minor/`?
2. Does its `normalized_term` match the filename stem?
3. Is the related_term string a valid Pali form or slug?

Unresolved terms render as plain text in the output, which is intentional—never breaking links.

## Contributing

To improve the generator:

1. Edit the source files in `src/`
2. Test locally: `python3 build.py --data-dir ../shiny-adventure/terms --out dist`
3. Review the generated `dist/` folder
4. Commit and push to trigger the CI workflow

## Customizing the Data Repo Footer Link

Every page displays a footer link to the data repository. By default, this points to `https://github.com/YOUR_ORG/shiny-adventure`. You can customize it:

1. When building locally, pass `--data-repo-url`:
   ```bash
   python3 build.py --data-dir ../shiny-adventure/terms --out dist --data-repo-url https://github.com/myorg/myrepo
   ```

2. In the GitHub Actions workflow (`.github/workflows/deploy.yml`), you can optionally pass the flag if needed, or rely on the default.

## License

This generator and website are part of the [shiny-adventure](https://github.com/YOUR_ORG/shiny-adventure) project. See the main repo for licensing details.

## Support

For issues or suggestions, open an issue on the [shiny-adventure](https://github.com/YOUR_ORG/shiny-adventure) repository or the website repo.
