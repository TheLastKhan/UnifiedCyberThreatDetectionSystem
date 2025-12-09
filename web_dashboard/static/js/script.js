// ==================== DASHBOARD INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupCharts();
    setupEventListeners();
    loadModelsStatus();
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
    item.addEventListener('click', function(e) {
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
    
    // Update breadcrumb
    const breadcrumbMap = {
        'dashboard': 'Dashboard',
        'email-analysis': 'Email Analysis',
        'web-analysis': 'Web Analysis',
        'reports': 'Reports',
        'settings': 'Settings'
    };
    document.getElementById('breadcrumb-text').textContent = breadcrumbMap[pageName] || pageName;
}

// ==================== THEME TOGGLE ====================

document.getElementById('themeToggle').addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    
    this.innerHTML = isDarkMode ? 
        '<i class="fas fa-sun"></i>' : 
        '<i class="fas fa-moon"></i>';
});

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

// ==================== EMAIL ANALYSIS ====================

document.getElementById('analyzeEmailBtn')?.addEventListener('click', analyzeEmail);
document.getElementById('clearEmailBtn')?.addEventListener('click', clearEmailForm);

async function analyzeEmail() {
    const subject = document.getElementById('emailSubject').value;
    const body = document.getElementById('emailBody').value;
    const from = document.getElementById('emailFrom').value;

    if (!body) {
        alert('Please enter email body');
        return;
    }

    try {
        const response = await fetch('/api/email/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: subject,
                body: body,
                sender: from
            })
        });

        const result = await response.json();
        displayEmailResults(result);
    } catch (error) {
        console.error('Error analyzing email:', error);
        alert('Error analyzing email. Check console for details.');
    }
}

function displayEmailResults(result) {
    const resultsDiv = document.getElementById('emailResults');
    
    if (result.model_confidence) {
        const prob = result.model_confidence.phishing_probability;
        const isPhishing = result.model_confidence.prediction === 'phishing';
        
        document.getElementById('emailResultBadge').textContent = 
            isPhishing ? '🚨 PHISHING DETECTED' : '✅ LEGITIMATE';
        document.getElementById('emailResultBadge').style.color = 
            isPhishing ? '#ef4444' : '#10b981';
        
        document.getElementById('emailPrediction').textContent = 
            isPhishing ? 'Phishing' : 'Legitimate';
        
        document.getElementById('emailConfidence').textContent = 
            (prob * 100).toFixed(2) + '%';
        
        document.getElementById('emailRisk').textContent = 
            isPhishing ? 'High Risk' : 'Low Risk';
    }
    
    resultsDiv.style.display = 'block';
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
        
        document.getElementById('webResultBadge').textContent = 
            isAnomaly ? '⚠️ ANOMALY DETECTED' : '✅ NORMAL';
        document.getElementById('webResultBadge').style.color = 
            isAnomaly ? '#f59e0b' : '#10b981';
        
        document.getElementById('webStatus').textContent = 
            isAnomaly ? 'Anomalous' : 'Normal';
        
        document.getElementById('webAnomalyScore').textContent = 
            result.model_analysis.anomaly_score.toFixed(4);
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
    const allLoaded = Object.values(status).every(v => v === true);
    
    if (allLoaded) {
        statusElement.textContent = '✅ System Active (All Models Loaded)';
        document.querySelector('.status-dot').style.background = '#10b981';
    } else {
        statusElement.textContent = '⚠️ Some Models Missing';
        document.querySelector('.status-dot').style.background = '#f59e0b';
    }
}

// ==================== EVENT LISTENERS ====================

function setupEventListeners() {
    // Settings slider
    const thresholdSlider = document.querySelector('input[type="range"]');
    if (thresholdSlider) {
        thresholdSlider.addEventListener('input', function() {
            const value = (this.value / 100).toFixed(2);
            document.getElementById('thresholdValue').textContent = value;
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

console.log('✅ Dashboard scripts loaded successfully');
