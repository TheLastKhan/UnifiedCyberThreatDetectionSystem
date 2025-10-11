"""
Report Generation Module
"""

import json
from datetime import datetime

class ReportGenerator:
    """Tehdit analizi raporları oluşturan sınıf"""
    
    @staticmethod
    def generate_text_report(analysis_results):
        """Metin formatında rapor oluşturur"""
        report = []
        report.append("=" * 70)
        report.append("UNIFIED THREAT DETECTION PLATFORM - ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {analysis_results.get('timestamp', datetime.now().isoformat())}")
        report.append(f"Unified Risk Score: {analysis_results.get('unified_risk_score', 0)}/100")
        report.append(f"Threat Level: {analysis_results.get('threat_level', 'UNKNOWN')}")
        report.append("")
        
        # Email Analysis
        if analysis_results.get('email_analysis'):
            email = analysis_results['email_analysis']
            report.append("EMAIL THREAT ANALYSIS")
            report.append("-" * 70)
            report.append(f"Prediction: {email.get('prediction', 'N/A')}")
            report.append(f"Confidence: {email.get('confidence', 0):.1f}%")
            report.append("Risk Factors:")
            for factor in email.get('risk_factors', []):
                report.append(f"  • {factor}")
            report.append("")
        
        # Web Analysis
        if analysis_results.get('web_analysis'):
            web = analysis_results['web_analysis']
            report.append("WEB TRAFFIC ANALYSIS")
            report.append("-" * 70)
            report.append(f"Risk Level: {web.get('risk_level', 'N/A')}")
            report.append(f"Anomaly Score: {web.get('anomaly_score', 0):.3f}")
            report.append("Attack Patterns:")
            for pattern in web.get('attack_patterns', []):
                report.append(f"  • {pattern}")
            report.append("")
        
        # Recommendations
        if analysis_results.get('recommendations'):
            recs = analysis_results['recommendations']
            report.append("SECURITY RECOMMENDATIONS")
            report.append("-" * 70)
            
            if recs.get('immediate'):
                report.append("Immediate Actions:")
                for rec in recs['immediate']:
                    report.append(f"  • {rec}")
            
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    @staticmethod
    def generate_json_report(analysis_results):
        """JSON formatında rapor oluşturur"""
        return json.dumps(analysis_results, indent=2, default=str)
    
    @staticmethod
    def save_report(report_content, filepath, format='txt'):
        """Raporu dosyaya kaydeder"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"✅ Report saved to {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False