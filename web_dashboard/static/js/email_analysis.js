
// ==================== EMAIL ANALYSIS WITH LIME ====================

async function analyzeEmail() {
    const subject = document.getElementById('emailSubject').value;
    const from = document.getElementById('emailFrom').value;
    const body = document.getElementById('emailBody').value;

    if (!body) {
        alert('Please enter email content');
        return;
    }

    const loadingDiv = document.getElementById('emailLoading');
    const resultsDiv = document.getElementById('emailResults');

    loadingDiv.style.display = 'block';
    resultsDiv.style.display = 'none';

    try {
        // Analyze with all 3 models in parallel
        const [bertResult, fasttextResult, tfidfResult] = await Promise.all([
            fetch('/api/email/analyze/bert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_subject: subject,
                    email_content: body
                })
            }).then(r => r.json()),

            fetch('/api/email/analyze/fasttext', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_subject: subject,
                    email_content: body
                })
            }).then(r => r.json()),

            fetch('/api/email/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email_subject: subject,
                    email_content: body
                })
            }).then(r => r.json())
        ]);

        loadingDiv.style.display = 'none';

        displayEmailResults({
            bert: bertResult,
            fasttext: fasttextResult,
            tfidf: tfidfResult,
            keywords: [] // Will be extracted from models
        });

    } catch (error) {
        console.error('Email analysis error:', error);
        loadingDiv.style.display = 'none';
        alert('Analysis failed: ' + error.message);
    }
}

function displayEmailResults(results) {
    const resultsDiv = document.getElementById('emailResults');

    // Display BERT results
    displayModelResult('bert', results.bert, results.keywords);

    // Display FastText results
    displayModelResult('fasttext', results.fasttext, results.keywords);

    // Display TF-IDF results
    displayModelResult('tfidf', results.tfidf, results.keywords);

    // Display LIME Breakdown for all models (if available)
    if (results.bert && results.bert.lime_breakdown && results.bert.lime_breakdown.length > 0) {
        displayLimeBreakdown(results.bert.lime_breakdown, 'bert');
    }

    if (results.fasttext && results.fasttext.lime_breakdown && results.fasttext.lime_breakdown.length > 0) {
        displayLimeBreakdown(results.fasttext.lime_breakdown, 'fasttext');
    }

    if (results.tfidf && results.tfidf.lime_breakdown && results.tfidf.lime_breakdown.length > 0) {
        displayLimeBreakdown(results.tfidf.lime_breakdown, 'tfidf');
    }

    // Check VirusTotal reputation for email domain
    const emailFrom = document.getElementById('emailFrom').value;
    if (emailFrom) {
        checkEmailDomainReputation(emailFrom);
    }

    resultsDiv.style.display = 'block';
}

function displayModelResult(modelType, result, keywords) {
    if (!result) return;

    const isPhishing = result.prediction === 'phishing' || result.label === 'phishing';
    const confidence = result.confidence || 0;
    const score = result.score || result.phishing_score || 0;
    const riskLevel = result.risk_level || 'low';

    // Update badge
    const badge = document.getElementById(`${modelType}ResultBadge`);
    if (badge) {
        badge.textContent = isPhishing ? '🚨 PHISHING' : '✅ LEGITIMATE';
        badge.style.background = isPhishing ? '#ef4444' : '#10b981';
    }

    // Update prediction
    const predEl = document.getElementById(`${modelType}Prediction`);
    if (predEl) {
        predEl.textContent = isPhishing ? 'Phishing' : 'Legitimate';
    }

    // Update confidence
    const confEl = document.getElementById(`${modelType}Confidence`);
    if (confEl) {
        confEl.textContent = `${(confidence * 100).toFixed(1)}%`;
    }

    // Update risk level
    const riskEl = document.getElementById(`${modelType}RiskLevel`);
    if (riskEl) {
        const riskText = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);
        const riskScore = (score * 100).toFixed(1);
        riskEl.textContent = `${riskText} (${riskScore}%)`;
    }

    // Update processing time
    if (result.processing_time_ms) {
        const timeEl = document.getElementById(`${modelType}ProcessingTime`);
        if (timeEl) {
            timeEl.textContent = `${result.processing_time_ms.toFixed(1)}ms`;
        }
    }

    // Update indicators
    const indicatorsDiv = document.getElementById(`${modelType}Indicators`);
    if (indicatorsDiv && result.phishing_keywords) {
        displayKeywords(indicatorsDiv, result.phishing_keywords);
    }
}

function displayLimeBreakdown(limeData, modelType = 'tfidf') {
    const breakdownSection = document.getElementById(`${modelType}LimeBreakdownSection`);
    const breakdownDiv = document.getElementById(`${modelType}LimeBreakdown`);

    if (!limeData || limeData.length === 0) {
        if (breakdownSection) {
            breakdownSection.style.display = 'none';
        }
        return;
    }

    // Show section
    if (breakdownSection) {
        breakdownSection.style.display = 'block';
    }

    // Risk reason mapping for common phishing keywords
    const riskReasons = {
        'urgent': 'Urgency tactic',
        'suspended': 'Account threat',
        'verify': 'Verification scam',
        'account': 'Account threat',
        'password': 'Credential theft',
        'click': 'Clickbait tactic',
        'here': 'Clickbait link',
        'immediately': 'Urgency pressure',
        'expire': 'Time pressure',
        'confirm': 'Verification scam',
        'security': 'Fake security alert',
        'update': 'Fake update request',
        'ssn': 'Identity theft',
        'credit': 'Financial theft',
        'card': 'Financial theft',
        'bank': 'Financial impersonation',
        'paypal': 'Brand impersonation',
        'permanent': 'Consequence threat',
        'closure': 'Account threat',
        'funds': 'Financial loss threat',
        'number': 'Data harvesting',
        'information': 'Data harvesting',
        'details': 'Data harvesting',
        'customer': 'Generic greeting',
        'dear': 'Generic greeting',
        'user': 'Generic greeting',
        'login': 'Credential theft',
        'cvv': 'Credit card theft',
        'winner': 'Prize scam',
        'congratulations': 'Prize scam',
        'claim': 'Prize scam',
        'free': 'Bait offer',
        'limited': 'Scarcity tactic',
        'offer': 'Promotional bait',
        'act': 'Action pressure',
        'now': 'Time pressure',
        'final': 'Last chance pressure',
        'warning': 'Scare tactic',
        'result': 'Consequence',
        'failure': 'Consequence threat'
    };

    // Build HTML for breakdown
    let html = '<div class="lime-breakdown-container">';

    limeData.forEach((item, index) => {
        const featureName = item.feature || 'Unknown';
        const contribution = item.contribution || 0;
        const isPositive = item.positive !== false;

        // Clean up feature name
        const displayName = featureName.startsWith('word_') ?
            featureName.replace(/^word_\d+$/, 'Content Pattern') :
            featureName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

        // Get risk reason if available
        const lowerFeature = featureName.toLowerCase().trim();
        const riskReason = riskReasons[lowerFeature] || '';
        const reasonText = riskReason ? ` <span class="risk-reason">(${riskReason})</span>` : '';

        html += `
            <div class="lime-feature-bar">
                <div class="lime-feature-label">
                    <span class="lime-feature-name">${displayName}${reasonText}</span>
                    <span class="lime-feature-value">${contribution.toFixed(1)}%</span>
                </div>
                <div class="lime-progress-track">
                    <div class="lime-progress-fill ${isPositive ? 'positive' : 'negative'}" 
                         style="width: ${Math.min(contribution, 100)}%">
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    if (breakdownDiv) {
        breakdownDiv.innerHTML = html;
    }
}

function displayKeywords(container, keywords) {
    if (!keywords || keywords.length === 0) {
        container.innerHTML = '<p>No suspicious keywords detected</p>';
        return;
    }

    let html = '';
    keywords.forEach(kw => {
        const severity = kw.severity || 'low';
        const reason = kw.reason || 'Suspicious pattern';
        html += `
            <div class="keyword-item">
                <strong>"${kw.keyword}"</strong>
                <span class="keyword-reason">${reason} (${severity} severity)</span>
            </div>
        `;
    });
    container.innerHTML = html;
}

function checkEmailDomainReputation(email) {
    // Extract domain from email
    const domain = email.split('@')[1];
    if (!domain) return;

    const vtSection = document.getElementById('vtEmailSection');
    const vtBadge = document.getElementById('vtEmailBadge');
    const vtDomain = document.getElementById('vtEmailDomain');
    const vtReputation = document.getElementById('vtEmailReputation');
    const vtMalicious = document.getElementById('vtEmailMalicious');
    const vtSuspicious = document.getElementById('vtEmailSuspicious');
    const vtDetails = document.getElementById('vtEmailDetails');

    if (vtSection) vtSection.style.display = 'block';
    if (vtDetails) vtDetails.textContent = 'Checking domain reputation...';

    // Add timeout to prevent indefinite loading
    const timeoutId = setTimeout(() => {
        if (vtDetails) {
            vtDetails.textContent = 'VirusTotal API timeout - check manually';
        }
        if (vtBadge) {
            vtBadge.textContent = '⏳ TIMEOUT';
            vtBadge.style.background = '#f59e0b';
        }
    }, 10000); // 10 second timeout

    fetch(`/api/virustotal/domain/${domain}`)
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error('API unavailable');
            return response.json();
        })
        .then(data => {
            if (vtDomain) vtDomain.textContent = domain;
            if (vtReputation) vtReputation.textContent = data.reputation || 'Unknown';
            if (vtMalicious) vtMalicious.textContent = data.malicious || 0;
            if (vtSuspicious) vtSuspicious.textContent = data.suspicious || 0;

            const malCount = parseInt(data.malicious) || 0;
            if (vtBadge) {
                if (malCount > 0) {
                    vtBadge.textContent = '🔴 MALICIOUS';
                    vtBadge.style.background = '#ef4444';
                } else {
                    vtBadge.textContent = '✅ CLEAN';
                    vtBadge.style.background = '#10b981';
                }
            }
            if (vtDetails) vtDetails.textContent = 'Analysis complete';
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('VirusTotal error:', error);
            if (vtDetails) {
                vtDetails.textContent = 'VirusTotal API unavailable';
            }
            if (vtBadge) {
                vtBadge.textContent = '⚠️ UNAVAILABLE';
                vtBadge.style.background = '#6b7280';
            }
        });
}

// Attach to button
const analyzeBtn = document.getElementById('analyzeEmailBtn');
if (analyzeBtn) {
    analyzeBtn.addEventListener('click', analyzeEmail);
}
