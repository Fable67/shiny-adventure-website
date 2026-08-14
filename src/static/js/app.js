/**
 * Main application script for the Pali Dictionary website.
 * Handles general interactivity and enhancements.
 */

(function() {
    'use strict';

    /**
     * Initialize the application
     */
    function init() {
        // Add smooth scrolling for anchor links (modern browsers already do this via CSS)
        setupAnchorLinks();
        
        // Setup dark mode toggle if needed
        setupDarkModeToggle();
        
        // Setup related term previews
        setupRelatedTermHovers();
    }

    /**
     * Handle smooth scrolling to anchor links
     */
    function setupAnchorLinks() {
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a[href^="#"]');
            if (!link) return;
            
            const target = document.querySelector(link.getAttribute('href'));
            if (target && !link.href.includes('javascript:')) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    /**
     * Setup dark mode toggle (optional enhancement)
     */
    function setupDarkModeToggle() {
        // Check if system prefers dark mode
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // We could add a toggle button, but for now, let CSS handle it via prefers-color-scheme
        // Future: could add a manual toggle button that sets a data attribute
    }

    /**
     * Setup hover previews for related terms (if desired in future)
     */
    function setupRelatedTermHovers() {
        // This could load and display related term information on hover
        // For now, just direct linking is sufficient
    }



    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
