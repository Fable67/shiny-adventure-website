# Pali Dictionary Static Website

A fast, pure-Python static site generator that transforms the [shiny-adventure](https://github.com/timedrapery/shiny-adventure) Pali dictionary term data into a complete, searchable HTML website suitable for GitHub Pages hosting.

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
├── .gitmodules                # Git submodule configuration
├── build.py                   # Main build script (entry point)
├── data/
│   └── shiny-adventure/       # Git submodule (shared term data)
│       └── terms/             # Term JSON files
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

# Initialize submodule (required on first clone)
git submodule update --init --recursive

# Build the site (uses data/shiny-adventure/terms by default)
python3 build.py --out dist

# Serve locally for testing (Python 3.7+)
python3 -m http.server 8000 --directory dist

# Visit http://localhost:8000 in your browser
```

Alternatively, clone with submodules in one step:
```bash
git clone --recurse-submodules <this-repo-url>
```

### Command-line Options

```bash
python3 build.py \
  --data-dir <path>         # Path to terms/ directory (default: ./data/shiny-adventure/terms)
  --out <path>              # Output directory (default: ./dist)
  --data-repo-url <url>     # URL to the data repository for footer link (default: https://github.com/timedrapery/shiny-adventure)
```

#### Example with Custom Data Repo URL

```bash
python3 build.py --out dist --data-repo-url https://github.com/myorg/mydata-repo
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

### GitHub Actions (Recommended)

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that automates builds and deployment to GitHub Pages.

**How it works:**

- The `shiny-adventure` data repo is included as a **git submodule** at `data/shiny-adventure`, pinning it to a specific commit
- **On push to `main`**: The workflow checks out the website repo with its submodule, builds the site, and deploys to GitHub Pages
- **Every 6 hours (scheduled)**: The workflow pulls the latest commit from the data repo's default branch (`main`), detects changes, rebuilds and redeploys if there are new terms, and automatically commits the updated submodule pointer back to this repo's `main` branch — ensuring the pinned version stays in sync with deployed content
- **No extra secrets needed**: The submodule URL is public; `GITHUB_TOKEN` (provided by GitHub automatically) has sufficient permissions for checkout + deploy

**Setup steps:**

1. **Enable GitHub Pages** in your repo settings:
   - Go to **Settings → Pages**
   - Source: **GitHub Actions**

2. **Configure workflow permissions** (required for scheduled polling to auto-commit submodule updates):
   - Go to **Settings → Actions → General**
   - Under "Workflow permissions", select **"Read and write permissions"**
   - This allows the scheduled workflow to push the submodule pointer update back to `main`

3. Push to `main`, and the workflow will automatically build and deploy. The scheduled trigger will poll every 6 hours and rebuild when the data repo updates.

**Customizing the data repo:**

If you're using a fork of `shiny-adventure` or a different data repo entirely:

1. Update the submodule remote:
   ```bash
   git submodule set-url data/shiny-adventure <new-repo-url>
   ```

2. Update the footer link default in `build.py`:
   ```python
   default="https://github.com/yourorg/your-data-repo"
   ```

3. Commit and push these changes, then the workflow will use the new data source.

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
- `alternative_translations` (array of alternative translation strings, if available)
- `definition`
- `entry_type`
- `tags`
- `part_of_speech`

The client-side `search.js` loads this JSON and performs instant filtering as you type, using a heuristic scoring system that weights exact matches and term matches higher than definition matches. Matches against `alternative_translations` are scored lower than `preferred_translation` matches to prioritize preferred renderings.

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

## Keeping the Submodule Up to Date

### Locally

After cloning, pull the latest upstream data manually:

```bash
git submodule update --remote --merge data/shiny-adventure
```

This fetches the latest commit from the data repo's default branch and merges it into your local submodule working tree.

### On GitHub

The scheduled workflow (runs every 6 hours) automatically updates the submodule and commits the pointer when changes are detected. You can also manually trigger a rebuild by visiting **Actions** → **Build and Deploy to GitHub Pages** → **Run workflow** → **Branch: main** → **Run workflow**.

## License

This generator and website are part of the [shiny-adventure](https://github.com/timedrapery/shiny-adventure) project. See the main repo for licensing details.

## Support

For issues or suggestions, open an issue on the [shiny-adventure](https://github.com/timedrapery/shiny-adventure) repository or the website repo.
