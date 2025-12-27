#!/usr/bin/env python3
"""
Demo Data Generator CLI Script
Generates realistic test data for the Unified Cyber Threat Detection System

Usage:
    python scripts/generate_demo_data.py
    
    # Inside Docker:
    docker exec threat-detection-api python scripts/generate_demo_data.py
    
    # With custom parameters:
    python scripts/generate_demo_data.py --emails=50 --weblogs=30 --days=7
"""

import requests
import sys
import argparse


def generate_demo_data(base_url='http://localhost:5000', email_count=25, web_count=25, days_back=30):
    """
    Call the demo data generation API endpoint
    
    Args:
        base_url: Base URL of the API (default: http://localhost:5000)
        email_count: Number of email predictions to generate (default: 25)
        web_count: Number of web log predictions to generate (default: 25)
        days_back: Number of days to spread data over (default: 30)
    
    Returns:
        bool: True if successful, False otherwise
    """
    endpoint = f"{base_url}/api/demo/generate"
    payload = {
        'email_count': email_count,
        'web_count': web_count,
        'days_back': days_back
    }
    
    try:
        print(f"📊 Generating demo data...")
        print(f"   - Email predictions: {email_count}")
        print(f"   - Web log predictions: {web_count}")
        print(f"   - Time span: Last {days_back} days")
        print()
        
        response = requests.post(endpoint, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Demo data generated successfully!")
            print()
            print(f"Created:")
            print(f"  • {result['generated']['emails']} email predictions")
            print(f"  • {result['generated']['web_logs']} web log predictions")
            print(f"  • Total: {result['generated']['total']} records")
            print()
            print(f"Message: {result.get('message', 'Success')}")
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API")
        print(f"   Make sure the server is running at {base_url}")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        print("   The server might be overloaded or not responding")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point for the CLI script"""
    parser = argparse.ArgumentParser(
        description='Generate demo data for Cyber Threat Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (25 emails, 25 web logs):
  python scripts/generate_demo_data.py
  
  # Custom counts:
  python scripts/generate_demo_data.py --emails=50 --weblogs=30
  
  # Recent data only (last 7 days):
  python scripts/generate_demo_data.py --days=7
  
  # Inside Docker container:
  docker exec threat-detection-api python scripts/generate_demo_data.py
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:5000',
        help='Base URL of the API (default: http://localhost:5000)'
    )
    parser.add_argument(
        '--emails',
        type=int,
        default=25,
        help='Number of email predictions to generate (default: 25)'
    )
    parser.add_argument(
        '--weblogs',
        type=int,
        default=25,
        help='Number of web log predictions to generate (default: 25)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to spread data over (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.emails < 0 or args.weblogs < 0:
        print("❌ Error: Email and weblog counts must be positive")
        sys.exit(1)
    
    if args.days < 1 or args.days > 365:
        print("❌ Error: Days must be between 1 and 365")
        sys.exit(1)
    
    # Generate demo data
    success = generate_demo_data(
        base_url=args.url,
        email_count=args.emails,
        web_count=args.weblogs,
        days_back=args.days
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
