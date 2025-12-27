// Dark/Light Mode Theme Toggle
// ==================================

class ThemeManager {
    constructor() {
        this.STORAGE_KEY = 'app-theme';
        this.SYSTEM_DARK = '(prefers-color-scheme: dark)';
        this.init();
    }

    /**
     * Initialize theme manager
     * - Detect saved preference
     * - Apply system preference if no saved preference
     * - Set up event listeners
     */
    init() {
        const savedTheme = this.getSavedTheme();

        // Determine theme - default to LIGHT if no saved preference
        let theme = savedTheme || 'light';

        // Apply theme
        this.setTheme(theme);

        // Listen for system preference changes
        window.matchMedia(this.SYSTEM_DARK).addEventListener('change', (e) => {
            if (!this.getSavedTheme()) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });

        console.log('✅ Theme manager initialized:', theme);
    }

    /**
     * Get saved theme from localStorage
     * @returns {string|null} 'light', 'dark', or null
     */
    getSavedTheme() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (saved === 'light' || saved === 'dark') {
            return saved;
        }
        return null;
    }

    /**
     * Check if system prefers dark mode
     * @returns {boolean}
     */
    prefersDarkMode() {
        return window.matchMedia(this.SYSTEM_DARK).matches;
    }

    /**
     * Get current theme
     * @returns {string} 'light' or 'dark'
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    /**
     * Set theme
     * @param {string} theme - 'light', 'dark', or 'auto'
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark' && theme !== 'auto') {
            console.warn('Invalid theme:', theme);
            return;
        }

        // Apply to HTML
        if (theme === 'auto') {
            document.documentElement.removeAttribute('data-theme');
            localStorage.removeItem(this.STORAGE_KEY);
        } else {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem(this.STORAGE_KEY, theme);
        }

        // Apply to body for compatibility
        document.body.classList.remove('light-mode', 'dark-mode');
        document.body.classList.add(theme === 'dark' ? 'dark-mode' : 'light-mode');

        // Trigger custom event
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme }
        }));

        console.log('🎨 Theme changed to:', theme);
    }

    /**
     * Toggle between light and dark
     */
    toggle() {
        const current = this.getCurrentTheme();
        const next = current === 'light' ? 'dark' : 'light';
        this.setTheme(next);
    }

    /**
     * Enable dark mode
     */
    enableDarkMode() {
        this.setTheme('dark');
    }

    /**
     * Enable light mode
     */
    enableLightMode() {
        this.setTheme('light');
    }

    /**
     * Reset to system preference
     */
    useSystemPreference() {
        this.setTheme('auto');
    }

    /**
     * Get all theme options
     * @returns {Object}
     */
    getThemeInfo() {
        return {
            current: this.getCurrentTheme(),
            saved: this.getSavedTheme(),
            systemPreference: this.prefersDarkMode() ? 'dark' : 'light',
            storageKey: this.STORAGE_KEY
        };
    }
}

// Create global instance
const themeManager = new ThemeManager();

// ============================================================================
// THEME TOGGLE BUTTON INTEGRATION
// ============================================================================

class ThemeToggleUI {
    constructor() {
        this.createToggleButton();
        this.attachEventListeners();
    }

    /**
     * Create theme toggle button in DOM
     */
    createToggleButton() {
        const button = document.createElement('button');
        button.id = 'theme-toggle-btn';
        button.className = 'theme-toggle';
        button.innerHTML = this.getButtonContent();
        button.setAttribute('aria-label', 'Toggle dark/light mode');
        button.setAttribute('title', 'Toggle dark/light mode');

        // Add to body if not already present
        if (!document.getElementById('theme-toggle-btn')) {
            document.body.insertBefore(button, document.body.firstChild);
        }
    }

    /**
     * Get button content based on current theme
     */
    getButtonContent() {
        const theme = themeManager.getCurrentTheme();
        if (theme === 'dark') {
            return '☀️ Light Mode'; // Sun icon + text
        } else {
            return '🌙 Dark Mode'; // Moon icon + text
        }
    }

    /**
     * Update button content
     */
    updateButtonContent() {
        const button = document.getElementById('theme-toggle-btn');
        if (button) {
            button.innerHTML = this.getButtonContent();
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const button = document.getElementById('theme-toggle-btn');
        if (button) {
            button.addEventListener('click', () => {
                themeManager.toggle();
                this.updateButtonContent();
            });
        }

        // Listen to theme changes
        window.addEventListener('themechange', (e) => {
            this.updateButtonContent();
        });
    }
}

// Initialize UI when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ThemeToggleUI();
});

// ============================================================================
// STORAGE SYNC - Sync theme across tabs
// ============================================================================

window.addEventListener('storage', (e) => {
    if (e.key === 'app-theme' && e.newValue !== e.oldValue) {
        themeManager.setTheme(e.newValue || 'light');
    }
});

// ============================================================================
// CHART THEME INTEGRATION (for Chart.js, etc)
// ============================================================================

/**
 * Get chart colors based on current theme
 * Usage: const colors = getChartColors();
 */
window.getChartColors = function () {
    const isDark = themeManager.getCurrentTheme() === 'dark';

    return {
        text: isDark ? '#e4e4e7' : '#212529',
        gridColor: isDark ? '#404040' : '#e9ecef',
        backgroundColor: isDark ? '#242424' : '#ffffff',
        borderColor: isDark ? '#404040' : '#dee2e6',

        // Chart line colors
        primary: '#0d6efd',
        danger: isDark ? '#ff6b6b' : '#dc3545',
        warning: isDark ? '#ffa940' : '#ffc107',
        success: isDark ? '#52c41a' : '#28a745',
        info: isDark ? '#13c2c2' : '#17a2b8',

        // Dataset colors
        datasets: [
            '#0d6efd',
            '#0dcaf0',
            '#fd7e14',
            '#20c997',
            '#6f42c1'
        ]
    };
};

// ============================================================================
// PREFERENCES DIALOG
// ============================================================================

/**
 * Show theme preferences dialog
 */
window.showThemePreferences = function () {
    const info = themeManager.getThemeInfo();

    const dialog = document.createElement('div');
    dialog.className = 'modal';
    dialog.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Theme Preferences</h2>
                <button class="close" onclick="this.parentElement.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="setting-group">
                    <label>Current Theme: <strong>${info.current.toUpperCase()}</strong></label>
                </div>
                <div class="setting-group">
                    <label>System Preference: <strong>${info.systemPreference.toUpperCase()}</strong></label>
                </div>
                <div class="setting-group">
                    <button onclick="themeManager.enableLightMode(); location.reload();">
                        ☀️ Light Mode
                    </button>
                </div>
                <div class="setting-group">
                    <button onclick="themeManager.enableDarkMode(); location.reload();">
                        🌙 Dark Mode
                    </button>
                </div>
                <div class="setting-group">
                    <button onclick="themeManager.useSystemPreference(); location.reload();">
                        🔄 Use System Preference
                    </button>
                </div>
            </div>
        </div>
    `;

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.appendChild(dialog);
    overlay.onclick = (e) => {
        if (e.target === overlay) overlay.remove();
    };

    document.body.appendChild(overlay);
};

// ============================================================================
// EXPORTS
// ============================================================================

// Make available globally if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        themeManager,
        ThemeManager,
        ThemeToggleUI,
        getChartColors: window.getChartColors,
        showThemePreferences: window.showThemePreferences
    };
}
