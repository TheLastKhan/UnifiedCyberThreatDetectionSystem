
// ==================== SETTINGS MANAGEMENT ====================

async function loadSettings() {
    console.log('📋 Loading settings...');

    try {
        const response = await fetch('/api/settings');
        if (!response.ok) throw new Error('Failed to load settings');

        const settings = await response.json();
        console.log('✅ Settings loaded:', settings);

        // Apply settings to UI
        const darkModeToggle = document.getElementById('darkModeToggle');
        const thresholdSlider = document.getElementById('thresholdSlider');
        const thresholdValue = document.getElementById('thresholdValue');
        const autoReloadToggle = document.getElementById('autoReloadToggle');
        const highRiskToggle = document.getElementById('highRiskToggle');
        const dailyReportsToggle = document.getElementById('dailyReportsToggle');

        if (darkModeToggle) darkModeToggle.checked = settings.dark_mode === 'true';
        if (thresholdSlider && thresholdValue) {
            const thresholdFloat = parseFloat(settings.threshold || 0.50);
            thresholdSlider.value = Math.round(thresholdFloat * 100);
            thresholdValue.textContent = thresholdFloat.toFixed(2);
        }
        if (autoReloadToggle) autoReloadToggle.checked = settings.auto_reload === 'true';
        if (highRiskToggle) highRiskToggle.checked = settings.high_risk_alerts === 'true';
        if (dailyReportsToggle) dailyReportsToggle.checked = settings.daily_reports === 'true';

    } catch (error) {
        console.error('❌ Error loading settings:', error);
    }
}

async function saveSettings() {
    console.log('💾 Saving settings...');

    try {
        const settings = {
            dark_mode: document.getElementById('darkModeToggle')?.checked ? 'true' : 'false',
            threshold: (parseInt(document.getElementById('thresholdSlider')?.value || 50) / 100).toFixed(2),
            auto_reload: document.getElementById('autoReloadToggle')?.checked ? 'true' : 'false',
            high_risk_alerts: document.getElementById('highRiskToggle')?.checked ? 'true' : 'false',
            daily_reports: document.getElementById('dailyReportsToggle')?.checked ? 'true' : 'false'
        };

        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });

        if (!response.ok) throw new Error('Failed to save settings');

        const result = await response.json();
        console.log('✅ Settings saved successfully');
        alert('✅ Settings saved successfully!');

    } catch (error) {
        console.error('❌ Error saving settings:', error);
        alert('❌ Failed to save settings: ' + error.message);
    }
}

async function resetSettings() {
    if (!confirm('Reset all settings to default values?')) {
        return;
    }

    console.log('🔄 Resetting settings...');

    try {
        const defaultSettings = {
            dark_mode: 'false',
            threshold: '0.50',
            auto_reload: 'true',
            high_risk_alerts: 'true',
            daily_reports: 'true'
        };

        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(defaultSettings)
        });

        if (!response.ok) throw new Error('Failed to reset settings');

        // Reload settings to update UI
        await loadSettings();

        console.log('✅ Settings reset to defaults');
        alert('✅ Settings reset to defaults!');

    } catch (error) {
        console.error('❌ Error resetting settings:', error);
        alert('❌ Failed to reset settings: ' + error.message);
    }
}

// Threshold slider real-time update
document.addEventListener('DOMContentLoaded', () => {
    const thresholdSlider = document.getElementById('thresholdSlider');
    const thresholdValue = document.getElementById('thresholdValue');

    if (thresholdSlider && thresholdValue) {
        thresholdSlider.addEventListener('input', (e) => {
            thresholdValue.textContent = (e.target.value / 100).toFixed(2);
        });
    }

    // Load settings when Settings page is shown
    const settingsPage = document.getElementById('page-settings');
    if (settingsPage) {
        // Observe when settings page becomes visible
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.classList.contains('active')) {
                    loadSettings();
                }
            });
        });

        observer.observe(settingsPage, { attributes: true, attributeFilter: ['class'] });
    }
});
