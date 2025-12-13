#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Configuration Wizard
Interactive setup for production credentials
"""
import os
import sys
import secrets
import getpass
import re
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}[OK]{Colors.END} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {text}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}[ERROR]{Colors.END} {text}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}[INFO]{Colors.END} {text}")

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_api_key(key):
    """Validate API key format (alphanumeric, 32+ chars)"""
    return len(key) >= 32 and key.replace('-', '').replace('_', '').isalnum()

def generate_secret_key():
    """Generate strong secret key"""
    return secrets.token_hex(32)

def read_env_file():
    """Read current .env file"""
    env_path = Path('.env')
    if not env_path.exists():
        return {}
    
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def write_env_file(env_vars):
    """Write updated .env file"""
    env_path = Path('.env')
    
    # Read original file to preserve comments and structure
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update values
    new_lines = []
    for line in lines:
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in env_vars:
                new_lines.append(f"{key}={env_vars[key]}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Backup original
    backup_path = env_path.with_suffix('.env.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print_info(f"Backup created: {backup_path}")
    
    # Write new file
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print_success(f"Configuration saved to {env_path}")

def configure_virustotal():
    """Configure VirusTotal API"""
    print_header("1. VirusTotal API Configuration")
    
    print("Get your free API key:")
    print("1. Go to: https://www.virustotal.com/")
    print("2. Sign up or login")
    print("3. Profile → API Key")
    print()
    
    api_key = input("Enter VirusTotal API key (or press Enter to skip): ").strip()
    
    if api_key:
        if validate_api_key(api_key):
            print_success("API key validated")
            return api_key
        else:
            print_warning("API key format looks invalid (should be 32+ chars)")
            confirm = input("Use anyway? (y/N): ").strip().lower()
            if confirm == 'y':
                return api_key
    
    print_warning("VirusTotal integration will be disabled")
    return None

def configure_email():
    """Configure Email SMTP"""
    print_header("2. Email SMTP Configuration")
    
    print("Email alerts configuration")
    print("For Gmail: Use App Password (not your regular password)")
    print("Tutorial: https://support.google.com/accounts/answer/185833")
    print()
    
    smtp_server = input("SMTP Server [smtp.gmail.com]: ").strip() or "smtp.gmail.com"
    smtp_port = input("SMTP Port [587]: ").strip() or "587"
    
    smtp_username = input("SMTP Username (email): ").strip()
    if smtp_username and not validate_email(smtp_username):
        print_warning("Email format looks invalid")
    
    smtp_password = getpass.getpass("SMTP Password (hidden): ").strip()
    
    alert_recipients = input("Alert recipients (comma-separated): ").strip()
    
    if smtp_username and smtp_password:
        return {
            'SMTP_SERVER': smtp_server,
            'SMTP_PORT': smtp_port,
            'SMTP_USERNAME': smtp_username,
            'SMTP_PASSWORD': smtp_password,
            'ALERT_EMAIL_RECIPIENTS': alert_recipients or smtp_username
        }
    
    print_warning("Email notifications will be disabled")
    return None

def configure_secret_key():
    """Configure Flask secret key"""
    print_header("3. Flask Secret Key")
    
    current_key = read_env_file().get('SECRET_KEY', '')
    
    if current_key.startswith('dev-'):
        print_warning("Current key is a development key (not secure for production)")
        generate = input("Generate new secure key? (Y/n): ").strip().lower()
        if generate != 'n':
            new_key = generate_secret_key()
            print_success(f"Generated: {new_key[:16]}...{new_key[-8:]}")
            return new_key
    else:
        print_info("Secret key already configured")
        regenerate = input("Generate new key? (y/N): ").strip().lower()
        if regenerate == 'y':
            new_key = generate_secret_key()
            print_success(f"Generated: {new_key[:16]}...{new_key[-8:]}")
            return new_key
    
    return None

def configure_slack():
    """Configure Slack webhook"""
    print_header("4. Slack Webhook (Optional)")
    
    print("Slack notifications setup:")
    print("1. Go to: https://api.slack.com/apps")
    print("2. Create New App → From scratch")
    print("3. Enable 'Incoming Webhooks'")
    print("4. Add webhook to workspace")
    print()
    
    webhook_url = input("Slack Webhook URL (or press Enter to skip): ").strip()
    
    if webhook_url:
        if webhook_url.startswith('https://hooks.slack.com/'):
            channel = input("Slack Channel [#security-alerts]: ").strip() or "#security-alerts"
            print_success("Slack webhook configured")
            return {
                'SLACK_WEBHOOK_URL': webhook_url,
                'SLACK_CHANNEL': channel
            }
        else:
            print_error("Invalid webhook URL format")
    
    print_info("Slack notifications will be disabled")
    return None

def test_configuration():
    """Test the configuration"""
    print_header("5. Configuration Test")
    
    test = input("Test configuration now? (Y/n): ").strip().lower()
    if test == 'n':
        return
    
    print("\nTesting configuration...")
    
    # Test imports
    try:
        from src.integrations.virustotal import get_virustotal_client
        from src.integrations.notifications import get_email_notifier, get_slack_notifier
        from src.utils.cache import get_redis_cache
        print_success("All modules imported successfully")
    except Exception as e:
        print_error(f"Import failed: {e}")
        return
    
    # Test VirusTotal
    try:
        vt = get_virustotal_client()
        if vt.enabled:
            print_success("VirusTotal: Configured")
        else:
            print_warning("VirusTotal: Disabled (API key not set)")
    except Exception as e:
        print_error(f"VirusTotal error: {e}")
    
    # Test Email
    try:
        email = get_email_notifier()
        if email.enabled:
            print_success("Email SMTP: Configured")
        else:
            print_warning("Email SMTP: Disabled (credentials not set)")
    except Exception as e:
        print_error(f"Email error: {e}")
    
    # Test Slack
    try:
        slack = get_slack_notifier()
        if slack.enabled:
            print_success("Slack: Configured")
        else:
            print_info("Slack: Not configured (optional)")
    except Exception as e:
        print_error(f"Slack error: {e}")
    
    # Test Redis
    try:
        cache = get_redis_cache()
        if cache.enabled:
            print_success("Redis Cache: Connected")
        else:
            print_warning("Redis Cache: Not available")
    except Exception as e:
        print_error(f"Redis error: {e}")

def main():
    """Main configuration wizard"""
    print_header("PRODUCTION CONFIGURATION WIZARD")
    print("This wizard will help you configure production credentials")
    print("Press Ctrl+C at any time to cancel")
    
    try:
        # Read current configuration
        env_vars = read_env_file()
        updated = False
        
        # 1. VirusTotal
        vt_key = configure_virustotal()
        if vt_key:
            env_vars['VIRUSTOTAL_API_KEY'] = vt_key
            env_vars['ENABLE_VIRUSTOTAL_INTEGRATION'] = 'True'
            updated = True
        
        # 2. Email
        email_config = configure_email()
        if email_config:
            env_vars.update(email_config)
            updated = True
        
        # 3. Secret Key
        secret_key = configure_secret_key()
        if secret_key:
            env_vars['SECRET_KEY'] = secret_key
            updated = True
        
        # 4. Slack
        slack_config = configure_slack()
        if slack_config:
            env_vars.update(slack_config)
            updated = True
        
        # Save configuration
        if updated:
            print_header("Save Configuration")
            confirm = input("Save changes to .env file? (Y/n): ").strip().lower()
            if confirm != 'n':
                write_env_file(env_vars)
                print_success("Configuration saved successfully!")
                
                # Test configuration
                test_configuration()
                
                print_header("Next Steps")
                print("1. Review .env file for any additional settings")
                print("2. Restart services: docker compose restart")
                print("3. Check logs: docker compose logs -f api")
                print("4. Test API: curl http://localhost:5000/api/health")
                print()
                print_success("Configuration complete! ✅")
            else:
                print_warning("Changes not saved")
        else:
            print_info("No changes made")
    
    except KeyboardInterrupt:
        print("\n")
        print_warning("Configuration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Configuration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
