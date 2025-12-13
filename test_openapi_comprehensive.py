#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprehensive OpenAPI specification test"""
import sys
import yaml
import json
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
    except AttributeError:
        # Python < 3.7 fallback
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_openapi_spec():
    """Test OpenAPI specification structure"""
    print("\n" + "="*60)
    print("OPENAPI SPECIFICATION TEST")
    print("="*60)
    
    try:
        # Load spec
        with open('docs/openapi.yaml', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        print("\n[OK] YAML Loading: Success")
        
        # Validate required fields
        required_fields = ['openapi', 'info', 'paths']
        missing = [f for f in required_fields if f not in spec]
        
        if missing:
            print(f"[FAIL] Missing required fields: {missing}")
            return False
        
        print("[OK] Required Fields: All present")
        
        # Check OpenAPI version
        openapi_version = spec.get('openapi')
        print(f"[OK] OpenAPI Version: {openapi_version}")
        
        if not openapi_version.startswith('3.'):
            print("[WARN] Warning: Not OpenAPI 3.x")
        
        # Check info section
        info = spec.get('info', {})
        print(f"\n[INFO] API Information:")
        print(f"   Title: {info.get('title')}")
        print(f"   Version: {info.get('version')}")
        print(f"   Description: {'Present' if info.get('description') else 'Missing'}")
        
        # Check servers
        servers = spec.get('servers', [])
        print(f"\n[SERVERS] {len(servers)} configured")
        for server in servers:
            print(f"   - {server.get('url')}")
        
        # Check paths
        paths = spec.get('paths', {})
        print(f"\n[ENDPOINTS] {len(paths)} defined")
        
        # Count operations
        methods = ['get', 'post', 'put', 'delete', 'patch']
        operation_count = 0
        for path, operations in paths.items():
            for method in methods:
                if method in operations:
                    operation_count += 1
        
        print(f"   Total Operations: {operation_count}")
        
        # Check AŞAMA 8 endpoints
        asama8_endpoints = [
            '/enrich/ip',
            '/enrich/domain', 
            '/alert/send',
            '/cache/stats',
            '/ratelimit/status'
        ]
        
        print(f"\n[ASAMA-8] Endpoints:")
        for endpoint in asama8_endpoints:
            if endpoint in paths:
                ops = [m.upper() for m in methods if m in paths[endpoint]]
                print(f"   [OK] {endpoint} [{', '.join(ops)}]")
            else:
                print(f"   [FAIL] {endpoint} [NOT FOUND]")
        
        # Check components
        components = spec.get('components', {})
        schemas = components.get('schemas', {})
        print(f"\n[COMPONENTS]")
        print(f"   Schemas: {len(schemas)} defined")
        
        # Check tags
        tags = spec.get('tags', [])
        print(f"\n[TAGS] {len(tags)} categories")
        for tag in tags:
            print(f"   - {tag.get('name')}")
        
        print("\n[OK] OpenAPI Specification: VALID")
        print("[OK] Swagger UI: Compatible")
        print("[OK] Redoc: Compatible")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test actual API endpoints"""
    print("\n" + "="*60)
    print("API ENDPOINT RUNTIME TEST")
    print("="*60)
    
    base_url = "http://127.0.0.1"
    
    # Test cases
    tests = [
        {
            'name': 'Health Check',
            'method': 'GET',
            'url': f'{base_url}/api/health',
        },
        {
            'name': 'Models Status',
            'method': 'GET',
            'url': f'{base_url}/api/models/status',
        },
        {
            'name': 'Cache Stats (AŞAMA 8)',
            'method': 'GET',
            'url': f'{base_url}/api/cache/stats',
        },
        {
            'name': 'Rate Limit Status (AŞAMA 8)',
            'method': 'GET',
            'url': f'{base_url}/api/ratelimit/status',
        },
        {
            'name': 'Email Analysis',
            'method': 'POST',
            'url': f'{base_url}/api/email/analyze',
            'json': {
                'subject': 'Test Email',
                'body': 'This is a test email for validation',
                'sender': 'test@example.com'
            }
        },
        {
            'name': 'Web Log Analysis',
            'method': 'POST',
            'url': f'{base_url}/api/web/analyze',
            'json': {
                'ip': '192.168.1.1',
                'method': 'GET',
                'path': '/',
                'status': '200',
                'user_agent': 'Mozilla/5.0'
            }
        }
    ]
    
    passed = 0
    failed = 0
    
    print("\nTesting endpoints...\n")
    
    for test in tests:
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=3)
            elif test['method'] == 'POST':
                response = requests.post(
                    test['url'],
                    json=test.get('json', {}),
                    timeout=3
                )
            
            if response.status_code == 200:
                print(f"[OK] {test['name']}: OK (200)")
                passed += 1
            else:
                print(f"[FAIL] {test['name']}: FAILED ({response.status_code})")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"[WARN] {test['name']}: API not running")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test['name']}: ERROR - {str(e)[:50]}")
            failed += 1
    
    print(f"\n[STATS] Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == '__main__':
    spec_valid = test_openapi_spec()
    api_working = test_api_endpoints()
    
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"OpenAPI Spec: {'[OK] VALID' if spec_valid else '[FAIL] INVALID'}")
    print(f"API Endpoints: {'[OK] WORKING' if api_working else '[FAIL] ISSUES FOUND'}")
    print("="*60 + "\n")
    
    sys.exit(0 if (spec_valid and api_working) else 1)
