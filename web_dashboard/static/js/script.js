async function loadDemo(demoType) {
    try {
        const response = await fetch(`/api/demo/${demoType}`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('emailContent').value = data.email_content || '';
            document.getElementById('emailSender').value = data.email_sender || '';
            document.getElementById('emailSubject').value = data.email_subject || '';
            document.getElementById('ipAddress').value = data.ip_address || '';
            document.getElementById('requestCount').value = data.request_count || 10;
            document.getElementById('errorRate').value = data.error_rate || 5;
            
            // Show demo loaded message
            showNotification(`${demoType.toUpperCase()} demo data loaded!`, 'success');
        } else {
            showNotification('Failed to load demo data', 'error');
        }
    } catch (error) {
        console.error('Demo load error:', error);
        showNotification('Error loading demo data', 'error');
    }
}

async function analyzeThreat() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = '🔍 Analyzing...';
    
    // Show loading
    document.getElementById('resultsContent').innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <h3>🔍 Analyzing Threats...</h3>
            <p>Running AI models and correlation analysis...</p>
        </div>
    `;
    
    try {
        const requestData = {
            email_content: document.getElementById('emailContent').value,
            email_sender: document.getElementById('emailSender').value,
            email_subject: document.getElementById('emailSubject').value,
            ip_address: document.getElementById('ipAddress').value,
            request_count: parseInt(document.getElementById('requestCount').value) || 0,
            error_rate: parseFloat(document.getElementById('errorRate').value) || 0
        };
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const results = await response.json();
        
        if (response.ok && results.success) {
            displayResults(results);
        } else {
            showError(results.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError('Network error occurred');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = '🔍 Analyze Threats';
    }
}

function displayResults(results) {
    const riskColor = getRiskColor(results.unified_risk_score);
    const threatClass = `threat-${results.threat_level.toLowerCase()}`;
    
    let html = `
        <div class="risk-score-card" style="background: ${riskColor};">
            <div class="risk-score">${results.unified_risk_score}</div>
            <div class="risk-label">Unified Risk Score</div>
            <div style="margin-top: 10px;">
                <span class="threat-indicator ${threatClass}">${results.threat_level}</span>
            </div>
        </div>
    `;
    
    // Email Analysis Section
    if (results.email_analysis) {
        const emailPrediction = results.email_analysis.prediction;
        const emailConfidence = results.email_analysis.confidence;
        const predictionClass = emailPrediction === 'Phishing' ? 'threat-high' : 'threat-low';
        
        html += `
            <div class="analysis-section">
                <h3>📧 Email Threat Analysis</h3>
                <div style="margin-bottom: 15px;">
                    <strong>Prediction:</strong> 
                    <span class="threat-indicator ${predictionClass}">${emailPrediction}</span>
                    <strong>Confidence:</strong> ${emailConfidence.toFixed(1)}%
                </div>
                <div><strong>Risk Factors:</strong></div>
                <ul class="feature-list">
        `;
        
        results.email_analysis.risk_factors?.forEach(factor => {
            html += `<li>• ${factor}</li>`;
        });
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // Web Analysis Section
    if (results.web_analysis) {
        const webRiskClass = `threat-${results.web_analysis.risk_level.toLowerCase()}`;
        
        html += `
            <div class="analysis-section">
                <h3>🌐 Web Traffic Analysis</h3>
                <div style="margin-bottom: 15px;">
                    <strong>Risk Level:</strong> 
                    <span class="threat-indicator ${webRiskClass}">${results.web_analysis.risk_level}</span>
                    <strong>Anomaly Score:</strong> ${results.web_analysis.anomaly_score.toFixed(3)}
                </div>
        `;
        
        if (results.web_analysis.attack_patterns?.length > 0) {
            html += `
                <div><strong>Attack Patterns:</strong></div>
                <ul class="feature-list">
            `;
            results.web_analysis.attack_patterns.forEach(pattern => {
                html += `<li>⚡ ${pattern}</li>`;
            });
            html += `</ul>`;
        }
        
        if (results.web_analysis.behavioral_insights?.length > 0) {
            html += `
                <div style="margin-top: 15px;"><strong>Behavioral Insights:</strong></div>
                <ul class="feature-list">
            `;
            results.web_analysis.behavioral_insights.forEach(insight => {
                html += `<li>💡 ${insight}</li>`;
            });
            html += `</ul>`;
        }
        
        html += `</div>`;
    }
    
    // Correlation Analysis
    if (results.correlation_analysis?.indicators?.length > 0) {
        html += `
            <div class="analysis-section">
                <h3>🔗 Correlation Analysis</h3>
                <div><strong>Coordinated Attack Indicators:</strong></div>
                <ul class="feature-list">
        `;
        
        results.correlation_analysis.indicators.forEach(indicator => {
            html += `<li>🎯 ${indicator.type}: ${indicator.description}</li>`;
        });
        
        html += `
                </ul>
            </div>
        `;
    }
    
    // Recommendations
    if (results.recommendations) {
        html += `
            <div class="recommendations">
                <h3>🛠️ Security Recommendations</h3>
        `;
        
        ['immediate', 'short_term', 'long_term'].forEach(category => {
            const recs = results.recommendations[category];
            if (recs && recs.length > 0) {
                const categoryNames = {
                    'immediate': '🚨 Immediate Actions',
                    'short_term': '📅 Short-term Actions', 
                    'long_term': '🔮 Long-term Improvements'
                };
                
                html += `<h4>${categoryNames[category]}</h4>`;
                recs.forEach(rec => {
                    html += `<div class="recommendation-item">${rec}</div>`;
                });
            }
        });
        
        html += `</div>`;
    }
    
    document.getElementById('resultsContent').innerHTML = html;
}

function showError(message) {
    document.getElementById('resultsContent').innerHTML = `
        <div class="loading">
            <h3 style="color: #e74c3c;">❌ Analysis Error</h3>
            <p>${message}</p>
            <p style="margin-top: 15px;">Please check your input and try again.</p>
        </div>
    `;
}

function showNotification(message, type) {
    // Simple notification system
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function getRiskColor(score) {
    if (score >= 80) return 'linear-gradient(135deg, #c0392b, #e74c3c)';
    if (score >= 60) return 'linear-gradient(135deg, #d35400, #e67e22)';
    if (score >= 40) return 'linear-gradient(135deg, #f39c12, #f1c40f)';
    return 'linear-gradient(135deg, #27ae60, #2ecc71)';
}

// Auto-load demo data on page load
window.addEventListener('load', function() {
    setTimeout(() => loadDemo('phishing'), 1000);
});
