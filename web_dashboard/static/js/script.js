// ==================== DASHBOARD INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function () {
    initializeDashboard();
    setupCharts();
    setupEventListeners();
    loadSettings();  // Load saved settings
    loadModelsStatus();
    loadDashboardData();  // Load real-time dashboard data
});

function initializeDashboard() {
    console.log('🚀 Initializing CyberGuard Dashboard...');

    // Load theme preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        document.getElementById('themeToggle').innerHTML = '<i class="fas fa-sun"></i>';
    }
}

// ==================== NAVIGATION ====================

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();
        const pageName = this.dataset.page;
        showPage(pageName);
    });
});

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    const page = document.getElementById(`page-${pageName}`);
    if (page) {
        page.classList.add('active');
    }

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });

    // Update page title
    const pageTitleMap = {
        'dashboard': 'Dashboard',
        'email-analysis': 'Email Analysis',
        'web-analysis': 'Web Analysis',
        'correlation-analysis': 'Correlation Analysis',
        'model-comparison': 'Model Comparison',
        'reports': 'Reports',
        'settings': 'Settings'
    };
    const pageTitleEl = document.getElementById('page-title-text');
    if (pageTitleEl) {
        pageTitleEl.textContent = pageTitleMap[pageName] || pageName;
    }

    // Load page-specific data
    if (pageName === 'reports') {
        loadReportsData();
    } else if (pageName === 'correlation-analysis') {
        loadCorrelationAnalysis();
    } else if (pageName === 'model-comparison') {
        loadModelComparison();
    }
}

// ==================== THEME TOGGLE ====================

document.getElementById('themeToggle').addEventListener('click', async function () {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);

    this.innerHTML = isDarkMode ?
        '<i class="fas fa-sun"></i>' :
        '<i class="fas fa-moon"></i>';

    // Also sync to darkModeToggle checkbox in settings
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.checked = isDarkMode;
    }

    // SAVE TO API for persistence across browser restarts
    try {
        await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ dark_mode: isDarkMode ? 'true' : 'false' })
        });
        console.log('🎨 Theme saved to API:', isDarkMode ? 'dark' : 'light');
    } catch (error) {
        console.warn('Could not save theme to API:', error);
    }
});

// ==================== LANGUAGE TOGGLE ====================

// Language translations
const translations = {
    tr: {
        'Dashboard': 'Ana Sayfa',
        'Email Analysis': 'E-posta Analizi',
        'Web Analysis': 'Web Analizi',
        'Reports': 'Raporlar',
        'Settings': 'Ayarlar',
        'Model Comparison': 'Model Karşılaştırma',
        'Correlation Analysis': 'Korelasyon Analizi',
        'System Status': 'Sistem Durumu',
        'Email Detection': 'E-posta Tespiti',
        'Web Anomaly Detection': 'Web Anomali Tespiti',
        'Total Threats': 'Toplam Tehditler',
        'Predictions': 'Tahminler',
        'All Time': 'Tüm Zamanlar',
        'analyzed': 'analiz edildi',
        'phishing detected': 'phishing tespit edildi',
        'anomalies detected': 'anomali tespit edildi',
        'Clear History': 'Geçmişi Temizle',
        'System Active': 'Sistem Aktif',
        'System Degraded': 'Sistem Sorunlu',
        'Email Subject': 'E-posta Konusu',
        'From Address': 'Gönderen Adresi',
        'Email Body': 'E-posta İçeriği',
        'Analyze Email': 'E-postayı Analiz Et',
        'Clear': 'Temizle',
        'Analysis Result': 'Analiz Sonucu',
        'Prediction': 'Tahmin',
        'Confidence': 'Güven',
        'Risk Level': 'Risk Seviyesi',
        'Source IP': 'Kaynak IP',
        'HTTP Method': 'HTTP Metodu',
        'Request Path': 'İstek Yolu',
        'HTTP Status': 'HTTP Durumu',
        'User Agent': 'Kullanıcı Aracısı',
        'Analyze Log': 'Logu Analiz Et',
        'Threat Distribution': 'Tehdit Dağılımı',
        'Model Performance': 'Model Performansı',
        'Recent Alerts': 'Son Uyarılar',
        'System Settings': 'Sistem Ayarları',
        'Display Settings': 'Görünüm Ayarları',
        'Dark Mode': 'Karanlık Mod',
        'Language': 'Dil',
        'Model Settings': 'Model Ayarları',
        'Email Detection Threshold': 'E-posta Tespit Eşiği',
        'Auto-reload Models': 'Modelleri Otomatik Yükle',
        'Notifications': 'Bildirimler',
        'High Risk Alerts': 'Yüksek Risk Uyarıları',
        'Daily Reports': 'Günlük Raporlar',
        'Save Settings': 'Ayarları Kaydet',
        'Reset to Default': 'Varsayılana Sıfırla'
    },
    en: {
        'Ana Sayfa': 'Dashboard',
        'E-posta Analizi': 'Email Analysis',
        'Web Analizi': 'Web Analysis',
        'Raporlar': 'Reports',
        'Ayarlar': 'Settings',
        'Model Karşılaştırma': 'Model Comparison',
        'Korelasyon Analizi': 'Correlation Analysis',
        'Sistem Durumu': 'System Status',
        'E-posta Tespiti': 'Email Detection',
        'Web Anomali Tespiti': 'Web Anomaly Detection',
        'Toplam Tehditler': 'Total Threats',
        'Tahminler': 'Predictions',
        'Tüm Zamanlar': 'All Time',
        'analiz edildi': 'analyzed',
        'phishing tespit edildi': 'phishing detected',
        'anomali tespit edildi': 'anomalies detected',
        'Geçmişi Temizle': 'Clear History',
        'Sistem Aktif': 'System Active',
        'Sistem Sorunlu': 'System Degraded',
        'E-posta Konusu': 'Email Subject',
        'Gönderen Adresi': 'From Address',
        'E-posta İçeriği': 'Email Body',
        'E-postayı Analiz Et': 'Analyze Email',
        'Temizle': 'Clear',
        'Analiz Sonucu': 'Analysis Result',
        'Tahmin': 'Prediction',
        'Güven': 'Confidence',
        'Risk Seviyesi': 'Risk Level',
        'Kaynak IP': 'Source IP',
        'HTTP Metodu': 'HTTP Method',
        'İstek Yolu': 'Request Path',
        'HTTP Durumu': 'HTTP Status',
        'Kullanıcı Aracısı': 'User Agent',
        'Logu Analiz Et': 'Analyze Log',
        'Tehdit Dağılımı': 'Threat Distribution',
        'Model Performansı': 'Model Performance',
        'Son Uyarılar': 'Recent Alerts',
        'Sistem Ayarları': 'System Settings',
        'Görünüm Ayarları': 'Display Settings',
        'Karanlık Mod': 'Dark Mode',
        'Dil': 'Language',
        'Model Ayarları': 'Model Settings',
        'E-posta Tespit Eşiği': 'Email Detection Threshold',
        'Modelleri Otomatik Yükle': 'Auto-reload Models',
        'Bildirimler': 'Notifications',
        'Yüksek Risk Uyarıları': 'High Risk Alerts',
        'Günlük Raporlar': 'Daily Reports',
        'Ayarları Kaydet': 'Save Settings',
        'Varsayılana Sıfırla': 'Reset to Default'
    }
};

let currentLang = localStorage.getItem('language') || 'en';

document.getElementById('langToggle')?.addEventListener('click', function () {
    // Toggle language
    currentLang = currentLang === 'en' ? 'tr' : 'en';
    localStorage.setItem('language', currentLang);

    // Update button text
    this.innerHTML = `<span>${currentLang.toUpperCase()}</span>`;

    // Update settings checkbox if it exists
    const languageToggle = document.getElementById('languageToggle');
    if (languageToggle) {
        languageToggle.checked = (currentLang === 'tr');
    }

    // Translate page content
    translatePage(currentLang);
});

function translatePage(lang) {
    const trans = translations[lang];
    if (!trans) return;

    // Translate navigation items
    document.querySelectorAll('.nav-item span').forEach(el => {
        const text = el.textContent.trim();
        if (trans[text]) {
            el.textContent = trans[text];
        }
    });

    // Translate h3 headings (dashboard cards, charts)
    document.querySelectorAll('h3').forEach(el => {
        const text = el.textContent.trim();
        if (trans[text]) {
            el.textContent = trans[text];
        }
    });

    // Translate labels
    document.querySelectorAll('label').forEach(el => {
        const text = el.textContent.trim();
        if (trans[text]) {
            el.textContent = trans[text];
        }
    });

    // Translate buttons (including icons)
    document.querySelectorAll('button').forEach(el => {
        // Extract text without icons
        const textNode = Array.from(el.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
        if (textNode) {
            const text = textNode.textContent.trim();
            if (trans[text]) {
                textNode.textContent = ' ' + trans[text];
            }
        }
    });

    // Translate metric labels
    document.querySelectorAll('.metric-label').forEach(el => {
        const text = el.textContent.trim();
        if (trans[text]) {
            el.textContent = trans[text];
        }
    });

    // Translate system status
    const statusEl = document.getElementById('system-status');
    if (statusEl && trans[statusEl.textContent]) {
        statusEl.textContent = trans[statusEl.textContent];
    }

    // Translate page title
    const pageTitleEl = document.getElementById('page-title-text');
    if (pageTitleEl && trans[pageTitleEl.textContent]) {
        pageTitleEl.textContent = trans[pageTitleEl.textContent];
    }

    console.log(` Language changed to: ${lang.toUpperCase()}`);
}

// Initialize language on load
if (currentLang === 'tr') {
    const langBtn = document.getElementById('langToggle');
    if (langBtn) langBtn.innerHTML = '<span>TR</span>';
    translatePage('tr');
}

// ==================== CHARTS ====================

let threatChart, performanceChart;

function setupCharts() {
    // Threat Distribution Chart
    const threatCtx = document.getElementById('threatChart')?.getContext('2d');
    if (threatCtx) {
        threatChart = new Chart(threatCtx, {
            type: 'doughnut',
            data: {
                labels: ['Phishing', 'Spam', 'Normal', 'Malware'],
                datasets: [{
                    data: [35, 20, 40, 5],
                    backgroundColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#10b981',
                        '#6366f1'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Model Performance Chart
    const perfCtx = document.getElementById('performanceChart')?.getContext('2d');
    if (perfCtx) {
        performanceChart = new Chart(perfCtx, {
            type: 'bar',
            data: {
                labels: ['Stacking\nEnsemble', 'Voting\nEnsemble', 'Random\nForest'],
                datasets: [
                    {
                        label: 'Accuracy',
                        data: [89.6, 88.48, 85.82],
                        backgroundColor: '#6366f1',
                        borderRadius: 8
                    },
                    {
                        label: 'F1-Score',
                        data: [86.18, 84.28, 78.59],
                        backgroundColor: '#8b5cf6',
                        borderRadius: 8
                    },
                    {
                        label: 'ROC-AUC',
                        data: [96.65, 96.39, 95.48],
                        backgroundColor: '#10b981',
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}
function displayModelError(modelType, errorMessage) {
    // Set badge to show model unavailable
    const badge = document.getElementById(`${modelType}ResultBadge`);
    badge.textContent = '⚠️ MODEL NOT LOADED';
    badge.style.color = '#f39c12';
    badge.style.fontWeight = 'bold';
    badge.style.padding = '8px 16px';
    badge.style.borderRadius = '20px';
    badge.style.background = '#fef3cd';

    // Set all fields to N/A
    document.getElementById(`${modelType}Prediction`).textContent = 'Model Not Available';
    document.getElementById(`${modelType}Prediction`).style.color = '#7f8c8d';

    document.getElementById(`${modelType}Confidence`).textContent = 'N/A';
    document.getElementById(`${modelType}Confidence`).style.color = '#95a5a6';

    document.getElementById(`${modelType}Risk`).textContent = 'N/A';
    document.getElementById(`${modelType}Risk`).style.color = '#95a5a6';

    document.getElementById(`${modelType}Time`).textContent = 'N/A';
    document.getElementById(`${modelType}Time`).style.color = '#95a5a6';

    // Display error message in indicators
    const indicatorsDiv = document.getElementById(`${modelType}Indicators`);
    indicatorsDiv.innerHTML = `
        <div style="text-align: center; padding: 30px; color: #7f8c8d; background: #f8f9fa; border-radius: 8px;">
            <i class="fas fa-exclamation-circle" style="font-size: 32px; margin-bottom: 15px; color: #f39c12;"></i>
            <p style="margin: 0; font-weight: bold; font-size: 14px; color: #2c3e50;">Model Not Loaded</p>
            <p style="margin: 10px 0 0 0; font-style: italic; font-size: 12px; color: #7f8c8d;">${errorMessage || 'Please train this model first'}</p>
        </div>
    `;
}
// ==================== EMAIL ANALYSIS ====================

document.getElementById('analyzeEmailBtn')?.addEventListener('click', analyzeEmail);
document.getElementById('clearEmailBtn')?.addEventListener('click', clearEmailForm);

async function analyzeEmail() {
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;
    const from = document.getElementById('emailSender').value;  // Updated ID
    const senderIP = document.getElementById('senderIP').value;  // NEW: Get sender IP

    if (!body) {
        alert('Please enter email body');
        return;
    }

    // Show loading indicator
    document.getElementById('emailLoading').style.display = 'block';
    document.getElementById('emailResults').style.display = 'none';

    try {
        // Call ensemble API for weighted voting and get details for all models
        const requestBody = {
            email_subject: subject,
            email_content: body,
            email_sender: from,
            sender_ip: senderIP
        };

        // Call single ensemble endpoint (saves 1 record to DB)
        const response = await fetch('/api/email/analyze/ensemble', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Analysis failed');
        }

        const data = await response.json();

        // Extract model results from unified response
        const bertResult = data.models?.bert || { error: 'BERT unavailable' };
        const fasttextResult = data.models?.fasttext || { error: 'FastText unavailable' };
        const tfidfResult = data.models?.tfidf || { error: 'TF-IDF unavailable' };
        const ensembleResult = data.ensemble || {};

        // Extract keywords for indicators
        const keywords = extractSuspiciousKeywords(body, subject);

        // Display all three models + Ensemble in dashboard
        // Note: passing ensembleResult can be used to update a main status card if needed
        displayEmailResults({
            bert: bertResult,
            fasttext: fasttextResult,
            tfidf: tfidfResult,
            keywords: keywords,
            ensemble: ensembleResult // Pass ensemble result too
        });

        document.getElementById('emailLoading').style.display = 'none';
    } catch (error) {
        console.error('Error analyzing email:', error);
        document.getElementById('emailLoading').style.display = 'none';
        alert('Error analyzing email. Check console for details.');
    }
}

function extractSuspiciousKeywords(body, subject) {
    const text = `${subject} ${body}`.toLowerCase();
    const keywords = [];

    // Phishing keywords database
    const phishingPatterns = [
        { keyword: 'urgent', reason: 'Creates false sense of urgency', severity: 'high' },
        { keyword: 'verify', reason: 'Common phishing tactic', severity: 'medium' },
        { keyword: 'suspended', reason: 'Account threat language', severity: 'high' },
        { keyword: 'click here', reason: 'Suspicious call-to-action', severity: 'medium' },
        { keyword: 'account', reason: 'Account-related threat', severity: 'medium' },
        { keyword: 'password', reason: 'Credential harvesting attempt', severity: 'high' },
        { keyword: 'confirm', reason: 'Verification phishing', severity: 'medium' },
        { keyword: 'update', reason: 'Fake update request', severity: 'low' },
        { keyword: 'security', reason: 'Impersonating security', severity: 'medium' },
        { keyword: 'expire', reason: 'Expiration threat', severity: 'medium' },
        { keyword: 'limited', reason: 'Account limitation threat', severity: 'high' },
        { keyword: 'alert', reason: 'Fake security alert', severity: 'medium' },
        { keyword: 'immediately', reason: 'Urgency pressure tactic', severity: 'high' },
        { keyword: 'act now', reason: 'Pressure to act quickly', severity: 'high' },
        { keyword: 'congratulations', reason: 'Prize/lottery scam', severity: 'medium' },
        { keyword: 'winner', reason: 'Fake prize notification', severity: 'medium' },
        { keyword: 'claim', reason: 'Prize claim scam', severity: 'medium' },
        { keyword: 'paypal', reason: 'Brand impersonation', severity: 'high' },
        { keyword: 'bank', reason: 'Banking impersonation', severity: 'high' },
        { keyword: 'ssn', reason: 'Social security harvesting', severity: 'critical' },
        { keyword: 'credit card', reason: 'Financial credential theft', severity: 'critical' },
        { keyword: 'cvv', reason: 'Credit card security code theft', severity: 'critical' },
        { keyword: 'pin', reason: 'PIN number harvesting', severity: 'critical' }
    ];

    phishingPatterns.forEach(pattern => {
        if (text.includes(pattern.keyword)) {
            keywords.push(pattern);
        }
    });

    // Check for suspicious URLs
    const urlPattern = /http[s]?:\/\/[^\s]+/g;
    const urls = text.match(urlPattern);
    if (urls && urls.length > 0) {
        urls.forEach(url => {
            if (!url.includes('https://') || url.includes('bit.ly') || url.includes('.ru') || url.includes('verify') || url.includes('secure')) {
                keywords.push({
                    keyword: url.substring(0, 50) + '...',
                    reason: 'Suspicious or malicious URL',
                    severity: 'critical'
                });
            }
        });
    }

    return keywords;
}

function displayEmailResults(results) {
    const resultsDiv = document.getElementById('emailResults');

    // Display Ensemble Result (Highlighted!)
    if (results.ensemble) {
        displayEnsembleResult(results.ensemble);
    }

    // Display BERT results
    displayModelResult('bert', results.bert, results.keywords);

    // Normalize FastText confidence to be between BERT and TF-IDF
    if (results.fasttext && results.bert && results.tfidf) {
        // Get PHISHING SCORES (not confidence) for risk level calculation
        // For legitimate predictions, phishing_score should be low
        let bertPhishingScore = results.bert.phishing_score || results.bert.score || 0;
        let tfidfPhishingScore = results.tfidf.model_confidence?.phishing_probability ||
            results.tfidf.phishing_score ||
            results.tfidf.score || 0;

        // Get confidence values for display
        let bertConf = results.bert.confidence || 0;
        let tfidfConf = results.tfidf.model_confidence?.confidence || results.tfidf.confidence || 0;

        console.log('BERT phishing_score:', bertPhishingScore, 'confidence:', bertConf);
        console.log('TF-IDF phishing_score:', tfidfPhishingScore, 'confidence:', tfidfConf);
        console.log('FastText original score:', results.fasttext.score, 'confidence:', results.fasttext.confidence);

        // Normalize to 0-1 range if values are > 1 (percentage format)
        if (bertPhishingScore > 1) bertPhishingScore = bertPhishingScore / 100;
        if (tfidfPhishingScore > 1) tfidfPhishingScore = tfidfPhishingScore / 100;
        if (bertConf > 1) bertConf = bertConf / 100;
        if (tfidfConf > 1) tfidfConf = tfidfConf / 100;

        // For RISK LEVEL: use phishing scores (how likely to be phishing)
        const normalizedPhishingScore = (bertPhishingScore + tfidfPhishingScore) / 2;

        // For CONFIDENCE: use confidence values  
        const normalizedConf = (bertConf + tfidfConf) / 2;

        console.log('Normalized phishing_score for risk:', normalizedPhishingScore, `(${(normalizedPhishingScore * 100).toFixed(1)}%)`);
        console.log('Normalized confidence:', normalizedConf, `(${(normalizedConf * 100).toFixed(1)}%)`);

        // Create adjusted FastText result with normalized values


        // --- FASTTEXT LIME SYNTHESIS (AVERAGING LOGIC) ---
        // Create a map to aggregate scores from BERT and TF-IDF
        const featureScores = new Map();

        // Helper to add scores
        const addScores = (breakdown) => {
            if (!breakdown) return;
            breakdown.forEach(item => {
                const word = (item.feature || item.word || '').toLowerCase();
                if (!word) return;

                // Get the raw contribution value
                let val = item.score !== undefined ? item.score : (item.contribution !== undefined ? item.contribution : 0);

                if (!featureScores.has(word)) {
                    featureScores.set(word, { total: 0, count: 0 });
                }
                const entry = featureScores.get(word);
                entry.total += val;
                entry.count += 1;
            });
        };

        // Add both BERT and TF-IDF scores
        addScores(results.bert?.lime_breakdown);
        addScores(results.tfidf?.lime_breakdown);

        // Create synthetic breakdown list
        const syntheticBreakdown = [];
        featureScores.forEach((data, word) => {
            // Calculate average: (BERT + TFIDF) / 2
            // Always divide by 2 to penalize words not found by both models (middle ground effect)
            const avgScore = data.total / 2;

            // Push to new list
            syntheticBreakdown.push({
                feature: word,
                score: avgScore,
                contribution: avgScore,
                type: 'derived'
            });
        });

        // Sort by magnitude
        syntheticBreakdown.sort((a, b) => Math.abs(b.score) - Math.abs(a.score));

        // Take top features
        const topSynthetic = syntheticBreakdown.slice(0, 10);



        const adjustedFasttext = {
            ...results.fasttext,
            confidence: normalizedConf,  // How confident the model is
            score: normalizedPhishingScore,  // PHISHING SCORE for risk percentage
            phishing_score: normalizedPhishingScore,
            risk_level: normalizedPhishingScore >= 0.9 ? 'critical' : normalizedPhishingScore >= 0.7 ? 'high' : normalizedPhishingScore >= 0.5 ? 'medium' : 'low',
            original_confidence: results.fasttext.confidence,
            original_score: results.fasttext.score,
            lime_breakdown: topSynthetic // Use the synthesized average list
        };

        displayModelResult('fasttext', adjustedFasttext, results.keywords);
    } else {
        // Fallback if normalization not possible
        displayModelResult('fasttext', results.fasttext, results.keywords);
    }

    // Display TF-IDF results
    displayModelResult('tfidf', results.tfidf, results.keywords);


    // Note: displayModelResult now handles LIME breakdown rendering internally


    // Check VirusTotal reputation for email domain
    const emailFrom = document.getElementById('emailSender').value;  // Fixed ID
    if (emailFrom) {
        checkEmailDomainReputation(emailFrom);
    }

    resultsDiv.style.display = 'block';
}




function toTitleCase(str) {
    if (!str) return '';
    return str.replace(/\w\S*/g, function (txt) {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

function displayEnsembleResult(ensemble) {
    const card = document.getElementById('ensembleCard');
    if (!card || !ensemble) return;

    const prediction = ensemble.prediction || 'unknown';
    const confidence = ensemble.confidence || 0;
    const riskLevel = ensemble.risk_level || 'unknown';
    const modelsUsed = ensemble.models_used || [];
    const weightsApplied = ensemble.weights_applied || {};

    const isPhishing = prediction.toLowerCase() === 'phishing';
    const colorClass = isPhishing ? 'text-danger' : 'text-success';

    // Show card apply styling
    card.style.display = 'block';
    if (!card.classList.contains('model-card')) {
        card.classList.add('model-card');
    }

    // Update prediction badge (Target Theme: uppercase)
    const badge = document.getElementById('ensembleResultBadge');
    badge.textContent = isPhishing ? 'PHISHING' : 'LEGITIMATE';
    badge.className = 'result-badge ' + (isPhishing ? 'badge-danger' : 'badge-success');

    // Update metrics with Capitalization and Colors
    const predElem = document.getElementById('ensemblePrediction');
    predElem.textContent = toTitleCase(prediction);
    predElem.className = `metric-value ${colorClass}`;
    predElem.style.fontWeight = 'bold';

    const confElem = document.getElementById('ensembleConfidence');
    confElem.textContent = (confidence * 100).toFixed(1) + '%';
    confElem.className = `metric-value ${colorClass}`;
    confElem.style.fontWeight = 'bold';

    // Risk Level with percentage - dark red for phishing
    const riskElem = document.getElementById('ensembleRiskLevel');
    const riskText = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);

    // Invert percentage for Legitimate (Safe) results
    // If Legitimate with 99% confidence -> Risk is 1%
    // If Phishing with 99% confidence -> Risk is 99%
    let displayRiskPercent = confidence * 100;
    if (!isPhishing) {
        displayRiskPercent = 100 - displayRiskPercent;
        if (displayRiskPercent < 0) displayRiskPercent = 0; // Floating point safety
    }

    riskElem.textContent = `${riskText} (${displayRiskPercent.toFixed(1)}%)`;
    riskElem.style.color = isPhishing ? '#c0392b' : '#27ae60'; // Dark red or green
    riskElem.style.fontWeight = 'bold';

    // Models used - same color as Risk Level
    const modelsUsedElem = document.getElementById('ensembleModelsUsed');
    const formattedModels = modelsUsed.map(m => {
        if (m.toLowerCase() === 'tfidf') return 'TF-IDF';
        if (m.toLowerCase() === 'bert') return 'Bert';
        if (m.toLowerCase() === 'fasttext') return 'FastText';
        return toTitleCase(m);
    }).join(', ');
    modelsUsedElem.textContent = formattedModels;
    modelsUsedElem.style.color = isPhishing ? '#c0392b' : '#27ae60';

    // Update weights display - BOLD as requested
    const weightsText = Object.entries(weightsApplied)
        .map(([model, weight]) => {
            let modelName = model;
            if (model.toLowerCase() === 'tfidf') modelName = 'TF-IDF';
            else if (model.toLowerCase() === 'bert') modelName = 'Bert';
            else if (model.toLowerCase() === 'fasttext') modelName = 'FastText';
            else modelName = toTitleCase(model);

            return `${modelName} ${(weight * 100).toFixed(0)}%`;
        })
        .join(', ');
    const weightsElem = document.getElementById('ensembleWeights');
    weightsElem.textContent = weightsText || 'Bert 50%, FastText 30%, TF-IDF 20%';
    weightsElem.style.fontWeight = 'bold';
}

function displayModelResult(modelType, result, keywords) {
    const sectionId = modelType === 'bert' ? 'bert' : (modelType === 'fasttext' ? 'fasttext' : 'tfidf');

    let isPhishing = false;
    let confidence = 0;
    let score = 0;
    let riskLevel = 'unknown';
    let processingTime = 0;
    let limeBreakdown = [];

    // Parse result based on model type
    if (modelType === 'bert') {
        isPhishing = result.prediction === 'phishing';
        confidence = result.confidence || 0;
        score = result.score || 0;
        riskLevel = result.risk_level || 'unknown';
        processingTime = result.processing_time_ms;
        limeBreakdown = result.lime_breakdown || [];
    } else if (modelType === 'fasttext') {
        isPhishing = result.prediction === 'phishing';
        confidence = result.confidence || 0;
        score = result.score || 0;
        riskLevel = result.risk_level || 'unknown';
        processingTime = result.processing_time_ms;
        limeBreakdown = result.lime_breakdown || [];
    } else if (modelType === 'tfidf') {
        const tfidfData = result.model_confidence || result;
        isPhishing = (tfidfData.prediction === 'phishing');
        confidence = tfidfData.confidence || tfidfData.phishing_probability || 0;
        score = tfidfData.phishing_probability || 0;
        riskLevel = tfidfData.risk_level || 'unknown';
        processingTime = result.processing_time_ms || result.time_ms;
        limeBreakdown = tfidfData.lime_breakdown || [];
    }

    // Fix for processing time
    processingTime = processingTime || result.time_ms;

    // Title Case Prediction
    const predText = isPhishing ? 'Phishing' : 'Legitimate';

    // Set badge (Target Theme: uppercase, no emoji)
    const badge = document.getElementById(`${modelType}ResultBadge`);
    if (badge) {
        badge.textContent = isPhishing ? 'PHISHING' : 'LEGITIMATE';
        badge.className = 'result-badge ' + (isPhishing ? 'badge-danger' : 'badge-success');
    }


    // Update metrics with colors as per user request (reverting to "old" style)
    const colorClass = isPhishing ? 'text-danger' : 'text-success';

    // Prediction Metric
    const predElem = document.getElementById(`${modelType}Prediction`);
    if (predElem) {
        predElem.textContent = predText;
        predElem.className = `metric-value ${colorClass}`;
        predElem.style.fontWeight = 'bold';
    }

    // Confidence Metric
    const confElem = document.getElementById(`${modelType}Confidence`);
    if (confElem) {
        confElem.textContent = (confidence * 100).toFixed(1) + '%';
        confElem.className = `metric-value ${colorClass}`;
        confElem.style.fontWeight = 'bold';
    }

    // Risk Level Metric - Format: "Critical (XX.X%)" with dark red
    const riskElem = document.getElementById(`${modelType}Risk`);
    if (riskElem) {
        const riskText = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);

        // Invert percentage for Legitimate (Safe) results
        let displayRiskPercent = confidence * 100;
        if (!isPhishing) {
            displayRiskPercent = 100 - displayRiskPercent;
            if (displayRiskPercent < 0) displayRiskPercent = 0;
        }

        riskElem.textContent = `${riskText} (${displayRiskPercent.toFixed(1)}%)`;
        riskElem.style.color = isPhishing ? '#c0392b' : '#27ae60'; // Dark red or green
        riskElem.style.fontWeight = 'bold';
    }

    // Processing Time - same color as Risk Level
    const timeElem = document.getElementById(`${modelType}Time`);
    if (timeElem) {
        timeElem.textContent = processingTime ? `${processingTime.toFixed(1)}ms` : 'N/A';
        timeElem.style.color = isPhishing ? '#c0392b' : '#27ae60';
        timeElem.style.fontWeight = 'bold';
    }

    // Display Key Indicators (using passed keywords or generating them)
    // Assuming displayKeyIndicators function exists and takes (elementId, keywords)
    const indicatorsId = `${modelType}Indicators`;
    if (document.getElementById(indicatorsId)) {
        // If we have LIME breakdown, we can use it to highlight specific words
        // But for now, let's stick to the keyword extraction logic as fallback
        if (keywords && keywords.length > 0) {
            // Reuse existing keyword display logic if available
            // (Assuming 'displayKeyIndicators' function exists in file)
            displayKeyIndicators(indicatorsId, keywords);
        } else {
            document.getElementById(indicatorsId).innerHTML = '<span class="text-muted">No specific indicators found</span>';
        }
    }

    // Display LIME Breakdown if available
    const limeSectionId = modelType === 'tfidf' ? 'tfidfLimeBreakdown' : `${modelType}LimeBreakdownSection`;
    const limeContentId = modelType === 'tfidf' ? 'tfidfLimeContent' : `${modelType}LimeBreakdown`;

    if (limeBreakdown && limeBreakdown.length > 0) {
        const section = document.getElementById(limeSectionId);
        if (section) section.style.display = 'block';
        renderLimeBreakdown(limeContentId, limeBreakdown);
    } else {
        const section = document.getElementById(limeSectionId);
        if (section) section.style.display = 'none';
    }
}

function renderLimeBreakdown(containerId, breakdown) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!breakdown || breakdown.length === 0) {
        container.innerHTML = '<div class="text-muted">No feature importance data available</div>';
        return;
    }

    // Use original lime_breakdown.css classes
    // Phishing keyword descriptions
    // Phishing keyword descriptions - Comprehensive Map
    const keywordDescriptions = {
        // Urgency & Time
        'urgent': 'Urgency pressure tactic',
        'immediately': 'Urgency pressure tactic',
        'now': 'Temporal urgency',
        'today': 'Temporal urgency',
        'tomorrow': 'Temporal urgency',
        'date': 'Phishing indicator', // From screenshot
        'december': 'Temporal urgency', // From screenshot
        'january': 'Temporal urgency',
        'february': 'Temporal urgency',
        'march': 'Temporal urgency',
        'april': 'Temporal urgency',
        'may': 'Temporal urgency',
        'june': 'Temporal urgency',
        'july': 'Temporal urgency',
        'august': 'Temporal urgency',
        'september': 'Temporal urgency',
        'october': 'Temporal urgency',
        'november': 'Temporal urgency',
        'expire': 'Expiration threat',
        'time': 'Temporal urgency',

        // Account & Security
        'verify': 'Account verification request',
        'account': 'Account threat', // From screenshot
        'password': 'Credential harvesting',
        'login': 'Credential harvesting',
        'security': 'Fake alert', // From screenshot
        'suspend': 'Account suspension threat',
        'locked': 'Account threat',
        'unauthorized': 'Fake alert',
        'confirm': 'Confirmation scam',
        'access': 'Account threat',
        'update': 'Fake update request',

        // Personal Targeting
        'your': 'Personal targeting', // From screenshot
        'you': 'Personal targeting',
        'dear': 'Generic greeting',
        'customer': 'Generic greeting',
        'user': 'Generic greeting',
        'name': 'Phishing indicator', // From screenshot

        // Financial
        'funds': 'Financial loss', // From screenshot
        'financial': 'Financial phishing',
        'bank': 'Financial phishing',
        'credit': 'Financial phishing',
        'money': 'Financial lure',
        'transfer': 'Wire transfer scam',
        'payment': 'Financial phishing',
        'invoice': 'Financial lure',
        'winner': 'Prize scam',
        'lottery': 'Lottery scam',
        'free': 'Too good to be true',
        'offer': 'Too good to be true',

        // Technical & Common
        'http': 'Suspicious URL',
        'https': 'Suspicious URL',
        'com': 'Common word',
        'net': 'Common word',
        'org': 'Common word',
        'html': 'Technical term',
        'click': 'Click bait tactic',
        'link': 'Suspicious link',
        'here': 'Click bait tactic',
        'email': 'Communication channel',
        'message': 'Communication channel',
        'been': 'Phishing indicator',
        'full': 'Phishing indicator',
        'following': 'Phishing indicator',

        // Expanded List
        'action': 'Urgency pressure tactic',
        'required': 'Urgency pressure tactic',
        'attention': 'Urgency pressure tactic',
        'warning': 'Urgency pressure tactic',
        'notice': 'Urgency pressure tactic',
        'alert': 'Fake security alert',
        'blocked': 'Account threat',
        'restricted': 'Account threat',
        'suspended': 'Account threat',
        'terminated': 'Account threat',
        'disabled': 'Account threat',
        'device': 'Security context',
        'unusual': 'Security context',
        'signin': 'Credential harvesting',
        'sign-in': 'Credential harvesting',
        'validation': 'Credential harvesting',
        'identity': 'Credential harvesting',
        'billing': 'Financial context',
        'invoice': 'Financial lure',
        'receipt': 'Financial lure',
        'payment': 'Financial lure',
        'transaction': 'Financial context',
        'refund': 'Financial lure',
        'cost': 'Financial lure',
        'amount': 'Financial context',
        'due': 'Financial pressure',
        'balance': 'Financial context',
        'statement': 'Financial context',
        'service': 'Service impersonation',
        'support': 'Service impersonation',
        'team': 'Service impersonation',
        'admin': 'Service impersonation',
        'department': 'Service impersonation',
        'policy': 'Authority lure',
        'terms': 'Authority lure',
        'contract': 'Authority lure',
        'document': 'Malicious attachment risk',
        'file': 'Malicious attachment risk',
        'attachment': 'Malicious attachment risk',
        'pdf': 'Malicious attachment risk',
        'doc': 'Malicious attachment risk',
        'docx': 'Malicious attachment risk',
        'xls': 'Malicious attachment risk',
        'zip': 'Malicious attachment risk',
        'open': 'Action request',
        'review': 'Action request',
        'check': 'Action request',
        'read': 'Action request',
        'download': 'Action request',
        'contact': 'Action request',
        'reply': 'Action request',
        'help': 'Assistance lure',
        'problem': 'Assistance lure',
        'error': 'Technical lure',
        'failed': 'Technical lure',
        'failure': 'Technical lure',
        'browser': 'Technical context',
        'system': 'Technical context',
        'server': 'Technical context',
        'information': 'Data gathering',
        'details': 'Data gathering',
        'address': 'Data gathering',
        'phone': 'Data gathering',
        'mobile': 'Data gathering'
    };

    let html = '<div class="lime-breakdown-container">';

    // Sort by absolute score (importance)
    const sortedFeatures = [...breakdown].sort((a, b) => {
        const scoreA = Math.abs(a.score !== undefined ? a.score : (a.contribution !== undefined ? a.contribution : 0));
        const scoreB = Math.abs(b.score !== undefined ? b.score : (b.contribution !== undefined ? b.contribution : 0));
        return scoreB - scoreA;
    });

    // Max score for width calculation  
    const maxScore = Math.max(...sortedFeatures.map(f => Math.abs(f.score !== undefined ? f.score : (f.contribution !== undefined ? f.contribution : 0)))) || 1;

    // Show top 5 features using original CSS classes
    sortedFeatures.slice(0, 5).forEach(feature => {
        const rawScore = feature.score !== undefined ? feature.score : (feature.contribution !== undefined ? feature.contribution : 0);
        const contribution = feature.contribution !== undefined ? feature.contribution : Math.abs(rawScore);

        // Use contribution value directly as percentage (capped at 100)
        const percentage = Math.min(Math.abs(contribution), 100);

        // Positive = contributes to phishing (risk), Negative = contributes to legitimate (safe)
        const fillClass = rawScore > 0 ? 'positive' : 'negative';

        // Feature name - capitalize first letter (Title Case)
        let featureName = feature.feature || feature.word || 'Unknown';
        const featureLower = featureName.toLowerCase();
        // Convert entire string to lowercase first, then capitalize first char
        featureName = featureLower.charAt(0).toUpperCase() + featureLower.slice(1);

        // Get description from dictionary - default for unknown keywords
        const description = keywordDescriptions[featureLower.toLowerCase()] || 'Phishing indicator';
        const riskReason = `<span class="risk-reason">(${description})</span>`;

        html += `
            <div class="lime-feature-bar">
                <div class="lime-feature-label">
                    <span class="lime-feature-name">${featureName}${riskReason}</span>
                    <span class="lime-feature-value">${percentage.toFixed(1)}%</span>
                </div>
                <div class="lime-progress-track">
                    <div class="lime-progress-fill ${fillClass}" style="width: ${percentage}%;"></div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

function displayKeyIndicators(elementId, keywords) {
    const indicatorsDiv = document.getElementById(elementId);
    if (!indicatorsDiv) return;

    indicatorsDiv.innerHTML = '';

    if (keywords && keywords.length > 0) {
        // Sort by severity
        const severityOrder = { 'critical': 0, 'high': 1, 'medium': 2, 'low': 3 };
        keywords.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);

        keywords.slice(0, 5).forEach(kw => {
            const item = document.createElement('div');
            item.className = 'indicator-item';
            item.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <div class="indicator-content">
                    <div class="indicator-keyword">"${kw.keyword}"</div>
                    <div class="indicator-reason">${kw.reason} (${kw.severity} severity)</div>
                </div>
            `;
            indicatorsDiv.appendChild(item);
        });
    } else {
        indicatorsDiv.innerHTML = '<div class="no-indicators">No suspicious patterns detected</div>';
    }
}

function clearEmailForm() {
    document.getElementById('emailSubject').value = '';
    document.getElementById('emailBody').value = '';
    document.getElementById('emailFrom').value = '';
    document.getElementById('emailResults').style.display = 'none';
}

// ==================== WEB LOG ANALYSIS ====================

document.getElementById('analyzeLogBtn')?.addEventListener('click', analyzeWebLog);
document.getElementById('clearLogBtn')?.addEventListener('click', clearWebForm);

async function analyzeWebLog() {
    const ip = document.getElementById('logIP').value;
    const method = document.getElementById('logMethod').value;
    const path = document.getElementById('logPath').value;
    const status = document.getElementById('logStatus').value;
    const size = document.getElementById('logSize').value;  // Added
    const agent = document.getElementById('logAgent').value;

    if (!ip || !path) {
        alert('Please enter IP and path');
        return;
    }

    try {
        const response = await fetch('/api/web/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ip: ip,
                method: method,
                path: path,
                status: status,
                size: size,  // Added
                user_agent: agent
            })
        });

        const result = await response.json();
        displayWebResults(result);
    } catch (error) {
        console.error('Error analyzing log:', error);
        alert('Error analyzing log. Check console for details.');
    }
}

function displayWebResults(result) {
    const resultsDiv = document.getElementById('webResults');

    if (result.model_analysis) {
        const isAnomaly = result.model_analysis.is_anomalous;
        const scorePercent = result.model_analysis.anomaly_score_percent || (result.model_analysis.anomaly_score * 100);
        const requestFreq = result.model_analysis.request_frequency || 0;

        const webBadge = document.getElementById('webResultBadge');
        webBadge.textContent = isAnomaly ? 'ANOMALY DETECTED' : 'NORMAL';
        // Use standard classes to match VirusTotal style (Square-ish + Gradient)
        webBadge.className = isAnomaly ? 'result-badge badge-warning' : 'result-badge badge-success';

        // Remove ALL inline overrides to allow CSS to take effect
        webBadge.style = '';

        document.getElementById('webStatus').textContent =
            isAnomaly ? 'Anomalous' : 'Normal';

        // Show percentage score (0-100) instead of decimal
        document.getElementById('webAnomalyScore').textContent =
            scorePercent.toFixed(2) + '%';

        // Add patterns and frequency info inside the Analysis Result card
        let additionalInfo = '';
        if (result.model_analysis.patterns_detected && result.model_analysis.patterns_detected.length > 0) {
            additionalInfo += `<p style="margin: 8px 0;"><strong>Patterns:</strong> ${result.model_analysis.patterns_detected.join(', ')}</p>`;
        }
        if (requestFreq > 0) {
            additionalInfo += `<p style="margin: 8px 0;"><strong>Request Frequency:</strong> ${requestFreq} requests from this IP (last 7 days)</p>`;
        }

        const infoSection = document.getElementById('webAdditionalInfo');
        const infoContent = document.getElementById('webAdditionalInfoContent');
        if (additionalInfo && infoSection && infoContent) {
            infoContent.innerHTML = additionalInfo;
            infoSection.style.display = 'block';
        } else if (infoSection) {
            infoSection.style.display = 'none';
        }

        // Check VirusTotal reputation for IP
        const ip = document.getElementById('logIP').value;
        if (ip) {
            checkIPReputation(ip);
        }
    }

    resultsDiv.style.display = 'block';
}

function clearWebForm() {
    document.getElementById('logIP').value = '';
    document.getElementById('logPath').value = '';
    document.getElementById('logStatus').value = '';
    document.getElementById('logAgent').value = '';
    document.getElementById('webResults').style.display = 'none';
}

// ==================== MODEL STATUS ====================

async function loadModelsStatus() {
    try {
        const response = await fetch('/api/models/status');
        const status = await response.json();

        console.log('📊 Models Status:', status);
        updateSystemStatus(status);
    } catch (error) {
        console.error('Error loading model status:', error);
    }
}

function updateSystemStatus(status) {
    const statusElement = document.getElementById('system-status');
    const statusDot = document.querySelector('.status-dot');

    // Check if elements exist
    if (!statusElement || !statusDot) {
        // console.warn('System status elements not found');
        return;
    }

    const allLoaded = Object.values(status).every(v => v === true);

    if (allLoaded) {
        statusElement.textContent = '✅ System Active (All Models Loaded)';
        statusDot.style.background = '#10b981';
    } else {
        statusElement.textContent = '⚠️ Some Models Missing';
        statusDot.style.background = '#f59e0b';
    }
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Settings slider
    const thresholdSlider = document.getElementById('thresholdSlider');
    if (thresholdSlider) {
        thresholdSlider.addEventListener('input', function () {
            const value = (this.value / 100).toFixed(2);
            document.getElementById('thresholdValue').textContent = value;
        });
    }

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function () {
            toggleTheme();
        });
    }
}

// ==================== UTILITY FUNCTIONS ====================

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ==================== DASHBOARD REAL-TIME DATA ====================

// Flag to track if this is the initial load
let isInitialDashboardLoad = true;

async function loadDashboardData() {
    console.log('📊 Loading real-time dashboard data...');

    try {
        // On initial load, load everything including alerts
        if (isInitialDashboardLoad) {
            await Promise.all([
                loadDashboardStats(),
                loadDashboardAlerts(),
                loadDashboardCharts()
            ]);
            isInitialDashboardLoad = false;
        } else {
            // On auto-refresh, skip alerts to preserve lazy loaded state
            await Promise.all([
                loadDashboardStats(),
                loadDashboardCharts()
            ]);
        }

        console.log('✅ Dashboard data loaded successfully');

        // Auto-refresh every 5 seconds (but skip alerts)
        setTimeout(loadDashboardData, 5000);

    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        // Retry after 10 seconds on error
        setTimeout(loadDashboardData, 10000);
    }
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) throw new Error('Failed to load stats');

        const data = await response.json();
        console.log('📈 Stats loaded:', data);

        // Update System Status
        const systemCard = document.querySelector('.metric-card:nth-child(1)');
        if (systemCard) {
            const statusBadge = systemCard.querySelector('.status-badge');
            const metricValue = systemCard.querySelector('.metric-value');

            statusBadge.textContent = data.system_status.operational === 100 ? 'Active' : 'Degraded';
            statusBadge.className = `status-badge ${data.system_status.operational === 100 ? 'healthy' : 'warning'}`;
            metricValue.textContent = `${data.system_status.operational}%`;

            // Update status indicators
            const statusDetails = systemCard.querySelectorAll('.metric-details span');
            if (statusDetails.length >= 2) {
                statusDetails[0].innerHTML = data.system_status.models_loaded ?
                    '<i class="fas fa-check"></i> All models loaded' :
                    '<i class="fas fa-times"></i> Models loading...';
                statusDetails[1].innerHTML = data.system_status.api_responding ?
                    '<i class="fas fa-check"></i> API responding' :
                    '<i class="fas fa-times"></i> API error';
            }
        }

        // Update Email Detection
        const emailCard = document.querySelector('.metric-card:nth-child(2)');
        if (emailCard) {
            // Update prediction count
            const emailCountEl = document.getElementById('emailPredictionsCount');
            const emailAnalyzedEl = document.getElementById('emailAnalyzedCount');
            const emailPhishingEl = document.getElementById('emailPhishingCount');

            if (emailCountEl) emailCountEl.textContent = data.email_detection.total_predictions || 0;
            if (emailAnalyzedEl) emailAnalyzedEl.textContent = data.email_detection.total_predictions || 0;
            if (emailPhishingEl) emailPhishingEl.textContent = data.email_detection.phishing_detected || 0;
        }

        // Update Web Anomaly Detection
        const webCard = document.querySelector('.metric-card:nth-child(3)');
        if (webCard) {
            // Update prediction count
            const webCountEl = document.getElementById('webPredictionsCount');
            const webAnalyzedEl = document.getElementById('webAnalyzedCount');
            const webAnomaliesEl = document.getElementById('webAnomaliesCount');

            if (webCountEl) webCountEl.textContent = data.web_analysis.total_predictions || 0;
            if (webAnalyzedEl) webAnalyzedEl.textContent = data.web_analysis.total_predictions || 0;
            if (webAnomaliesEl) webAnomaliesEl.textContent = data.web_analysis.anomalies_detected || 0;
        }

        // Update Total Threats (all time, not just 24h)
        const threatsCard = document.querySelector('.metric-card:nth-child(4)');
        if (threatsCard) {
            const totalPhishing = data.email_detection.phishing_detected || 0;
            const totalAnomalies = data.web_analysis.anomalies_detected || 0;
            const totalThreats = totalPhishing + totalAnomalies;

            // Update all elements
            const totalCountBadge = document.getElementById('totalThreatsCount');
            const totalValueEl = document.getElementById('totalThreatsValue');
            const totalPhishingEl = document.getElementById('totalPhishingCount');
            const totalAnomaliesEl = document.getElementById('totalAnomaliesCount');

            if (totalCountBadge) {
                totalCountBadge.textContent = totalThreats;
                totalCountBadge.className = totalThreats > 0 ? 'status-badge warning' : 'status-badge';
            }
            if (totalValueEl) totalValueEl.textContent = totalThreats;
            if (totalPhishingEl) totalPhishingEl.textContent = totalPhishing;
            if (totalAnomaliesEl) totalAnomaliesEl.textContent = totalAnomalies;
        }

        // Update system status indicator in header
        const systemStatus = document.getElementById('system-status');
        if (systemStatus) {
            systemStatus.textContent = data.system_status.operational === 100 ? 'System Active' : 'System Degraded';
        }

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

async function loadDashboardAlerts() {
    try {
        const response = await fetch('/api/dashboard/alerts?limit=50');
        if (!response.ok) throw new Error('Failed to load alerts');

        const data = await response.json();
        console.log('🚨 Alerts loaded:', data);

        const alertsList = document.querySelector('.alerts-list');
        if (!alertsList || !data.alerts || data.alerts.length === 0) {
            if (alertsList) {
                alertsList.innerHTML = '<div class="alert-item" style="text-align: center; padding: 20px;"><p>No recent alerts</p></div>';
            }
            return;
        }

        // Store all alerts for lazy loading
        window.allAlerts = data.alerts;
        window.alertsOffset = 0;
        window.alertsPerPage = 10;
        window.alertsLoading = false;

        // Clear existing alerts
        alertsList.innerHTML = '';

        // Load initial batch
        loadMoreAlerts();

        // Setup infinite scroll on window (page scroll)
        if (!window.alertsScrollListenerAdded) {
            window.addEventListener('scroll', handleWindowScrollForAlerts);
            window.alertsScrollListenerAdded = true;
        }

    } catch (error) {
        console.error('Error loading dashboard alerts:', error);
    }
}

// Handle window scroll for lazy loading alerts
function handleWindowScrollForAlerts() {
    // Check if we're on dashboard page
    const alertsList = document.querySelector('.alerts-list');
    if (!alertsList) return;

    // Calculate if user scrolled near the bottom of the page
    const scrollTop = window.scrollY;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;

    // If scrolled within 200px of bottom, load more
    if (documentHeight - scrollTop - windowHeight < 200) {
        loadMoreAlerts();
    }
}

// Load more alerts (lazy loading)
function loadMoreAlerts() {
    if (window.alertsLoading) return;
    if (!window.allAlerts || window.alertsOffset >= window.allAlerts.length) {
        return;
    }

    window.alertsLoading = true;
    const alertsList = document.querySelector('.alerts-list');
    if (!alertsList) return;

    // Remove loading indicator if exists
    const loadingIndicator = alertsList.querySelector('.alerts-loading');
    if (loadingIndicator) loadingIndicator.remove();

    // Get next batch
    const nextBatch = window.allAlerts.slice(
        window.alertsOffset,
        window.alertsOffset + window.alertsPerPage
    );

    // Add alerts
    nextBatch.forEach(alert => {
        const alertLevel = alert.severity || 'medium';
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item alert-${alertLevel}`;

        const iconMap = {
            high: 'fas fa-exclamation-circle',
            medium: 'fas fa-warning',
            low: 'fas fa-info-circle'
        };

        alertItem.innerHTML = `
            <div class="alert-icon">
                <i class="${iconMap[alertLevel] || 'fas fa-warning'}"></i>
            </div>
            <div class="alert-content">
                <div class="alert-title">
                    ${alert.title}
                    ${alert.severity_badge ? `<span class="severity-badge severity-${alertLevel}">${alert.severity_badge}</span>` : ''}
                </div>
                <div class="alert-description">${alert.description}</div>
                <div class="alert-time">${alert.time_ago}</div>
            </div>
            ${alert.confidence ? `<div class="alert-confidence">${alert.confidence}%</div>` : ''}
        `;

        alertsList.appendChild(alertItem);
    });

    window.alertsOffset += nextBatch.length;
    window.alertsLoading = false;

    console.log(`📋 Loaded ${window.alertsOffset}/${window.allAlerts.length} alerts`);
}


async function loadDashboardCharts() {
    try {
        const response = await fetch('/api/dashboard/charts');
        if (!response.ok) throw new Error('Failed to load charts');

        const data = await response.json();
        console.log('📊 Charts data loaded:', data);

        // Update Threat Distribution Chart
        if (threatChart && data.threat_distribution) {
            if (data.threat_distribution.labels.length > 0) {
                // Update chart with real data from database
                threatChart.data.labels = data.threat_distribution.labels.map(l =>
                    l.charAt(0).toUpperCase() + l.slice(1)
                );
                threatChart.data.datasets[0].data = data.threat_distribution.data;
                threatChart.update();
            } else {
                // Clear chart when database is empty (e.g., after clearing history)
                threatChart.data.labels = ['No Data'];
                threatChart.data.datasets[0].data = [1];
                threatChart.data.datasets[0].backgroundColor = ['#e5e7eb']; // Gray color
                threatChart.update();
                console.log('ℹ️ Chart cleared - no data in database');
            }
        }

        // Update Model Performance Chart (keep static training metrics)
        // Charts already have accurate training data, no need to change

    } catch (error) {
        console.error('Error loading dashboard charts:', error);
    }
}

// ==================== GENERATE DEMO DATA ====================

async function generateDemoData() {
    if (!confirm('Generate realistic test data?\n\nThis will create:\n• 25 email predictions (5 per severity level)\n• 25 web log predictions (5 per severity level)\n\nContinue?')) {
        return;
    }

    // Disable button and show loading state
    const btn = document.getElementById('generateDemoBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

    try {
        const response = await fetch('/api/demo/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email_count: 25,
                web_count: 25,
                days_back: 30
            })
        });

        if (!response.ok) throw new Error('Failed to generate demo data');

        const result = await response.json();

        // Show success message
        alert(`✅ Demo data generated successfully!

Created:
• ${result.generated.emails} email predictions
• ${result.generated.web_logs} web log predictions
• ${result.generated.coordinated_attacks || 5} coordinated attack scenarios
• Total: ${result.generated.total} records

Dashboard will refresh automatically.`);

        // Small delay to ensure database is fully updated before refresh
        await new Promise(resolve => setTimeout(resolve, 500));

        // Reload dashboard data
        await loadDashboardData();

    } catch (error) {
        console.error('Error generating demo data:', error);
        alert('❌ Failed to generate demo data: ' + error.message);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// ==================== CLEAR PREDICTION HISTORY ====================

async function clearPredictionHistory() {
    if (!confirm('Are you sure you want to clear all prediction history? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/api/database/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error('Failed to clear history');

        const result = await response.json();
        alert(`✅ History cleared successfully!\n\nDeleted:\n- ${result.email_deleted} email predictions\n- ${result.web_deleted} web predictions`);

        // Reload dashboard data
        await loadDashboardData();

    } catch (error) {
        console.error('Error clearing history:', error);
        alert('❌ Failed to clear history: ' + error.message);
    }
}

// ==================== SETTINGS MANAGEMENT ====================

function loadSettings() {
    console.log('⚙️ Loading settings from localStorage...');

    // Load dark mode setting
    const darkMode = localStorage.getItem('darkMode') === 'true';
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.checked = darkMode;
    }

    // Load threshold setting
    const threshold = parseFloat(localStorage.getItem('emailThreshold') || '0.50');
    const thresholdSlider = document.getElementById('thresholdSlider');
    const thresholdValue = document.getElementById('thresholdValue');
    if (thresholdSlider && thresholdValue) {
        thresholdSlider.value = threshold * 100;
        thresholdValue.textContent = threshold.toFixed(2);
    }

    // Load auto-reload setting
    const autoReload = localStorage.getItem('autoReloadModels') !== 'false';
    const autoReloadToggle = document.getElementById('autoReloadToggle');
    if (autoReloadToggle) {
        autoReloadToggle.checked = autoReload;
    }

    // Load notification settings
    const highRisk = localStorage.getItem('highRiskAlerts') !== 'false';
    const dailyReports = localStorage.getItem('dailyReports') !== 'false';
    const highRiskToggle = document.getElementById('highRiskToggle');
    const dailyReportsToggle = document.getElementById('dailyReportsToggle');
    if (highRiskToggle) highRiskToggle.checked = highRisk;
    if (dailyReportsToggle) dailyReportsToggle.checked = dailyReports;

    console.log('✅ Settings loaded:', { darkMode, threshold, autoReload, highRisk, dailyReports });
}

function saveSettings() {
    console.log('💾 Saving settings...');

    try {
        // Save dark mode
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            localStorage.setItem('darkMode', darkModeToggle.checked);
        }

        // Save threshold
        const thresholdSlider = document.getElementById('thresholdSlider');
        if (thresholdSlider) {
            const threshold = (thresholdSlider.value / 100).toFixed(2);
            localStorage.setItem('emailThreshold', threshold);
        }

        // Save auto-reload
        const autoReloadToggle = document.getElementById('autoReloadToggle');
        if (autoReloadToggle) {
            localStorage.setItem('autoReloadModels', autoReloadToggle.checked);
        }

        // Save notifications
        const highRiskToggle = document.getElementById('highRiskToggle');
        const dailyReportsToggle = document.getElementById('dailyReportsToggle');
        if (highRiskToggle) {
            localStorage.setItem('highRiskAlerts', highRiskToggle.checked);
        }
        if (dailyReportsToggle) {
            localStorage.setItem('dailyReports', dailyReportsToggle.checked);
        }

        alert('✅ Settings saved successfully!');
        console.log('✅ Settings saved to localStorage');

    } catch (error) {
        console.error('Error saving settings:', error);
        alert('❌ Failed to save settings: ' + error.message);
    }
}

function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to default?')) {
        return;
    }

    console.log('🔄 Resetting settings to default...');

    // Clear all settings from localStorage
    localStorage.removeItem('darkMode');
    localStorage.removeItem('emailThreshold');
    localStorage.removeItem('autoReloadModels');
    localStorage.removeItem('highRiskAlerts');
    localStorage.removeItem('dailyReports');

    // Reset to defaults
    const darkModeToggle = document.getElementById('darkModeToggle');
    const thresholdSlider = document.getElementById('thresholdSlider');
    const thresholdValue = document.getElementById('thresholdValue');
    const autoReloadToggle = document.getElementById('autoReloadToggle');
    const highRiskToggle = document.getElementById('highRiskToggle');
    const dailyReportsToggle = document.getElementById('dailyReportsToggle');

    if (darkModeToggle) darkModeToggle.checked = false;
    if (thresholdSlider) thresholdSlider.value = 50;
    if (thresholdValue) thresholdValue.textContent = '0.50';
    if (autoReloadToggle) autoReloadToggle.checked = true;
    if (highRiskToggle) highRiskToggle.checked = true;
    if (dailyReportsToggle) dailyReportsToggle.checked = true;

    // Apply dark mode reset
    if (document.body.classList.contains('dark-mode')) {
        toggleTheme();
    }

    alert('✅ Settings reset to default!');
    console.log('✅ Settings reset completed');
}

// ==================== EXPORT / IMPORT FUNCTIONS ====================

async function exportToExcel() {
    console.log('📊 Exporting to Excel...');

    try {
        const response = await fetch('/api/reports/export/excel', {
            method: 'GET'
        });

        if (!response.ok) throw new Error('Failed to export Excel');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threat_report_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        console.log('✅ Excel export completed');
        alert('✅ Excel file downloaded successfully!');

    } catch (error) {
        console.error('Error exporting to Excel:', error);
        alert('❌ Failed to export Excel: ' + error.message);
    }
}

async function exportToPDF() {
    console.log('📄 Exporting to PDF...');

    try {
        const response = await fetch('/api/reports/export/pdf', {
            method: 'GET'
        });

        if (!response.ok) throw new Error('Failed to export PDF');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threat_report_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        console.log('✅ PDF export completed');
        alert('✅ PDF file downloaded successfully!');

    } catch (error) {
        console.error('Error exporting to PDF:', error);
        alert('❌ Failed to export PDF: ' + error.message);
    }
}

async function exportToJSON() {
    console.log('💾 Exporting to JSON...');

    try {
        const response = await fetch('/api/reports/export/json', {
            method: 'GET'
        });

        if (!response.ok) throw new Error('Failed to export JSON');

        const data = await response.json();
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threat_report_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        console.log('✅ JSON export completed');
        alert('✅ JSON file downloaded successfully!');

    } catch (error) {
        console.error('Error exporting to JSON:', error);
        alert('❌ Failed to export JSON: ' + error.message);
    }
}

async function importFromExcel(event) {
    console.log('📊 Importing from Excel...');

    const file = event.target.files[0];
    if (!file) return;

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/reports/import/excel', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Failed to import Excel');

        const result = await response.json();
        alert(`✅ Excel import completed!\n\nImported:\n- ${result.email_count || 0} email predictions\n- ${result.web_count || 0} web predictions`);

        // Reload dashboard
        await loadDashboardData();

        console.log('✅ Excel import completed');

    } catch (error) {
        console.error('Error importing from Excel:', error);
        alert('❌ Failed to import Excel: ' + error.message);
    }

    // Reset input
    event.target.value = '';
}

async function importFromJSON(event) {
    console.log('💾 Importing from JSON...');

    const file = event.target.files[0];
    if (!file) return;

    try {
        const text = await file.text();
        const data = JSON.parse(text);

        const response = await fetch('/api/reports/import/json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Failed to import JSON');

        const result = await response.json();
        alert(`✅ JSON import completed!\n\nImported:\n- ${result.email_count || 0} email predictions\n- ${result.web_count || 0} web predictions`);

        // Reload dashboard
        await loadDashboardData();

        console.log('✅ JSON import completed');

    } catch (error) {
        console.error('Error importing from JSON:', error);
        alert('❌ Failed to import JSON: ' + error.message);
    }

    // Reset input
    event.target.value = '';
}

// ==================== LOAD REPORTS DATA ====================

async function loadReportsData() {
    console.log('📊 Loading reports data...');

    try {
        const response = await fetch('/api/reports/summary');
        const data = await response.json();

        // Update summary metrics
        document.getElementById('reportTotalBadge').textContent = data.total_threats || 0;
        document.getElementById('reportTotalThreats').textContent = data.total_threats || 0;
        document.getElementById('reportPhishing').textContent = data.phishing_count || 0;
        document.getElementById('reportAnomalies').textContent = data.anomalies_count || 0;

        document.getElementById('reportDetectionRate').textContent =
            (data.avg_confidence * 100).toFixed(1) + '%' || '0%';
        document.getElementById('reportCritical').textContent = data.critical_count || 0;
        document.getElementById('reportHigh').textContent = data.high_count || 0;

        // Update detection badge
        const detectionBadge = document.getElementById('reportDetectionBadge');
        const avgConf = data.avg_confidence || 0;
        if (avgConf >= 0.9) {
            detectionBadge.className = 'status-badge success';
            detectionBadge.textContent = 'High';
        } else if (avgConf >= 0.7) {
            detectionBadge.className = 'status-badge warning';
            detectionBadge.textContent = 'Medium';
        } else {
            detectionBadge.className = 'status-badge danger';
            detectionBadge.textContent = 'Low';
        }

        // Load recent predictions list
        if (data.recent_predictions && data.recent_predictions.length > 0) {
            const listEl = document.getElementById('reportPredictionsList');
            listEl.innerHTML = data.recent_predictions.map(pred => {
                // Calculate score percentage - web logs need *100, emails already 0-1
                const scorePercent = pred.type === 'web'
                    ? (pred.confidence || pred.anomaly_score || 0) * 100
                    : (pred.confidence || 0) * 100;

                // Determine badge color based on risk level
                let badgeClass = 'success'; // default green (low/normal)
                if (pred.risk_level === 'critical') badgeClass = 'danger';
                else if (pred.risk_level === 'high') badgeClass = 'warning';
                else if (pred.risk_level === 'medium') badgeClass = 'warning'; // Using warning for medium too
                // Low uses default 'success' (green)

                return `
                <div style="padding: 1rem; border-bottom: 1px solid var(--border-color);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>${pred.type === 'email' ? '📧 Email' : '🌐 Web'}</strong>
                            <span style="color: var(--text-secondary); margin-left: 1rem;">
                                ${new Date(pred.timestamp).toLocaleString()}
                            </span>
                        </div>
                        <span class="status-badge ${badgeClass}">
                            ${scorePercent.toFixed(1)}%
                        </span>
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--text-secondary);">
                        ${pred.details || 'No details available'}
                    </div>
                </div>
            `}).join('');
        }

        console.log('✅ Reports data loaded');

    } catch (error) {
        console.error('Error loading reports data:', error);
    }
}

// ==================== CORRELATION ANALYSIS ====================

// Global chart instances
let correlationTimelineChart = null;
let emailWebScatterChart = null;

async function loadCorrelationAnalysis() {
    console.log('📊 Loading correlation analysis...');

    try {
        const response = await fetch('/api/correlation/analyze');
        const data = await response.json();

        // Update correlation score
        document.getElementById('correlationScore').textContent = data.correlation_score.toFixed(2);
        document.getElementById('correlationStrength').textContent = data.correlation_strength;

        // Update correlation status badge
        const statusBadge = document.getElementById('correlationStatusBadge');
        if (Math.abs(data.correlation_score) >= 0.7) {
            statusBadge.className = 'status-badge danger';
            statusBadge.textContent = 'High';
        } else if (Math.abs(data.correlation_score) >= 0.4) {
            statusBadge.className = 'status-badge warning';
            statusBadge.textContent = 'Medium';
        } else {
            statusBadge.className = 'status-badge success';
            statusBadge.textContent = 'Low';
        }

        // Update coordinated attacks
        document.getElementById('coordinatedAttacksBadge').textContent = data.coordinated_attacks;
        document.getElementById('coordinatedAttacksCount').textContent = data.coordinated_attacks;

        // ===== IP-BASED COORDINATION =====
        if (data.coordinated_ips && data.coordinated_ips.length > 0) {
            console.log(`🎯 IP-Based Coordination detected: ${data.coordinated_ips.length} IPs`);
            console.log('Coordinated IPs:', data.coordinated_ips);

            // Update correlation strength badge if IP coordination detected
            const ipBoost = data.ip_correlation_boost || 0;
            if (ipBoost > 0) {
                statusBadge.textContent += ` (+${ipBoost.toFixed(2)} IP boost)`;
            }
        }

        if (data.coordinated_events && data.coordinated_events.length > 0) {
            const lastEvent = data.coordinated_events[data.coordinated_events.length - 1];
            const eventTime = new Date(lastEvent.timestamp).toLocaleString();
            document.getElementById('lastCoordinatedAttack').textContent = eventTime;
        }

        // Display correlated events list with IP info
        if (data.coordinated_events && data.coordinated_events.length > 0) {
            const listEl = document.getElementById('correlatedEventsList');
            listEl.innerHTML = data.coordinated_events.map(event => `
                <div style="padding: 1rem; border-bottom: 1px solid var(--border-color);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>${new Date(event.timestamp).toLocaleString()}</strong>
                        <span class="status-badge warning">${event.total} threats</span>
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--text-secondary);">
                        📧 ${event.email_threats} email threats | 🌐 ${event.web_threats} web threats
                    </div>
                </div>
            `).join('');
        }

        // ===== NEW: Display IP-Based Coordinated Attacks =====
        if (data.coordinated_ips && data.coordinated_ips.length > 0) {
            const listEl = document.getElementById('correlatedEventsList');
            const ipSection = `
                <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 2px solid var(--border-color);">
                    <h4 style="margin-bottom: 1rem; color: var(--danger);">
                        <i class="fas fa-network-wired"></i> IP-Based Coordinated Attacks
                    </h4>
                    ${data.coordinated_ips.map(ip => `
                        <div style="padding: 1rem; margin-bottom: 0.5rem; background: rgba(239, 68, 68, 0.1); border-left: 3px solid var(--danger); border-radius: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong style="font-family: monospace; color: var(--danger);">${ip.ip}</strong>
                                <span class="status-badge danger">${ip.total_threats} total</span>
                            </div>
                            <div style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.9rem;">
                                📧 ${ip.email_threats} phishing emails | 🌐 ${ip.web_threats} web attacks
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            listEl.innerHTML += ipSection;
        }

        // ===== CHART 1: Timeline Chart =====
        if (data.timeline_data && data.timeline_data.length > 0) {
            const ctx = document.getElementById('correlationTimelineChart');
            if (ctx) {
                // Destroy existing chart
                if (correlationTimelineChart) {
                    correlationTimelineChart.destroy();
                }

                const labels = data.timeline_data.map(t => new Date(t.hour).toLocaleDateString());
                const emailData = data.timeline_data.map(t => t.email);
                const webData = data.timeline_data.map(t => t.web);

                correlationTimelineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Email Threats',
                                data: emailData,
                                borderColor: '#ef4444',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                tension: 0.4,
                                fill: true
                            },
                            {
                                label: 'Web Threats',
                                data: webData,
                                borderColor: '#3b82f6',
                                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                                tension: 0.4,
                                fill: true
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 4,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: false }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { precision: 0 }
                            }
                        }
                    }
                });
            }
        }

        // ===== CHART 2: Bar Chart (Email vs Web Side by Side) =====
        if (data.timeline_data && data.timeline_data.length > 0) {
            const ctx2 = document.getElementById('emailWebScatterChart');
            if (ctx2) {
                // Destroy existing chart
                if (emailWebScatterChart) {
                    emailWebScatterChart.destroy();
                }

                // Take last 10 data points for readability
                const recentData = data.timeline_data.slice(-10);
                const labels = recentData.map(t => new Date(t.hour).toLocaleDateString());
                const emailData = recentData.map(t => t.email);
                const webData = recentData.map(t => t.web);

                emailWebScatterChart = new Chart(ctx2, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Email Threats',
                                data: emailData,
                                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                                borderColor: '#ef4444',
                                borderWidth: 1
                            },
                            {
                                label: 'Web Threats',
                                data: webData,
                                backgroundColor: 'rgba(59, 130, 246, 0.8)',
                                borderColor: '#3b82f6',
                                borderWidth: 1
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 2.5,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: false },
                            tooltip: {
                                callbacks: {
                                    footer: function (context) {
                                        const index = context[0].dataIndex;
                                        const email = emailData[index];
                                        const web = webData[index];
                                        if (email >= 2 && web >= 2) {
                                            return '⚠️ Coordinated Attack!';
                                        }
                                        return '';
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { precision: 0 },
                                title: { display: true, text: 'Number of Threats' }
                            },
                            x: {
                                title: { display: true, text: 'Date' }
                            }
                        }
                    }
                });
            }
        }

        // ===== HEATMAP (Simple Text-Based) =====
        const heatmapEl = document.getElementById('correlationHeatmap');
        if (heatmapEl) {
            const score = data.correlation_score;
            const strength = data.correlation_strength;

            // Create visual heatmap representation
            const getColor = (val) => {
                const absVal = Math.abs(val);
                if (absVal >= 0.7) return '#ef4444'; // Strong - Red
                if (absVal >= 0.4) return '#f59e0b'; // Medium - Orange
                return '#10b981'; // Weak - Green
            };

            heatmapEl.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 64px; font-weight: bold; color: ${getColor(score)}; margin-bottom: 1rem;">
                        ${score.toFixed(2)}
                    </div>
                    <div style="font-size: 18px; color: var(--text-secondary); margin-bottom: 1rem;">
                        ${strength} Correlation
                    </div>
                    <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1.5rem;">
                        <div style="padding: 0.5rem 1rem; border-radius: 8px; background: #10b981; color: white;">
                            Weak (0.0-0.4)
                        </div>
                        <div style="padding: 0.5rem 1rem; border-radius: 8px; background: #f59e0b; color: white;">
                            Medium (0.4-0.7)
                        </div>
                        <div style="padding: 0.5rem 1rem; border-radius: 8px; background: #ef4444; color: white;">
                            Strong (0.7+)
                        </div>
                    </div>
                </div>
            `;
        }

        console.log('✅ Correlation analysis loaded');

    } catch (error) {
        console.error('Error loading correlation analysis:', error);

        // Show error state
        const heatmapEl = document.getElementById('correlationHeatmap');
        if (heatmapEl) {
            heatmapEl.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading correlation data</p>
                </div>
            `;
        }
    }
}

// ==================== MODEL COMPARISON ====================

async function loadModelComparison() {
    console.log('🤖 Loading model comparison...');

    try {
        const response = await fetch('/api/monitoring/metrics/compare');
        const data = await response.json();

        if (data.status !== 'success') {
            console.error('API error:', data);
            return;
        }

        const models = data.comparison;
        const modelNames = Object.keys(models);
        const accuracies = modelNames.map(n => models[n].accuracy * 100);
        const precisions = modelNames.map(n => models[n].precision * 100);
        const recalls = modelNames.map(n => models[n].recall * 100);
        const f1Scores = modelNames.map(n => models[n].f1_score * 100);

        // Update card for TF-IDF (shown as "Random Forest" in old UI)
        if (models['TF-IDF + Random Forest']) {
            const m = models['TF-IDF + Random Forest'];
            if (document.getElementById('rfAccuracy'))
                document.getElementById('rfAccuracy').textContent = (m.accuracy * 100).toFixed(1) + '%';
            if (document.getElementById('rfPrecision'))
                document.getElementById('rfPrecision').textContent = (m.precision * 100).toFixed(1) + '%';
            if (document.getElementById('rfRecall'))
                document.getElementById('rfRecall').textContent = (m.recall * 100).toFixed(1) + '%';
        }

        // Create charts with explicit container sizing
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true, position: 'top' } },
            scales: { y: { beginAtZero: false, min: 85, max: 100 } }
        };

        // Accuracy Chart
        const accCtx = document.getElementById('modelAccuracyChart');
        if (accCtx) {
            accCtx.parentElement.style.height = '300px';
            if (window.modelAccuracyChartInstance) window.modelAccuracyChartInstance.destroy();
            window.modelAccuracyChartInstance = new Chart(accCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: modelNames,
                    datasets: [{ label: 'Accuracy (%)', data: accuracies, backgroundColor: ['#667eea', '#f59e0b', '#10b981'] }]
                },
                options: chartOptions
            });
        }

        // Precision vs Recall Chart  
        const prCtx = document.getElementById('precisionRecallChart');
        if (prCtx) {
            prCtx.parentElement.style.height = '300px';
            if (window.precisionRecallChartInstance) window.precisionRecallChartInstance.destroy();
            window.precisionRecallChartInstance = new Chart(prCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: modelNames,
                    datasets: [
                        { label: 'Precision (%)', data: precisions, backgroundColor: '#667eea' },
                        { label: 'Recall (%)', data: recalls, backgroundColor: '#10b981' }
                    ]
                },
                options: chartOptions
            });
        }

        // F1 Score Chart
        const f1Ctx = document.getElementById('f1ScoreChart');
        if (f1Ctx) {
            f1Ctx.parentElement.style.height = '300px';
            if (window.f1ScoreChartInstance) window.f1ScoreChartInstance.destroy();
            window.f1ScoreChartInstance = new Chart(f1Ctx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: modelNames,
                    datasets: [{ label: 'F1 Score (%)', data: f1Scores, backgroundColor: ['#667eea', '#f59e0b', '#10b981'] }]
                },
                options: chartOptions
            });
        }

        console.log('✅ Model comparison loaded with charts');
    } catch (error) {
        console.error('Error loading model comparison:', error);
    }
}

// ==================== VIRUSTOTAL INTEGRATION ====================

async function checkEmailDomainReputation(email) {
    try {
        // Extract domain from email
        const domain = email.split('@')[1];
        if (!domain) return;

        const response = await fetch(`/api/virustotal/check-domain/${domain}`);
        const data = await response.json();

        // Show VirusTotal card
        const vtCard = document.getElementById('virusTotalEmailCard');
        vtCard.style.display = 'block';

        // Update domain info
        document.getElementById('vtEmailDomain').textContent = domain;

        // Update reputation badge - match BERT/FastText/TF-IDF badge styling
        const vtBadge = document.getElementById('vtEmailBadge');
        const maliciousCount = data.malicious || 0;
        const suspiciousCount = data.suspicious || 0;

        // Clear any inline styles and classes first
        // Reset to let CSS classes work
        vtBadge.style = '';

        if (maliciousCount > 0) {
            vtBadge.textContent = '🚨 MALICIOUS';
            vtBadge.className = 'result-badge badge-danger';
        } else if (suspiciousCount > 0) {
            vtBadge.textContent = '⚠️ SUSPICIOUS';
            vtBadge.className = 'result-badge badge-warning';
        } else {
            vtBadge.textContent = ' CLEAN';
            vtBadge.className = 'result-badge badge-success';
        }

        // Update reputation details
        document.getElementById('vtEmailReputation').textContent = data.reputation || 'Unknown';
        document.getElementById('vtEmailMalicious').textContent = maliciousCount;
        document.getElementById('vtEmailSuspicious').textContent = suspiciousCount;

        // Update details (Fix for stuck "Checking..." message)
        const detailsDiv = document.getElementById('vtEmailDetails');
        if (data.categories && Object.keys(data.categories).length > 0) {
            let detailsHtml = '<ul style="list-style: none; padding: 0; font-size: 0.9em; max-height: 150px; overflow-y: auto;">';
            for (const [engine, category] of Object.entries(data.categories)) {
                detailsHtml += `<li style="margin-bottom: 4px;"><strong style="color: var(--text-secondary);">${engine}:</strong> ${category}</li>`;
            }
            detailsHtml += '</ul>';
            detailsDiv.innerHTML = detailsHtml;
        } else {
            detailsDiv.textContent = 'No specific category classification available.';
        }

    } catch (error) {
        console.error('Error checking domain reputation:', error);
    }
}

async function checkIPReputation(ip) {
    try {
        const response = await fetch(`/api/virustotal/check-ip/${ip}`);
        const data = await response.json();

        // Show VirusTotal card
        const vtCard = document.getElementById('virusTotalWebCard');
        vtCard.style.display = 'block';

        // Update IP info
        document.getElementById('vtWebIP').textContent = ip;

        // Update reputation badge - match BERT/FastText/TF-IDF badge styling
        const vtBadge = document.getElementById('vtWebBadge');
        const maliciousCount = data.malicious || 0;
        const suspiciousCount = data.suspicious || 0;

        if (vtBadge) {
            // Clear any inline styles and classes first
            // Reset to let CSS classes work
            vtBadge.style = '';

            if (maliciousCount > 0) {
                vtBadge.textContent = ' MALICIOUS';
                vtBadge.className = 'result-badge badge-danger';
            } else if (suspiciousCount > 0) {
                vtBadge.textContent = '⚠️ SUSPICIOUS';
                vtBadge.className = 'result-badge badge-warning';
            } else {
                vtBadge.textContent = ' CLEAN';
                vtBadge.className = 'result-badge badge-success';
            }
        }

        // Update reputation details
        document.getElementById('vtWebReputation').textContent = data.reputation || 'Unknown';
        document.getElementById('vtWebMalicious').textContent = maliciousCount;
        document.getElementById('vtWebCountry').textContent = data.country || 'Unknown';
        document.getElementById('vtWebASN').textContent = data.asn || 'Unknown';

    } catch (error) {
        console.error('Error checking IP reputation:', error);
    }
}

// ==================== LIME EXPLAINABILITY (XAI) ====================

function displayLimeBreakdown(limeData, modelType = 'tfidf') {
    // Map model types to their actual HTML div IDs
    const divMapping = {
        'bert': {
            section: 'bertLimeBreakdownSection',
            content: 'bertLimeBreakdown'
        },
        'fasttext': {
            section: 'fasttextLimeBreakdownSection',
            content: 'fasttextLimeBreakdown'
        },
        'tfidf': {
            section: 'tfidfLimeBreakdown',
            content: 'tfidfLimeContent'
        }
    };

    const mapping = divMapping[modelType] || divMapping['tfidf'];
    const breakdownSection = document.getElementById(mapping.section);
    const breakdownDiv = document.getElementById(mapping.content);

    if (!limeData || limeData.length === 0) {
        if (breakdownSection) breakdownSection.style.display = 'none';
        return;
    }

    if (breakdownSection) breakdownSection.style.display = 'block';

    // Risk reason mapping
    const riskReasons = {
        // Urgency tactics
        'urgent': 'Urgency tactic', 'immediately': 'Urgency', 'now': 'Urgency',
        'must': 'Urgency requirement', 'required': 'Required action', 'expire': 'Time pressure',
        'final': 'Last chance', 'act': 'Action pressure', 'action': 'Action pressure',

        // Account threats
        'suspended': 'Account threat', 'account': 'Account threat', 'closure': 'Account threat',
        'verify': 'Verification scam', 'confirm': 'Verification scam',

        // Credential theft
        'password': 'Credential theft', 'login': 'Credential theft', 'click': 'Clickbait',
        'here': 'Clickbait link',

        // Financial threats
        'credit': 'Financial theft', 'card': 'Financial theft', 'cvv': 'Credit card theft',
        'ssn': 'Identity theft', 'funds': 'Financial loss', 'bank': 'Impersonation',
        'paypal': 'Brand impersonation',

        // Scams
        'winner': 'Prize scam', 'free': 'Bait offer', 'security': 'Fake alert',

        // Generic/filler words that appear in phishing
        'customer': 'Generic greeting', 'dear': 'Generic greeting', 'user': 'Generic greeting',
        'permanent': 'Threat', 'activity': 'Suspicious activity', 'information': 'Data request',
        'details': 'Data request', 'will': 'Future threat', 'be': 'Conditional threat',
        'on': 'Temporal reference', 'to': 'Action directive', 'your': 'Personal targeting',
        'you': 'Direct address', 'the': 'Common word', 'of': 'Relationship word',
        'december': 'Temporal urgency', 'by': 'Deadline pressure', 'temporary': 'Time pressure',
        'temporary': 'Urgency tactic', 'temporarily': 'Urgency tactic'
    };

    let html = '<div class="lime-breakdown-container">';
    limeData.forEach((item) => {
        const name = item.feature || 'Unknown';
        const contrib = item.contribution || 0;
        const pos = item.positive !== false;
        const display = name.startsWith('word_') ? 'Pattern' :
            name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        // Get reason with fallback
        let reason = riskReasons[name.toLowerCase().trim()];
        if (!reason) {
            if (/^\d+$/.test(name)) reason = 'Numerical pattern';
            else if (name.length <= 3) reason = 'Common word';
            else reason = 'Phishing indicator';
        }
        const reasonText = reason ? ` <span class="risk-reason">(${reason})</span>` : '';

        html += `<div class="lime-feature-bar">
            <div class="lime-feature-label">
                <span class="lime-feature-name">${display}${reasonText}</span>
                <span class="lime-feature-value">${contrib.toFixed(1)}%</span>
            </div>
            <div class="lime-progress-track">
                <div class="lime-progress-fill ${pos ? 'positive' : 'negative'}" 
                     style="width: ${Math.min(contrib, 100)}%"></div>
            </div>
        </div>`;
    });
    html += '</div>';
    if (breakdownDiv) breakdownDiv.innerHTML = html;
}

// ==================== SETTINGS MANAGEMENT ====================

async function loadSettings() {
    console.log('⚙️ Loading settings...');

    try {
        const response = await fetch('/api/settings');
        if (!response.ok) throw new Error('Failed to load settings');

        const settings = await response.json();
        console.log('⚙️ Settings loaded:', settings);

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

        // APPLY DARK MODE THEME VISUALLY
        if (settings.dark_mode === 'true') {
            document.body.classList.add('dark-mode');
            const themeToggleBtn = document.getElementById('themeToggle');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            }
            // Sync with localStorage
            localStorage.setItem('darkMode', 'true');
        } else {
            document.body.classList.remove('dark-mode');
            const themeToggleBtn = document.getElementById('themeToggle');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            }
            // Sync with localStorage
            localStorage.setItem('darkMode', 'false');
        }

    } catch (error) {
        console.error('⚙️ Error loading settings:', error);
    }
}

async function saveSettings() {
    console.log('⚙️ Saving settings...');

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

        // APPLY DARK MODE IMMEDIATELY
        const darkModeEnabled = settings.dark_mode === 'true';
        if (darkModeEnabled) {
            document.body.classList.add('dark-mode');
            const themeToggleBtn = document.getElementById('themeToggle');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            }
        } else {
            document.body.classList.remove('dark-mode');
            const themeToggleBtn = document.getElementById('themeToggle');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            }
        }

        alert('✅ Settings saved successfully!');

    } catch (error) {
        console.error('⚙️ Error saving settings:', error);
        alert('⚙️ Failed to save settings: ' + error.message);
    }
}

async function resetSettings() {
    if (!confirm('Reset all settings to default values?')) {
        return;
    }

    console.log('⚙️ Resetting settings...');

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

        console.log('⚙️ Settings reset to defaults');
        alert('⚙️ Settings reset to defaults!');

    } catch (error) {
        console.error('⚙️ Error resetting settings:', error);
        alert('⚙️ Failed to reset settings: ' + error.message);
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

    // Dark Mode toggle - immediate visual feedback
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('dark-mode');
                const themeToggleBtn = document.getElementById('themeToggle');
                if (themeToggleBtn) {
                    themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
                }
            } else {
                document.body.classList.remove('dark-mode');
                const themeToggleBtn = document.getElementById('themeToggle');
                if (themeToggleBtn) {
                    themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
                }
            }
        });
    }

    // Language toggle - immediate visual feedback
    const languageToggle = document.getElementById('languageToggle');
    if (languageToggle) {
        languageToggle.addEventListener('change', (e) => {
            // Toggle language: checked = TR, unchecked = EN
            const newLang = e.target.checked ? 'tr' : 'en';
            currentLang = newLang;
            localStorage.setItem('language', newLang);

            // Update header button
            const langBtn = document.getElementById('langToggle');
            if (langBtn) {
                langBtn.innerHTML = `<span>${newLang.toUpperCase()}</span>`;
            }

            // Translate page content
            translatePage(newLang);
        });

        // Initialize checkbox based on current language
        languageToggle.checked = (currentLang === 'tr');
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






