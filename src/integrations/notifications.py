"""
Notification system for threat alerts
Supports Email (SMTP) and Slack webhooks
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    SMTP email notifier for threat alerts
    """
    
    def __init__(self, 
                 smtp_host: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 smtp_user: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 from_email: Optional[str] = None):
        """
        Initialize email notifier
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (587 for TLS, 465 for SSL)
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
        """
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST')
        self.smtp_port = int(smtp_port or os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = from_email or os.getenv('SMTP_FROM_EMAIL', self.smtp_user)
        
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])
        
        if not self.enabled:
            logger.warning("Email notifications not configured. Check SMTP environment variables.")
    
    def send_alert(self, 
                   to_emails: List[str], 
                   subject: str, 
                   threat_data: Dict,
                   severity: str = 'HIGH') -> bool:
        """
        Send threat alert email
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject line
            threat_data: Dict containing threat details
            severity: Alert severity (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            logger.warning("Email notifications not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email  # type: ignore[assignment]
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[{severity}] {subject}"
            
            # HTML email body
            html_body = self._generate_html_body(threat_data, severity)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Plain text fallback
            text_body = self._generate_text_body(threat_data, severity)
            msg.attach(MIMEText(text_body, 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:  # type: ignore[arg-type]
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)  # type: ignore[arg-type]
                server.send_message(msg)
            
            logger.info(f"Alert email sent to {to_emails}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _generate_html_body(self, threat_data: Dict, severity: str) -> str:
        """Generate HTML email body"""
        severity_colors = {
            'LOW': '#3498db',
            'MEDIUM': '#f39c12',
            'HIGH': '#e67e22',
            'CRITICAL': '#e74c3c'
        }
        
        color = severity_colors.get(severity, '#95a5a6')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px; }}
                .content {{ padding: 20px; background-color: #f4f4f4; border-radius: 5px; margin-top: 10px; }}
                .field {{ margin: 10px 0; }}
                .field-label {{ font-weight: bold; color: #333; }}
                .field-value {{ color: #666; }}
                .footer {{ margin-top: 20px; padding: 10px; background-color: #ecf0f1; border-radius: 5px; font-size: 12px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🚨 Threat Detection Alert [{severity}]</h2>
                <p>Detected at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="content">
                <h3>Threat Details:</h3>
        """
        
        for key, value in threat_data.items():
            if isinstance(value, dict):
                html += f"<div class='field'><span class='field-label'>{key}:</span><pre>{value}</pre></div>"
            else:
                html += f"<div class='field'><span class='field-label'>{key}:</span> <span class='field-value'>{value}</span></div>"
        
        html += """
            </div>
            
            <div class="footer">
                <p>This is an automated alert from Unified Cyber Threat Detection System.</p>
                <p>Please review and take appropriate action.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_text_body(self, threat_data: Dict, severity: str) -> str:
        """Generate plain text email body"""
        text = f"""
THREAT DETECTION ALERT [{severity}]
========================================

Detected at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Threat Details:
---------------
"""
        
        for key, value in threat_data.items():
            text += f"\n{key}: {value}"
        
        text += """

----------------------------------------
This is an automated alert from Unified Cyber Threat Detection System.
Please review and take appropriate action.
"""
        
        return text


class SlackNotifier:
    """
    Slack webhook notifier for threat alerts
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Slack notifier
        
        Args:
            webhook_url: Slack incoming webhook URL
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            logger.warning("Slack notifications not configured. Set SLACK_WEBHOOK_URL.")
    
    def send_alert(self, 
                   channel: Optional[str],
                   threat_data: Dict,
                   severity: str = 'HIGH') -> bool:
        """
        Send threat alert to Slack
        
        Args:
            channel: Slack channel (optional, overrides webhook default)
            threat_data: Dict containing threat details
            severity: Alert severity (LOW, MEDIUM, HIGH, CRITICAL)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            logger.warning("Slack notifications not configured")
            return False
        
        try:
            # Severity emoji and color mapping
            severity_config = {
                'LOW': {'emoji': ':large_blue_circle:', 'color': '#3498db'},
                'MEDIUM': {'emoji': ':large_yellow_circle:', 'color': '#f39c12'},
                'HIGH': {'emoji': ':large_orange_circle:', 'color': '#e67e22'},
                'CRITICAL': {'emoji': ':red_circle:', 'color': '#e74c3c'}
            }
            
            config = severity_config.get(severity, severity_config['MEDIUM'])
            
            # Build Slack message
            payload = {
                'text': f"{config['emoji']} *Threat Detection Alert [{severity}]*",
                'attachments': [{
                    'color': config['color'],
                    'fields': [
                        {
                            'title': key.replace('_', ' ').title(),
                            'value': str(value),
                            'short': len(str(value)) < 40
                        }
                        for key, value in threat_data.items()
                    ],
                    'footer': 'Unified Cyber Threat Detection System',
                    'ts': int(datetime.utcnow().timestamp())
                }]
            }
            
            if channel:
                payload['channel'] = channel
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,  # type: ignore[arg-type]
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Alert sent to Slack: {severity}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False


# Global singleton instances
_email_notifier = None
_slack_notifier = None

def get_email_notifier() -> EmailNotifier:
    """Get or create email notifier singleton"""
    global _email_notifier
    if _email_notifier is None:
        _email_notifier = EmailNotifier()
    return _email_notifier

def get_slack_notifier() -> SlackNotifier:
    """Get or create Slack notifier singleton"""
    global _slack_notifier
    if _slack_notifier is None:
        _slack_notifier = SlackNotifier()
    return _slack_notifier
