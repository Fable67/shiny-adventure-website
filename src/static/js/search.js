/**
 * Client-side search functionality for the Pali Dictionary.
 * Loads a search index and provides instant, as-you-type filtering.
 */

class PaliDictionarySearch {
    constructor(indexUrl = 'search-index.json', inputSelector = '#search-input', resultsSelector = '#search-results') {
        this.indexUrl = indexUrl;
        this.inputEl = document.querySelector(inputSelector);
        this.resultsEl = document.querySelector(resultsSelector);
        this.statusEl = document.querySelector('#search-status');
        this.formEl = document.querySelector('#search-form');
        this.searchIndex = [];
        this.init();
    }

    async init() {
        try {
            // Load search index
            const response = await fetch(this.indexUrl);
            if (!response.ok) {
                console.error('Failed to load search index');
                return;
            }
            this.searchIndex = await response.json();
            
            // Prevent form submission for live search
            if (this.formEl) {
                this.formEl.addEventListener('submit', (e) => e.preventDefault());
            }
            
            // Set up event listeners
            if (this.inputEl) {
                this.inputEl.addEventListener('input', (e) => this.onSearch(e));
                this.inputEl.addEventListener('blur', () => setTimeout(() => this.hide(), 300));
                this.inputEl.addEventListener('focus', (e) => {
                    if (this.inputEl.value.length > 0) {
                        this.show();
                    }
                });
            }
        } catch (err) {
            console.error('Error initializing search:', err);
        }
    }

    onSearch(event) {
        const query = event.target.value.trim();
        
        if (query.length === 0) {
            this.hide();
            if (this.statusEl) {
                this.statusEl.textContent = '';
            }
            return;
        }
        
        const results = this.search(query);
        this.displayResults(results, query);
        
        if (results.length > 0) {
            this.show();
        } else {
            this.hide();
        }
    }

    /**
     * Perform fuzzy/substring search on the index.
     * Weights: exact matches > term matches > translation matches > definition matches
     */
    search(query) {
        const queryLower = query.toLowerCase();
        const maxResults = 20;
        const results = [];
        
        for (const entry of this.searchIndex) {
            const score = this.scoreMatch(entry, queryLower);
            if (score > 0) {
                results.push({ ...entry, score });
            }
        }
        
        // Sort by score (higher first) then by normalized_term
        results.sort((a, b) => {
            if (b.score !== a.score) {
                return b.score - a.score;
            }
            return a.normalized_term.localeCompare(b.normalized_term);
        });
        
        return results.slice(0, maxResults);
    }

    /**
     * Score a single entry match against the query.
     * Heuristic scoring based on what field matches.
     */
    scoreMatch(entry, queryLower) {
        let score = 0;
        
        // Exact match on normalized_term (highest priority)
        if (entry.normalized_term === queryLower) {
            score += 100;
        }
        // Starts with normalized_term (high priority)
        else if (entry.normalized_term.startsWith(queryLower)) {
            score += 50;
        }
        // Contains in normalized_term
        else if (entry.normalized_term.includes(queryLower)) {
            score += 30;
        }
        
        // Match in Pali term (case-insensitive)
        const termLower = entry.term.toLowerCase();
        if (termLower === queryLower) {
            score += 90;
        } else if (termLower.startsWith(queryLower)) {
            score += 40;
        } else if (termLower.includes(queryLower)) {
            score += 20;
        }
        
        // Match in preferred translation
        const transLower = entry.preferred_translation.toLowerCase();
        if (transLower === queryLower) {
            score += 70;
        } else if (transLower.startsWith(queryLower)) {
            score += 25;
        } else if (transLower.includes(queryLower)) {
            score += 10;
        }
        
        // Match in definition (low priority, but still counts)
        const defLower = entry.definition.toLowerCase();
        if (defLower.includes(queryLower)) {
            score += 5;
        }
        
        // Boost major entries slightly
        if (entry.entry_type === 'major') {
            score *= 1.1;
        }
        
        return score;
    }

    displayResults(results, query) {
        this.resultsEl.innerHTML = '';
        
        if (results.length === 0) {
            if (this.statusEl) {
                this.statusEl.textContent = `No results found for "${query}"`;
            }
            return;
        }
        
        // Create semantic <ul> wrapper
        const ul = document.createElement('ul');
        
        for (const result of results) {
            const li = document.createElement('li');
            li.className = 'search-result';
            
            // Build the link URL (normalized_term is already safe as a slug)
            const baseUrl = this.getBaseUrl();
            const resultUrl = `${baseUrl}term/${encodeURIComponent(result.normalized_term)}.html`;
            
            // Highlight query in term and translation (with HTML escaping)
            const highlightedTerm = this.highlightQuery(this.escapeHtml(result.term), query);
            const highlightedTrans = this.highlightQuery(this.escapeHtml(result.preferred_translation), query);
            
             li.innerHTML = `
                 <a href="${resultUrl}" class="search-result-link">
                     <span class="search-result-term" lang="pi">${highlightedTerm}</span>
                     <span class="search-result-trans">${highlightedTrans}</span>
                     <span class="search-result-badge">
                         <span class="badge badge-${this.escapeHtml(result.entry_type)}">${this.escapeHtml(result.entry_type)}</span>
                     </span>
                 </a>
             `;
            
            ul.appendChild(li);
        }
        
        this.resultsEl.appendChild(ul);
        
        // Update status message for live region
        if (this.statusEl) {
            this.statusEl.textContent = `${results.length} result${results.length === 1 ? '' : 's'} found for "${query}"`;
        }
    }

    /**
     * Escape HTML special characters to prevent injection
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Get the base URL for the site (uses relative path, no base URL needed)
     */
    getBaseUrl() {
        // All URLs in this site are relative per-page, so base URL is empty
        return '';
    }

    highlightQuery(text, query) {
        if (!text) return '';
        
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    show() {
        if (this.resultsEl) {
            this.resultsEl.classList.add('active');
        }
    }

    hide() {
        if (this.resultsEl) {
            this.resultsEl.classList.remove('active');
        }
    }
}

// Initialize search when DOM is ready (only if search elements are present)
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#search-input') && document.querySelector('#search-results')) {
        new PaliDictionarySearch();
    }
});
